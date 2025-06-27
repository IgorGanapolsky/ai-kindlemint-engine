"""
Vibe Engine for KindleMint Vibecoding System

The vibe engine translates user emotional expressions, creative intentions,
and atmospheric descriptions into actionable creative guidance for book creation.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple

from ..context.models import VoiceInput, EmotionProfile, Intent, CreativeMood
from .vibe_templates import (
    VibeLibrary, 
    CreativeVibe, 
    VibeTemplate, 
    VibeElement,
    VibeArchetype,
    VibeCategory,
    VibeIntensity,
    MoodMapper
)

logger = logging.getLogger(__name__)


class VibeTranslator:
    """Translates user input into vibe specifications"""
    
    def __init__(self, vibe_library: VibeLibrary):
        self.vibe_library = vibe_library
        self.mood_mapper = MoodMapper(vibe_library)
        
        # Intensity detection patterns
        self.intensity_patterns = {
            VibeIntensity.SUBTLE: [
                "gentle", "soft", "quiet", "subtle", "hint of", "touch of",
                "barely", "whisper", "delicate", "understated"
            ],
            VibeIntensity.MODERATE: [
                "moderate", "balanced", "medium", "comfortable", "steady",
                "regular", "normal", "even", "measured"
            ],
            VibeIntensity.STRONG: [
                "strong", "powerful", "bold", "intense", "deep", "rich",
                "vivid", "compelling", "striking", "pronounced"
            ],
            VibeIntensity.INTENSE: [
                "intense", "overwhelming", "explosive", "maximum", "extreme",
                "blazing", "fierce", "consuming", "passionate", "electrifying"
            ]
        }
        
        # Emotional expressions to vibe archetypes
        self.emotion_archetype_map = {
            "passionate": VibeArchetype.PASSIONATE_LOVE,
            "mysterious": VibeArchetype.DARK_MYSTERY,
            "cozy": VibeArchetype.COZY_WARMTH,
            "magical": VibeArchetype.ETHEREAL_MAGIC,
            "thrilling": VibeArchetype.HEART_POUNDING,
            "peaceful": VibeArchetype.GENTLE_REFLECTION,
            "heroic": VibeArchetype.HEROIC_JOURNEY,
            "nostalgic": VibeArchetype.BITTERSWEET_NOSTALGIA,
            "transformative": VibeArchetype.TRANSFORMATION,
            "redemptive": VibeArchetype.REDEMPTION_ARC
        }
    
    async def translate_voice_to_vibe(self, voice_input: VoiceInput) -> CreativeVibe:
        """Translate voice input into a creative vibe"""
        
        # Extract vibe indicators from text
        text_vibes = self._extract_vibe_indicators(voice_input.text)
        
        # Get emotion-based vibe elements
        emotion_vibes = self._map_emotions_to_vibes(voice_input.emotions)
        
        # Detect intensity
        intensity = self._detect_intensity(voice_input.text, voice_input.emotions)
        
        # Find best matching archetype
        archetype = self._determine_archetype(text_vibes, emotion_vibes, voice_input)
        
        # Combine elements
        primary_elements = self._combine_vibe_elements(text_vibes, emotion_vibes)
        
        # Create vibe
        vibe = CreativeVibe(
            name=self._generate_vibe_name(archetype, intensity),
            description=self._generate_vibe_description(voice_input.text, archetype),
            archetype=archetype,
            primary_elements=primary_elements,
            overall_intensity=intensity,
            creative_mood=voice_input.emotions.mood
        )
        
        # Enhance with guidance
        await self._enhance_vibe_guidance(vibe, voice_input)
        
        logger.info(f"Translated voice input to vibe: {vibe.name} ({archetype.value})")
        
        return vibe
    
    def _extract_vibe_indicators(self, text: str) -> List[str]:
        """Extract vibe-related words and phrases from text"""
        
        vibe_indicators = []
        text_lower = text.lower()
        
        # Emotional descriptors
        emotional_words = [
            "passionate", "romantic", "love", "heartbreak", "joy", "sadness",
            "angry", "peaceful", "excited", "calm", "melancholy", "nostalgic",
            "hopeful", "desperate", "content", "yearning"
        ]
        
        # Atmospheric descriptors
        atmospheric_words = [
            "dark", "bright", "mysterious", "cozy", "cold", "warm", "ethereal",
            "gritty", "dreamy", "realistic", "magical", "mundane", "exotic",
            "familiar", "haunting", "comforting", "unsettling", "beautiful"
        ]
        
        # Energy descriptors
        energy_words = [
            "fast-paced", "slow", "explosive", "gentle", "intense", "subtle",
            "dynamic", "static", "flowing", "jarring", "smooth", "rough",
            "energetic", "lethargic", "vibrant", "muted"
        ]
        
        # Thematic descriptors
        thematic_words = [
            "redemption", "transformation", "discovery", "loss", "growth",
            "journey", "quest", "search", "finding", "healing", "breaking",
            "building", "destroying", "creating", "exploring"
        ]
        
        all_vibe_words = emotional_words + atmospheric_words + energy_words + thematic_words
        
        for word in all_vibe_words:
            if word in text_lower:
                vibe_indicators.append(word)
        
        # Look for descriptive phrases
        vibe_phrases = [
            "makes you feel", "atmosphere of", "mood of", "sense of",
            "feeling of", "vibe of", "tone of", "spirit of"
        ]
        
        for phrase in vibe_phrases:
            if phrase in text_lower:
                # Extract what follows the phrase
                start_idx = text_lower.find(phrase) + len(phrase)
                following_text = text[start_idx:start_idx + 50].strip()
                if following_text:
                    vibe_indicators.append(following_text.split()[0])
        
        return vibe_indicators
    
    def _map_emotions_to_vibes(self, emotions: EmotionProfile) -> List[VibeElement]:
        """Map emotional profile to vibe elements"""
        
        vibe_elements = []
        
        # Map primary emotion
        primary_mapping = {
            "excited": "heart_pounding",
            "passionate": "passionate_romance",
            "calm": "gentle_contemplation",
            "mysterious": "dark_mystery",
            "nostalgic": "melancholy_nostalgia",
            "romantic": "passionate_romance",
            "contemplative": "gentle_contemplation"
        }
        
        primary_element_id = primary_mapping.get(emotions.primary_emotion)
        if primary_element_id and primary_element_id in self.vibe_library.elements:
            vibe_elements.append(self.vibe_library.elements[primary_element_id])
        
        # Map creative mood
        mood_mapping = {
            CreativeMood.PASSIONATE: "passionate_romance",
            CreativeMood.CONTEMPLATIVE: "gentle_contemplation",
            CreativeMood.ENERGETIC: "heart_pounding",
            CreativeMood.INSPIRED: "discovery_wonder",
            CreativeMood.EXPERIMENTAL: "ethereal_magic",
            CreativeMood.REFLECTIVE: "melancholy_nostalgia"
        }
        
        mood_element_id = mood_mapping.get(emotions.mood)
        if mood_element_id and mood_element_id in self.vibe_library.elements:
            mood_element = self.vibe_library.elements[mood_element_id]
            if mood_element not in vibe_elements:
                vibe_elements.append(mood_element)
        
        # Add intensity-based elements
        if emotions.intensity > 0.7:
            if "heart_pounding" in self.vibe_library.elements:
                heart_pounding = self.vibe_library.elements["heart_pounding"]
                if heart_pounding not in vibe_elements:
                    vibe_elements.append(heart_pounding)
        elif emotions.intensity < 0.3:
            if "gentle_contemplation" in self.vibe_library.elements:
                gentle = self.vibe_library.elements["gentle_contemplation"]
                if gentle not in vibe_elements:
                    vibe_elements.append(gentle)
        
        return vibe_elements
    
    def _detect_intensity(self, text: str, emotions: EmotionProfile) -> VibeIntensity:
        """Detect the desired intensity level"""
        
        text_lower = text.lower()
        
        # Check for explicit intensity words
        for intensity, patterns in self.intensity_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return intensity
        
        # Use emotion intensity as backup
        emotion_intensity = emotions.intensity
        
        if emotion_intensity >= 0.8:
            return VibeIntensity.INTENSE
        elif emotion_intensity >= 0.6:
            return VibeIntensity.STRONG
        elif emotion_intensity >= 0.4:
            return VibeIntensity.MODERATE
        else:
            return VibeIntensity.SUBTLE
    
    def _determine_archetype(self, text_vibes: List[str], emotion_vibes: List[VibeElement],
                           voice_input: VoiceInput) -> VibeArchetype:
        """Determine the most appropriate vibe archetype"""
        
        # Score archetypes based on text indicators
        archetype_scores = {}
        
        # Text-based scoring
        for vibe_word in text_vibes:
            for emotion_word, archetype in self.emotion_archetype_map.items():
                if emotion_word in vibe_word or vibe_word in emotion_word:
                    archetype_scores[archetype] = archetype_scores.get(archetype, 0) + 2
        
        # Element-based scoring
        for element in emotion_vibes:
            element_archetype_map = {
                "passionate_romance": VibeArchetype.PASSIONATE_LOVE,
                "dark_mystery": VibeArchetype.DARK_MYSTERY,
                "cozy_warmth": VibeArchetype.COZY_WARMTH,
                "ethereal_magic": VibeArchetype.ETHEREAL_MAGIC,
                "heart_pounding": VibeArchetype.HEART_POUNDING,
                "gentle_contemplation": VibeArchetype.GENTLE_REFLECTION,
                "redemption_journey": VibeArchetype.REDEMPTION_ARC,
                "discovery_wonder": VibeArchetype.DISCOVERY_WONDER
            }
            
            archetype = element_archetype_map.get(element.element_id)
            if archetype:
                archetype_scores[archetype] = archetype_scores.get(archetype, 0) + 3
        
        # Intent-based scoring
        intent_archetype_map = {
            Intent.CREATE_BOOK: VibeArchetype.DISCOVERY_WONDER,
            Intent.SET_VIBE: VibeArchetype.ETHEREAL_MAGIC,
            Intent.EXPLORE_IDEAS: VibeArchetype.DISCOVERY_WONDER,
            Intent.REFINE_STYLE: VibeArchetype.GENTLE_REFLECTION
        }
        
        intent_archetype = intent_archetype_map.get(voice_input.intent)
        if intent_archetype:
            archetype_scores[intent_archetype] = archetype_scores.get(intent_archetype, 0) + 1
        
        # Return highest scoring archetype or default
        if archetype_scores:
            return max(archetype_scores, key=archetype_scores.get)
        
        return VibeArchetype.GENTLE_REFLECTION  # Default
    
    def _combine_vibe_elements(self, text_vibes: List[str], 
                              emotion_vibes: List[VibeElement]) -> List[VibeElement]:
        """Combine text-based and emotion-based vibe elements"""
        
        combined_elements = emotion_vibes.copy()
        
        # Add text-based elements
        for vibe_word in text_vibes:
            # Find matching elements in library
            for element in self.vibe_library.elements.values():
                if (vibe_word in element.name.lower() or 
                    any(vibe_word in keyword for keyword in element.keywords)):
                    if element not in combined_elements:
                        combined_elements.append(element)
        
        # Limit to most relevant elements
        return combined_elements[:4]  # Max 4 primary elements
    
    def _generate_vibe_name(self, archetype: VibeArchetype, intensity: VibeIntensity) -> str:
        """Generate a descriptive name for the vibe"""
        
        intensity_prefixes = {
            VibeIntensity.SUBTLE: "Gentle",
            VibeIntensity.MODERATE: "Balanced",
            VibeIntensity.STRONG: "Rich",
            VibeIntensity.INTENSE: "Powerful"
        }
        
        archetype_names = {
            VibeArchetype.PASSIONATE_LOVE: "Romance",
            VibeArchetype.DARK_MYSTERY: "Mystery",
            VibeArchetype.COZY_WARMTH: "Comfort",
            VibeArchetype.ETHEREAL_MAGIC: "Wonder",
            VibeArchetype.HEART_POUNDING: "Thriller",
            VibeArchetype.GENTLE_REFLECTION: "Contemplation",
            VibeArchetype.HEROIC_JOURNEY: "Adventure",
            VibeArchetype.BITTERSWEET_NOSTALGIA: "Nostalgia",
            VibeArchetype.REDEMPTION_ARC: "Redemption",
            VibeArchetype.DISCOVERY_WONDER: "Discovery"
        }
        
        prefix = intensity_prefixes.get(intensity, "Balanced")
        base_name = archetype_names.get(archetype, "Creative")
        
        return f"{prefix} {base_name}"
    
    def _generate_vibe_description(self, user_text: str, archetype: VibeArchetype) -> str:
        """Generate a description of the vibe based on user input"""
        
        # Extract key phrases from user input
        key_phrases = self._extract_key_phrases(user_text)
        
        archetype_descriptions = {
            VibeArchetype.PASSIONATE_LOVE: "A vibe of intense romantic connection and emotional depth",
            VibeArchetype.DARK_MYSTERY: "An atmosphere of secrets, shadows, and intriguing puzzles",
            VibeArchetype.COZY_WARMTH: "A feeling of comfort, safety, and welcoming familiarity",
            VibeArchetype.ETHEREAL_MAGIC: "A sense of wonder, otherworldly beauty, and mystical possibility",
            VibeArchetype.HEART_POUNDING: "An energy of excitement, urgency, and breathless anticipation",
            VibeArchetype.GENTLE_REFLECTION: "A mood of peaceful contemplation and thoughtful introspection",
            VibeArchetype.HEROIC_JOURNEY: "An epic sense of growth, challenge, and transformative adventure",
            VibeArchetype.BITTERSWEET_NOSTALGIA: "A wistful longing mixed with fond memories and gentle sadness",
            VibeArchetype.REDEMPTION_ARC: "A powerful journey from darkness to light, mistake to forgiveness",
            VibeArchetype.DISCOVERY_WONDER: "The thrill of uncovering something new and amazing"
        }
        
        base_description = archetype_descriptions.get(
            archetype, 
            "A unique creative atmosphere"
        )
        
        if key_phrases:
            return f"{base_description}, inspired by your vision of {', '.join(key_phrases[:3])}"
        
        return base_description
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key descriptive phrases from user text"""
        
        # Simple extraction of descriptive phrases
        text_lower = text.lower()
        phrases = []
        
        # Look for "I want..." patterns
        want_pattern = r"i want.*?(?:\.|$)"
        want_matches = re.findall(want_pattern, text_lower)
        for match in want_matches:
            clean_match = match.replace("i want", "").strip(" .")
            if clean_match:
                phrases.append(clean_match)
        
        # Look for "feels like..." patterns
        feels_pattern = r"feels? like.*?(?:\.|$)"
        feels_matches = re.findall(feels_pattern, text_lower)
        for match in feels_matches:
            clean_match = match.replace("feels like", "").replace("feel like", "").strip(" .")
            if clean_match:
                phrases.append(clean_match)
        
        # Look for adjective + noun combinations
        adjective_noun_pattern = r"\b(?:dark|bright|cozy|mysterious|exciting|peaceful|intense|gentle|magical|romantic)\s+\w+\b"
        adj_noun_matches = re.findall(adjective_noun_pattern, text_lower)
        phrases.extend(adj_noun_matches)
        
        return phrases[:5]  # Limit to 5 key phrases
    
    async def _enhance_vibe_guidance(self, vibe: CreativeVibe, voice_input: VoiceInput):
        """Enhance vibe with specific guidance based on user input"""
        
        # Generate tone guidance
        vibe.tone_guidance = self._generate_contextual_tone_guidance(vibe, voice_input)
        
        # Generate style guidance
        vibe.style_guidance = self._generate_contextual_style_guidance(vibe, voice_input)
        
        # Generate structure guidance
        vibe.structure_guidance = self._generate_contextual_structure_guidance(vibe, voice_input)
    
    def _generate_contextual_tone_guidance(self, vibe: CreativeVibe, voice_input: VoiceInput) -> Dict[str, any]:
        """Generate tone guidance specific to this vibe and user input"""
        
        base_guidance = {
            "emotional_register": "medium",
            "formality_level": "casual",
            "perspective": "close_third_person"
        }
        
        # Adjust based on archetype
        if vibe.archetype == VibeArchetype.PASSIONATE_LOVE:
            base_guidance.update({
                "emotional_register": "high",
                "sensory_language": "emphasized",
                "intimacy_level": "close"
            })
        elif vibe.archetype == VibeArchetype.DARK_MYSTERY:
            base_guidance.update({
                "atmospheric_language": "rich",
                "ambiguity_level": "moderate",
                "tension_building": "gradual"
            })
        elif vibe.archetype == VibeArchetype.COZY_WARMTH:
            base_guidance.update({
                "warmth_indicators": "frequent",
                "comfort_language": "emphasized",
                "community_focus": "strong"
            })
        
        # Adjust based on intensity
        if vibe.overall_intensity == VibeIntensity.INTENSE:
            base_guidance["language_intensity"] = "heightened"
            base_guidance["emotional_language"] = "vivid"
        elif vibe.overall_intensity == VibeIntensity.SUBTLE:
            base_guidance["language_intensity"] = "understated"
            base_guidance["emotional_language"] = "restrained"
        
        # Add user-specific elements
        if "funny" in voice_input.text.lower() or "humor" in voice_input.text.lower():
            base_guidance["humor_level"] = "moderate"
        
        if "serious" in voice_input.text.lower() or "important" in voice_input.text.lower():
            base_guidance["gravity_level"] = "high"
        
        return base_guidance
    
    def _generate_contextual_style_guidance(self, vibe: CreativeVibe, voice_input: VoiceInput) -> Dict[str, any]:
        """Generate style guidance specific to this vibe"""
        
        base_guidance = {
            "sentence_variety": "balanced",
            "paragraph_length": "medium",
            "description_density": "moderate"
        }
        
        # Adjust based on primary category
        primary_cat = vibe.primary_category
        
        if primary_cat == VibeCategory.ATMOSPHERIC:
            base_guidance.update({
                "sensory_details": "rich",
                "setting_description": "detailed",
                "atmosphere_building": "layered"
            })
        elif primary_cat == VibeCategory.EMOTIONAL:
            base_guidance.update({
                "internal_monologue": "detailed",
                "emotion_showing": "emphasized",
                "character_psychology": "deep"
            })
        elif primary_cat == VibeCategory.ENERGETIC:
            base_guidance.update({
                "action_verbs": "strong",
                "sentence_pace": "varied",
                "momentum_building": "consistent"
            })
        
        # Adjust based on user's energy level
        if voice_input.emotions.energy_level > 0.7:
            base_guidance["writing_energy"] = "high"
            base_guidance["verb_choice"] = "active"
        elif voice_input.emotions.energy_level < 0.3:
            base_guidance["writing_energy"] = "contemplative"
            base_guidance["verb_choice"] = "reflective"
        
        return base_guidance
    
    def _generate_contextual_structure_guidance(self, vibe: CreativeVibe, voice_input: VoiceInput) -> Dict[str, any]:
        """Generate structure guidance specific to this vibe"""
        
        base_guidance = {
            "pacing": "steady",
            "chapter_length": "medium",
            "scene_transitions": "smooth"
        }
        
        # Adjust based on archetype
        if vibe.archetype == VibeArchetype.HEART_POUNDING:
            base_guidance.update({
                "pacing": "fast",
                "cliffhangers": "frequent",
                "tension_breaks": "minimal"
            })
        elif vibe.archetype == VibeArchetype.GENTLE_REFLECTION:
            base_guidance.update({
                "pacing": "leisurely",
                "contemplative_moments": "frequent",
                "introspective_breaks": "regular"
            })
        elif vibe.archetype == VibeArchetype.HEROIC_JOURNEY:
            base_guidance.update({
                "structure_type": "episodic",
                "growth_moments": "clear",
                "challenge_escalation": "gradual"
            })
        
        # Adjust based on intent
        if voice_input.intent == Intent.CREATE_BOOK:
            base_guidance["opening_focus"] = "strong_hook"
        elif voice_input.intent == Intent.REFINE_STYLE:
            base_guidance["style_consistency"] = "high"
        
        return base_guidance


class VibeEngine:
    """Main engine for processing and applying vibes in the vibecoding system"""
    
    def __init__(self):
        self.vibe_library = VibeLibrary()
        self.vibe_translator = VibeTranslator(self.vibe_library)
        self.active_vibes: Dict[str, CreativeVibe] = {}  # session_id -> vibe
        self.logger = logging.getLogger(__name__)
    
    async def process_vibe_input(self, voice_input: VoiceInput, session_id: str) -> CreativeVibe:
        """Process voice input and create/update vibe for session"""
        
        try:
            # Translate voice input to vibe
            new_vibe = await self.vibe_translator.translate_voice_to_vibe(voice_input)
            
            # Check if we have an existing vibe for this session
            existing_vibe = self.active_vibes.get(session_id)
            
            if existing_vibe:
                # Merge with existing vibe
                merged_vibe = await self._merge_vibes(existing_vibe, new_vibe, voice_input)
                self.active_vibes[session_id] = merged_vibe
                self.logger.info(f"Merged vibe for session {session_id}: {merged_vibe.name}")
                return merged_vibe
            else:
                # Store new vibe
                self.active_vibes[session_id] = new_vibe
                self.logger.info(f"Created new vibe for session {session_id}: {new_vibe.name}")
                return new_vibe
                
        except Exception as e:
            self.logger.error(f"Error processing vibe input for session {session_id}: {e}")
            
            # Return default vibe on error
            default_vibe = self.vibe_library.templates[list(self.vibe_library.templates.keys())[0]].create_vibe()
            self.active_vibes[session_id] = default_vibe
            return default_vibe
    
    async def _merge_vibes(self, existing: CreativeVibe, new: CreativeVibe, 
                          voice_input: VoiceInput) -> CreativeVibe:
        """Merge existing vibe with new vibe information"""
        
        # Determine if this is a refinement or a new direction
        compatibility = existing.is_compatible_with(new)
        
        if compatibility > 0.6:
            # High compatibility - merge elements
            merged_vibe = self._merge_compatible_vibes(existing, new)
        elif compatibility > 0.3:
            # Medium compatibility - blend carefully
            merged_vibe = self._blend_vibes(existing, new, voice_input)
        else:
            # Low compatibility - user wants something different
            merged_vibe = new
            merged_vibe.name = f"Evolved {existing.name}"
            merged_vibe.description = f"Evolved from {existing.description} based on new direction"
        
        # Update usage stats
        merged_vibe.usage_count = existing.usage_count + 1
        
        return merged_vibe
    
    def _merge_compatible_vibes(self, existing: CreativeVibe, new: CreativeVibe) -> CreativeVibe:
        """Merge two compatible vibes"""
        
        # Combine elements, prioritizing new elements
        combined_primary = new.primary_elements.copy()
        
        # Add existing elements that don't conflict
        for existing_element in existing.primary_elements:
            element_exists = any(
                existing_element.element_id == new_elem.element_id 
                for new_elem in combined_primary
            )
            
            if not element_exists and len(combined_primary) < 4:
                combined_primary.append(existing_element)
        
        # Combine secondary elements
        combined_secondary = new.secondary_elements.copy()
        for existing_element in existing.secondary_elements:
            element_exists = any(
                existing_element.element_id == new_elem.element_id 
                for new_elem in combined_secondary
            )
            
            if not element_exists and len(combined_secondary) < 3:
                combined_secondary.append(existing_element)
        
        # Create merged vibe
        merged = CreativeVibe(
            name=f"Enhanced {existing.name}",
            description=f"Enhanced version combining {existing.name} with new elements",
            archetype=new.archetype or existing.archetype,
            primary_elements=combined_primary,
            secondary_elements=combined_secondary,
            overall_intensity=new.overall_intensity,
            compatible_genres=existing.compatible_genres | new.compatible_genres,
            creative_mood=new.creative_mood,
            usage_count=existing.usage_count
        )
        
        # Merge guidance
        merged.tone_guidance = {**existing.tone_guidance, **new.tone_guidance}
        merged.style_guidance = {**existing.style_guidance, **new.style_guidance}
        merged.structure_guidance = {**existing.structure_guidance, **new.structure_guidance}
        
        return merged
    
    def _blend_vibes(self, existing: CreativeVibe, new: CreativeVibe, 
                    voice_input: VoiceInput) -> CreativeVibe:
        """Blend two vibes with medium compatibility"""
        
        # Determine dominant vibe based on voice energy
        if voice_input.emotions.energy_level > 0.7:
            # High energy - prioritize new vibe
            dominant, secondary = new, existing
            blend_name = f"Dynamic {new.name}"
        else:
            # Lower energy - blend more evenly
            dominant, secondary = existing, new
            blend_name = f"Evolved {existing.name}"
        
        # Select best elements from both
        blended_elements = dominant.primary_elements[:2].copy()  # Top 2 from dominant
        
        # Add compatible elements from secondary
        for element in secondary.primary_elements:
            if len(blended_elements) < 4:
                # Check compatibility with existing elements
                compatible = True
                for existing_elem in blended_elements:
                    if element.element_id in existing_elem.incompatible_with:
                        compatible = False
                        break
                
                if compatible:
                    blended_elements.append(element)
        
        # Create blended vibe
        blended = CreativeVibe(
            name=blend_name,
            description=f"Blended vibe combining elements of {existing.name} and {new.name}",
            archetype=dominant.archetype,
            primary_elements=blended_elements,
            overall_intensity=new.overall_intensity,  # Use latest intensity
            compatible_genres=existing.compatible_genres | new.compatible_genres,
            creative_mood=new.creative_mood,
            usage_count=existing.usage_count
        )
        
        # Blend guidance with priority to new
        blended.tone_guidance = {**existing.tone_guidance, **new.tone_guidance}
        blended.style_guidance = {**existing.style_guidance, **new.style_guidance}
        blended.structure_guidance = {**existing.structure_guidance, **new.structure_guidance}
        
        return blended
    
    def get_vibe_suggestions(self, user_input: str) -> List[VibeTemplate]:
        """Get vibe template suggestions based on user input"""
        
        # Search templates
        search_results = self.vibe_library.search_templates(user_input)
        
        # Get mood-based suggestions
        mood_suggestions = self.vibe_translator.mood_mapper.suggest_templates_for_mood(user_input)
        
        # Combine and deduplicate
        all_suggestions = search_results + mood_suggestions
        seen_ids = set()
        unique_suggestions = []
        
        for template in all_suggestions:
            if template.template_id not in seen_ids:
                seen_ids.add(template.template_id)
                unique_suggestions.append(template)
        
        return unique_suggestions[:6]  # Return top 6 suggestions
    
    def get_session_vibe(self, session_id: str) -> Optional[CreativeVibe]:
        """Get current vibe for a session"""
        return self.active_vibes.get(session_id)
    
    def update_vibe_feedback(self, session_id: str, feedback: str, rating: Optional[float] = None):
        """Update vibe based on user feedback"""
        
        vibe = self.active_vibes.get(session_id)
        if not vibe:
            return
        
        # Add feedback
        vibe.user_feedback.append(feedback)
        
        # Update rating
        if rating is not None:
            if vibe.user_rating is None:
                vibe.user_rating = rating
            else:
                # Average with existing rating
                vibe.user_rating = (vibe.user_rating + rating) / 2
        
        self.logger.info(f"Updated vibe feedback for session {session_id}")
    
    def get_vibe_analytics(self) -> Dict[str, any]:
        """Get analytics about vibe usage"""
        
        total_vibes = len(self.active_vibes)
        
        if total_vibes == 0:
            return {"total_vibes": 0}
        
        # Archetype distribution
        archetype_counts = {}
        intensity_counts = {}
        category_counts = {}
        
        for vibe in self.active_vibes.values():
            # Count archetypes
            archetype = vibe.archetype.value if vibe.archetype else "unknown"
            archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1
            
            # Count intensities
            intensity = vibe.overall_intensity.value
            intensity_counts[intensity] = intensity_counts.get(intensity, 0) + 1
            
            # Count categories
            category = vibe.primary_category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate averages
        avg_rating = None
        rated_vibes = [v for v in self.active_vibes.values() if v.user_rating is not None]
        if rated_vibes:
            avg_rating = sum(v.user_rating for v in rated_vibes) / len(rated_vibes)
        
        return {
            "total_vibes": total_vibes,
            "archetype_distribution": archetype_counts,
            "intensity_distribution": intensity_counts,
            "category_distribution": category_counts,
            "average_rating": avg_rating,
            "total_feedback_items": sum(len(v.user_feedback) for v in self.active_vibes.values())
        }