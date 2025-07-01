"""
Context Memory Store for KindleMint Vibecoding System

Provides persistent storage and retrieval of context data including author profiles,
session history, and success patterns for the vibecoding system.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .models import AuthorContext, VibecodeSession, VoiceInput

logger = logging.getLogger(__name__)


class ContextMemoryStore:
    """Persistent storage for context data with SQLite backend"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Use project data directory
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data" / "context"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "context_memory.db")

        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS author_contexts (
                        user_id TEXT PRIMARY KEY,
                        context_data TEXT NOT NULL,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_sessions INTEGER DEFAULT 0,
                        total_words_created INTEGER DEFAULT 0
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS vibecode_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP,
                        session_data TEXT NOT NULL,
                        session_status TEXT DEFAULT 'active',
                        total_input_words INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES author_contexts (user_id)
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS voice_inputs (
                        input_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        input_data TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        confidence REAL,
                        intent TEXT,
                        FOREIGN KEY (session_id) REFERENCES vibecode_sessions (session_id),
                        FOREIGN KEY (user_id) REFERENCES author_contexts (user_id)
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS context_synthesis_history (
                        synthesis_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        synthesis_data TEXT NOT NULL,
                        quality_score REAL,
                        coherence_score REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES vibecode_sessions (session_id),
                        FOREIGN KEY (user_id) REFERENCES author_contexts (user_id)
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS success_metrics (
                        metric_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        metric_type TEXT NOT NULL,
                        metric_data TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES author_contexts (user_id)
                    )
                """
                )

                # Create indexes for better performance
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON vibecode_sessions (user_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_voice_inputs_session ON voice_inputs (session_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_synthesis_session ON context_synthesis_history (session_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_metrics_user ON success_metrics (user_id)"
                )

                conn.commit()

            self.logger.info(
                f"Context memory database initialized at {self.db_path}")

        except Exception as e:
            self.logger.error(
                f"Failed to initialize context memory database: {e}")
            raise

    async def store_author_context(self, user_id: str, context: AuthorContext) -> bool:
        """Store or update author context"""
        try:
            context_json = self._serialize_author_context(context)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO author_contexts
                    (user_id, context_data, last_updated, total_sessions, total_words_created)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        user_id,
                        context_json,
                        datetime.now().isoformat(),
                        context.total_sessions,
                        context.total_words_created,
                    ),
                )
                conn.commit()

            self.logger.debug(f"Stored author context for user {user_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to store author context for user {user_id}: {e}")
            return False

    async def get_author_context(self, user_id: str) -> Optional[AuthorContext]:
        """Retrieve author context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT context_data FROM author_contexts WHERE user_id = ?
                """,
                    (user_id,),
                )

                row = cursor.fetchone()
                if row:
                    return self._deserialize_author_context(row[0])

            return None

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve author context for user {user_id}: {e}"
            )
            return None

    async def store_vibecode_session(self, session: VibecodeSession) -> bool:
        """Store vibecode session"""
        try:
            session_json = self._serialize_vibecode_session(session)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO vibecode_sessions
                    (session_id, user_id, start_time, end_time, session_data, session_status, total_input_words)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        session.session_id,
                        session.user_id,
                        session.start_time.isoformat(),
                        session.end_time.isoformat() if session.end_time else None,
                        session_json,
                        session.session_status,
                        session.total_input_words,
                    ),
                )
                conn.commit()

            self.logger.debug(f"Stored vibecode session {session.session_id}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to store vibecode session {session.session_id}: {e}"
            )
            return False

    async def get_vibecode_session(self, session_id: str) -> Optional[VibecodeSession]:
        """Retrieve vibecode session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT session_data FROM vibecode_sessions WHERE session_id = ?
                """,
                    (session_id,),
                )

                row = cursor.fetchone()
                if row:
                    return self._deserialize_vibecode_session(row[0])

            return None

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve vibecode session {session_id}: {e}")
            return None

    async def store_voice_input(self, voice_input: VoiceInput) -> bool:
        """Store voice input"""
        try:
            input_json = self._serialize_voice_input(voice_input)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO voice_inputs
                    (input_id, session_id, user_id, input_data, timestamp, confidence, intent)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        voice_input.input_id,
                        voice_input.session_id,
                        "unknown",  # Will be filled by session context
                        input_json,
                        voice_input.timestamp.isoformat(),
                        voice_input.confidence,
                        voice_input.intent.value,
                    ),
                )
                conn.commit()

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to store voice input {voice_input.input_id}: {e}"
            )
            return False

    async def get_recent_sessions(
        self, user_id: str, days: int = 30
    ) -> List[Dict[str, any]]:
        """Get recent sessions for success pattern analysis"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT session_id, start_time, end_time, session_data, total_input_words
                    FROM vibecode_sessions
                    WHERE user_id = ? AND start_time >= ?
                    ORDER BY start_time DESC
                """,
                    (user_id, cutoff_date.isoformat()),
                )

                sessions = []
                for row in cursor.fetchall():
                    session_id, start_time, end_time, session_data, total_words = row

                    # Parse session data for analysis
                    session_dict = json.loads(session_data)

                    # Calculate productivity metrics
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = (
                        datetime.fromisoformat(
                            end_time) if end_time else datetime.now()
                    )
                    duration_minutes = (end_dt - start_dt).total_seconds() / 60

                    words_per_minute = total_words / max(duration_minutes, 1)

                    sessions.append(
                        {
                            "session_id": session_id,
                            "start_time": start_dt,
                            "end_time": end_dt,
                            "duration_minutes": duration_minutes,
                            "total_words": total_words,
                            "words_per_minute": words_per_minute,
                            "mood": session_dict.get("session_metadata", {}).get(
                                "mood", "focused"
                            ),
                            "energy_level": session_dict.get(
                                "session_metadata", {}
                            ).get("energy_level", 0.5),
                            "success_score": session_dict.get(
                                "session_metadata", {}
                            ).get("success_score", 0.0),
                        }
                    )

                return sessions

        except Exception as e:
            self.logger.error(
                f"Failed to retrieve recent sessions for user {user_id}: {e}"
            )
            return []

    async def store_success_metric(
        self,
        user_id: str,
        session_id: Optional[str],
        metric_type: str,
        metric_data: Dict[str, any],
    ) -> bool:
        """Store success metric"""
        try:
            metric_id = f"{user_id}_{metric_type}_{datetime.now().isoformat()}"
            metric_json = json.dumps(metric_data)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO success_metrics
                    (metric_id, user_id, session_id, metric_type, metric_data, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        metric_id,
                        user_id,
                        session_id,
                        metric_type,
                        metric_json,
                        datetime.now().isoformat(),
                    ),
                )
                conn.commit()

            return True

        except Exception as e:
            self.logger.error(f"Failed to store success metric: {e}")
            return False

    async def get_user_statistics(self, user_id: str) -> Dict[str, any]:
        """Get comprehensive user statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get basic user stats
                cursor = conn.execute(
                    """
                    SELECT total_sessions, total_words_created, last_updated
                    FROM author_contexts WHERE user_id = ?
                """,
                    (user_id,),
                )

                basic_stats = cursor.fetchone()
                if not basic_stats:
                    return {}

                total_sessions, total_words, last_updated = basic_stats

                # Get session statistics
                cursor = conn.execute(
                    """
                    SELECT COUNT(*), AVG(total_input_words),
                           MIN(start_time), MAX(start_time)
                    FROM vibecode_sessions WHERE user_id = ?
                """,
                    (user_id,),
                )

                session_stats = cursor.fetchone()
                session_count, avg_words, first_session, last_session = session_stats

                # Get voice input statistics
                cursor = conn.execute(
                    """
                    SELECT COUNT(*), AVG(confidence)
                    FROM voice_inputs WHERE user_id = ?
                """,
                    (user_id,),
                )

                voice_stats = cursor.fetchone()
                input_count, avg_confidence = voice_stats

                return {
                    "total_sessions": total_sessions,
                    "total_words_created": total_words,
                    "last_updated": last_updated,
                    "session_count": session_count or 0,
                    "avg_words_per_session": avg_words or 0,
                    "first_session": first_session,
                    "last_session": last_session,
                    "total_voice_inputs": input_count or 0,
                    "avg_voice_confidence": avg_confidence or 0,
                }

        except Exception as e:
            self.logger.error(
                f"Failed to get user statistics for {user_id}: {e}")
            return {}

    async def cleanup_old_data(self, days_to_keep: int = 90) -> bool:
        """Clean up old data beyond retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_iso = cutoff_date.isoformat()

            with sqlite3.connect(self.db_path) as conn:
                # Clean up old voice inputs
                cursor = conn.execute(
                    """
                    DELETE FROM voice_inputs WHERE timestamp < ?
                """,
                    (cutoff_iso,),
                )
                voice_deleted = cursor.rowcount

                # Clean up old synthesis history
                cursor = conn.execute(
                    """
                    DELETE FROM context_synthesis_history WHERE timestamp < ?
                """,
                    (cutoff_iso,),
                )
                synthesis_deleted = cursor.rowcount

                # Clean up old sessions (but keep at least 10 most recent per user)
                cursor = conn.execute(
                    """
                    DELETE FROM vibecode_sessions
                    WHERE start_time < ?
                    AND session_id NOT IN (
                        SELECT session_id FROM vibecode_sessions
                        WHERE user_id = vibecode_sessions.user_id
                        ORDER BY start_time DESC LIMIT 10
                    )
                """,
                    (cutoff_iso,),
                )
                sessions_deleted = cursor.rowcount

                conn.commit()

                self.logger.info(
                    f"Cleaned up old data: {voice_deleted} voice inputs, "
                    f"{synthesis_deleted} synthesis records, {
                        sessions_deleted} sessions"
                )
                return True

        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return False

    def _serialize_author_context(self, context: AuthorContext) -> str:
        """Serialize author context to JSON"""
        # Convert enums and complex objects to serializable format
        serializable_context = {
            "user_id": context.user_id,
            "writing_style": {
                "tone": context.writing_style.tone,
                "complexity": context.writing_style.complexity,
                "sentence_length_preference": context.writing_style.sentence_length_preference,
                "vocabulary_level": context.writing_style.vocabulary_level,
                "narrative_voice": context.writing_style.narrative_voice,
                "dialogue_style": context.writing_style.dialogue_style,
                "pacing_preference": context.writing_style.pacing_preference,
                "genre_preferences": [
                    g.value for g_var in context.writing_style.genre_preferences
                ],
                "favorite_themes": context.writing_style.favorite_themes,
                "writing_patterns": context.writing_style.writing_patterns,
            },
            "preferences": {
                "preferred_length": context.preferences.preferred_length,
                "target_audience": context.preferences.target_audience,
                "content_rating": context.preferences.content_rating,
                "publishing_goals": context.preferences.publishing_goals,
                "market_focus": context.preferences.market_focus,
                "collaboration_style": context.preferences.collaboration_style,
                "feedback_frequency": context.preferences.feedback_frequency,
                "quality_focus": context.preferences.quality_focus,
            },
            "past_works": [
                {
                    "title": work.title,
                    "genre": work.genre.value,
                    "length": work.length,
                    "success_metrics": work.success_metrics,
                    "style_analysis": work.style_analysis,
                    "market_performance": work.market_performance,
                    "lessons_learned": work.lessons_learned,
                }
                for work in context.past_works
            ],
            "success_patterns": {
                "effective_genres": [
                    g.value for g_var in context.success_patterns.effective_genres
                ],
                "successful_themes": context.success_patterns.successful_themes,
                "optimal_writing_times": context.success_patterns.optimal_writing_times,
                "productive_moods": [
                    m.value for m_var in context.success_patterns.productive_moods
                ],
                "market_insights": context.success_patterns.market_insights,
                "quality_indicators": context.success_patterns.quality_indicators,
            },
            "current_mood": context.current_mood.value,
            "session_intent": context.session_intent.value,
            "creative_energy": context.creative_energy,
            "last_updated": context.last_updated.isoformat(),
            "total_sessions": context.total_sessions,
            "total_words_created": context.total_words_created,
        }

        return json.dumps(serializable_context)

    def _deserialize_author_context(self, json_str: str) -> AuthorContext:
        """Deserialize author context from JSON"""
        from .models import BookGenre, CreativeMood, Intent  # Avoid circular imports

        data = json.loads(json_str)

        # Reconstruct complex objects
        context = AuthorContext(user_id=data["user_id"])

        # Reconstruct writing style
        style_data = data.get("writing_style", {})
        context.writing_style.tone = style_data.get("tone", "conversational")
        context.writing_style.complexity = style_data.get("complexity", 0.5)
        context.writing_style.sentence_length_preference = style_data.get(
            "sentence_length_preference", "medium"
        )
        context.writing_style.vocabulary_level = style_data.get(
            "vocabulary_level", "accessible"
        )
        context.writing_style.narrative_voice = style_data.get(
            "narrative_voice", "third_person"
        )
        context.writing_style.dialogue_style = style_data.get(
            "dialogue_style", "natural"
        )
        context.writing_style.pacing_preference = style_data.get(
            "pacing_preference", "balanced"
        )
        context.writing_style.genre_preferences = [
            BookGenre(g) for g_var in style_data.get("genre_preferences", [])
        ]
        context.writing_style.favorite_themes = style_data.get(
            "favorite_themes", [])
        context.writing_style.writing_patterns = style_data.get(
            "writing_patterns", {})

        # Reconstruct preferences
        prefs_data = data.get("preferences", {})
        context.preferences.preferred_length = prefs_data.get(
            "preferred_length", "medium"
        )
        context.preferences.target_audience = prefs_data.get(
            "target_audience", "general"
        )
        context.preferences.content_rating = prefs_data.get(
            "content_rating", "pg")
        context.preferences.publishing_goals = prefs_data.get(
            "publishing_goals", [])
        context.preferences.market_focus = prefs_data.get("market_focus", [])
        context.preferences.collaboration_style = prefs_data.get(
            "collaboration_style", "guided"
        )
        context.preferences.feedback_frequency = prefs_data.get(
            "feedback_frequency", "regular"
        )
        context.preferences.quality_focus = prefs_data.get(
            "quality_focus", "balanced")

        # Reconstruct other fields
        context.current_mood = CreativeMood(
            data.get("current_mood", "focused"))
        context.session_intent = Intent(
            data.get("session_intent", "explore_ideas"))
        context.creative_energy = data.get("creative_energy", 0.5)
        context.last_updated = datetime.fromisoformat(
            data.get("last_updated", datetime.now().isoformat())
        )
        context.total_sessions = data.get("total_sessions", 0)
        context.total_words_created = data.get("total_words_created", 0)

        return context

    def _serialize_vibecode_session(self, session: VibecodeSession) -> str:
        """Serialize vibecode session to JSON"""
        return json.dumps(
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "session_metadata": session.session_metadata,
                "target_book_metadata": session.target_book_metadata,
                "session_status": session.session_status,
                "voice_input_count": len(session.voice_inputs),
                "context_history_count": len(session.context_history),
                "feedback_count": len(session.feedback_history),
            }
        )

    def _deserialize_vibecode_session(self, json_str: str) -> VibecodeSession:
        """Deserialize vibecode session from JSON"""
        data = json.loads(json_str)

        session = VibecodeSession()
        session.session_id = data["session_id"]
        session.user_id = data["user_id"]
        session.start_time = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            session.end_time = datetime.fromisoformat(data["end_time"])
        session.session_metadata = data.get("session_metadata", {})
        session.target_book_metadata = data.get("target_book_metadata", {})
        session.session_status = data.get("session_status", "active")

        return session

    def _serialize_voice_input(self, voice_input: VoiceInput) -> str:
        """Serialize voice input to JSON"""
        return json.dumps(
            {
                "input_id": voice_input.input_id,
                "session_id": voice_input.session_id,
                "text": voice_input.text,
                "confidence": voice_input.confidence,
                "emotions": {
                    "primary_emotion": voice_input.emotions.primary_emotion,
                    "intensity": voice_input.emotions.intensity,
                    "secondary_emotions": voice_input.emotions.secondary_emotions,
                    "mood": voice_input.emotions.mood.value,
                    "energy_level": voice_input.emotions.energy_level,
                    "creative_intent": voice_input.emotions.creative_intent,
                    "emotional_stability": voice_input.emotions.emotional_stability,
                    "enthusiasm_score": voice_input.emotions.enthusiasm_score,
                },
                "intent": voice_input.intent.value,
                "voice_characteristics": {
                    "tone": voice_input.voice_characteristics.tone,
                    "pace": voice_input.voice_characteristics.pace,
                    "emphasis_patterns": voice_input.voice_characteristics.emphasis_patterns,
                    "speech_markers": voice_input.voice_characteristics.speech_markers,
                    "personality_indicators": voice_input.voice_characteristics.personality_indicators,
                    "clarity_score": voice_input.voice_characteristics.clarity_score,
                    "confidence_level": voice_input.voice_characteristics.confidence_level,
                },
                "timestamp": voice_input.timestamp.isoformat(),
                "raw_audio_path": voice_input.raw_audio_path,
                "processing_metadata": voice_input.processing_metadata,
            }
        )
