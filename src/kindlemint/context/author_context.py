"""
Author Context Builder for KindleMint Vibecoding System

This module builds and maintains comprehensive author profiles that enable
personalized, context-aware content generation through voice interaction.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from .context_memory import ContextMemoryStore
from .models import (
    AuthorContext,
    BookGenre,
    CreativeMood,
    Intent,
    SuccessPatterns,
    UserPreferences,
    VoiceInput,
    WorkProfile,
    WritingStyleProfile,
)

logger = logging.getLogger(__name__)


class WritingStyleAnalyzer:
    """Analyzes and updates writing style based on voice patterns and content"""

    def __init__(self):
        self.tone_keywords = {
            "formal": ["furthermore", "therefore", "consequently", "moreover"],
            "casual": ["yeah", "kinda", "stuff", "things", "like"],
            "conversational": ["you know", "well", "so", "actually", "basically"],
            "academic": ["hypothesis", "methodology", "analysis", "framework"],
            "creative": ["imagine", "envision", "perhaps", "wonder", "dream"],
        }

        self.complexity_indicators = {
            "simple": {
                "avg_words_per_sentence": (1, 10),
                "syllables_per_word": (1.0, 1.5),
            },
            "accessible": {
                "avg_words_per_sentence": (10, 20),
                "syllables_per_word": (1.5, 2.0),
            },
            "advanced": {
                "avg_words_per_sentence": (20, 30),
                "syllables_per_word": (2.0, 2.5),
            },
            "academic": {
                "avg_words_per_sentence": (30, 50),
                "syllables_per_word": (2.5, 3.5),
            },
        }

    async def analyze_voice_input(self, voice_input: VoiceInput) -> Dict[str, any]:
        """Analyze writing style indicators from voice input"""
        text = voice_input.text.lower()
        words = text.split()
        sentences = text.split(".")

        # Analyze tone
        tone_scores = {}
        for tone, keywords in self.tone_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text) / len(keywords)
            tone_scores[tone] = score

        # Determine dominant tone
        dominant_tone = (
            max(tone_scores, key=tone_scores.get) if tone_scores else "conversational"
        )

        # Analyze complexity
        avg_words_per_sentence = len(words) / max(len(sentences), 1)
        avg_syllables = self._estimate_avg_syllables(words)

        complexity = self._determine_complexity(avg_words_per_sentence, avg_syllables)

        # Analyze voice characteristics for writing style
        voice_style_indicators = self._extract_voice_style_indicators(voice_input)

        return {
            "tone": dominant_tone,
            "tone_confidence": tone_scores.get(dominant_tone, 0),
            "complexity": complexity,
            "avg_words_per_sentence": avg_words_per_sentence,
            "avg_syllables_per_word": avg_syllables,
            "voice_characteristics": voice_style_indicators,
            "sample_phrases": self._extract_characteristic_phrases(text),
            "creative_markers": self._identify_creative_markers(text),
        }

    def _estimate_avg_syllables(self, words: List[str]) -> float:
        """Estimate average syllables per word (simplified)"""
        if not words:
            return 1.0

        total_syllables = 0
        for word in words:
            # Simple syllable counting heuristic
            vowels = "aeiouy"
            syllable_count = 0
            prev_was_vowel = False

            for char in word.lower():
                is_vowel = char in vowels
                if is_vowel and not prev_was_vowel:
                    syllable_count += 1
                prev_was_vowel = is_vowel

            # Minimum of 1 syllable per word
            total_syllables += max(syllable_count, 1)

        return total_syllables / len(words)

    def _determine_complexity(self, avg_words: float, avg_syllables: float) -> str:
        """Determine complexity level based on metrics"""
        for level, ranges in self.complexity_indicators.items():
            word_range = ranges["avg_words_per_sentence"]
            syllable_range = ranges["syllables_per_word"]

            if (
                word_range[0] <= avg_words <= word_range[1]
                and syllable_range[0] <= avg_syllables <= syllable_range[1]
            ):
                return level

        return "accessible"  # default

    def _extract_voice_style_indicators(
        self, voice_input: VoiceInput
    ) -> Dict[str, any]:
        """Extract style indicators from voice characteristics"""
        voice_chars = voice_input.voice_characteristics
        emotions = voice_input.emotions

        return {
            "energy_level": emotions.energy_level,
            "confidence": voice_chars.confidence_level,
            "pace_preference": (
                "fast"
                if voice_chars.pace > 1.2
                else "slow" if voice_chars.pace < 0.8 else "medium"
            ),
            "expressiveness": emotions.intensity,
            "enthusiasm": emotions.enthusiasm_score,
        }

    def _extract_characteristic_phrases(self, text: str) -> List[str]:
        """Extract characteristic phrases that indicate writing style"""
        characteristic_phrases = []

        # Common transitional phrases
        transitions = [
            "however",
            "meanwhile",
            "in addition",
            "furthermore",
            "on the other hand",
        ]
        for transition in transitions:
            if transition in text:
                characteristic_phrases.append(transition)

        # Creative expressions
        creative_expressions = ["imagine", "picture this", "what if", "suddenly"]
        for expression in creative_expressions:
            if expression in text:
                characteristic_phrases.append(expression)

        return characteristic_phrases[:5]  # Limit to top 5

    def _identify_creative_markers(self, text: str) -> List[str]:
        """Identify markers that indicate creative intent"""
        creative_markers = []

        markers = {
            "sensory": ["hear", "see", "feel", "taste", "smell", "touch"],
            "emotional": ["love", "fear", "joy", "anger", "sadness", "excitement"],
            "temporal": ["suddenly", "meanwhile", "later", "before", "after"],
            "descriptive": ["beautiful", "dark", "bright", "mysterious", "ancient"],
            "action": ["run", "jump", "fight", "dance", "fly", "climb"],
        }

        for category, words in markers.items():
            found_words = [word for word in words if word in text]
            if found_words:
                creative_markers.extend(
                    [f"{category}:{word}" for word in found_words[:2]]
                )

        return creative_markers


class PreferenceEngine:
    """Manages and updates user preferences based on interactions"""

    def __init__(self):
        self.genre_keywords = {
            BookGenre.MYSTERY: [
                "mystery",
                "detective",
                "clue",
                "solve",
                "investigation",
            ],
            BookGenre.ROMANCE: ["love", "romance", "relationship", "heart", "passion"],
            BookGenre.FANTASY: ["magic", "dragon", "quest", "realm", "wizard"],
            BookGenre.SCIENCE_FICTION: [
                "future",
                "space",
                "technology",
                "alien",
                "robot",
            ],
            BookGenre.THRILLER: ["suspense", "danger", "chase", "tension", "escape"],
            BookGenre.HORROR: ["fear", "scary", "nightmare", "ghost", "dark"],
            BookGenre.SELF_HELP: ["improve", "guide", "tips", "success", "personal"],
            BookGenre.BUSINESS: [
                "strategy",
                "marketing",
                "profit",
                "business",
                "entrepreneur",
            ],
        }

    async def update_preferences(
        self,
        current_prefs: UserPreferences,
        voice_input: VoiceInput,
        session_context: Dict[str, any],
    ) -> UserPreferences:
        """Update user preferences based on new voice input and session data"""

        # Analyze genre preferences from voice input
        genre_preferences = self._analyze_genre_preferences(voice_input.text)

        # Update publishing goals based on expressed intent
        publishing_goals = self._extract_publishing_goals(voice_input)

        # Analyze collaboration style from interaction patterns
        collaboration_style = self._determine_collaboration_style(
            voice_input, session_context
        )

        # Update preferences
        updated_prefs = UserPreferences(
            preferred_length=current_prefs.preferred_length,
            target_audience=self._infer_target_audience(voice_input),
            content_rating=current_prefs.content_rating,
            publishing_goals=list(
                set(current_prefs.publishing_goals + publishing_goals)
            ),
            market_focus=current_prefs.market_focus,
            collaboration_style=collaboration_style,
            feedback_frequency=self._determine_feedback_frequency(voice_input),
            quality_focus=self._determine_quality_focus(voice_input),
        )

        return updated_prefs

    def _analyze_genre_preferences(self, text: str) -> List[BookGenre]:
        """Analyze text to identify genre preferences"""
        text_lower = text.lower()
        genre_scores = {}

        for genre, keywords in self.genre_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                genre_scores[genre] = score

        # Return genres sorted by score
        return [
            genre
            for genre, score in sorted(
                genre_scores.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _extract_publishing_goals(self, voice_input: VoiceInput) -> List[str]:
        """Extract publishing goals from voice input"""
        text = voice_input.text.lower()
        goals = []

        goal_indicators = {
            "bestseller": ["bestseller", "popular", "success", "hit"],
            "passive_income": ["income", "money", "profit", "earnings"],
            "creative_expression": ["express", "creative", "art", "personal"],
            "help_others": ["help", "teach", "guide", "inspire"],
            "build_authority": ["expert", "authority", "credibility", "reputation"],
        }

        for goal, indicators in goal_indicators.items():
            if any(indicator in text for indicator in indicators):
                goals.append(goal)

        return goals

    def _determine_collaboration_style(
        self, voice_input: VoiceInput, session_context: Dict[str, any]
    ) -> str:
        """Determine preferred collaboration style"""
        text = voice_input.text.lower()

        if any(phrase in text for phrase in ["help me", "guide me", "suggestions"]):
            return "guided"
        elif any(
            phrase in text for phrase in ["work together", "collaborate", "partner"]
        ):
            return "collaborative"
        elif any(phrase in text for phrase in ["on my own", "independent", "myself"]):
            return "independent"

        return "guided"  # default

    def _infer_target_audience(self, voice_input: VoiceInput) -> str:
        """Infer target audience from voice input"""
        text = voice_input.text.lower()

        if any(word in text for word in ["kids", "children", "young"]):
            return "children"
        elif any(word in text for word in ["teen", "teenager", "ya"]):
            return "ya"
        elif any(word in text for word in ["academic", "scholarly", "research"]):
            return "academic"

        return "general"

    def _determine_feedback_frequency(self, voice_input: VoiceInput) -> str:
        """Determine preferred feedback frequency"""
        text = voice_input.text.lower()

        if any(
            phrase in text
            for phrase in ["check often", "frequent feedback", "keep checking"]
        ):
            return "frequent"
        elif any(
            phrase in text
            for phrase in ["minimal feedback", "less interruption", "minimal"]
        ):
            return "minimal"

        return "regular"

    def _determine_quality_focus(self, voice_input: VoiceInput) -> str:
        """Determine quality vs speed preference"""
        text = voice_input.text.lower()

        if any(
            phrase in text for phrase in ["perfect", "high quality", "best possible"]
        ):
            return "perfectionist"
        elif any(phrase in text for phrase in ["quick", "fast", "rapid", "speed"]):
            return "speed"

        return "balanced"


class SuccessPatternsAnalyzer:
    """Analyzes and identifies patterns that lead to success"""

    async def analyze_success_patterns(
        self, past_works: List[WorkProfile], recent_sessions: List[Dict[str, any]]
    ) -> SuccessPatterns:
        """Analyze past works and sessions to identify success patterns"""

        if not past_works:
            return SuccessPatterns()

        # Analyze effective genres
        effective_genres = self._analyze_effective_genres(past_works)

        # Analyze successful themes
        successful_themes = self._analyze_successful_themes(past_works)

        # Analyze optimal writing times from sessions
        optimal_times = self._analyze_optimal_writing_times(recent_sessions)

        # Analyze productive moods
        productive_moods = self._analyze_productive_moods(recent_sessions)

        # Extract market insights
        market_insights = self._extract_market_insights(past_works)

        # Calculate quality indicators
        quality_indicators = self._calculate_quality_indicators(past_works)

        return SuccessPatterns(
            effective_genres=effective_genres,
            successful_themes=successful_themes,
            optimal_writing_times=optimal_times,
            productive_moods=productive_moods,
            market_insights=market_insights,
            quality_indicators=quality_indicators,
        )

    def _analyze_effective_genres(
        self, past_works: List[WorkProfile]
    ) -> List[BookGenre]:
        """Identify genres with highest success rates"""
        genre_performance = {}

        for work in past_works:
            genre = work.genre
            success_score = work.success_metrics.get("overall_score", 0)

            if genre not in genre_performance:
                genre_performance[genre] = []
            genre_performance[genre].append(success_score)

        # Calculate average performance per genre
        genre_averages = {}
        for genre, scores in genre_performance.items():
            genre_averages[genre] = sum(scores) / len(scores)

        # Return genres sorted by average performance
        return [
            genre
            for genre, avg in sorted(
                genre_averages.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _analyze_successful_themes(self, past_works: List[WorkProfile]) -> List[str]:
        """Identify themes that correlate with success"""
        theme_performance = {}

        for work in past_works:
            success_score = work.success_metrics.get("overall_score", 0)
            themes = work.style_analysis.get("themes", [])

            for theme in themes:
                if theme not in theme_performance:
                    theme_performance[theme] = []
                theme_performance[theme].append(success_score)

        # Calculate average performance per theme
        theme_averages = {}
        for theme, scores in theme_performance.items():
            if len(scores) >= 2:  # Only consider themes with multiple data points
                theme_averages[theme] = sum(scores) / len(scores)

        # Return top performing themes
        return [
            theme
            for theme, avg in sorted(
                theme_averages.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

    def _analyze_optimal_writing_times(
        self, recent_sessions: List[Dict[str, any]]
    ) -> List[str]:
        """Analyze when the user is most productive"""
        time_productivity = {}

        for session in recent_sessions:
            start_time = session.get("start_time", datetime.now())
            hour = start_time.hour
            productivity = session.get("words_per_minute", 0)

            time_slot = self._get_time_slot(hour)
            if time_slot not in time_productivity:
                time_productivity[time_slot] = []
            time_productivity[time_slot].append(productivity)

        # Calculate average productivity per time slot
        slot_averages = {}
        for slot, productivities in time_productivity.items():
            slot_averages[slot] = sum(productivities) / len(productivities)

        # Return time slots sorted by productivity
        return [
            slot
            for slot, avg in sorted(
                slot_averages.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _analyze_productive_moods(
        self, recent_sessions: List[Dict[str, any]]
    ) -> List[CreativeMood]:
        """Analyze which moods lead to highest productivity"""
        mood_productivity = {}

        for session in recent_sessions:
            mood_str = session.get("mood", "focused")
            try:
                mood = CreativeMood(mood_str)
                productivity = session.get("words_per_minute", 0)

                if mood not in mood_productivity:
                    mood_productivity[mood] = []
                mood_productivity[mood].append(productivity)
            except ValueError:
                continue  # Skip invalid moods

        # Calculate average productivity per mood
        mood_averages = {}
        for mood, productivities in mood_productivity.items():
            mood_averages[mood] = sum(productivities) / len(productivities)

        # Return moods sorted by productivity
        return [
            mood
            for mood, avg in sorted(
                mood_averages.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _extract_market_insights(self, past_works: List[WorkProfile]) -> Dict[str, any]:
        """Extract market insights from past performance"""
        insights = {
            "high_performing_keywords": [],
            "effective_pricing": {},
            "successful_launch_strategies": [],
            "audience_preferences": {},
        }

        for work in past_works:
            market_data = work.market_performance
            success_score = work.success_metrics.get("overall_score", 0)

            # Only consider successful works (score > 0.7)
            if success_score > 0.7:
                keywords = market_data.get("keywords", [])
                insights["high_performing_keywords"].extend(keywords)

                pricing = market_data.get("pricing_strategy")
                if pricing:
                    insights["effective_pricing"][work.title] = pricing

        return insights

    def _calculate_quality_indicators(
        self, past_works: List[WorkProfile]
    ) -> Dict[str, float]:
        """Calculate quality indicators based on past performance"""
        if not past_works:
            return {}

        total_works = len(past_works)
        successful_works = sum(
            1
            for work in past_works
            if work.success_metrics.get("overall_score", 0) > 0.7
        )

        avg_length = sum(work.length for work in past_works) / total_works
        avg_success = (
            sum(work.success_metrics.get("overall_score", 0) for work in past_works)
            / total_works
        )

        return {
            "success_rate": successful_works / total_works,
            "average_length": avg_length,
            "average_success_score": avg_success,
            "consistency_score": 1.0
            - (
                max(w.success_metrics.get("overall_score", 0) for w in past_works)
                - min(w.success_metrics.get("overall_score", 0) for w in past_works)
            ),
        }

    def _get_time_slot(self, hour: int) -> str:
        """Convert hour to readable time slot"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"


class AuthorContextBuilder:
    """Main class for building and maintaining author context"""

    def __init__(self, memory_store: Optional[ContextMemoryStore] = None):
        self.memory_store = memory_store or ContextMemoryStore()
        self.style_analyzer = WritingStyleAnalyzer()
        self.preference_engine = PreferenceEngine()
        self.success_analyzer = SuccessPatternsAnalyzer()
        self.logger = logging.getLogger(__name__)

    async def build_context(
        self, user_id: str, voice_input: VoiceInput
    ) -> AuthorContext:
        """Build comprehensive author context for the given user and voice input"""

        try:
            # Retrieve existing author profile
            existing_context = await self.memory_store.get_author_context(user_id)

            # Analyze current voice input for style updates
            style_analysis = await self.style_analyzer.analyze_voice_input(voice_input)

            # Update writing style
            updated_style = await self._update_writing_style(
                (
                    existing_context.writing_style
                    if existing_context
                    else WritingStyleProfile()
                ),
                style_analysis,
            )

            # Update preferences
            updated_preferences = await self.preference_engine.update_preferences(
                existing_context.preferences if existing_context else UserPreferences(),
                voice_input,
                {"style_analysis": style_analysis},
            )

            # Get recent session data for success pattern analysis
            recent_sessions = await self.memory_store.get_recent_sessions(
                user_id, days=30
            )

            # Update success patterns
            past_works = existing_context.past_works if existing_context else []
            updated_success_patterns = (
                await self.success_analyzer.analyze_success_patterns(
                    past_works, recent_sessions
                )
            )

            # Determine current creative mood from voice input
            current_mood = self._determine_creative_mood(voice_input)

            # Build updated context
            author_context = AuthorContext(
                user_id=user_id,
                writing_style=updated_style,
                preferences=updated_preferences,
                past_works=past_works,
                success_patterns=updated_success_patterns,
                current_mood=current_mood,
                session_intent=voice_input.intent,
                creative_energy=voice_input.emotions.energy_level,
                last_updated=datetime.now(),
                total_sessions=(
                    (existing_context.total_sessions + 1) if existing_context else 1
                ),
                total_words_created=(
                    (
                        existing_context.total_words_created
                        + len(voice_input.text.split())
                    )
                    if existing_context
                    else len(voice_input.text.split())
                ),
            )

            # Store updated context
            await self.memory_store.store_author_context(user_id, author_context)

            self.logger.info(
                f"Built author context for user {user_id} with mood {current_mood.value}"
            )
            return author_context

        except Exception as e:
            self.logger.error(f"Error building author context for user {user_id}: {e}")
            # Return basic context on error
            return AuthorContext(
                user_id=user_id,
                current_mood=self._determine_creative_mood(voice_input),
                session_intent=voice_input.intent,
                creative_energy=voice_input.emotions.energy_level,
            )

    async def _update_writing_style(
        self, current_style: WritingStyleProfile, style_analysis: Dict[str, any]
    ) -> WritingStyleProfile:
        """Update writing style based on new analysis"""

        # Merge tone with confidence weighting
        if style_analysis["tone_confidence"] > 0.5:
            current_style.tone = style_analysis["tone"]

        # Update complexity
        current_style.complexity = self._blend_complexity(
            current_style.complexity,
            self._complexity_to_score(style_analysis["complexity"]),
        )

        # Update vocabulary level based on analysis
        current_style.vocabulary_level = style_analysis["complexity"]

        # Update patterns
        voice_characteristics = style_analysis["voice_characteristics"]
        current_style.writing_patterns.update(
            {
                "energy_level": voice_characteristics["energy_level"],
                "confidence": voice_characteristics["confidence"],
                "pace_preference": voice_characteristics["pace_preference"],
                "expressiveness": voice_characteristics["expressiveness"],
            }
        )

        # Add creative markers to favorite themes
        creative_markers = style_analysis.get("creative_markers", [])
        for marker in creative_markers:
            if marker not in current_style.favorite_themes:
                current_style.favorite_themes.append(marker)

        # Limit favorite themes to most recent/relevant
        current_style.favorite_themes = current_style.favorite_themes[-20:]

        return current_style

    def _complexity_to_score(self, complexity: str) -> float:
        """Convert complexity level to numeric score"""
        complexity_scores = {
            "simple": 0.2,
            "accessible": 0.5,
            "advanced": 0.8,
            "academic": 0.9,
        }
        return complexity_scores.get(complexity, 0.5)

    def _blend_complexity(
        self, current: float, new: float, weight: float = 0.3
    ) -> float:
        """Blend current and new complexity scores"""
        return current * (1 - weight) + new * weight

    def _determine_creative_mood(self, voice_input: VoiceInput) -> CreativeMood:
        """Determine creative mood from voice input"""
        emotions = voice_input.emotions

        # Map emotions to creative moods
        if emotions.primary_emotion == "excited" and emotions.energy_level > 0.7:
            return CreativeMood.ENERGETIC
        elif emotions.primary_emotion == "calm" and emotions.intensity > 0.6:
            return CreativeMood.FOCUSED
        elif emotions.energy_level > 0.8:
            return CreativeMood.INSPIRED
        elif (
            "explore" in voice_input.text.lower()
            or "experiment" in voice_input.text.lower()
        ):
            return CreativeMood.EXPERIMENTAL
        elif emotions.intensity < 0.3:
            return CreativeMood.CONTEMPLATIVE
        elif emotions.enthusiasm_score > 0.7:
            return CreativeMood.PASSIONATE
        elif "play" in voice_input.text.lower() or "fun" in voice_input.text.lower():
            return CreativeMood.PLAYFUL
        elif emotions.primary_emotion in ["serious", "determined"]:
            return CreativeMood.SERIOUS
        elif (
            "think" in voice_input.text.lower()
            or "consider" in voice_input.text.lower()
        ):
            return CreativeMood.REFLECTIVE
        else:
            return CreativeMood.FOCUSED  # default
