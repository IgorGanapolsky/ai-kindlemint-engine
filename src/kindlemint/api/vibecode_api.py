"""
Vibecode API for KindleMint Conversational Interface

FastAPI-based REST API for the vibecoding system, enabling frontend applications
to interact with the conversational book creation system.
"""

import asyncio
import base64
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..agents.vibecode_agent import VibecodeAgent
from ..agents.task_system import Task, TaskType
from ..context.models import VibecodeSession, Intent

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class VibecodeSessionCreate(BaseModel):
    user_id: str
    initial_preferences: Optional[Dict[str, any]] = None
    session_config: Optional[Dict[str, any]] = None

class VibecodeSessionResponse(BaseModel):
    session_id: str
    user_id: str
    status: str
    greeting: str
    conversation_state: Dict[str, any]
    created_at: str

class VoiceInputRequest(BaseModel):
    session_id: str
    audio_data: str  # Base64 encoded audio
    audio_format: str = "wav"
    additional_context: Optional[Dict[str, any]] = None

class TextInputRequest(BaseModel):
    session_id: str
    text: str
    additional_context: Optional[Dict[str, any]] = None

class VibecodeResponse(BaseModel):
    session_id: str
    response_type: str
    text_response: str
    suggestions: List[str] = []
    generated_content: Optional[Dict[str, any]] = None
    conversation_state: Dict[str, any]
    next_steps: List[str] = []
    confidence_score: float = 0.0

class FeedbackRequest(BaseModel):
    session_id: str
    feedback_text: Optional[str] = None
    feedback_audio: Optional[str] = None  # Base64 encoded
    feedback_type: str = "general"  # general, content, style, pace

class RefinementRequest(BaseModel):
    session_id: str
    instructions: str
    target_element: Optional[str] = None  # character, plot, style, etc.

class ExportRequest(BaseModel):
    session_id: str
    export_format: str = "pdf"  # pdf, epub, docx, txt
    include_metadata: bool = True

class SessionStatus(BaseModel):
    session_id: str
    status: str
    current_phase: str
    progress_percentage: float
    word_count: int
    duration_minutes: float
    last_activity: str

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_message(self, session_id: str, message: Dict[str, any]):
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send WebSocket message to {session_id}: {e}")
                self.disconnect(session_id)
    
    async def broadcast_to_session(self, session_id: str, message: Dict[str, any]):
        await self.send_message(session_id, message)

# FastAPI app
app = FastAPI(
    title="KindleMint Vibecode API",
    description="API for conversational book creation through voice interaction",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
vibecode_agent = VibecodeAgent()
connection_manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize the vibecode agent on startup"""
    try:
        await vibecode_agent.start()
        logger.info("Vibecode API started successfully")
    except Exception as e:
        logger.error(f"Failed to start vibecode agent: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    try:
        await vibecode_agent.stop()
        logger.info("Vibecode API shutdown successfully")
    except Exception as e:
        logger.error(f"Error during vibecode API shutdown: {e}")

# REST API Endpoints

@app.post("/api/v1/vibecode/sessions", response_model=VibecodeSessionResponse)
async def create_vibecode_session(request: VibecodeSessionCreate):
    """Create a new vibecode session"""
    
    try:
        # Create task for starting vibecode session
        task = Task(
            task_type="START_VIBECODE_SESSION",
            name="Start Vibecode Session",
            description=f"Start new vibecode session for user {request.user_id}",
            input_data={
                "user_id": request.user_id,
                "initial_preferences": request.initial_preferences,
                "session_config": request.session_config
            }
        )
        
        # Execute task
        success = await vibecode_agent.assign_task(task)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start vibecode session")
        
        # Wait for completion (with timeout)
        timeout_seconds = 30
        for _ in range(timeout_seconds * 10):  # Check every 100ms
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        if task.status.value != "completed":
            raise HTTPException(status_code=500, detail="Session creation timed out")
        
        # Extract result
        result = task.result
        if not result or not result.success:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        return VibecodeSessionResponse(
            session_id=result.output_data["session_id"],
            user_id=request.user_id,
            status="active",
            greeting=result.output_data["greeting"],
            conversation_state=result.output_data["conversation_state"],
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating vibecode session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vibecode/voice-input", response_model=VibecodeResponse)
async def process_voice_input(request: VoiceInputRequest):
    """Process voice input and generate response"""
    
    try:
        # Decode audio data
        audio_data = base64.b64decode(request.audio_data)
        
        # Create task for processing voice input
        task = Task(
            task_type="PROCESS_VOICE_INPUT",
            name="Process Voice Input",
            description=f"Process voice input for session {request.session_id}",
            input_data={
                "session_id": request.session_id,
                "audio_data": audio_data,
                "audio_format": request.audio_format,
                "additional_context": request.additional_context
            }
        )
        
        # Execute task
        success = await vibecode_agent.assign_task(task)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process voice input")
        
        # Wait for completion
        timeout_seconds = 30
        for _ in range(timeout_seconds * 10):
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        if task.status.value != "completed":
            raise HTTPException(status_code=500, detail="Voice processing timed out")
        
        result = task.result
        if not result or not result.success:
            raise HTTPException(status_code=500, detail="Failed to process voice input")
        
        # Notify WebSocket clients
        await connection_manager.broadcast_to_session(
            request.session_id,
            {
                "type": "voice_processed",
                "data": result.output_data
            }
        )
        
        # Return response
        response_data = result.output_data["response"]
        return VibecodeResponse(
            session_id=request.session_id,
            response_type="voice_response",
            text_response=response_data["text_response"],
            suggestions=response_data.get("suggestions", []),
            generated_content=response_data.get("generated_content"),
            conversation_state=result.output_data["conversation_state"],
            next_steps=response_data.get("next_steps", []),
            confidence_score=result.output_data.get("voice_input", {}).get("confidence", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error processing voice input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vibecode/text-input", response_model=VibecodeResponse)
async def process_text_input(request: TextInputRequest):
    """Process text input (fallback for voice)"""
    
    try:
        # Create simulated audio data for text input
        audio_data = request.text.encode('utf-8')
        
        # Create task for processing text as voice input
        task = Task(
            task_type="PROCESS_VOICE_INPUT",
            name="Process Text Input",
            description=f"Process text input for session {request.session_id}",
            input_data={
                "session_id": request.session_id,
                "audio_data": audio_data,
                "audio_format": "text",
                "text_override": request.text,
                "additional_context": request.additional_context
            }
        )
        
        # Execute and wait for completion (similar to voice input)
        success = await vibecode_agent.assign_task(task)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process text input")
        
        # Wait for completion
        timeout_seconds = 30
        for _ in range(timeout_seconds * 10):
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        if task.status.value != "completed":
            raise HTTPException(status_code=500, detail="Text processing timed out")
        
        result = task.result
        if not result or not result.success:
            raise HTTPException(status_code=500, detail="Failed to process text input")
        
        # Notify WebSocket clients
        await connection_manager.broadcast_to_session(
            request.session_id,
            {
                "type": "text_processed",
                "data": result.output_data
            }
        )
        
        # Return response
        response_data = result.output_data["response"]
        return VibecodeResponse(
            session_id=request.session_id,
            response_type="text_response",
            text_response=response_data["text_response"],
            suggestions=response_data.get("suggestions", []),
            generated_content=response_data.get("generated_content"),
            conversation_state=result.output_data["conversation_state"],
            next_steps=response_data.get("next_steps", []),
            confidence_score=1.0  # Perfect confidence for text
        )
        
    except Exception as e:
        logger.error(f"Error processing text input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vibecode/feedback")
async def provide_feedback(request: FeedbackRequest):
    """Provide feedback on the conversation or content"""
    
    try:
        # Prepare feedback data
        feedback_data = {
            "session_id": request.session_id,
            "feedback_type": request.feedback_type
        }
        
        if request.feedback_audio:
            feedback_data["feedback_audio"] = base64.b64decode(request.feedback_audio)
        elif request.feedback_text:
            feedback_data["feedback_text"] = request.feedback_text
        else:
            raise HTTPException(status_code=400, detail="Either feedback_text or feedback_audio is required")
        
        # Create task for processing feedback
        task = Task(
            task_type="PROVIDE_FEEDBACK",
            name="Process User Feedback",
            description=f"Process user feedback for session {request.session_id}",
            input_data=feedback_data
        )
        
        # Execute task
        success = await vibecode_agent.assign_task(task)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process feedback")
        
        # Wait for completion
        timeout_seconds = 20
        for _ in range(timeout_seconds * 10):
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        if task.status.value != "completed":
            raise HTTPException(status_code=500, detail="Feedback processing timed out")
        
        result = task.result
        if not result or not result.success:
            raise HTTPException(status_code=500, detail="Failed to process feedback")
        
        # Notify WebSocket clients
        await connection_manager.broadcast_to_session(
            request.session_id,
            {
                "type": "feedback_processed",
                "data": result.output_data
            }
        )
        
        return {"status": "success", "message": "Feedback processed successfully"}
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vibecode/refine")
async def refine_content(request: RefinementRequest):
    """Refine generated content based on instructions"""
    
    try:
        # Create task for content refinement
        task = Task(
            task_type="REFINE_CONTENT",
            name="Refine Content",
            description=f"Refine content for session {request.session_id}",
            input_data={
                "session_id": request.session_id,
                "instructions": request.instructions,
                "target_element": request.target_element
            }
        )
        
        # Execute task
        success = await vibecode_agent.assign_task(task)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to refine content")
        
        # Wait for completion
        timeout_seconds = 30
        for _ in range(timeout_seconds * 10):
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        if task.status.value != "completed":
            raise HTTPException(status_code=500, detail="Content refinement timed out")
        
        result = task.result
        if not result or not result.success:
            raise HTTPException(status_code=500, detail="Failed to refine content")
        
        # Notify WebSocket clients
        await connection_manager.broadcast_to_session(
            request.session_id,
            {
                "type": "content_refined",
                "data": result.output_data
            }
        )
        
        return {
            "status": "success",
            "refined_content": result.output_data["refined_content"]
        }
        
    except Exception as e:
        logger.error(f"Error refining content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vibecode/export")
async def export_book(request: ExportRequest):
    """Export the created book in the requested format"""
    
    try:
        # Create task for book export
        task = Task(
            task_type="EXPORT_BOOK",
            name="Export Book",
            description=f"Export book for session {request.session_id}",
            input_data={
                "session_id": request.session_id,
                "format": request.export_format,
                "include_metadata": request.include_metadata
            }
        )
        
        # Execute task
        success = await vibecode_agent.assign_task(task)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to export book")
        
        # Wait for completion (export might take longer)
        timeout_seconds = 60
        for _ in range(timeout_seconds * 10):
            if task.status.value in ["completed", "failed"]:
                break
            await asyncio.sleep(0.1)
        
        if task.status.value != "completed":
            raise HTTPException(status_code=500, detail="Book export timed out")
        
        result = task.result
        if not result or not result.success:
            raise HTTPException(status_code=500, detail="Failed to export book")
        
        # Notify WebSocket clients
        await connection_manager.broadcast_to_session(
            request.session_id,
            {
                "type": "book_exported",
                "data": result.output_data
            }
        )
        
        return {
            "status": "success",
            "export_path": result.output_data["export_path"],
            "format": result.output_data["format"],
            "word_count": result.output_data.get("word_count", 0)
        }
        
    except Exception as e:
        logger.error(f"Error exporting book: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/vibecode/sessions/{session_id}/status", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """Get current session status"""
    
    try:
        # Get session from vibecode agent
        session = vibecode_agent.active_sessions.get(session_id)
        conversation_state = vibecode_agent.conversation_states.get(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Calculate progress
        progress_percentage = _calculate_progress(conversation_state)
        
        return SessionStatus(
            session_id=session_id,
            status=session.session_status,
            current_phase=conversation_state.current_phase if conversation_state else "unknown",
            progress_percentage=progress_percentage,
            word_count=session.total_input_words,
            duration_minutes=session.session_duration or 0,
            last_activity=conversation_state.last_interaction.isoformat() if conversation_state else session.start_time.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/vibecode/sessions/{session_id}/content")
async def get_session_content(session_id: str):
    """Get all generated content for a session"""
    
    try:
        session = vibecode_agent.active_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session_id,
            "generated_content": session.generated_content,
            "voice_inputs": [
                {
                    "text": vi.text,
                    "intent": vi.intent.value,
                    "timestamp": vi.timestamp.isoformat(),
                    "emotions": {
                        "mood": vi.emotions.mood.value,
                        "energy_level": vi.emotions.energy_level
                    }
                }
                for vi in session.voice_inputs
            ],
            "word_count": session.total_input_words,
            "session_metadata": session.session_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/api/v1/vibecode/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time vibecode communication"""
    
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "ping":
                await connection_manager.send_message(session_id, {"type": "pong"})
            
            elif message_type == "status_request":
                # Send current session status
                try:
                    session = vibecode_agent.active_sessions.get(session_id)
                    if session:
                        status_data = {
                            "type": "status_update",
                            "session_id": session_id,
                            "status": session.session_status,
                            "word_count": session.total_input_words,
                            "timestamp": datetime.now().isoformat()
                        }
                        await connection_manager.send_message(session_id, status_data)
                except Exception as e:
                    logger.error(f"Error sending status update: {e}")
            
            elif message_type == "realtime_voice":
                # Handle real-time voice streaming (future feature)
                logger.info(f"Real-time voice data received for session {session_id}")
            
    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        connection_manager.disconnect(session_id)

# Utility functions
def _calculate_progress(conversation_state) -> float:
    """Calculate session progress percentage"""
    if not conversation_state:
        return 0.0
    
    phase_progress = {
        "greeting": 10.0,
        "intention_discovery": 25.0,
        "context_building": 40.0,
        "content_creation": 75.0,
        "refinement": 90.0,
        "completion": 100.0
    }
    
    return phase_progress.get(conversation_state.current_phase, 0.0)

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent_status": vibecode_agent.status.value if vibecode_agent else "unknown",
        "active_sessions": len(vibecode_agent.active_sessions) if vibecode_agent else 0
    }

# API documentation
@app.get("/api/v1/vibecode/info")
async def api_info():
    """Get API information and capabilities"""
    return {
        "name": "KindleMint Vibecode API",
        "version": "1.0.0",
        "description": "Conversational book creation through voice interaction",
        "capabilities": [
            "voice_input_processing",
            "conversational_interface",
            "real_time_feedback",
            "content_generation",
            "style_adaptation",
            "multi_format_export"
        ],
        "supported_formats": ["pdf", "epub", "docx", "txt"],
        "websocket_endpoint": "/api/v1/vibecode/ws/{session_id}",
        "max_session_duration": "2 hours",
        "supported_languages": ["en"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)