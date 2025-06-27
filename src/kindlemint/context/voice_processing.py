"""
Voice Input Processing for KindleMint Vibecoding System

This module handles voice input processing including transcription, emotion detection,
intent classification, and voice characteristic analysis for the vibecoding system.
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from .models import (
    CreativeMood,
    EmotionProfile,
    Intent,
    VoiceCharacteristics,
    VoiceInput,
)

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user intent from voice input"""
    
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.confidence_threshold = 0.6
    
    def _initialize_intent_patterns(self) -> Dict[Intent, List[str]]:
        """Initialize intent classification patterns"""
        return {
            Intent.CREATE_BOOK: [
                "create", "write", "start", "begin", "new book", "new story",
                "compose", "draft", "author", "novel", "write a book"
            ],
            Intent.EDIT_CONTENT: [
                "edit", "change", "modify", "update", "revise", "rewrite",
                "fix", "improve", "adjust", "alter", "correct"
            ],
            Intent.ADD_CHAPTER: [
                "add chapter", "new chapter", "next chapter", "continue story",
                "chapter", "section", "part", "episode"
            ],
            Intent.REFINE_STYLE: [
                "style", "tone", "voice", "writing style", "improve writing",
                "make it more", "change the tone", "refine", "polish"
            ],
            Intent.CHANGE_GENRE: [
                "genre", "type of book", "category", "switch to", "make it",
                "romance", "mystery", "fantasy", "thriller", "business"
            ],
            Intent.MARKET_OPTIMIZE: [
                "market", "sell", "bestseller", "optimize", "popular",
                "trending", "audience", "readers", "marketing", "promote"
            ],
            Intent.PUBLISH_BOOK: [
                "publish", "release", "print", "kindle", "amazon", "ebook",
                "paperback", "distribution", "launch", "go live"
            ],
            Intent.GET_FEEDBACK: [
                "feedback", "opinion", "review", "what do you think",
                "how does this sound", "critique", "suggestions", "advice"
            ],
            Intent.EXPLORE_IDEAS: [
                "explore", "brainstorm", "ideas", "inspiration", "what if",
                "maybe", "consider", "think about", "possibilities"
            ],
            Intent.SET_VIBE: [
                "vibe", "mood", "feeling", "atmosphere", "tone", "energy",
                "make it feel", "want it to be", "capture the essence"
            ]
        }
    
    async def classify_intent(self, text: str, voice_characteristics: VoiceCharacteristics) -> Tuple[Intent, float]:
        """Classify intent from text and voice characteristics"""
        text_lower = text.lower()
        intent_scores = {}
        
        # Score based on keyword matching
        for intent, patterns in self.intent_patterns.items():
            score = 0
            total_patterns = len(patterns)
            
            for pattern in patterns:
                if pattern in text_lower:
                    # Boost score for exact matches
                    score += 2
                elif any(word in text_lower for word in pattern.split()):
                    # Partial match gets lower score
                    score += 1
            
            # Normalize score
            if total_patterns > 0:
                intent_scores[intent] = score / total_patterns
        
        # Boost scores based on voice characteristics
        intent_scores = self._adjust_scores_by_voice(intent_scores, voice_characteristics)
        
        # Get best intent and confidence
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[best_intent], 1.0)
            
            # Use default if confidence too low
            if confidence < self.confidence_threshold:
                return Intent.EXPLORE_IDEAS, confidence
            
            return best_intent, confidence
        
        return Intent.EXPLORE_IDEAS, 0.5
    
    def _adjust_scores_by_voice(self, scores: Dict[Intent, float], 
                               voice_chars: VoiceCharacteristics) -> Dict[Intent, float]:
        """Adjust intent scores based on voice characteristics"""
        adjusted_scores = scores.copy()
        
        # High energy voice boosts creative intents
        if voice_chars.confidence_level > 0.7:
            if Intent.CREATE_BOOK in adjusted_scores:
                adjusted_scores[Intent.CREATE_BOOK] *= 1.2
            if Intent.EXPLORE_IDEAS in adjusted_scores:
                adjusted_scores[Intent.EXPLORE_IDEAS] *= 1.1
        
        # Fast pace might indicate editing intent
        if voice_chars.pace > 1.2:
            if Intent.EDIT_CONTENT in adjusted_scores:
                adjusted_scores[Intent.EDIT_CONTENT] *= 1.1
        
        # Calm, clear voice might indicate publishing intent
        if voice_chars.clarity_score > 0.8 and voice_chars.pace < 1.1:
            if Intent.PUBLISH_BOOK in adjusted_scores:
                adjusted_scores[Intent.PUBLISH_BOOK] *= 1.1
        
        return adjusted_scores


class EmotionAnalyzer:
    """Analyzes emotional context from voice and text"""
    
    def __init__(self):
        self.emotion_keywords = self._initialize_emotion_keywords()
        self.mood_patterns = self._initialize_mood_patterns()
    
    def _initialize_emotion_keywords(self) -> Dict[str, List[str]]:
        """Initialize emotion detection keywords"""
        return {
            "excited": ["excited", "thrilled", "amazing", "awesome", "fantastic", "incredible"],
            "happy": ["happy", "joy", "cheerful", "delighted", "pleased", "glad"],
            "calm": ["calm", "peaceful", "serene", "relaxed", "tranquil", "zen"],
            "focused": ["focused", "concentrated", "determined", "committed", "dedicated"],
            "frustrated": ["frustrated", "annoyed", "stuck", "difficult", "challenging"],
            "nervous": ["nervous", "anxious", "worried", "uncertain", "unsure"],
            "confident": ["confident", "sure", "certain", "positive", "strong", "capable"],
            "creative": ["creative", "inspired", "imaginative", "artistic", "innovative"],
            "analytical": ["logical", "systematic", "structured", "organized", "methodical"],
            "passionate": ["passionate", "intense", "driven", "motivated", "energetic"]
        }
    
    def _initialize_mood_patterns(self) -> Dict[CreativeMood, List[str]]:
        """Initialize creative mood patterns"""
        return {
            CreativeMood.INSPIRED: [
                "inspired", "brilliant idea", "eureka", "breakthrough", "vision",
                "spark", "light bulb", "suddenly realized"
            ],
            CreativeMood.FOCUSED: [
                "focused", "concentrated", "deep work", "in the zone", "flow state",
                "laser focus", "tunnel vision", "undistracted"
            ],
            CreativeMood.EXPLORATORY: [
                "explore", "discover", "experiment", "try different", "what if",
                "maybe we could", "let's see", "investigate"
            ],
            CreativeMood.PLAYFUL: [
                "playful", "fun", "silly", "whimsical", "light-hearted",
                "amusing", "entertaining", "joy"
            ],
            CreativeMood.SERIOUS: [
                "serious", "important", "critical", "significant", "meaningful",
                "profound", "deep", "weighty"
            ],
            CreativeMood.EXPERIMENTAL: [
                "experiment", "test", "try", "prototype", "beta", "pilot",
                "innovative", "unconventional", "boundary pushing"
            ],
            CreativeMood.REFLECTIVE: [
                "reflect", "think deeply", "contemplate", "consider", "ponder",
                "meditate", "introspective", "thoughtful"
            ],
            CreativeMood.ENERGETIC: [
                "energetic", "high energy", "pumped", "amped", "fired up",
                "enthusiastic", "vigorous", "dynamic"
            ],
            CreativeMood.CONTEMPLATIVE: [
                "contemplative", "philosophical", "deep thinking", "spiritual",
                "existential", "meaning", "purpose"
            ],
            CreativeMood.PASSIONATE: [
                "passionate", "burning desire", "obsessed", "driven", "intense",
                "fervent", "zealous", "devoted"
            ]
        }
    
    async def analyze_emotions(self, text: str, voice_characteristics: VoiceCharacteristics) -> EmotionProfile:
        """Analyze emotions from text and voice characteristics"""
        
        # Analyze text-based emotions
        text_emotions = self._analyze_text_emotions(text)
        
        # Analyze voice-based emotions
        voice_emotions = self._analyze_voice_emotions(voice_characteristics)
        
        # Determine creative mood
        creative_mood = self._determine_creative_mood(text, voice_characteristics)
        
        # Combine and synthesize
        primary_emotion = self._determine_primary_emotion(text_emotions, voice_emotions)
        intensity = self._calculate_emotion_intensity(text_emotions, voice_emotions)
        secondary_emotions = self._get_secondary_emotions(text_emotions, voice_emotions)
        energy_level = self._calculate_energy_level(voice_characteristics, text_emotions)
        creative_intent = self._extract_creative_intent(text)
        emotional_stability = self._assess_emotional_stability(voice_characteristics)
        enthusiasm_score = self._calculate_enthusiasm(text_emotions, voice_characteristics)
        
        return EmotionProfile(
            primary_emotion=primary_emotion,
            intensity=intensity,
            secondary_emotions=secondary_emotions,
            mood=creative_mood,
            energy_level=energy_level,
            creative_intent=creative_intent,
            emotional_stability=emotional_stability,
            enthusiasm_score=enthusiasm_score
        )
    
    def _analyze_text_emotions(self, text: str) -> Dict[str, float]:
        """Analyze emotions from text content"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            
            if len(keywords) > 0:
                emotion_scores[emotion] = score / len(keywords)
        
        return emotion_scores
    
    def _analyze_voice_emotions(self, voice_chars: VoiceCharacteristics) -> Dict[str, float]:
        """Analyze emotions from voice characteristics"""
        voice_emotions = {}
        
        # Map voice characteristics to emotions
        if voice_chars.pace > 1.3:
            voice_emotions["excited"] = 0.7
            voice_emotions["energetic"] = 0.8
        elif voice_chars.pace < 0.7:
            voice_emotions["calm"] = 0.8
            voice_emotions["contemplative"] = 0.6
        
        if voice_chars.confidence_level > 0.8:
            voice_emotions["confident"] = 0.9
        elif voice_chars.confidence_level < 0.4:
            voice_emotions["nervous"] = 0.7
        
        # Tone-based emotions
        if voice_chars.tone == "warm":
            voice_emotions["happy"] = 0.6
        elif voice_chars.tone == "intense":
            voice_emotions["passionate"] = 0.8
        elif voice_chars.tone == "steady":
            voice_emotions["focused"] = 0.7
        
        return voice_emotions
    
    def _determine_creative_mood(self, text: str, voice_chars: VoiceCharacteristics) -> CreativeMood:
        """Determine creative mood from text and voice"""
        text_lower = text.lower()
        mood_scores = {}
        
        # Score based on text patterns
        for mood, patterns in self.mood_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            
            if len(patterns) > 0:
                mood_scores[mood] = score / len(patterns)
        
        # Adjust based on voice characteristics
        if voice_chars.energy_level > 0.8:
            mood_scores[CreativeMood.ENERGETIC] = mood_scores.get(CreativeMood.ENERGETIC, 0) + 0.3
        if voice_chars.pace > 1.2:
            mood_scores[CreativeMood.INSPIRED] = mood_scores.get(CreativeMood.INSPIRED, 0) + 0.2
        if voice_chars.confidence_level > 0.8:
            mood_scores[CreativeMood.PASSIONATE] = mood_scores.get(CreativeMood.PASSIONATE, 0) + 0.2
        
        # Return highest scoring mood, or default
        if mood_scores:
            return max(mood_scores, key=mood_scores.get)
        
        return CreativeMood.FOCUSED
    
    def _determine_primary_emotion(self, text_emotions: Dict[str, float], 
                                 voice_emotions: Dict[str, float]) -> str:
        """Determine primary emotion from combined analysis"""
        combined_emotions = {}
        
        # Combine text and voice emotions with weighting
        all_emotions = set(text_emotions.keys()) | set(voice_emotions.keys())
        
        for emotion in all_emotions:
            text_score = text_emotions.get(emotion, 0) * 0.6  # Text weight
            voice_score = voice_emotions.get(emotion, 0) * 0.4  # Voice weight
            combined_emotions[emotion] = text_score + voice_score
        
        # Return highest scoring emotion or default
        if combined_emotions:
            return max(combined_emotions, key=combined_emotions.get)
        
        return "neutral"
    
    def _calculate_emotion_intensity(self, text_emotions: Dict[str, float], 
                                   voice_emotions: Dict[str, float]) -> float:
        """Calculate overall emotion intensity"""
        text_max = max(text_emotions.values()) if text_emotions else 0
        voice_max = max(voice_emotions.values()) if voice_emotions else 0
        
        # Combined intensity with weighting
        intensity = text_max * 0.6 + voice_max * 0.4
        return min(intensity, 1.0)
    
    def _get_secondary_emotions(self, text_emotions: Dict[str, float], 
                               voice_emotions: Dict[str, float]) -> List[str]:
        """Get secondary emotions (top 3 excluding primary)"""
        combined_emotions = {}
        
        all_emotions = set(text_emotions.keys()) | set(voice_emotions.keys())
        for emotion in all_emotions:
            text_score = text_emotions.get(emotion, 0) * 0.6
            voice_score = voice_emotions.get(emotion, 0) * 0.4
            combined_emotions[emotion] = text_score + voice_score
        
        # Sort and return top 3 (excluding primary)
        sorted_emotions = sorted(combined_emotions.items(), key=lambda x: x[1], reverse=True)
        return [emotion for emotion, score in sorted_emotions[1:4] if score > 0.1]
    
    def _calculate_energy_level(self, voice_chars: VoiceCharacteristics, 
                               text_emotions: Dict[str, float]) -> float:
        """Calculate energy level from voice and text"""
        # Base energy from voice pace and confidence
        voice_energy = (voice_chars.pace + voice_chars.confidence_level) / 2
        
        # Boost from energetic emotions in text
        energetic_emotions = ["excited", "passionate", "energetic", "enthusiastic"]
        text_energy_boost = sum(text_emotions.get(emotion, 0) for emotion in energetic_emotions)
        
        # Combine with weighting
        energy_level = voice_energy * 0.7 + text_energy_boost * 0.3
        return min(energy_level, 1.0)
    
    def _extract_creative_intent(self, text: str) -> List[str]:
        """Extract creative intent markers from text"""
        text_lower = text.lower()
        creative_markers = []
        
        creative_intent_patterns = {
            "world_building": ["world", "setting", "place", "environment", "location"],
            "character_development": ["character", "personality", "protagonist", "hero", "villain"],
            "plot_development": ["plot", "story", "narrative", "sequence", "events"],
            "dialogue_focus": ["dialogue", "conversation", "speech", "talking", "voices"],
            "theme_exploration": ["theme", "meaning", "message", "purpose", "deeper"],
            "style_refinement": ["style", "voice", "tone", "writing", "prose"],
            "pacing_control": ["pace", "speed", "rhythm", "flow", "tempo"],
            "emotion_capture": ["emotion", "feeling", "mood", "atmosphere", "vibe"]
        }
        
        for intent_type, keywords in creative_intent_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                creative_markers.append(intent_type)
        
        return creative_markers[:5]  # Limit to top 5
    
    def _assess_emotional_stability(self, voice_chars: VoiceCharacteristics) -> float:
        """Assess emotional stability from voice characteristics"""
        # Stability based on consistency indicators
        stability = 1.0
        
        # Reduce stability for extreme values
        if voice_chars.pace < 0.5 or voice_chars.pace > 2.0:
            stability -= 0.2
        
        if voice_chars.clarity_score < 0.5:
            stability -= 0.3
        
        # Confidence contributes to stability
        stability = stability * 0.7 + voice_chars.confidence_level * 0.3
        
        return max(stability, 0.0)
    
    def _calculate_enthusiasm(self, text_emotions: Dict[str, float], 
                            voice_chars: VoiceCharacteristics) -> float:
        """Calculate enthusiasm score"""
        # Text-based enthusiasm
        enthusiasm_emotions = ["excited", "passionate", "thrilled", "amazing"]
        text_enthusiasm = sum(text_emotions.get(emotion, 0) for emotion in enthusiasm_emotions)
        
        # Voice-based enthusiasm (pace + confidence)
        voice_enthusiasm = (voice_chars.pace - 1.0) * 0.5 + voice_chars.confidence_level * 0.5
        voice_enthusiasm = max(voice_enthusiasm, 0)
        
        # Combine
        enthusiasm = text_enthusiasm * 0.6 + voice_enthusiasm * 0.4
        return min(enthusiasm, 1.0)


class VoiceCharacteristicsExtractor:
    """Extracts voice characteristics from audio analysis"""
    
    def __init__(self):
        self.tone_indicators = {
            "warm": ["gentle", "friendly", "caring", "comfortable"],
            "energetic": ["fast", "dynamic", "lively", "vibrant"],
            "calm": ["steady", "peaceful", "composed", "measured"],
            "intense": ["passionate", "urgent", "strong", "powerful"],
            "professional": ["clear", "articulate", "formal", "structured"]
        }
    
    async def extract_characteristics(self, audio_analysis: Dict[str, any], 
                                    text: str) -> VoiceCharacteristics:
        """Extract voice characteristics from audio analysis"""
        
        # Extract basic metrics (simulated - in production would use real audio analysis)
        pace = self._analyze_speaking_pace(audio_analysis, text)
        tone = self._determine_tone(audio_analysis, text)
        clarity_score = self._calculate_clarity(audio_analysis)
        confidence_level = self._assess_confidence(audio_analysis, text)
        
        # Extract patterns
        emphasis_patterns = self._extract_emphasis_patterns(audio_analysis, text)
        speech_markers = self._extract_speech_markers(audio_analysis, text)
        personality_indicators = self._extract_personality_indicators(audio_analysis, text)
        
        return VoiceCharacteristics(
            tone=tone,
            pace=pace,
            emphasis_patterns=emphasis_patterns,
            speech_markers=speech_markers,
            personality_indicators=personality_indicators,
            clarity_score=clarity_score,
            confidence_level=confidence_level
        )
    
    def _analyze_speaking_pace(self, audio_analysis: Dict[str, any], text: str) -> float:
        """Analyze speaking pace (words per minute relative to normal)"""
        # Simulate pace analysis
        word_count = len(text.split())
        duration_seconds = audio_analysis.get("duration", 30)  # Default 30 seconds
        
        if duration_seconds > 0:
            words_per_minute = (word_count / duration_seconds) * 60
            # Normal pace is around 150 WPM, so calculate relative pace
            relative_pace = words_per_minute / 150
            return min(max(relative_pace, 0.3), 3.0)  # Clamp between 0.3x and 3x
        
        return 1.0  # Default normal pace
    
    def _determine_tone(self, audio_analysis: Dict[str, any], text: str) -> str:
        """Determine voice tone"""
        # Simulate tone analysis based on audio features and text
        pitch_mean = audio_analysis.get("pitch_mean", 200)
        pitch_variance = audio_analysis.get("pitch_variance", 50)
        energy = audio_analysis.get("energy", 0.5)
        
        text_lower = text.lower()
        
        # Rule-based tone detection
        if energy > 0.7 and pitch_variance > 60:
            return "energetic"
        elif energy < 0.3 and pitch_variance < 30:
            return "calm"
        elif pitch_mean > 250 and "!" in text:
            return "excited"
        elif any(word in text_lower for word in ["important", "serious", "critical"]):
            return "professional"
        elif any(word in text_lower for word in ["love", "wonderful", "beautiful"]):
            return "warm"
        else:
            return "neutral"
    
    def _calculate_clarity(self, audio_analysis: Dict[str, any]) -> float:
        """Calculate speech clarity score"""
        # Simulate clarity analysis
        signal_to_noise = audio_analysis.get("signal_to_noise_ratio", 10)
        articulation_score = audio_analysis.get("articulation_score", 0.8)
        
        # Combine factors for clarity
        clarity = (signal_to_noise / 20) * 0.4 + articulation_score * 0.6
        return min(max(clarity, 0.0), 1.0)
    
    def _assess_confidence(self, audio_analysis: Dict[str, any], text: str) -> float:
        """Assess speaker confidence level"""
        # Voice-based confidence indicators
        volume_consistency = audio_analysis.get("volume_consistency", 0.7)
        pause_frequency = audio_analysis.get("pause_frequency", 0.1)
        filler_word_ratio = audio_analysis.get("filler_word_ratio", 0.05)
        
        # Text-based confidence indicators
        text_lower = text.lower()
        confident_words = ["definitely", "absolutely", "certainly", "confident", "sure"]
        uncertain_words = ["maybe", "perhaps", "might", "possibly", "not sure", "um", "uh"]
        
        confident_count = sum(1 for word in confident_words if word in text_lower)
        uncertain_count = sum(1 for word in uncertain_words if word in text_lower)
        
        # Calculate confidence score
        voice_confidence = volume_consistency * (1 - pause_frequency) * (1 - filler_word_ratio)
        text_confidence = max(0, confident_count - uncertain_count * 2) / max(len(text.split()), 1)
        
        confidence = voice_confidence * 0.7 + text_confidence * 0.3
        return min(max(confidence, 0.0), 1.0)
    
    def _extract_emphasis_patterns(self, audio_analysis: Dict[str, any], text: str) -> List[str]:
        """Extract emphasis patterns from speech"""
        patterns = []
        
        # Simulate emphasis detection
        emphasis_points = audio_analysis.get("emphasis_points", [])
        words = text.split()
        
        for point in emphasis_points:
            if point < len(words):
                patterns.append(f"emphasis_on_{words[point].lower()}")
        
        # Add punctuation-based emphasis
        if "!" in text:
            patterns.append("exclamatory_emphasis")
        if "?" in text:
            patterns.append("questioning_emphasis")
        if text.count('"') >= 2:
            patterns.append("quoted_emphasis")
        
        return patterns[:5]  # Limit to top 5
    
    def _extract_speech_markers(self, audio_analysis: Dict[str, any], text: str) -> Dict[str, any]:
        """Extract speech markers and patterns"""
        markers = {}
        
        # Breathing patterns
        markers["breath_pattern"] = audio_analysis.get("breath_pattern", "normal")
        
        # Pause patterns
        markers["pause_pattern"] = audio_analysis.get("pause_pattern", "regular")
        
        # Repetition patterns
        words = text.lower().split()
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = [word for word, count in word_counts.items() if count > 2]
        markers["repetitive_words"] = repeated_words[:3]
        
        # Sentence structure patterns
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        markers["avg_sentence_length"] = avg_sentence_length
        
        return markers
    
    def _extract_personality_indicators(self, audio_analysis: Dict[str, any], text: str) -> Dict[str, float]:
        """Extract personality indicators from voice and speech patterns"""
        indicators = {}
        
        # Extraversion indicators
        volume = audio_analysis.get("average_volume", 0.5)
        pace = self._analyze_speaking_pace(audio_analysis, text)
        
        indicators["extraversion"] = min((volume + pace / 2) / 1.5, 1.0)
        
        # Conscientiousness indicators
        consistency = audio_analysis.get("volume_consistency", 0.7)
        structure_score = self._assess_text_structure(text)
        
        indicators["conscientiousness"] = (consistency + structure_score) / 2
        
        # Openness indicators
        vocabulary_diversity = self._calculate_vocabulary_diversity(text)
        creative_language = self._assess_creative_language(text)
        
        indicators["openness"] = (vocabulary_diversity + creative_language) / 2
        
        # Neuroticism indicators (reverse scored - higher is more stable)
        speech_stability = audio_analysis.get("speech_stability", 0.8)
        indicators["emotional_stability"] = speech_stability
        
        # Agreeableness indicators
        positive_language = self._assess_positive_language(text)
        collaborative_language = self._assess_collaborative_language(text)
        
        indicators["agreeableness"] = (positive_language + collaborative_language) / 2
        
        return indicators
    
    def _assess_text_structure(self, text: str) -> float:
        """Assess structure and organization of text"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Check for consistent sentence length variance
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        # Lower variance indicates better structure
        structure_score = max(0, 1 - (variance / 100))
        return min(structure_score, 1.0)
    
    def _calculate_vocabulary_diversity(self, text: str) -> float:
        """Calculate vocabulary diversity (type-token ratio)"""
        words = text.lower().split()
        unique_words = set(words)
        
        if not words:
            return 0.0
        
        diversity = len(unique_words) / len(words)
        return min(diversity * 2, 1.0)  # Scale up since TTR is typically low
    
    def _assess_creative_language(self, text: str) -> float:
        """Assess use of creative language"""
        creative_indicators = [
            "imagine", "envision", "create", "dream", "invent", "discover",
            "magical", "wonderful", "amazing", "brilliant", "unique", "innovative"
        ]
        
        text_lower = text.lower()
        creative_count = sum(1 for indicator in creative_indicators if indicator in text_lower)
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        creative_ratio = creative_count / word_count
        return min(creative_ratio * 10, 1.0)  # Scale appropriately
    
    def _assess_positive_language(self, text: str) -> float:
        """Assess use of positive language"""
        positive_words = [
            "good", "great", "excellent", "wonderful", "amazing", "beautiful",
            "love", "like", "enjoy", "happy", "pleased", "excited", "fantastic"
        ]
        
        negative_words = [
            "bad", "terrible", "awful", "hate", "dislike", "angry", "frustrated",
            "disappointed", "worried", "sad", "upset", "annoyed"
        ]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate net positivity
        net_positive = positive_count - negative_count
        word_count = len(text.split())
        
        if word_count == 0:
            return 0.5  # Neutral
        
        positivity_ratio = (net_positive / word_count) + 0.5  # Center around 0.5
        return min(max(positivity_ratio, 0.0), 1.0)
    
    def _assess_collaborative_language(self, text: str) -> float:
        """Assess use of collaborative language"""
        collaborative_words = [
            "we", "us", "together", "collaborate", "team", "share", "help",
            "support", "work with", "partner", "join", "cooperate"
        ]
        
        text_lower = text.lower()
        collaborative_count = sum(1 for word in collaborative_words if word in text_lower)
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        collaborative_ratio = collaborative_count / word_count
        return min(collaborative_ratio * 5, 1.0)  # Scale appropriately


class VoiceInputProcessor:
    """Main processor for voice input handling"""
    
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.emotion_analyzer = EmotionAnalyzer()
        self.voice_extractor = VoiceCharacteristicsExtractor()
        self.logger = logging.getLogger(__name__)
    
    async def process_voice_input(self, audio_data: bytes, session_id: str, 
                                audio_metadata: Optional[Dict[str, any]] = None) -> VoiceInput:
        """Process voice input and return structured VoiceInput object"""
        
        try:
            # Step 1: Transcribe audio (simulated - would use real STT service)
            transcription_result = await self._transcribe_audio(audio_data, audio_metadata)
            
            # Step 2: Extract voice characteristics
            voice_characteristics = await self.voice_extractor.extract_characteristics(
                transcription_result["audio_analysis"], 
                transcription_result["text"]
            )
            
            # Step 3: Classify intent
            intent, intent_confidence = await self.intent_classifier.classify_intent(
                transcription_result["text"], 
                voice_characteristics
            )
            
            # Step 4: Analyze emotions
            emotions = await self.emotion_analyzer.analyze_emotions(
                transcription_result["text"], 
                voice_characteristics
            )
            
            # Step 5: Create VoiceInput object
            voice_input = VoiceInput(
                session_id=session_id,
                text=transcription_result["text"],
                confidence=transcription_result["confidence"],
                emotions=emotions,
                intent=intent,
                voice_characteristics=voice_characteristics,
                timestamp=datetime.now(),
                processing_metadata={
                    "intent_confidence": intent_confidence,
                    "transcription_method": transcription_result.get("method", "whisper"),
                    "audio_duration": transcription_result.get("duration", 0),
                    "processing_time": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"Processed voice input for session {session_id}: intent={intent.value}, emotion={emotions.primary_emotion}")
            
            return voice_input
            
        except Exception as e:
            self.logger.error(f"Failed to process voice input for session {session_id}: {e}")
            
            # Return minimal voice input on error
            return VoiceInput(
                session_id=session_id,
                text="",
                confidence=0.0,
                intent=Intent.EXPLORE_IDEAS,
                processing_metadata={"error": str(e)}
            )
    
    async def _transcribe_audio(self, audio_data: bytes, 
                               metadata: Optional[Dict[str, any]] = None) -> Dict[str, any]:
        """Transcribe audio to text (simulated implementation)"""
        
        # In production, this would call OpenAI Whisper, Google Speech-to-Text, etc.
        # For now, simulate transcription
        
        # Simulate processing time
        await asyncio.sleep(0.1)
        
        # Simulate transcription result
        simulated_text = "I want to create a mystery novel set in a small coastal town with an amateur detective who solves crimes."
        
        # Simulate audio analysis results
        audio_analysis = {
            "duration": 12.5,
            "pitch_mean": 180,
            "pitch_variance": 45,
            "energy": 0.6,
            "signal_to_noise_ratio": 15,
            "articulation_score": 0.85,
            "volume_consistency": 0.8,
            "pause_frequency": 0.08,
            "filler_word_ratio": 0.03,
            "emphasis_points": [2, 7, 12],  # Word indices with emphasis
            "breath_pattern": "normal",
            "pause_pattern": "regular",
            "speech_stability": 0.82,
            "average_volume": 0.65
        }
        
        return {
            "text": simulated_text,
            "confidence": 0.92,
            "method": "whisper_simulation",
            "duration": audio_analysis["duration"],
            "audio_analysis": audio_analysis
        }
    
    async def process_text_input(self, text: str, session_id: str) -> VoiceInput:
        """Process text input as if it were voice (for testing/fallback)"""
        
        try:
            # Create default voice characteristics for text input
            default_voice_chars = VoiceCharacteristics(
                tone="neutral",
                pace=1.0,
                clarity_score=1.0,
                confidence_level=0.8
            )
            
            # Classify intent
            intent, intent_confidence = await self.intent_classifier.classify_intent(text, default_voice_chars)
            
            # Analyze emotions (text-only)
            emotions = await self.emotion_analyzer.analyze_emotions(text, default_voice_chars)
            
            # Create VoiceInput object
            voice_input = VoiceInput(
                session_id=session_id,
                text=text,
                confidence=1.0,  # Perfect confidence for text
                emotions=emotions,
                intent=intent,
                voice_characteristics=default_voice_chars,
                timestamp=datetime.now(),
                processing_metadata={
                    "input_type": "text",
                    "intent_confidence": intent_confidence,
                    "processing_time": datetime.now().isoformat()
                }
            )
            
            self.logger.info(f"Processed text input for session {session_id}: intent={intent.value}")
            
            return voice_input
            
        except Exception as e:
            self.logger.error(f"Failed to process text input for session {session_id}: {e}")
            
            return VoiceInput(
                session_id=session_id,
                text=text,
                confidence=1.0,
                intent=Intent.EXPLORE_IDEAS,
                processing_metadata={"error": str(e)}
            )