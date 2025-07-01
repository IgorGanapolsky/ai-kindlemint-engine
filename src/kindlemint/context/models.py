"""
Core data models for the KindleMint Context Engine

Defines the fundamental data structures used throughout the vibecoding system
for context management, voice processing, and content generation.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Intent(Enum):
    """User intent classifications for voice input"""

    CREATE_BOOK = "create_book"
    EDIT_CONTENT = "edit_content"
    ADD_CHAPTER = "add_chapter"
    REFINE_STYLE = "refine_style"
    CHANGE_GENRE = "change_genre"
    MARKET_OPTIMIZE = "market_optimize"
    PUBLISH_BOOK = "publish_book"
    GET_FEEDBACK = "get_feedback"
    EXPLORE_IDEAS = "explore_ideas"
    SET_VIBE = "set_vibe"


class CreativeMood(Enum):
    """Creative mood classifications"""

    INSPIRED = "inspired"
    FOCUSED = "focused"
    EXPLORATORY = "exploratory"
    PLAYFUL = "playful"
    SERIOUS = "serious"
    EXPERIMENTAL = "experimental"
    REFLECTIVE = "reflective"
    ENERGETIC = "energetic"
    CONTEMPLATIVE = "contemplative"
    PASSIONATE = "passionate"


class BookGenre(Enum):
    """Book genre classifications"""

    MYSTERY = "mystery"
    ROMANCE = "romance"
    FANTASY = "fantasy"
    SCIENCE_FICTION = "science_fiction"
    THRILLER = "thriller"
    HORROR = "horror"
    LITERARY_FICTION = "literary_fiction"
    HISTORICAL_FICTION = "historical_fiction"
    YOUNG_ADULT = "young_adult"
    CHILDREN = "children"
    NON_FICTION = "non_fiction"
    SELF_HELP = "self_help"
    BIOGRAPHY = "biography"
    BUSINESS = "business"
    HEALTH = "health"
    TRAVEL = "travel"
    COOKBOOK = "cookbook"
    PUZZLE_BOOK = "puzzle_book"


@dataclass
class VoiceCharacteristics:
    """Characteristics extracted from voice patterns"""

    tone: str = ""  # warm, energetic, calm, etc.
    pace: float = 1.0  # speaking pace relative to normal
    emphasis_patterns: List[str] = field(default_factory=list)
    speech_markers: Dict[str, Any] = field(default_factory=dict)
    personality_indicators: Dict[str, float] = field(default_factory=dict)
    clarity_score: float = 1.0
    confidence_level: float = 1.0


@dataclass
class EmotionProfile:
    """Emotional context extracted from voice and content"""

    primary_emotion: str = "neutral"
    intensity: float = 0.5  # 0.0 to 1.0
    secondary_emotions: List[str] = field(default_factory=list)
    mood: CreativeMood = CreativeMood.FOCUSED
    energy_level: float = 0.5  # 0.0 to 1.0
    creative_intent: List[str] = field(default_factory=list)
    emotional_stability: float = 1.0
    enthusiasm_score: float = 0.5


@dataclass
class VoiceInput:
    """Processed voice input with rich metadata"""

    session_id: str
    input_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    confidence: float = 0.0
    emotions: EmotionProfile = field(default_factory=EmotionProfile)
    intent: Intent = Intent.EXPLORE_IDEAS
    voice_characteristics: VoiceCharacteristics = field(
        default_factory=VoiceCharacteristics
    )
    timestamp: datetime = field(default_factory=datetime.now)
    raw_audio_path: Optional[str] = None
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WritingStyleProfile:
    """Author's writing style characteristics"""

    tone: str = "conversational"  # formal, casual, conversational, etc.
    complexity: float = 0.5  # 0.0 simple to 1.0 complex
    sentence_length_preference: str = "medium"  # short, medium, long, varied
    vocabulary_level: str = "accessible"  # simple, accessible, advanced, academic
    narrative_voice: str = "third_person"  # first_person, third_person, omniscient
    dialogue_style: str = "natural"  # formal, natural, stylized
    pacing_preference: str = "balanced"  # fast, balanced, slow, varied
    genre_preferences: List[BookGenre] = field(default_factory=list)
    favorite_themes: List[str] = field(default_factory=list)
    writing_patterns: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPreferences:
    """User preferences for content creation"""

    preferred_length: str = "medium"  # short, medium, long
    target_audience: str = "general"  # children, ya, adult, academic
    content_rating: str = "pg"  # g, pg, pg13, r
    publishing_goals: List[str] = field(default_factory=list)
    market_focus: List[str] = field(default_factory=list)
    collaboration_style: str = "guided"  # independent, guided, collaborative
    feedback_frequency: str = "regular"  # minimal, regular, frequent
    quality_focus: str = "balanced"  # speed, balanced, perfectionist


@dataclass
class WorkProfile:
    """Profile of a past work"""

    title: str
    genre: BookGenre
    length: int  # word count
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    style_analysis: Dict[str, Any] = field(default_factory=dict)
    market_performance: Dict[str, Any] = field(default_factory=dict)
    lessons_learned: List[str] = field(default_factory=list)


@dataclass
class SuccessPatterns:
    """Patterns that lead to success for this author"""

    effective_genres: List[BookGenre] = field(default_factory=list)
    successful_themes: List[str] = field(default_factory=list)
    optimal_writing_times: List[str] = field(default_factory=list)
    productive_moods: List[CreativeMood] = field(default_factory=list)
    market_insights: Dict[str, Any] = field(default_factory=dict)
    quality_indicators: Dict[str, float] = field(default_factory=dict)


@dataclass
class AuthorContext:
    """Comprehensive author context"""

    user_id: str
    writing_style: WritingStyleProfile = field(default_factory=WritingStyleProfile)
    preferences: UserPreferences = field(default_factory=UserPreferences)
    past_works: List[WorkProfile] = field(default_factory=list)
    success_patterns: SuccessPatterns = field(default_factory=SuccessPatterns)
    current_mood: CreativeMood = CreativeMood.FOCUSED
    session_intent: Intent = Intent.EXPLORE_IDEAS
    creative_energy: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)
    total_sessions: int = 0
    total_words_created: int = 0


@dataclass
class MarketTrend:
    """Market trend information"""

    trend_id: str
    category: str
    popularity_score: float
    growth_rate: float
    keywords: List[str] = field(default_factory=list)
    target_demographics: List[str] = field(default_factory=list)
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    competition_level: str = "medium"


@dataclass
class MarketContext:
    """Market intelligence context"""

    current_trends: List[MarketTrend] = field(default_factory=list)
    target_keywords: List[str] = field(default_factory=list)
    competition_analysis: Dict[str, Any] = field(default_factory=dict)
    pricing_insights: Dict[str, Any] = field(default_factory=dict)
    audience_preferences: Dict[str, Any] = field(default_factory=dict)
    seasonal_opportunities: Dict[str, Any] = field(default_factory=dict)
    platform_optimizations: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class CreativePattern:
    """Creative writing pattern"""

    pattern_id: str
    name: str
    genre: BookGenre
    structure_template: Dict[str, Any] = field(default_factory=dict)
    character_archetypes: List[str] = field(default_factory=list)
    plot_devices: List[str] = field(default_factory=list)
    theme_elements: List[str] = field(default_factory=list)
    style_guidelines: Dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0


@dataclass
class CreativeContext:
    """Creative writing context and patterns"""

    relevant_patterns: List[CreativePattern] = field(default_factory=list)
    genre_conventions: Dict[str, Any] = field(default_factory=dict)
    story_structures: Dict[str, Any] = field(default_factory=dict)
    character_development: Dict[str, Any] = field(default_factory=dict)
    world_building: Dict[str, Any] = field(default_factory=dict)
    dialogue_patterns: Dict[str, Any] = field(default_factory=dict)
    narrative_techniques: List[str] = field(default_factory=list)
    creative_constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishingFormat:
    """Publishing format specification"""

    format_type: str  # ebook, paperback, hardcover, audio
    platform: str  # kdp, ingramspark, etc.
    specifications: Dict[str, Any] = field(default_factory=dict)
    optimization_rules: Dict[str, Any] = field(default_factory=dict)
    quality_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishingContext:
    """Publishing platform context"""

    target_formats: List[PublishingFormat] = field(default_factory=list)
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    seo_optimizations: Dict[str, Any] = field(default_factory=dict)
    metadata_templates: Dict[str, Any] = field(default_factory=dict)
    quality_standards: Dict[str, Any] = field(default_factory=dict)
    distribution_strategies: Dict[str, Any] = field(default_factory=dict)
    monetization_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextSynthesisWeights:
    """Weights for context synthesis attention mechanism"""

    author_weight: float = 0.4
    market_weight: float = 0.2
    creative_weight: float = 0.3
    publishing_weight: float = 0.1

        """Normalize"""
    def normalize(self):
        """Normalize weights to sum to 1.0"""
        total = (
            self.author_weight
            + self.market_weight
            + self.creative_weight
            + self.publishing_weight
        )
        if total > 0:
            self.author_weight /= total
            self.market_weight /= total
            self.creative_weight /= total
            self.publishing_weight /= total


@dataclass
class SynthesizedContext:
    """Synthesized multi-layer context for content generation"""

    session_id: str
    author: AuthorContext
    market: MarketContext
    creative: CreativeContext
    publishing: PublishingContext
    synthesis_weights: ContextSynthesisWeights = field(
        default_factory=ContextSynthesisWeights
    )
    synthesis_timestamp: datetime = field(default_factory=datetime.now)
    quality_score: float = 0.0
    coherence_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)

    def get_primary_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the primary context elements"""
        return {
            "author_mood": self.author.current_mood.value,
            "writing_style": self.author.writing_style.tone,
            "genre_preferences": [
                g.value for g_var in self.author.writing_style.genre_preferences
            ],
            "market_trends": [t.category for t_var in self.market.current_trends[:3]],
            "creative_patterns": [p.name for p_var in self.creative.relevant_patterns[:3]],
            "target_formats": [f.format_type f_varor f_var in self.publishing.target_formats],
            "synthesis_quality": self.quality_score,
        }


@dataclass
class VibecodeSession:
    """A complete vibecoding session"""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    voice_inputs: List[VoiceInput] = field(default_factory=list)
    context_history: List[SynthesizedContext] = field(default_factory=list)
    generated_content: Dict[str, Any] = field(default_factory=dict)
    feedback_history: List[Dict[str, Any]] = field(default_factory=list)
    session_metadata: Dict[str, Any] = field(default_factory=dict)
    target_book_metadata: Dict[str, Any] = field(default_factory=dict)
    session_status: str = "active"  # active, paused, completed, abandoned

    @property
    def session_duration(self) -> Optional[float]:
        """Get session duration in minutes"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60
        return (datetime.now() - self.start_time).total_seconds() / 60

    @property
    def total_input_words(self) -> int:
        """Get total words in voice inputs"""
        return sum(len(vi.text.split()) for vi in self.voice_inputs)

    @property
    def latest_context(self) -> Optional[SynthesizedContext]:
        """Get the most recent context"""
        return self.context_history[-1] if self.context_history else None
