"""
Vibe Templates for KindleMint Vibecoding System

Defines vibe templates that capture creative intentions, moods, and atmospheric
qualities that users want to express in their books, translating feelings into
actionable creative guidance.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from ..context.models import BookGenre, CreativeMood


class VibeIntensity(Enum):
    """Intensity levels for vibes"""
    SUBTLE = "subtle"           # 0.1-0.3
    MODERATE = "moderate"       # 0.3-0.6  
    STRONG = "strong"          # 0.6-0.8
    INTENSE = "intense"        # 0.8-1.0


class VibeCategory(Enum):
    """Categories of creative vibes"""
    EMOTIONAL = "emotional"           # Love, heartbreak, joy, melancholy
    ATMOSPHERIC = "atmospheric"       # Dark, bright, mysterious, cozy
    ENERGETIC = "energetic"          # Fast-paced, slow-burn, explosive, gentle
    THEMATIC = "thematic"            # Redemption, discovery, transformation
    SENSORY = "sensory"              # Vivid, dreamlike, gritty, ethereal
    RELATIONAL = "relational"        # Intimate, community, isolation, connection


class VibeArchetype(Enum):
    """Fundamental vibe archetypes"""
    # Emotional archetypes
    PASSIONATE_LOVE = "passionate_love"
    BITTERSWEET_NOSTALGIA = "bittersweet_nostalgia"
    RIGHTEOUS_ANGER = "righteous_anger"
    QUIET_MELANCHOLY = "quiet_melancholy"
    INFECTIOUS_JOY = "infectious_joy"
    
    # Atmospheric archetypes  
    DARK_MYSTERY = "dark_mystery"
    COZY_WARMTH = "cozy_warmth"
    ETHEREAL_MAGIC = "ethereal_magic"
    GRITTY_REALISM = "gritty_realism"
    BRIGHT_OPTIMISM = "bright_optimism"
    
    # Energetic archetypes
    HEART_POUNDING = "heart_pounding"
    SLOW_CONTEMPLATION = "slow_contemplation"
    EXPLOSIVE_ACTION = "explosive_action"
    GENTLE_REFLECTION = "gentle_reflection"
    
    # Thematic archetypes
    HEROIC_JOURNEY = "heroic_journey"
    REDEMPTION_ARC = "redemption_arc"
    DISCOVERY_WONDER = "discovery_wonder"
    LOSS_AND_HEALING = "loss_and_healing"
    TRANSFORMATION = "transformation"


@dataclass
class VibeElement:
    """Individual element that contributes to a vibe"""
    element_id: str
    name: str
    description: str
    category: VibeCategory
    intensity: float = 0.5  # 0.0 to 1.0
    keywords: List[str] = field(default_factory=list)
    incompatible_with: List[str] = field(default_factory=list)
    enhances: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, any]:
        return {
            "element_id": self.element_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "intensity": self.intensity,
            "keywords": self.keywords,
            "incompatible_with": self.incompatible_with,
            "enhances": self.enhances
        }


@dataclass 
class CreativeVibe:
    """A complete creative vibe composed of multiple elements"""
    vibe_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    archetype: Optional[VibeArchetype] = None
    primary_elements: List[VibeElement] = field(default_factory=list)
    secondary_elements: List[VibeElement] = field(default_factory=list)
    overall_intensity: VibeIntensity = VibeIntensity.MODERATE
    compatible_genres: Set[BookGenre] = field(default_factory=set)
    creative_mood: CreativeMood = CreativeMood.FOCUSED
    
    # Content guidance
    tone_guidance: Dict[str, any] = field(default_factory=dict)
    style_guidance: Dict[str, any] = field(default_factory=dict)
    structure_guidance: Dict[str, any] = field(default_factory=dict)
    
    # User experience
    created_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    user_rating: Optional[float] = None
    user_feedback: List[str] = field(default_factory=list)
    
    @property
    def primary_category(self) -> VibeCategory:
        """Get the most prominent vibe category"""
        if not self.primary_elements:
            return VibeCategory.ATMOSPHERIC
        
        category_counts = {}
        for element in self.primary_elements:
            category = element.category
            category_counts[category] = category_counts.get(category, 0) + element.intensity
        
        return max(category_counts, key=category_counts.get)
    
    @property 
    def intensity_score(self) -> float:
        """Calculate overall intensity score"""
        if not self.primary_elements:
            return 0.5
        
        total_intensity = sum(element.intensity for element in self.primary_elements)
        return min(total_intensity / len(self.primary_elements), 1.0)
    
    def get_all_keywords(self) -> List[str]:
        """Get all keywords from all elements"""
        keywords = []
        for element in self.primary_elements + self.secondary_elements:
            keywords.extend(element.keywords)
        return list(set(keywords))  # Remove duplicates
    
    def is_compatible_with(self, other: 'CreativeVibe') -> float:
        """Calculate compatibility score with another vibe (0.0 to 1.0)"""
        if not other:
            return 0.0
        
        # Check genre compatibility
        genre_overlap = len(self.compatible_genres & other.compatible_genres)
        max_genres = max(len(self.compatible_genres), len(other.compatible_genres), 1)
        genre_score = genre_overlap / max_genres
        
        # Check element compatibility
        element_score = self._calculate_element_compatibility(other)
        
        # Check intensity compatibility
        intensity_diff = abs(self.intensity_score - other.intensity_score)
        intensity_score = 1.0 - intensity_diff
        
        # Combined score
        return (genre_score * 0.4 + element_score * 0.4 + intensity_score * 0.2)
    
    def _calculate_element_compatibility(self, other: 'CreativeVibe') -> float:
        """Calculate element compatibility score"""
        my_keywords = set(self.get_all_keywords())
        other_keywords = set(other.get_all_keywords())
        
        if not my_keywords or not other_keywords:
            return 0.5
        
        # Keyword overlap
        overlap = len(my_keywords & other_keywords)
        total_unique = len(my_keywords | other_keywords)
        
        return overlap / total_unique if total_unique > 0 else 0.0
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization"""
        return {
            "vibe_id": self.vibe_id,
            "name": self.name,
            "description": self.description,
            "archetype": self.archetype.value if self.archetype else None,
            "primary_elements": [elem.to_dict() for elem in self.primary_elements],
            "secondary_elements": [elem.to_dict() for elem in self.secondary_elements],
            "overall_intensity": self.overall_intensity.value,
            "compatible_genres": [g.value for g in self.compatible_genres],
            "creative_mood": self.creative_mood.value,
            "tone_guidance": self.tone_guidance,
            "style_guidance": self.style_guidance,
            "structure_guidance": self.structure_guidance,
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count,
            "user_rating": self.user_rating,
            "primary_category": self.primary_category.value,
            "intensity_score": self.intensity_score,
            "keywords": self.get_all_keywords()
        }


@dataclass
class VibeTemplate:
    """Template for creating consistent vibes"""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    archetype: VibeArchetype = VibeArchetype.GENTLE_REFLECTION
    template_elements: List[VibeElement] = field(default_factory=list)
    default_intensity: VibeIntensity = VibeIntensity.MODERATE
    suggested_genres: Set[BookGenre] = field(default_factory=set)
    
    # Template metadata
    category: VibeCategory = VibeCategory.ATMOSPHERIC
    popularity_score: float = 0.0
    success_rate: float = 0.0
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.now)
    
    # Usage and customization
    usage_examples: List[str] = field(default_factory=list)
    customization_options: Dict[str, any] = field(default_factory=dict)
    
    def create_vibe(self, 
                   intensity_override: Optional[VibeIntensity] = None,
                   custom_elements: Optional[List[VibeElement]] = None) -> CreativeVibe:
        """Create a vibe instance from this template"""
        
        # Use template elements as base
        primary_elements = self.template_elements.copy()
        
        # Add custom elements if provided
        if custom_elements:
            primary_elements.extend(custom_elements)
        
        # Determine intensity
        intensity = intensity_override or self.default_intensity
        
        # Create vibe
        vibe = CreativeVibe(
            name=self.name,
            description=self.description,
            archetype=self.archetype,
            primary_elements=primary_elements,
            overall_intensity=intensity,
            compatible_genres=self.suggested_genres.copy(),
            creative_mood=self._determine_creative_mood(intensity)
        )
        
        # Generate guidance based on template
        vibe.tone_guidance = self._generate_tone_guidance(vibe)
        vibe.style_guidance = self._generate_style_guidance(vibe)
        vibe.structure_guidance = self._generate_structure_guidance(vibe)
        
        return vibe
    
    def _determine_creative_mood(self, intensity: VibeIntensity) -> CreativeMood:
        """Determine creative mood based on archetype and intensity"""
        
        mood_mapping = {
            VibeArchetype.PASSIONATE_LOVE: CreativeMood.PASSIONATE,
            VibeArchetype.DARK_MYSTERY: CreativeMood.CONTEMPLATIVE,
            VibeArchetype.COZY_WARMTH: CreativeMood.REFLECTIVE,
            VibeArchetype.HEART_POUNDING: CreativeMood.ENERGETIC,
            VibeArchetype.EXPLOSIVE_ACTION: CreativeMood.INSPIRED,
            VibeArchetype.GENTLE_REFLECTION: CreativeMood.CONTEMPLATIVE,
            VibeArchetype.HEROIC_JOURNEY: CreativeMood.INSPIRED,
            VibeArchetype.DISCOVERY_WONDER: CreativeMood.EXPLORATORY
        }
        
        base_mood = mood_mapping.get(self.archetype, CreativeMood.FOCUSED)
        
        # Modify based on intensity
        if intensity == VibeIntensity.INTENSE:
            if base_mood == CreativeMood.CONTEMPLATIVE:
                return CreativeMood.PASSIONATE
            elif base_mood == CreativeMood.REFLECTIVE:
                return CreativeMood.INSPIRED
        elif intensity == VibeIntensity.SUBTLE:
            if base_mood == CreativeMood.ENERGETIC:
                return CreativeMood.FOCUSED
            elif base_mood == CreativeMood.PASSIONATE:
                return CreativeMood.CONTEMPLATIVE
        
        return base_mood
    
    def _generate_tone_guidance(self, vibe: CreativeVibe) -> Dict[str, any]:
        """Generate tone guidance for the vibe"""
        
        # Base tone guidance on archetype
        tone_guidance = {
            VibeArchetype.PASSIONATE_LOVE: {
                "primary_tone": "romantic_intense",
                "emotional_register": "high",
                "language_style": "poetic_flowing",
                "voice_characteristics": ["warm", "intimate", "expressive"]
            },
            VibeArchetype.DARK_MYSTERY: {
                "primary_tone": "mysterious_atmospheric",
                "emotional_register": "medium",
                "language_style": "evocative_shadowed",
                "voice_characteristics": ["enigmatic", "suspenseful", "layered"]
            },
            VibeArchetype.COZY_WARMTH: {
                "primary_tone": "comfortable_inviting",
                "emotional_register": "medium",
                "language_style": "warm_accessible",
                "voice_characteristics": ["friendly", "reassuring", "gentle"]
            },
            VibeArchetype.HEART_POUNDING: {
                "primary_tone": "urgent_exciting",
                "emotional_register": "high",
                "language_style": "dynamic_immediate",
                "voice_characteristics": ["energetic", "gripping", "fast-paced"]
            }
        }
        
        return tone_guidance.get(self.archetype, {
            "primary_tone": "balanced_engaging",
            "emotional_register": "medium",
            "language_style": "clear_accessible",
            "voice_characteristics": ["authentic", "engaging", "clear"]
        })
    
    def _generate_style_guidance(self, vibe: CreativeVibe) -> Dict[str, any]:
        """Generate style guidance for the vibe"""
        
        # Determine style based on elements and intensity
        style_guidance = {
            "sentence_structure": "varied",
            "vocabulary_level": "accessible",
            "imagery_density": "moderate",
            "dialogue_style": "natural"
        }
        
        # Modify based on intensity
        if vibe.overall_intensity == VibeIntensity.INTENSE:
            style_guidance.update({
                "sentence_structure": "varied_dramatic",
                "imagery_density": "rich",
                "emotional_language": "heightened"
            })
        elif vibe.overall_intensity == VibeIntensity.SUBTLE:
            style_guidance.update({
                "sentence_structure": "smooth_flowing",
                "imagery_density": "selective",
                "emotional_language": "understated"
            })
        
        # Modify based on primary category
        if vibe.primary_category == VibeCategory.ATMOSPHERIC:
            style_guidance["sensory_details"] = "emphasized"
            style_guidance["setting_description"] = "immersive"
        elif vibe.primary_category == VibeCategory.EMOTIONAL:
            style_guidance["internal_monologue"] = "rich"
            style_guidance["character_emotions"] = "detailed"
        elif vibe.primary_category == VibeCategory.ENERGETIC:
            style_guidance["pacing"] = "dynamic"
            style_guidance["action_description"] = "vivid"
        
        return style_guidance
    
    def _generate_structure_guidance(self, vibe: CreativeVibe) -> Dict[str, any]:
        """Generate structure guidance for the vibe"""
        
        structure_guidance = {
            "opening_style": "engaging",
            "chapter_pacing": "balanced",
            "tension_management": "gradual_build",
            "resolution_style": "satisfying"
        }
        
        # Modify based on archetype
        archetype_structures = {
            VibeArchetype.HEART_POUNDING: {
                "opening_style": "immediate_action",
                "chapter_pacing": "fast",
                "tension_management": "high_sustained"
            },
            VibeArchetype.GENTLE_REFLECTION: {
                "opening_style": "contemplative",
                "chapter_pacing": "measured",
                "tension_management": "subtle_emotional"
            },
            VibeArchetype.DARK_MYSTERY: {
                "opening_style": "atmospheric_hook",
                "chapter_pacing": "building_suspense",
                "tension_management": "layered_reveals"
            },
            VibeArchetype.HEROIC_JOURNEY: {
                "opening_style": "call_to_adventure",
                "chapter_pacing": "episodic_growth",
                "tension_management": "escalating_challenges"
            }
        }
        
        if self.archetype in archetype_structures:
            structure_guidance.update(archetype_structures[self.archetype])
        
        return structure_guidance


class VibeLibrary:
    """Library of pre-defined vibe templates and elements"""
    
    def __init__(self):
        self.templates: Dict[str, VibeTemplate] = {}
        self.elements: Dict[str, VibeElement] = {}
        self.user_vibes: Dict[str, CreativeVibe] = {}
        
        # Initialize with default templates and elements
        self._initialize_default_elements()
        self._initialize_default_templates()
    
    def _initialize_default_elements(self):
        """Initialize library with default vibe elements"""
        
        # Emotional elements
        self.elements["passionate_romance"] = VibeElement(
            element_id="passionate_romance",
            name="Passionate Romance",
            description="Intense romantic feelings and attraction",
            category=VibeCategory.EMOTIONAL,
            intensity=0.8,
            keywords=["passionate", "intense", "romantic", "desire", "attraction", "chemistry"],
            enhances=["intimate_moments", "emotional_vulnerability"]
        )
        
        self.elements["melancholy_nostalgia"] = VibeElement(
            element_id="melancholy_nostalgia",
            name="Melancholy Nostalgia",
            description="Bittersweet longing for the past",
            category=VibeCategory.EMOTIONAL,
            intensity=0.6,
            keywords=["nostalgic", "bittersweet", "longing", "memories", "wistful"],
            enhances=["reflective_moments", "character_backstory"]
        )
        
        # Atmospheric elements
        self.elements["dark_mystery"] = VibeElement(
            element_id="dark_mystery",
            name="Dark Mystery",
            description="Shadowy, enigmatic atmosphere with hidden secrets",
            category=VibeCategory.ATMOSPHERIC,
            intensity=0.7,
            keywords=["mysterious", "dark", "shadowy", "secrets", "enigmatic", "hidden"],
            enhances=["suspense_building", "atmospheric_tension"]
        )
        
        self.elements["cozy_warmth"] = VibeElement(
            element_id="cozy_warmth",
            name="Cozy Warmth",
            description="Comfortable, inviting, safe atmosphere",
            category=VibeCategory.ATMOSPHERIC,
            intensity=0.4,
            keywords=["cozy", "warm", "comfortable", "safe", "inviting", "homey"],
            enhances=["character_bonding", "peaceful_moments"]
        )
        
        self.elements["ethereal_magic"] = VibeElement(
            element_id="ethereal_magic",
            name="Ethereal Magic",
            description="Otherworldly, mystical, dreamlike quality",
            category=VibeCategory.ATMOSPHERIC,
            intensity=0.6,
            keywords=["ethereal", "mystical", "magical", "otherworldly", "dreamlike", "enchanted"],
            enhances=["fantasy_elements", "wonder_moments"]
        )
        
        # Energetic elements
        self.elements["heart_pounding"] = VibeElement(
            element_id="heart_pounding",
            name="Heart Pounding",
            description="Fast-paced, adrenaline-filled energy",
            category=VibeCategory.ENERGETIC,
            intensity=0.9,
            keywords=["fast-paced", "thrilling", "adrenaline", "urgent", "exciting", "breathless"],
            enhances=["action_sequences", "chase_scenes"]
        )
        
        self.elements["gentle_contemplation"] = VibeElement(
            element_id="gentle_contemplation",
            name="Gentle Contemplation",
            description="Peaceful, reflective, meditative energy",
            category=VibeCategory.ENERGETIC,
            intensity=0.3,
            keywords=["gentle", "peaceful", "contemplative", "meditative", "serene", "calm"],
            enhances=["character_development", "introspective_moments"]
        )
        
        # Thematic elements
        self.elements["redemption_journey"] = VibeElement(
            element_id="redemption_journey",
            name="Redemption Journey",
            description="Path from mistake to forgiveness and growth",
            category=VibeCategory.THEMATIC,
            intensity=0.7,
            keywords=["redemption", "forgiveness", "growth", "second chances", "healing", "transformation"],
            enhances=["character_arcs", "moral_complexity"]
        )
        
        self.elements["discovery_wonder"] = VibeElement(
            element_id="discovery_wonder",
            name="Discovery Wonder",
            description="Excitement of finding something new and amazing",
            category=VibeCategory.THEMATIC,
            intensity=0.6,
            keywords=["discovery", "wonder", "amazement", "revelation", "exploration", "new"],
            enhances=["plot_reveals", "world_building"]
        )
    
    def _initialize_default_templates(self):
        """Initialize library with default vibe templates"""
        
        # Passionate Romance Template
        passionate_romance = VibeTemplate(
            name="Passionate Romance",
            description="Intense romantic connection with emotional depth",
            archetype=VibeArchetype.PASSIONATE_LOVE,
            template_elements=[
                self.elements["passionate_romance"],
                self.elements["cozy_warmth"]
            ],
            default_intensity=VibeIntensity.STRONG,
            suggested_genres={BookGenre.ROMANCE},
            category=VibeCategory.EMOTIONAL,
            usage_examples=[
                "I want to write a romance that makes readers' hearts race",
                "Create a love story with intense emotional connection",
                "Write about passionate love that overcomes all obstacles"
            ]
        )
        self.templates[passionate_romance.template_id] = passionate_romance
        
        # Cozy Mystery Template
        cozy_mystery = VibeTemplate(
            name="Cozy Mystery",
            description="Comfortable mystery with gentle suspense and warm community",
            archetype=VibeArchetype.COZY_WARMTH,
            template_elements=[
                self.elements["dark_mystery"],
                self.elements["cozy_warmth"],
                self.elements["gentle_contemplation"]
            ],
            default_intensity=VibeIntensity.MODERATE,
            suggested_genres={BookGenre.MYSTERY},
            category=VibeCategory.ATMOSPHERIC,
            usage_examples=[
                "I want a mystery that feels safe and comfortable",
                "Create a puzzle with atmosphere but not scary",
                "Write a small-town mystery with likeable characters"
            ]
        )
        self.templates[cozy_mystery.template_id] = cozy_mystery
        
        # Dark Fantasy Template
        dark_fantasy = VibeTemplate(
            name="Dark Fantasy",
            description="Mystical world with shadowy atmosphere and moral complexity",
            archetype=VibeArchetype.DARK_MYSTERY,
            template_elements=[
                self.elements["dark_mystery"],
                self.elements["ethereal_magic"],
                self.elements["redemption_journey"]
            ],
            default_intensity=VibeIntensity.STRONG,
            suggested_genres={BookGenre.FANTASY, BookGenre.HORROR},
            category=VibeCategory.ATMOSPHERIC,
            usage_examples=[
                "I want fantasy with dark undertones",
                "Create a magical world that feels dangerous",
                "Write about magic with moral consequences"
            ]
        )
        self.templates[dark_fantasy.template_id] = dark_fantasy
        
        # Heart-Pounding Thriller Template
        thriller = VibeTemplate(
            name="Heart-Pounding Thriller",
            description="Non-stop action with breathless pacing and high stakes",
            archetype=VibeArchetype.HEART_POUNDING,
            template_elements=[
                self.elements["heart_pounding"],
                self.elements["dark_mystery"]
            ],
            default_intensity=VibeIntensity.INTENSE,
            suggested_genres={BookGenre.THRILLER, BookGenre.MYSTERY},
            category=VibeCategory.ENERGETIC,
            usage_examples=[
                "I want readers on the edge of their seats",
                "Create non-stop action and suspense",
                "Write a page-turner that keeps people up all night"
            ]
        )
        self.templates[thriller.template_id] = thriller
        
        # Contemplative Literary Template
        literary = VibeTemplate(
            name="Contemplative Literary",
            description="Deep character exploration with thoughtful prose and emotional resonance",
            archetype=VibeArchetype.GENTLE_REFLECTION,
            template_elements=[
                self.elements["gentle_contemplation"],
                self.elements["melancholy_nostalgia"],
                self.elements["discovery_wonder"]
            ],
            default_intensity=VibeIntensity.MODERATE,
            suggested_genres={BookGenre.LITERARY_FICTION},
            category=VibeCategory.EMOTIONAL,
            usage_examples=[
                "I want to explore deep human emotions",
                "Create a thoughtful, character-driven story",
                "Write something meaningful and profound"
            ]
        )
        self.templates[literary.template_id] = literary
        
        # Heroic Adventure Template
        adventure = VibeTemplate(
            name="Heroic Adventure",
            description="Epic journey of growth with wonder and transformation",
            archetype=VibeArchetype.HEROIC_JOURNEY,
            template_elements=[
                self.elements["discovery_wonder"],
                self.elements["redemption_journey"],
                self.elements["heart_pounding"]
            ],
            default_intensity=VibeIntensity.STRONG,
            suggested_genres={BookGenre.FANTASY, BookGenre.SCIENCE_FICTION},
            category=VibeCategory.THEMATIC,
            usage_examples=[
                "I want to write an epic hero's journey",
                "Create an adventure with personal growth",
                "Write about transformation through challenges"
            ]
        )
        self.templates[adventure.template_id] = adventure
    
    def get_template_by_name(self, name: str) -> Optional[VibeTemplate]:
        """Get template by name"""
        for template in self.templates.values():
            if template.name.lower() == name.lower():
                return template
        return None
    
    def get_templates_by_category(self, category: VibeCategory) -> List[VibeTemplate]:
        """Get all templates in a category"""
        return [t for t in self.templates.values() if t.category == category]
    
    def get_templates_by_genre(self, genre: BookGenre) -> List[VibeTemplate]:
        """Get templates compatible with a genre"""
        return [t for t in self.templates.values() if genre in t.suggested_genres]
    
    def get_templates_by_archetype(self, archetype: VibeArchetype) -> List[VibeTemplate]:
        """Get templates with specific archetype"""
        return [t for t in self.templates.values() if t.archetype == archetype]
    
    def search_templates(self, query: str) -> List[VibeTemplate]:
        """Search templates by keywords"""
        query_lower = query.lower()
        matches = []
        
        for template in self.templates.values():
            # Check name and description
            if (query_lower in template.name.lower() or 
                query_lower in template.description.lower()):
                matches.append(template)
                continue
            
            # Check usage examples
            if any(query_lower in example.lower() for example in template.usage_examples):
                matches.append(template)
                continue
            
            # Check element keywords
            for element in template.template_elements:
                if any(query_lower in keyword.lower() for keyword in element.keywords):
                    matches.append(template)
                    break
        
        return matches
    
    def create_custom_vibe(self, user_input: str, base_template: Optional[VibeTemplate] = None) -> CreativeVibe:
        """Create custom vibe from user input"""
        # This would use NLP to parse user intent and create appropriate vibe
        # For now, return a basic vibe
        
        if base_template:
            return base_template.create_vibe()
        
        # Create generic vibe
        return CreativeVibe(
            name="Custom Vibe",
            description=f"Custom vibe based on: {user_input}",
            primary_elements=list(self.elements.values())[:2],  # Use first 2 elements
        )
    
    def get_popular_templates(self, limit: int = 5) -> List[VibeTemplate]:
        """Get most popular templates"""
        return sorted(
            self.templates.values(),
            key=lambda t: t.popularity_score,
            reverse=True
        )[:limit]
    
    def get_successful_templates(self, limit: int = 5) -> List[VibeTemplate]:
        """Get templates with highest success rates"""
        return sorted(
            self.templates.values(),
            key=lambda t: t.success_rate,
            reverse=True
        )[:limit]


class MoodMapper:
    """Maps user emotional expressions to vibe elements"""
    
    def __init__(self, vibe_library: VibeLibrary):
        self.vibe_library = vibe_library
        self.mood_patterns = self._initialize_mood_patterns()
    
    def _initialize_mood_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for mapping moods to elements"""
        return {
            "passionate": ["passionate_romance", "heart_pounding"],
            "mysterious": ["dark_mystery", "ethereal_magic"],
            "cozy": ["cozy_warmth", "gentle_contemplation"],
            "exciting": ["heart_pounding", "discovery_wonder"],
            "contemplative": ["gentle_contemplation", "melancholy_nostalgia"],
            "romantic": ["passionate_romance", "cozy_warmth"],
            "dark": ["dark_mystery", "redemption_journey"],
            "magical": ["ethereal_magic", "discovery_wonder"],
            "thrilling": ["heart_pounding", "dark_mystery"],
            "peaceful": ["cozy_warmth", "gentle_contemplation"],
            "nostalgic": ["melancholy_nostalgia", "gentle_contemplation"],
            "adventurous": ["discovery_wonder", "heart_pounding"],
            "redemptive": ["redemption_journey", "discovery_wonder"]
        }
    
    def map_mood_to_elements(self, mood_expression: str) -> List[VibeElement]:
        """Map mood expression to vibe elements"""
        mood_lower = mood_expression.lower()
        matched_elements = []
        
        for mood, element_ids in self.mood_patterns.items():
            if mood in mood_lower:
                for element_id in element_ids:
                    if element_id in self.vibe_library.elements:
                        matched_elements.append(self.vibe_library.elements[element_id])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for element in matched_elements:
            if element.element_id not in seen:
                seen.add(element.element_id)
                unique_elements.append(element)
        
        return unique_elements[:3]  # Return top 3 matches
    
    def suggest_templates_for_mood(self, mood_expression: str) -> List[VibeTemplate]:
        """Suggest templates based on mood expression"""
        mood_lower = mood_expression.lower()
        matching_templates = []
        
        # Direct keyword matching
        for template in self.vibe_library.templates.values():
            if any(mood in example.lower() for example in template.usage_examples):
                matching_templates.append(template)
        
        # Element-based matching
        relevant_elements = self.map_mood_to_elements(mood_expression)
        for template in self.vibe_library.templates.values():
            template_element_ids = {elem.element_id for elem in template.template_elements}
            relevant_element_ids = {elem.element_id for elem in relevant_elements}
            
            if template_element_ids & relevant_element_ids:  # Intersection
                if template not in matching_templates:
                    matching_templates.append(template)
        
        return matching_templates[:5]  # Return top 5 matches