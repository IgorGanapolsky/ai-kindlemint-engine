"""
Vibecode Agent for KindleMint Conversational Interface

This agent implements the core vibecoding experience, enabling users to create books
through natural conversation instead of traditional UI forms.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..agents.base_agent import AgentCapability, BaseAgent
from ..agents.task_system import Task, TaskResult, TaskStatus, TaskType
from ..context import (
    AuthorContextBuilder,
    ContextSynthesisEngine, 
    VoiceInputProcessor,
    VibecodeSession,
    VoiceInput,
    SynthesizedContext,
    Intent,
    CreativeMood
)

logger = logging.getLogger(__name__)


class VibecodeAgent(BaseAgent):
    """
    Agent specialized for conversational book creation through vibecoding.
    
    Handles natural language interaction, context synthesis, and real-time
    content generation based on voice input and conversation flow.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        super().__init__(
            agent_id=agent_id,
            agent_type="vibecode_agent",
            capabilities=[
                AgentCapability.CONTENT_GENERATION,
                AgentCapability.QUALITY_ASSURANCE,
                AgentCapability.TASK_COORDINATION,
                # Add new vibecode-specific capabilities
                "VIBE_INTERPRETATION",
                "CONVERSATIONAL_INTERFACE",
                "CONTEXT_SYNTHESIS",
                "REAL_TIME_FEEDBACK",
                "VOICE_PROCESSING"
            ],
            max_concurrent_tasks=3,
            heartbeat_interval=15
        )
        
        # Initialize vibecoding components
        self.voice_processor = VoiceInputProcessor()
        self.context_synthesizer = ContextSynthesisEngine()
        self.conversation_manager = ConversationManager()
        self.content_generator = ConversationalContentGenerator()
        self.feedback_processor = FeedbackProcessor()
        
        # Active sessions
        self.active_sessions: Dict[str, VibecodeSession] = {}
        
        # Conversation state
        self.conversation_states: Dict[str, ConversationState] = {}
        
        self.logger.info("Vibecode Agent initialized with conversational capabilities")
    
    async def _initialize(self) -> None:
        """Initialize vibecode agent components"""
        try:
            # Initialize conversation templates
            await self.conversation_manager.initialize_templates()
            
            # Initialize content generation models
            await self.content_generator.initialize()
            
            self.logger.info("Vibecode Agent components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize vibecode agent: {e}")
            raise
    
    async def _cleanup(self) -> None:
        """Clean up vibecode agent resources"""
        try:
            # Save active sessions
            for session_id, session in self.active_sessions.items():
                await self._save_session(session)
            
            # Clean up conversation states
            self.conversation_states.clear()
            
            self.logger.info("Vibecode Agent cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during vibecode agent cleanup: {e}")
    
    async def _execute_task(self, task: Task) -> TaskResult:
        """Execute vibecode-specific tasks"""
        
        try:
            if task.task_type == "START_VIBECODE_SESSION":
                return await self._start_vibecode_session(task)
            elif task.task_type == "PROCESS_VOICE_INPUT":
                return await self._process_voice_input(task)
            elif task.task_type == "GENERATE_RESPONSE":
                return await self._generate_conversational_response(task)
            elif task.task_type == "PROVIDE_FEEDBACK":
                return await self._process_user_feedback(task)
            elif task.task_type == "REFINE_CONTENT":
                return await self._refine_content(task)
            elif task.task_type == "EXPORT_BOOK":
                return await self._export_book(task)
            else:
                return TaskResult(
                    success=False,
                    task_id=task.task_id,
                    error_message=f"Unknown task type: {task.task_type}"
                )
                
        except Exception as e:
            self.logger.error(f"Error executing vibecode task {task.task_id}: {e}")
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message=str(e)
            )
    
    async def _start_vibecode_session(self, task: Task) -> TaskResult:
        """Start a new vibecode session"""
        
        user_id = task.input_data.get("user_id")
        if not user_id:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message="user_id is required to start vibecode session"
            )
        
        # Create new session
        session = VibecodeSession(user_id=user_id)
        
        # Initialize conversation state
        conversation_state = ConversationState(
            session_id=session.session_id,
            user_id=user_id,
            current_phase=ConversationPhase.GREETING,
            context_history=[]
        )
        
        # Store session and state
        self.active_sessions[session.session_id] = session
        self.conversation_states[session.session_id] = conversation_state
        
        # Generate initial greeting
        greeting = await self.conversation_manager.generate_greeting(user_id)
        
        self.logger.info(f"Started vibecode session {session.session_id} for user {user_id}")
        
        return TaskResult(
            success=True,
            task_id=task.task_id,
            output_data={
                "session_id": session.session_id,
                "greeting": greeting,
                "conversation_state": conversation_state.to_dict()
            }
        )
    
    async def _process_voice_input(self, task: Task) -> TaskResult:
        """Process voice input and generate response"""
        
        session_id = task.input_data.get("session_id")
        audio_data = task.input_data.get("audio_data")
        
        if not session_id or not audio_data:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message="session_id and audio_data are required"
            )
        
        # Get session and conversation state
        session = self.active_sessions.get(session_id)
        conversation_state = self.conversation_states.get(session_id)
        
        if not session or not conversation_state:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message=f"Session {session_id} not found"
            )
        
        # Process voice input
        voice_input = await self.voice_processor.process_voice_input(
            audio_data, session_id
        )
        
        # Add to session history
        session.voice_inputs.append(voice_input)
        
        # Synthesize context
        context = await self.context_synthesizer.synthesize_context(
            session.user_id, voice_input
        )
        
        # Add to session context history
        session.context_history.append(context)
        
        # Update conversation state based on input
        await self.conversation_manager.update_conversation_state(
            conversation_state, voice_input, context
        )
        
        # Generate response
        response = await self.conversation_manager.generate_response(
            conversation_state, voice_input, context
        )
        
        # Generate content if appropriate
        if conversation_state.current_phase == ConversationPhase.CONTENT_CREATION:
            content_result = await self.content_generator.generate_content(
                voice_input, context, conversation_state
            )
            response.update(content_result)
        
        self.logger.info(f"Processed voice input for session {session_id}: intent={voice_input.intent.value}")
        
        return TaskResult(
            success=True,
            task_id=task.task_id,
            output_data={
                "voice_input": voice_input.to_dict() if hasattr(voice_input, 'to_dict') else str(voice_input),
                "context": context.get_primary_context_summary(),
                "response": response,
                "conversation_state": conversation_state.to_dict()
            }
        )
    
    async def _generate_conversational_response(self, task: Task) -> TaskResult:
        """Generate a conversational response based on context"""
        
        session_id = task.input_data.get("session_id")
        message_type = task.input_data.get("message_type", "general")
        
        conversation_state = self.conversation_states.get(session_id)
        if not conversation_state:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message=f"Session {session_id} not found"
            )
        
        # Generate response based on type and state
        response = await self.conversation_manager.generate_contextual_response(
            conversation_state, message_type
        )
        
        return TaskResult(
            success=True,
            task_id=task.task_id,
            output_data={"response": response}
        )
    
    async def _process_user_feedback(self, task: Task) -> TaskResult:
        """Process user feedback and adjust content/approach"""
        
        session_id = task.input_data.get("session_id")
        feedback_audio = task.input_data.get("feedback_audio")
        
        if not session_id or not feedback_audio:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message="session_id and feedback_audio are required"
            )
        
        # Get session state
        session = self.active_sessions.get(session_id)
        conversation_state = self.conversation_states.get(session_id)
        
        if not session or not conversation_state:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message=f"Session {session_id} not found"
            )
        
        # Process feedback
        feedback_input = await self.voice_processor.process_voice_input(
            feedback_audio, session_id
        )
        
        # Analyze feedback and generate response
        feedback_response = await self.feedback_processor.process_feedback(
            feedback_input, conversation_state, session
        )
        
        # Update conversation state based on feedback
        await self.conversation_manager.apply_feedback(
            conversation_state, feedback_input, feedback_response
        )
        
        return TaskResult(
            success=True,
            task_id=task.task_id,
            output_data={
                "feedback_analysis": feedback_response,
                "updated_state": conversation_state.to_dict()
            }
        )
    
    async def _refine_content(self, task: Task) -> TaskResult:
        """Refine generated content based on user direction"""
        
        session_id = task.input_data.get("session_id")
        refinement_instructions = task.input_data.get("instructions")
        
        session = self.active_sessions.get(session_id)
        if not session:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message=f"Session {session_id} not found"
            )
        
        # Refine content using latest context
        latest_context = session.latest_context
        if not latest_context:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message="No context available for refinement"
            )
        
        refined_content = await self.content_generator.refine_content(
            session.generated_content,
            refinement_instructions,
            latest_context
        )
        
        # Update session content
        session.generated_content.update(refined_content)
        
        return TaskResult(
            success=True,
            task_id=task.task_id,
            output_data={"refined_content": refined_content}
        )
    
    async def _export_book(self, task: Task) -> TaskResult:
        """Export the created book in the requested format"""
        
        session_id = task.input_data.get("session_id")
        export_format = task.input_data.get("format", "pdf")
        
        session = self.active_sessions.get(session_id)
        if not session:
            return TaskResult(
                success=False,
                task_id=task.task_id,
                error_message=f"Session {session_id} not found"
            )
        
        # Export using existing publishing pipeline
        export_result = await self._export_to_format(session, export_format)
        
        # Mark session as completed
        session.session_status = "completed"
        session.end_time = datetime.now()
        
        return TaskResult(
            success=True,
            task_id=task.task_id,
            output_data=export_result
        )
    
    async def _save_session(self, session: VibecodeSession):
        """Save session to persistent storage"""
        try:
            # Save using context memory store
            await self.context_synthesizer.memory_store.store_vibecode_session(session)
        except Exception as e:
            self.logger.error(f"Failed to save session {session.session_id}: {e}")
    
    async def _export_to_format(self, session: VibecodeSession, format_type: str) -> Dict[str, any]:
        """Export session content to specified format"""
        # This would integrate with existing publishing pipeline
        # For now, return mock export result
        return {
            "export_path": f"/exports/{session.session_id}.{format_type}",
            "format": format_type,
            "word_count": session.total_input_words,
            "export_time": datetime.now().isoformat()
        }


class ConversationPhase:
    """Phases of vibecode conversation"""
    GREETING = "greeting"
    INTENTION_DISCOVERY = "intention_discovery"
    CONTEXT_BUILDING = "context_building"
    CONTENT_CREATION = "content_creation"
    REFINEMENT = "refinement"
    COMPLETION = "completion"


class ConversationState:
    """State management for vibecode conversations"""
    
    def __init__(self, session_id: str, user_id: str, 
                 current_phase: str = ConversationPhase.GREETING,
                 context_history: Optional[List] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.current_phase = current_phase
        self.context_history = context_history or []
        self.conversation_memory = {}
        self.user_preferences = {}
        self.current_topic = None
        self.pending_questions = []
        self.completed_milestones = []
        self.last_interaction = datetime.now()
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "current_phase": self.current_phase,
            "current_topic": self.current_topic,
            "conversation_memory": self.conversation_memory,
            "user_preferences": self.user_preferences,
            "pending_questions": self.pending_questions,
            "completed_milestones": self.completed_milestones,
            "last_interaction": self.last_interaction.isoformat()
        }


class ConversationManager:
    """Manages conversational flow and responses"""
    
    def __init__(self):
        self.conversation_templates = {}
        self.response_generators = {}
        self.logger = logging.getLogger(__name__)
    
    async def initialize_templates(self):
        """Initialize conversation templates"""
        self.conversation_templates = {
            ConversationPhase.GREETING: {
                "new_user": "Hello! I'm your AI writing companion. I'm here to help you create amazing books through conversation. What kind of story are you excited to tell?",
                "returning_user": "Welcome back! I remember you were working on {last_project}. Would you like to continue that or start something new?",
                "experienced_user": "Great to see you again! Ready to create another masterpiece? What's inspiring you today?"
            },
            ConversationPhase.INTENTION_DISCOVERY: {
                "explore_genre": "I can hear the excitement in your voice! What genre speaks to your soul right now? Mystery, romance, fantasy, or something completely different?",
                "clarify_vision": "Tell me more about the feeling you want your readers to experience. Should they be on the edge of their seats, falling in love, or lost in wonder?",
                "understand_goals": "What's your dream outcome for this book? Are you writing for the joy of creation, to reach bestseller status, or to share an important message?"
            },
            ConversationPhase.CONTEXT_BUILDING: {
                "gather_preferences": "I love your energy around {topic}! To help me write in your unique voice, tell me: do you prefer short, punchy sentences or flowing, descriptive prose?",
                "understand_audience": "Who do you picture reading this? Young adults hungry for adventure, busy professionals seeking escape, or perhaps cozy mystery lovers?",
                "set_expectations": "This is going to be amazing! How much time do you want to spend on this today? We can create a complete outline or dive deep into the first chapter."
            },
            ConversationPhase.CONTENT_CREATION: {
                "start_creation": "Perfect! I can feel your vision coming together. Let's start bringing your story to life. What's the very first thing you want your readers to experience?",
                "continue_flow": "This is fantastic! Your {creation_element} has such {positive_quality}. What happens next in your mind?",
                "encourage_creativity": "I love how you're thinking! That {creative_element} is going to really {impact_description}. Keep going with that energy!"
            },
            ConversationPhase.REFINEMENT: {
                "suggest_improvements": "This is really coming together! I notice we could make the {element} even more {quality}. What if we tried {suggestion}?",
                "offer_alternatives": "You have great instincts! Would you like to explore a different approach to {specific_element}, or does this feel right to you?",
                "polish_content": "Your story has such {strength}! Let's polish it to perfection. Which part would you like to refine first?"
            }
        }
    
    async def generate_greeting(self, user_id: str) -> str:
        """Generate personalized greeting"""
        # In production, would check user history
        # For now, assume new user
        return self.conversation_templates[ConversationPhase.GREETING]["new_user"]
    
    async def update_conversation_state(self, state: ConversationState, 
                                      voice_input: VoiceInput, 
                                      context: SynthesizedContext):
        """Update conversation state based on new input"""
        
        # Update last interaction
        state.last_interaction = datetime.now()
        
        # Store voice input context
        state.conversation_memory[f"input_{len(state.context_history)}"] = {
            "text": voice_input.text,
            "intent": voice_input.intent.value,
            "mood": voice_input.emotions.mood.value,
            "energy": voice_input.emotions.energy_level
        }
        
        # Update user preferences from context
        state.user_preferences.update({
            "writing_style": context.author.writing_style.tone,
            "genre_preferences": [g.value for g in context.author.writing_style.genre_preferences],
            "collaboration_style": context.author.preferences.collaboration_style
        })
        
        # Advance conversation phase if appropriate
        await self._maybe_advance_phase(state, voice_input, context)
    
    async def _maybe_advance_phase(self, state: ConversationState, 
                                 voice_input: VoiceInput, 
                                 context: SynthesizedContext):
        """Advance conversation phase if conditions are met"""
        
        current_phase = state.current_phase
        
        if current_phase == ConversationPhase.GREETING:
            # Move to intention discovery after user responds
            state.current_phase = ConversationPhase.INTENTION_DISCOVERY
            
        elif current_phase == ConversationPhase.INTENTION_DISCOVERY:
            # Move to context building if intent is clear
            if voice_input.intent in [Intent.CREATE_BOOK, Intent.SET_VIBE, Intent.CHANGE_GENRE]:
                state.current_phase = ConversationPhase.CONTEXT_BUILDING
                
        elif current_phase == ConversationPhase.CONTEXT_BUILDING:
            # Move to content creation if enough context
            if context.quality_score > 0.6:
                state.current_phase = ConversationPhase.CONTENT_CREATION
                
        elif current_phase == ConversationPhase.CONTENT_CREATION:
            # Move to refinement if user asks for changes
            if voice_input.intent in [Intent.EDIT_CONTENT, Intent.REFINE_STYLE]:
                state.current_phase = ConversationPhase.REFINEMENT
            elif voice_input.intent == Intent.PUBLISH_BOOK:
                state.current_phase = ConversationPhase.COMPLETION
    
    async def generate_response(self, state: ConversationState, 
                              voice_input: VoiceInput, 
                              context: SynthesizedContext) -> Dict[str, any]:
        """Generate appropriate response based on conversation state"""
        
        # Get template for current phase
        phase_templates = self.conversation_templates.get(state.current_phase, {})
        
        # Choose specific template based on context
        template_key = self._choose_template_key(state, voice_input, context)
        template = phase_templates.get(template_key, "I understand. Please tell me more.")
        
        # Personalize template with context
        personalized_response = await self._personalize_template(
            template, state, voice_input, context
        )
        
        # Add suggestions if appropriate
        suggestions = await self._generate_suggestions(state, voice_input, context)
        
        return {
            "text_response": personalized_response,
            "suggestions": suggestions,
            "phase": state.current_phase,
            "next_steps": await self._get_next_steps(state, context)
        }
    
    def _choose_template_key(self, state: ConversationState, 
                           voice_input: VoiceInput, 
                           context: SynthesizedContext) -> str:
        """Choose appropriate template key based on context"""
        
        if state.current_phase == ConversationPhase.GREETING:
            if context.author.total_sessions == 0:
                return "new_user"
            elif context.author.total_sessions < 5:
                return "returning_user"
            else:
                return "experienced_user"
                
        elif state.current_phase == ConversationPhase.INTENTION_DISCOVERY:
            if voice_input.intent == Intent.EXPLORE_IDEAS:
                return "explore_genre"
            elif voice_input.intent == Intent.SET_VIBE:
                return "clarify_vision"
            else:
                return "understand_goals"
                
        elif state.current_phase == ConversationPhase.CONTENT_CREATION:
            if len(state.context_history) == 1:
                return "start_creation"
            elif voice_input.emotions.energy_level > 0.7:
                return "encourage_creativity"
            else:
                return "continue_flow"
        
        # Default
        return "default"
    
    async def _personalize_template(self, template: str, state: ConversationState,
                                  voice_input: VoiceInput, context: SynthesizedContext) -> str:
        """Personalize template with context-specific information"""
        
        # Extract personalization variables
        variables = {
            "topic": voice_input.text.split()[:3] if voice_input.text else "your story",
            "last_project": "your mystery novel",  # Would come from context in production
            "creation_element": "character development",
            "positive_quality": "depth and authenticity",
            "creative_element": "plot twist",
            "impact_description": "keep readers guessing",
            "element": "dialogue",
            "quality": "natural and engaging",
            "suggestion": "adding more character-specific speech patterns",
            "strength": "emotional resonance"
        }
        
        # Apply variables to template
        try:
            return template.format(**variables)
        except KeyError:
            # Return template as-is if variables don't match
            return template
    
    async def _generate_suggestions(self, state: ConversationState,
                                  voice_input: VoiceInput, 
                                  context: SynthesizedContext) -> List[str]:
        """Generate helpful suggestions for the user"""
        
        suggestions = []
        
        if state.current_phase == ConversationPhase.INTENTION_DISCOVERY:
            suggestions.extend([
                "Tell me about a book that made you feel exactly how you want your readers to feel",
                "Describe the mood or atmosphere you're imagining",
                "What's the one thing you most want to express through this story?"
            ])
            
        elif state.current_phase == ConversationPhase.CONTENT_CREATION:
            suggestions.extend([
                "Describe the opening scene as if you're watching a movie",
                "Tell me about your main character's biggest challenge",
                "What's the most important moment in your story?"
            ])
        
        # Add context-specific suggestions
        if context.quality_score < 0.5:
            suggestions.append("Share more about your vision so I can help you better")
        
        if voice_input.emotions.energy_level > 0.8:
            suggestions.append("Your enthusiasm is contagious! Let's channel that energy into your story")
        
        return suggestions[:3]  # Limit to top 3
    
    async def _get_next_steps(self, state: ConversationState, 
                            context: SynthesizedContext) -> List[str]:
        """Get next steps for the conversation"""
        
        next_steps = []
        
        if state.current_phase == ConversationPhase.GREETING:
            next_steps.append("Share your story idea or writing goal")
            
        elif state.current_phase == ConversationPhase.INTENTION_DISCOVERY:
            next_steps.extend([
                "Clarify your genre and target audience",
                "Describe the mood and tone you want"
            ])
            
        elif state.current_phase == ConversationPhase.CONTEXT_BUILDING:
            next_steps.extend([
                "Provide more details about your preferences",
                "Share examples of writing you admire"
            ])
            
        elif state.current_phase == ConversationPhase.CONTENT_CREATION:
            next_steps.extend([
                "Continue developing your story",
                "Refine existing content",
                "Move to the next chapter or section"
            ])
        
        return next_steps
    
    async def generate_contextual_response(self, state: ConversationState, 
                                         message_type: str) -> str:
        """Generate contextual response for specific message types"""
        
        responses = {
            "encouragement": f"You're doing amazing! Your {state.current_topic or 'creativity'} is really shining through.",
            "clarification": "I want to make sure I understand you perfectly. Could you tell me more about that?",
            "celebration": "This is fantastic! I love how your story is developing.",
            "guidance": f"Based on what you've shared, I think the next step would be to {self._get_next_action(state)}."
        }
        
        return responses.get(message_type, "Please continue sharing your thoughts.")
    
    def _get_next_action(self, state: ConversationState) -> str:
        """Get next recommended action based on state"""
        if state.current_phase == ConversationPhase.INTENTION_DISCOVERY:
            return "explore your genre preferences in more detail"
        elif state.current_phase == ConversationPhase.CONTENT_CREATION:
            return "develop your main character's motivation"
        else:
            return "continue with your creative flow"
    
    async def apply_feedback(self, state: ConversationState, 
                           feedback_input: VoiceInput, 
                           feedback_response: Dict[str, any]):
        """Apply user feedback to conversation state"""
        
        # Update conversation memory with feedback
        state.conversation_memory["last_feedback"] = {
            "text": feedback_input.text,
            "sentiment": feedback_response.get("sentiment", "neutral"),
            "suggestions_accepted": feedback_response.get("accepted_suggestions", [])
        }
        
        # Adjust approach based on feedback
        if feedback_response.get("sentiment") == "positive":
            state.conversation_memory["positive_patterns"] = state.conversation_memory.get("positive_patterns", [])
            state.conversation_memory["positive_patterns"].append(state.current_phase)
        elif feedback_response.get("sentiment") == "negative":
            # Note areas for improvement
            state.conversation_memory["improvement_areas"] = state.conversation_memory.get("improvement_areas", [])
            state.conversation_memory["improvement_areas"].append(state.current_phase)


class ConversationalContentGenerator:
    """Generates content through conversational interaction"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self):
        """Initialize content generation models"""
        # In production, would initialize AI models
        self.logger.info("Conversational content generator initialized")
    
    async def generate_content(self, voice_input: VoiceInput, 
                             context: SynthesizedContext,
                             conversation_state: ConversationState) -> Dict[str, any]:
        """Generate content based on voice input and conversation context"""
        
        # Analyze what type of content to generate
        content_type = self._determine_content_type(voice_input, conversation_state)
        
        # Generate appropriate content
        if content_type == "story_opening":
            content = await self._generate_story_opening(voice_input, context)
        elif content_type == "character_description":
            content = await self._generate_character_description(voice_input, context)
        elif content_type == "scene_development":
            content = await self._generate_scene_development(voice_input, context)
        elif content_type == "dialogue":
            content = await self._generate_dialogue(voice_input, context)
        else:
            content = await self._generate_general_content(voice_input, context)
        
        return {
            "content_type": content_type,
            "generated_content": content,
            "word_count": len(content.split()),
            "style_match_score": await self._calculate_style_match(content, context)
        }
    
    def _determine_content_type(self, voice_input: VoiceInput, 
                              conversation_state: ConversationState) -> str:
        """Determine what type of content to generate"""
        
        text = voice_input.text.lower()
        
        if any(word in text for word in ["beginning", "start", "opening", "first"]):
            return "story_opening"
        elif any(word in text for word in ["character", "person", "protagonist", "hero"]):
            return "character_description"
        elif any(word in text for word in ["scene", "setting", "place", "where"]):
            return "scene_development"
        elif any(word in text for word in ["dialogue", "conversation", "talking", "said"]):
            return "dialogue"
        else:
            return "general_content"
    
    async def _generate_story_opening(self, voice_input: VoiceInput, 
                                    context: SynthesizedContext) -> str:
        """Generate story opening based on voice input"""
        
        # Extract key elements from voice input
        mood = voice_input.emotions.mood.value
        energy = voice_input.emotions.energy_level
        
        # Use context for personalization
        style = context.author.writing_style.tone
        genre_prefs = context.author.writing_style.genre_preferences
        
        # Generate opening (simplified example)
        if mood == "mysterious" or any(g.value == "mystery" for g in genre_prefs):
            opening = "The fog rolled in from the harbor just as Sarah noticed the letter slipped under her door—a letter that would change everything she thought she knew about her quiet coastal town."
        elif mood == "romantic" or any(g.value == "romance" for g in genre_prefs):
            opening = "Emma had sworn off love after her last heartbreak, but when she accidentally collided with the mysterious stranger at the coffee shop, sending papers flying everywhere, she couldn't ignore the spark that ignited between them."
        else:
            opening = "It was supposed to be an ordinary Tuesday, but as Maya soon discovered, ordinary was the last thing this day would be."
        
        return opening
    
    async def _generate_character_description(self, voice_input: VoiceInput, 
                                            context: SynthesizedContext) -> str:
        """Generate character description"""
        
        return "Alex was the kind of person who noticed everything—the way people's eyes shifted when they lied, the slight tremor in voices when fear crept in, the almost imperceptible pause before someone decided to trust. These observations had served well in their career as a detective, but in personal relationships, this hypervigilance often felt more like a curse than a gift."
    
    async def _generate_scene_development(self, voice_input: VoiceInput, 
                                        context: SynthesizedContext) -> str:
        """Generate scene development"""
        
        return "The old library stood at the heart of the town, its Gothic spires reaching toward storm clouds that seemed to gather whenever something important was about to happen. Inside, dust motes danced in streams of amber light filtering through stained glass windows, and the air held the comforting scent of aged paper and forgotten stories waiting to be rediscovered."
    
    async def _generate_dialogue(self, voice_input: VoiceInput, 
                               context: SynthesizedContext) -> str:
        """Generate dialogue"""
        
        return '"I know you think I\'m crazy," Sarah said, her hands trembling as she set down the photograph. "But I swear I\'ve seen this woman before, and according to this newspaper clipping, she disappeared fifty years ago."\n\n"Sarah," Detective Morgan replied gently, "people can look similar. It doesn\'t mean—"\n\n"She had the same scar," Sarah interrupted. "Right here on her left wrist. Exactly the same. How do you explain that?"'
    
    async def _generate_general_content(self, voice_input: VoiceInput, 
                                      context: SynthesizedContext) -> str:
        """Generate general content"""
        
        return "The story continued to unfold in ways that surprised even its creator. Each conversation, each revelation, each moment of discovery built upon the last, creating a tapestry of narrative that felt both carefully planned and beautifully spontaneous."
    
    async def _calculate_style_match(self, content: str, context: SynthesizedContext) -> float:
        """Calculate how well the content matches the user's style preferences"""
        
        # Simplified style matching
        style_tone = context.author.writing_style.tone
        complexity = context.author.writing_style.complexity
        
        # Basic analysis
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        # Match complexity preference
        if complexity < 0.3 and avg_sentence_length < 15:
            complexity_match = 0.8
        elif complexity > 0.7 and avg_sentence_length > 25:
            complexity_match = 0.8
        else:
            complexity_match = 0.6
        
        # Simple tone matching
        tone_match = 0.7  # Would be more sophisticated in production
        
        return (complexity_match + tone_match) / 2
    
    async def refine_content(self, existing_content: Dict[str, any], 
                           instructions: str, 
                           context: SynthesizedContext) -> Dict[str, any]:
        """Refine existing content based on instructions"""
        
        # Extract refinement intent
        instructions_lower = instructions.lower()
        
        refined_content = existing_content.copy()
        
        if "more descriptive" in instructions_lower:
            # Add more descriptive elements
            refined_content["description_level"] = "enhanced"
        elif "shorter" in instructions_lower or "concise" in instructions_lower:
            # Make more concise
            refined_content["style"] = "concise"
        elif "dialogue" in instructions_lower:
            # Focus on dialogue
            refined_content["dialogue_focus"] = True
        
        return refined_content


class FeedbackProcessor:
    """Processes user feedback and adjusts conversation approach"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_feedback(self, feedback_input: VoiceInput, 
                             conversation_state: ConversationState,
                             session: VibecodeSession) -> Dict[str, any]:
        """Process user feedback and generate appropriate response"""
        
        feedback_text = feedback_input.text.lower()
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(feedback_text)
        
        # Extract specific feedback points
        feedback_points = self._extract_feedback_points(feedback_text)
        
        # Determine adjustments needed
        adjustments = self._determine_adjustments(feedback_points, conversation_state)
        
        # Generate response to feedback
        response = self._generate_feedback_response(sentiment, feedback_points)
        
        return {
            "sentiment": sentiment,
            "feedback_points": feedback_points,
            "adjustments": adjustments,
            "response": response,
            "confidence": feedback_input.confidence
        }
    
    def _analyze_sentiment(self, feedback_text: str) -> str:
        """Analyze sentiment of feedback"""
        
        positive_indicators = ["good", "great", "love", "perfect", "exactly", "yes", "right"]
        negative_indicators = ["no", "wrong", "not", "different", "change", "bad", "too"]
        
        positive_count = sum(1 for word in positive_indicators if word in feedback_text)
        negative_count = sum(1 for word in negative_indicators if word in feedback_text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_feedback_points(self, feedback_text: str) -> List[str]:
        """Extract specific feedback points"""
        
        points = []
        
        if "too fast" in feedback_text or "slow down" in feedback_text:
            points.append("pace_too_fast")
        elif "too slow" in feedback_text or "speed up" in feedback_text:
            points.append("pace_too_slow")
        
        if "more detail" in feedback_text or "describe more" in feedback_text:
            points.append("need_more_detail")
        elif "less detail" in feedback_text or "too much" in feedback_text:
            points.append("too_much_detail")
        
        if "different style" in feedback_text or "change tone" in feedback_text:
            points.append("style_adjustment")
        
        return points
    
    def _determine_adjustments(self, feedback_points: List[str], 
                             conversation_state: ConversationState) -> Dict[str, any]:
        """Determine what adjustments to make based on feedback"""
        
        adjustments = {}
        
        for point in feedback_points:
            if point == "pace_too_fast":
                adjustments["conversation_pace"] = "slower"
            elif point == "pace_too_slow":
                adjustments["conversation_pace"] = "faster"
            elif point == "need_more_detail":
                adjustments["detail_level"] = "increased"
            elif point == "too_much_detail":
                adjustments["detail_level"] = "reduced"
            elif point == "style_adjustment":
                adjustments["style_adaptation"] = "required"
        
        return adjustments
    
    def _generate_feedback_response(self, sentiment: str, feedback_points: List[str]) -> str:
        """Generate appropriate response to feedback"""
        
        if sentiment == "positive":
            return "I'm so glad that resonates with you! Let's keep building on what's working."
        elif sentiment == "negative":
            return "Thank you for that feedback—it helps me understand exactly what you're looking for. Let me adjust my approach."
        else:
            return "I appreciate your input. Help me understand better what direction you'd like to go."