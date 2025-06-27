"""
Vibe Matching and Compatibility Engine for KindleMint Vibecoding

This module provides sophisticated vibe matching, compatibility analysis,
and recommendation systems for the vibecoding experience.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from ..context.models import BookGenre, CreativeMood, Intent
from .vibe_templates import (
    CreativeVibe, 
    VibeTemplate, 
    VibeElement,
    VibeArchetype,
    VibeCategory,
    VibeIntensity,
    VibeLibrary
)

logger = logging.getLogger(__name__)


@dataclass
class VibeMatch:
    """Represents a vibe match with scoring information"""
    vibe: CreativeVibe
    compatibility_score: float
    match_reasons: List[str]
    potential_enhancements: List[str]
    confidence: float
    
    def to_dict(self) -> Dict[str, any]:
        return {
            "vibe": self.vibe.to_dict(),
            "compatibility_score": self.compatibility_score,
            "match_reasons": self.match_reasons,
            "potential_enhancements": self.potential_enhancements,
            "confidence": self.confidence
        }


@dataclass 
class VibeRecommendation:
    """Represents a vibe recommendation with detailed analysis"""
    template: VibeTemplate
    relevance_score: float
    customization_suggestions: List[str]
    why_recommended: str
    genre_fit: float
    mood_alignment: float
    
    def to_dict(self) -> Dict[str, any]:
        return {
            "template_id": self.template.template_id,
            "template_name": self.template.name,
            "description": self.template.description,
            "relevance_score": self.relevance_score,
            "customization_suggestions": self.customization_suggestions,
            "why_recommended": self.why_recommended,
            "genre_fit": self.genre_fit,
            "mood_alignment": self.mood_alignment,
            "archetype": self.template.archetype.value
        }


class VibeCompatibilityEngine:
    """Engine for analyzing vibe compatibility and conflicts"""
    
    def __init__(self):
        # Define compatibility matrices between different vibe aspects
        self.archetype_compatibility = self._initialize_archetype_compatibility()
        self.category_compatibility = self._initialize_category_compatibility()
        self.intensity_compatibility = self._initialize_intensity_compatibility()
    
    def _initialize_archetype_compatibility(self) -> Dict[VibeArchetype, Dict[VibeArchetype, float]]:
        """Initialize compatibility matrix for vibe archetypes"""
        
        # Compatibility scores between archetypes (0.0 = incompatible, 1.0 = perfect match)
        compatibility = defaultdict(dict)
        
        # Self-compatibility is always perfect
        for archetype in VibeArchetype:
            compatibility[archetype][archetype] = 1.0
        
        # Define specific compatibilities
        compat_rules = [
            # Romantic vibes
            (VibeArchetype.PASSIONATE_LOVE, VibeArchetype.COZY_WARMTH, 0.8),
            (VibeArchetype.PASSIONATE_LOVE, VibeArchetype.BITTERSWEET_NOSTALGIA, 0.7),
            (VibeArchetype.PASSIONATE_LOVE, VibeArchetype.TRANSFORMATION, 0.6),
            
            # Mystery vibes  
            (VibeArchetype.DARK_MYSTERY, VibeArchetype.COZY_WARMTH, 0.9),  # Cozy mystery
            (VibeArchetype.DARK_MYSTERY, VibeArchetype.HEART_POUNDING, 0.7),  # Thriller
            (VibeArchetype.DARK_MYSTERY, VibeArchetype.ETHEREAL_MAGIC, 0.6),  # Dark fantasy
            
            # Contemplative vibes
            (VibeArchetype.GENTLE_REFLECTION, VibeArchetype.BITTERSWEET_NOSTALGIA, 0.9),
            (VibeArchetype.GENTLE_REFLECTION, VibeArchetype.DISCOVERY_WONDER, 0.7),
            (VibeArchetype.GENTLE_REFLECTION, VibeArchetype.TRANSFORMATION, 0.8),
            
            # Adventure vibes
            (VibeArchetype.HEROIC_JOURNEY, VibeArchetype.DISCOVERY_WONDER, 0.9),
            (VibeArchetype.HEROIC_JOURNEY, VibeArchetype.TRANSFORMATION, 0.8),
            (VibeArchetype.HEROIC_JOURNEY, VibeArchetype.REDEMPTION_ARC, 0.7),
            
            # Action vibes
            (VibeArchetype.HEART_POUNDING, VibeArchetype.HEROIC_JOURNEY, 0.7),
            (VibeArchetype.HEART_POUNDING, VibeArchetype.DISCOVERY_WONDER, 0.6),
            
            # Magic vibes
            (VibeArchetype.ETHEREAL_MAGIC, VibeArchetype.DISCOVERY_WONDER, 0.8),
            (VibeArchetype.ETHEREAL_MAGIC, VibeArchetype.TRANSFORMATION, 0.7),
            
            # Growth vibes
            (VibeArchetype.REDEMPTION_ARC, VibeArchetype.TRANSFORMATION, 0.9),
            (VibeArchetype.REDEMPTION_ARC, VibeArchetype.HEROIC_JOURNEY, 0.7),
            
            # Low compatibilities (conflicts)
            (VibeArchetype.HEART_POUNDING, VibeArchetype.GENTLE_REFLECTION, 0.2),
            (VibeArchetype.PASSIONATE_LOVE, VibeArchetype.DARK_MYSTERY, 0.3),
            (VibeArchetype.COZY_WARMTH, VibeArchetype.HEART_POUNDING, 0.3),
        ]
        
        # Apply compatibility rules (bidirectional)
        for arch1, arch2, score in compat_rules:
            compatibility[arch1][arch2] = score
            compatibility[arch2][arch1] = score
        
        # Default compatibility for undefined pairs
        for arch1 in VibeArchetype:
            for arch2 in VibeArchetype:
                if arch2 not in compatibility[arch1]:
                    compatibility[arch1][arch2] = 0.5  # Neutral compatibility
        
        return compatibility
    
    def _initialize_category_compatibility(self) -> Dict[VibeCategory, Dict[VibeCategory, float]]:
        """Initialize compatibility matrix for vibe categories"""
        
        compatibility = defaultdict(dict)
        
        # Self-compatibility
        for category in VibeCategory:
            compatibility[category][category] = 1.0
        
        # Define category compatibilities
        compat_rules = [
            (VibeCategory.EMOTIONAL, VibeCategory.ATMOSPHERIC, 0.8),
            (VibeCategory.EMOTIONAL, VibeCategory.RELATIONAL, 0.9),
            (VibeCategory.ATMOSPHERIC, VibeCategory.SENSORY, 0.9),
            (VibeCategory.THEMATIC, VibeCategory.EMOTIONAL, 0.7),
            (VibeCategory.THEMATIC, VibeCategory.RELATIONAL, 0.8),
            (VibeCategory.ENERGETIC, VibeCategory.ATMOSPHERIC, 0.6),
            (VibeCategory.ENERGETIC, VibeCategory.THEMATIC, 0.7),
        ]
        
        for cat1, cat2, score in compat_rules:
            compatibility[cat1][cat2] = score
            compatibility[cat2][cat1] = score
        
        # Default compatibility
        for cat1 in VibeCategory:
            for cat2 in VibeCategory:
                if cat2 not in compatibility[cat1]:
                    compatibility[cat1][cat2] = 0.6  # Slightly positive default
        
        return compatibility
    
    def _initialize_intensity_compatibility(self) -> Dict[VibeIntensity, Dict[VibeIntensity, float]]:
        """Initialize compatibility matrix for vibe intensities"""
        
        compatibility = defaultdict(dict)
        
        # Self-compatibility
        for intensity in VibeIntensity:
            compatibility[intensity][intensity] = 1.0
        
        # Adjacent intensities are quite compatible
        intensity_order = [VibeIntensity.SUBTLE, VibeIntensity.MODERATE, VibeIntensity.STRONG, VibeIntensity.INTENSE]
        
        for i, int1 in enumerate(intensity_order):
            for j, int2 in enumerate(intensity_order):
                if i == j:
                    continue  # Already handled above
                
                distance = abs(i - j)
                if distance == 1:
                    compatibility[int1][int2] = 0.8  # Adjacent
                elif distance == 2:
                    compatibility[int1][int2] = 0.5  # One step apart
                else:
                    compatibility[int1][int2] = 0.2  # Opposite extremes
        
        return compatibility
    
    def calculate_compatibility(self, vibe1: CreativeVibe, vibe2: CreativeVibe) -> Tuple[float, List[str]]:
        """Calculate detailed compatibility between two vibes"""
        
        compatibility_factors = []
        reasons = []
        
        # Archetype compatibility
        if vibe1.archetype and vibe2.archetype:
            archetype_compat = self.archetype_compatibility[vibe1.archetype][vibe2.archetype]
            compatibility_factors.append(archetype_compat * 0.3)  # 30% weight
            
            if archetype_compat > 0.7:
                reasons.append(f"Strong archetype synergy between {vibe1.archetype.value} and {vibe2.archetype.value}")
            elif archetype_compat < 0.4:
                reasons.append(f"Potential archetype conflict between {vibe1.archetype.value} and {vibe2.archetype.value}")
        
        # Category compatibility
        cat1, cat2 = vibe1.primary_category, vibe2.primary_category
        category_compat = self.category_compatibility[cat1][cat2]
        compatibility_factors.append(category_compat * 0.2)  # 20% weight
        
        if category_compat > 0.8:
            reasons.append(f"Excellent category alignment ({cat1.value} + {cat2.value})")
        
        # Intensity compatibility
        intensity_compat = self.intensity_compatibility[vibe1.overall_intensity][vibe2.overall_intensity]
        compatibility_factors.append(intensity_compat * 0.2)  # 20% weight
        
        if intensity_compat < 0.5:
            reasons.append(f"Intensity mismatch ({vibe1.overall_intensity.value} vs {vibe2.overall_intensity.value})")
        
        # Element compatibility
        element_compat = self._calculate_element_compatibility(vibe1, vibe2)
        compatibility_factors.append(element_compat * 0.2)  # 20% weight
        
        if element_compat > 0.6:
            reasons.append("Good element harmony")
        elif element_compat < 0.3:
            reasons.append("Conflicting elements detected")
        
        # Genre compatibility
        genre_compat = self._calculate_genre_compatibility(vibe1, vibe2)
        compatibility_factors.append(genre_compat * 0.1)  # 10% weight
        
        # Calculate overall compatibility
        overall_compatibility = sum(compatibility_factors)
        
        return overall_compatibility, reasons
    
    def _calculate_element_compatibility(self, vibe1: CreativeVibe, vibe2: CreativeVibe) -> float:
        """Calculate compatibility between vibe elements"""
        
        if not vibe1.primary_elements or not vibe2.primary_elements:
            return 0.5
        
        total_compatibility = 0
        comparisons = 0
        
        for elem1 in vibe1.primary_elements:
            for elem2 in vibe2.primary_elements:
                comparisons += 1
                
                # Check explicit incompatibilities
                if elem2.element_id in elem1.incompatible_with:
                    total_compatibility += 0.0
                    continue
                
                # Check enhancements
                if elem2.element_id in elem1.enhances:
                    total_compatibility += 1.0
                    continue
                
                # Category compatibility
                cat_compat = self.category_compatibility[elem1.category][elem2.category]
                total_compatibility += cat_compat
        
        return total_compatibility / comparisons if comparisons > 0 else 0.5
    
    def _calculate_genre_compatibility(self, vibe1: CreativeVibe, vibe2: CreativeVibe) -> float:
        """Calculate genre compatibility between vibes"""
        
        if not vibe1.compatible_genres or not vibe2.compatible_genres:
            return 0.5
        
        overlap = len(vibe1.compatible_genres & vibe2.compatible_genres)
        total_unique = len(vibe1.compatible_genres | vibe2.compatible_genres)
        
        return overlap / total_unique if total_unique > 0 else 0.0
    
    def find_conflicting_elements(self, vibe: CreativeVibe) -> List[Tuple[VibeElement, VibeElement, str]]:
        """Find conflicting elements within a single vibe"""
        
        conflicts = []
        
        all_elements = vibe.primary_elements + vibe.secondary_elements
        
        for i, elem1 in enumerate(all_elements):
            for elem2 in all_elements[i+1:]:
                # Check explicit incompatibilities
                if elem2.element_id in elem1.incompatible_with:
                    conflicts.append((elem1, elem2, "Explicit incompatibility"))
                
                # Check category conflicts
                cat_compat = self.category_compatibility[elem1.category][elem2.category]
                if cat_compat < 0.3:
                    conflicts.append((elem1, elem2, f"Category conflict ({elem1.category.value} vs {elem2.category.value})"))
                
                # Check intensity conflicts
                intensity_diff = abs(elem1.intensity - elem2.intensity)
                if intensity_diff > 0.6:
                    conflicts.append((elem1, elem2, f"Intensity mismatch ({elem1.intensity:.1f} vs {elem2.intensity:.1f})"))
        
        return conflicts
    
    def suggest_vibe_improvements(self, vibe: CreativeVibe) -> List[str]:
        """Suggest improvements for a vibe"""
        
        suggestions = []
        
        # Check for conflicts
        conflicts = self.find_conflicting_elements(vibe)
        if conflicts:
            suggestions.append(f"Consider resolving {len(conflicts)} element conflicts")
        
        # Check element balance
        if len(vibe.primary_elements) < 2:
            suggestions.append("Add more primary elements for richer vibe")
        elif len(vibe.primary_elements) > 4:
            suggestions.append("Consider reducing primary elements for clarity")
        
        # Check category diversity
        categories = {elem.category for elem in vibe.primary_elements}
        if len(categories) == 1:
            suggestions.append("Consider adding elements from other categories for depth")
        
        # Check intensity coherence
        intensities = [elem.intensity for elem in vibe.primary_elements]
        if intensities:
            intensity_range = max(intensities) - min(intensities)
            if intensity_range > 0.7:
                suggestions.append("Consider aligning element intensities for coherence")
        
        # Check genre compatibility
        if not vibe.compatible_genres:
            suggestions.append("Define compatible genres for better targeting")
        
        return suggestions


class VibeMatcher:
    """Main class for vibe matching and recommendations"""
    
    def __init__(self, vibe_library: VibeLibrary):
        self.vibe_library = vibe_library
        self.compatibility_engine = VibeCompatibilityEngine()
        self.logger = logging.getLogger(__name__)
    
    async def find_compatible_vibes(self, target_vibe: CreativeVibe, 
                                  candidates: Optional[List[CreativeVibe]] = None) -> List[VibeMatch]:
        """Find vibes compatible with the target vibe"""
        
        if candidates is None:
            # Generate candidates from templates
            candidates = [template.create_vibe() for template in self.vibe_library.templates.values()]
        
        matches = []
        
        for candidate in candidates:
            if candidate.vibe_id == target_vibe.vibe_id:
                continue  # Skip self
            
            compatibility, reasons = self.compatibility_engine.calculate_compatibility(target_vibe, candidate)
            
            if compatibility > 0.4:  # Minimum compatibility threshold
                # Generate enhancement suggestions
                enhancements = self._generate_enhancement_suggestions(target_vibe, candidate)
                
                # Calculate confidence based on multiple factors
                confidence = self._calculate_match_confidence(target_vibe, candidate, compatibility)
                
                match = VibeMatch(
                    vibe=candidate,
                    compatibility_score=compatibility,
                    match_reasons=reasons,
                    potential_enhancements=enhancements,
                    confidence=confidence
                )
                matches.append(match)
        
        # Sort by compatibility score
        matches.sort(key=lambda m: m.compatibility_score, reverse=True)
        
        self.logger.info(f"Found {len(matches)} compatible vibes for {target_vibe.name}")
        
        return matches[:10]  # Return top 10 matches
    
    async def recommend_vibes_for_user(self, user_intent: str, 
                                     preferred_genres: List[BookGenre] = None,
                                     creative_mood: CreativeMood = None,
                                     intensity_preference: VibeIntensity = None) -> List[VibeRecommendation]:
        """Recommend vibe templates based on user preferences"""
        
        recommendations = []
        
        for template in self.vibe_library.templates.values():
            relevance = await self._calculate_template_relevance(
                template, user_intent, preferred_genres, creative_mood, intensity_preference
            )
            
            if relevance > 0.3:  # Minimum relevance threshold
                # Generate customization suggestions
                customizations = self._generate_customization_suggestions(
                    template, user_intent, preferred_genres, creative_mood
                )
                
                # Generate explanation
                explanation = self._generate_recommendation_explanation(
                    template, user_intent, preferred_genres, creative_mood
                )
                
                # Calculate specific fit scores
                genre_fit = self._calculate_genre_fit(template, preferred_genres)
                mood_alignment = self._calculate_mood_alignment(template, creative_mood)
                
                recommendation = VibeRecommendation(
                    template=template,
                    relevance_score=relevance,
                    customization_suggestions=customizations,
                    why_recommended=explanation,
                    genre_fit=genre_fit,
                    mood_alignment=mood_alignment
                )
                recommendations.append(recommendation)
        
        # Sort by relevance
        recommendations.sort(key=lambda r: r.relevance_score, reverse=True)
        
        self.logger.info(f"Generated {len(recommendations)} vibe recommendations")
        
        return recommendations[:8]  # Return top 8 recommendations
    
    async def _calculate_template_relevance(self, template: VibeTemplate, 
                                          user_intent: str,
                                          preferred_genres: List[BookGenre] = None,
                                          creative_mood: CreativeMood = None,
                                          intensity_preference: VibeIntensity = None) -> float:
        """Calculate how relevant a template is to user preferences"""
        
        relevance_factors = []
        
        # Text similarity with user intent
        text_similarity = self._calculate_text_similarity(user_intent, template)
        relevance_factors.append(text_similarity * 0.3)  # 30% weight
        
        # Genre compatibility
        if preferred_genres:
            genre_overlap = len(set(preferred_genres) & template.suggested_genres)
            max_genres = max(len(preferred_genres), len(template.suggested_genres), 1)
            genre_score = genre_overlap / max_genres
            relevance_factors.append(genre_score * 0.25)  # 25% weight
        else:
            relevance_factors.append(0.5 * 0.25)  # Neutral
        
        # Mood alignment
        if creative_mood:
            mood_score = self._calculate_mood_template_alignment(creative_mood, template)
            relevance_factors.append(mood_score * 0.2)  # 20% weight
        else:
            relevance_factors.append(0.5 * 0.2)  # Neutral
        
        # Intensity preference
        if intensity_preference:
            intensity_score = self.compatibility_engine.intensity_compatibility[intensity_preference][template.default_intensity]
            relevance_factors.append(intensity_score * 0.15)  # 15% weight
        else:
            relevance_factors.append(0.5 * 0.15)  # Neutral
        
        # Template popularity and success
        popularity_score = min(template.popularity_score, 1.0)
        success_score = min(template.success_rate, 1.0)
        relevance_factors.append((popularity_score + success_score) / 2 * 0.1)  # 10% weight
        
        return sum(relevance_factors)
    
    def _calculate_text_similarity(self, user_intent: str, template: VibeTemplate) -> float:
        """Calculate text similarity between user intent and template"""
        
        user_words = set(user_intent.lower().split())
        
        # Check template name and description
        template_text = f"{template.name} {template.description}".lower()
        template_words = set(template_text.split())
        
        # Check usage examples
        for example in template.usage_examples:
            template_words.update(example.lower().split())
        
        # Check element keywords
        for element in template.template_elements:
            template_words.update(element.keywords)
        
        # Calculate overlap
        if not user_words or not template_words:
            return 0.0
        
        overlap = len(user_words & template_words)
        total_unique = len(user_words | template_words)
        
        return overlap / total_unique if total_unique > 0 else 0.0
    
    def _calculate_mood_template_alignment(self, mood: CreativeMood, template: VibeTemplate) -> float:
        """Calculate alignment between creative mood and template"""
        
        mood_archetype_alignment = {
            CreativeMood.PASSIONATE: {
                VibeArchetype.PASSIONATE_LOVE: 1.0,
                VibeArchetype.HEART_POUNDING: 0.7,
                VibeArchetype.TRANSFORMATION: 0.6
            },
            CreativeMood.CONTEMPLATIVE: {
                VibeArchetype.GENTLE_REFLECTION: 1.0,
                VibeArchetype.BITTERSWEET_NOSTALGIA: 0.8,
                VibeArchetype.DISCOVERY_WONDER: 0.6
            },
            CreativeMood.ENERGETIC: {
                VibeArchetype.HEART_POUNDING: 1.0,
                VibeArchetype.HEROIC_JOURNEY: 0.8,
                VibeArchetype.DISCOVERY_WONDER: 0.7
            },
            CreativeMood.INSPIRED: {
                VibeArchetype.DISCOVERY_WONDER: 1.0,
                VibeArchetype.ETHEREAL_MAGIC: 0.8,
                VibeArchetype.TRANSFORMATION: 0.7
            },
            CreativeMood.EXPERIMENTAL: {
                VibeArchetype.ETHEREAL_MAGIC: 1.0,
                VibeArchetype.DISCOVERY_WONDER: 0.8,
                VibeArchetype.TRANSFORMATION: 0.6
            },
            CreativeMood.REFLECTIVE: {
                VibeArchetype.GENTLE_REFLECTION: 1.0,
                VibeArchetype.BITTERSWEET_NOSTALGIA: 0.9,
                VibeArchetype.REDEMPTION_ARC: 0.7
            }
        }
        
        alignments = mood_archetype_alignment.get(mood, {})
        return alignments.get(template.archetype, 0.5)  # Default neutral alignment
    
    def _calculate_genre_fit(self, template: VibeTemplate, preferred_genres: List[BookGenre] = None) -> float:
        """Calculate how well template fits preferred genres"""
        
        if not preferred_genres:
            return 0.5  # Neutral
        
        overlap = len(set(preferred_genres) & template.suggested_genres)
        max_genres = max(len(preferred_genres), len(template.suggested_genres), 1)
        
        return overlap / max_genres
    
    def _calculate_mood_alignment(self, template: VibeTemplate, creative_mood: CreativeMood = None) -> float:
        """Calculate mood alignment score"""
        
        if not creative_mood:
            return 0.5  # Neutral
        
        return self._calculate_mood_template_alignment(creative_mood, template)
    
    def _generate_enhancement_suggestions(self, target_vibe: CreativeVibe, candidate_vibe: CreativeVibe) -> List[str]:
        """Generate suggestions for enhancing compatibility"""
        
        suggestions = []
        
        # Check intensity alignment
        if target_vibe.intensity_score > candidate_vibe.intensity_score + 0.3:
            suggestions.append("Increase intensity to match target energy")
        elif target_vibe.intensity_score < candidate_vibe.intensity_score - 0.3:
            suggestions.append("Reduce intensity for better harmony")
        
        # Check element synergies
        target_elements = {elem.element_id for elem in target_vibe.primary_elements}
        candidate_elements = {elem.element_id for elem in candidate_vibe.primary_elements}
        
        # Find enhancing elements
        for target_elem in target_vibe.primary_elements:
            for enhance_id in target_elem.enhances:
                if enhance_id in candidate_elements:
                    suggestions.append(f"Emphasize {enhance_id} element for synergy")
        
        # Genre alignment
        missing_genres = target_vibe.compatible_genres - candidate_vibe.compatible_genres
        if missing_genres:
            genre_names = [g.value.replace('_', ' ') for g in list(missing_genres)[:2]]
            suggestions.append(f"Consider {', '.join(genre_names)} genre elements")
        
        return suggestions[:3]  # Limit to top 3
    
    def _calculate_match_confidence(self, target_vibe: CreativeVibe, candidate_vibe: CreativeVibe, 
                                  compatibility: float) -> float:
        """Calculate confidence in the match"""
        
        confidence_factors = []
        
        # Base compatibility
        confidence_factors.append(compatibility * 0.4)
        
        # Element count alignment
        target_count = len(target_vibe.primary_elements)
        candidate_count = len(candidate_vibe.primary_elements)
        count_diff = abs(target_count - candidate_count)
        count_score = max(0, 1 - count_diff * 0.2)
        confidence_factors.append(count_score * 0.2)
        
        # Usage data confidence
        if candidate_vibe.usage_count > 0:
            usage_confidence = min(candidate_vibe.usage_count / 10, 1.0)
            confidence_factors.append(usage_confidence * 0.2)
        else:
            confidence_factors.append(0.1)  # Low confidence for unused vibes
        
        # Rating confidence
        if candidate_vibe.user_rating is not None:
            rating_confidence = candidate_vibe.user_rating / 5.0
            confidence_factors.append(rating_confidence * 0.2)
        else:
            confidence_factors.append(0.5)  # Neutral for unrated vibes
        
        return sum(confidence_factors)
    
    def _generate_customization_suggestions(self, template: VibeTemplate, 
                                          user_intent: str,
                                          preferred_genres: List[BookGenre] = None,
                                          creative_mood: CreativeMood = None) -> List[str]:
        """Generate customization suggestions for a template"""
        
        suggestions = []
        
        # Intensity customization
        if "intense" in user_intent.lower() or "powerful" in user_intent.lower():
            suggestions.append("Increase intensity to STRONG or INTENSE for more impact")
        elif "gentle" in user_intent.lower() or "subtle" in user_intent.lower():
            suggestions.append("Reduce intensity to SUBTLE for gentler approach")
        
        # Genre-specific customizations
        if preferred_genres:
            if BookGenre.ROMANCE in preferred_genres and template.archetype != VibeArchetype.PASSIONATE_LOVE:
                suggestions.append("Add romantic elements for genre alignment")
            elif BookGenre.MYSTERY in preferred_genres and template.archetype != VibeArchetype.DARK_MYSTERY:
                suggestions.append("Incorporate mystery elements for suspense")
            elif BookGenre.FANTASY in preferred_genres:
                suggestions.append("Enhance magical elements for fantasy appeal")
        
        # Mood-based customizations
        if creative_mood == CreativeMood.ENERGETIC:
            suggestions.append("Add dynamic pacing elements")
        elif creative_mood == CreativeMood.CONTEMPLATIVE:
            suggestions.append("Emphasize reflective and introspective elements")
        elif creative_mood == CreativeMood.EXPERIMENTAL:
            suggestions.append("Include innovative and unconventional elements")
        
        # Element additions based on user intent
        if "dark" in user_intent.lower():
            suggestions.append("Consider adding dark atmospheric elements")
        elif "bright" in user_intent.lower() or "light" in user_intent.lower():
            suggestions.append("Emphasize bright and uplifting elements")
        elif "cozy" in user_intent.lower():
            suggestions.append("Enhance comfort and warmth elements")
        
        return suggestions[:4]  # Limit to top 4
    
    def _generate_recommendation_explanation(self, template: VibeTemplate,
                                           user_intent: str,
                                           preferred_genres: List[BookGenre] = None,
                                           creative_mood: CreativeMood = None) -> str:
        """Generate explanation for why template is recommended"""
        
        reasons = []
        
        # Primary reason based on archetype
        archetype_reasons = {
            VibeArchetype.PASSIONATE_LOVE: "perfect for creating emotionally intense romantic connections",
            VibeArchetype.DARK_MYSTERY: "excellent for building atmospheric suspense and intrigue", 
            VibeArchetype.COZY_WARMTH: "ideal for comfortable, feel-good storytelling",
            VibeArchetype.HEART_POUNDING: "great for high-energy, exciting narratives",
            VibeArchetype.GENTLE_REFLECTION: "wonderful for thoughtful, character-driven stories",
            VibeArchetype.HEROIC_JOURNEY: "perfect for epic adventures and personal growth",
            VibeArchetype.DISCOVERY_WONDER: "excellent for stories of exploration and revelation"
        }
        
        primary_reason = archetype_reasons.get(template.archetype, "well-suited for your creative vision")
        reasons.append(primary_reason)
        
        # Genre alignment
        if preferred_genres:
            genre_overlap = set(preferred_genres) & template.suggested_genres
            if genre_overlap:
                genre_names = [g.value.replace('_', ' ') for g in genre_overlap]
                reasons.append(f"aligns with your {', '.join(genre_names)} preferences")
        
        # Mood alignment
        if creative_mood:
            mood_score = self._calculate_mood_template_alignment(creative_mood, template)
            if mood_score > 0.7:
                reasons.append(f"matches your {creative_mood.value} creative mood")
        
        # Success indicators
        if template.success_rate > 0.7:
            reasons.append("has a proven track record of success")
        elif template.popularity_score > 0.7:
            reasons.append("is popular among other creators")
        
        return f"Recommended because it's {', and '.join(reasons)}."
    
    async def analyze_vibe_trends(self, vibes: List[CreativeVibe]) -> Dict[str, any]:
        """Analyze trends in a collection of vibes"""
        
        if not vibes:
            return {"error": "No vibes to analyze"}
        
        # Archetype distribution
        archetype_counts = defaultdict(int)
        for vibe in vibes:
            if vibe.archetype:
                archetype_counts[vibe.archetype.value] += 1
        
        # Category distribution
        category_counts = defaultdict(int)
        for vibe in vibes:
            category_counts[vibe.primary_category.value] += 1
        
        # Intensity distribution
        intensity_counts = defaultdict(int)
        for vibe in vibes:
            intensity_counts[vibe.overall_intensity.value] += 1
        
        # Average ratings
        rated_vibes = [v for v in vibes if v.user_rating is not None]
        avg_rating = sum(v.user_rating for v in rated_vibes) / len(rated_vibes) if rated_vibes else None
        
        # Most common elements
        element_counts = defaultdict(int)
        for vibe in vibes:
            for element in vibe.primary_elements:
                element_counts[element.name] += 1
        
        top_elements = sorted(element_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Compatibility analysis
        total_pairs = 0
        compatible_pairs = 0
        
        for i, vibe1 in enumerate(vibes):
            for vibe2 in vibes[i+1:]:
                compatibility, _ = self.compatibility_engine.calculate_compatibility(vibe1, vibe2)
                total_pairs += 1
                if compatibility > 0.6:
                    compatible_pairs += 1
        
        compatibility_rate = compatible_pairs / total_pairs if total_pairs > 0 else 0
        
        return {
            "total_vibes": len(vibes),
            "archetype_distribution": dict(archetype_counts),
            "category_distribution": dict(category_counts),
            "intensity_distribution": dict(intensity_counts),
            "average_rating": avg_rating,
            "top_elements": top_elements,
            "compatibility_rate": compatibility_rate,
            "analysis_timestamp": datetime.now().isoformat()
        }