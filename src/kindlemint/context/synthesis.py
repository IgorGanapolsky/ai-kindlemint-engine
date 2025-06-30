"""
Context Synthesis Engine for KindleMint Vibecoding System

This module synthesizes multiple context layers (author, market, creative, publishing)
into a unified context for optimal content generation with attention-based weighting.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

from .author_context import AuthorContextBuilder
from .context_memory import ContextMemoryStore
from .models import (
    AuthorContext,
    BookGenre,
    ContextSynthesisWeights,
    CreativeContext,
    CreativePattern,
    MarketContext,
    MarketTrend,
    PublishingContext,
    PublishingFormat,
    SynthesizedContext,
    VoiceInput,
)

logger = logging.getLogger(__name__)


class MarketContextAnalyzer:
    """Analyzes market context for content optimization"""

    def __init__(self):
        self.trend_cache = {}
        self.last_refresh = None
        self.cache_duration_hours = 6

    async def get_relevant_context(
        self, intent_type: str, user_preferences: Optional[Dict] = None
    ) -> MarketContext:
        """Get market context relevant to user intent and preferences"""

        # Refresh market data if needed
        if self._should_refresh_cache():
            await self._refresh_market_data()

        # Get relevant trends based on intent
        relevant_trends = self._filter_trends_by_intent(intent_type)

        # Get target keywords
        target_keywords = await self._generate_target_keywords(
            intent_type, user_preferences
        )

        # Analyze competition
        competition_analysis = await self._analyze_competition(relevant_trends)

        # Get pricing insights
        pricing_insights = await self._get_pricing_insights(relevant_trends)

        # Get audience preferences
        audience_preferences = await self._analyze_audience_preferences(relevant_trends)

        # Get seasonal opportunities
        seasonal_opportunities = await self._get_seasonal_opportunities()

        # Get platform optimizations
        platform_optimizations = await self._get_platform_optimizations()

        return MarketContext(
            current_trends=relevant_trends,
            target_keywords=target_keywords,
            competition_analysis=competition_analysis,
            pricing_insights=pricing_insights,
            audience_preferences=audience_preferences,
            seasonal_opportunities=seasonal_opportunities,
            platform_optimizations=platform_optimizations,
            last_updated=datetime.now(),
        )

    def _should_refresh_cache(self) -> bool:
        """Check if market data cache should be refreshed"""
        if not self.last_refresh:
            return True

        hours_since_refresh = (
            datetime.now() - self.last_refresh
        ).total_seconds() / 3600
        return hours_since_refresh >= self.cache_duration_hours

    async def _refresh_market_data(self):
        """Refresh market trend data from various sources"""
        # Simulate market data refresh - in production, would call real APIs
        sample_trends = [
            MarketTrend(
                trend_id="cozy_mystery_2024",
                category="mystery",
                popularity_score=0.85,
                growth_rate=0.15,
                keywords=["cozy mystery", "amateur sleuth", "small town"],
                target_demographics=["women 35-65", "retirees"],
                seasonal_factors={"winter": 1.2, "summer": 0.9},
                competition_level="medium",
            ),
            MarketTrend(
                trend_id="ai_business_2024",
                category="business",
                popularity_score=0.92,
                growth_rate=0.35,
                keywords=["artificial intelligence", "AI automation", "business AI"],
                target_demographics=["entrepreneurs", "tech professionals"],
                seasonal_factors={"q1": 1.1, "q4": 1.3},
                competition_level="high",
            ),
            MarketTrend(
                trend_id="mindfulness_wellness_2024",
                category="self_help",
                popularity_score=0.78,
                growth_rate=0.08,
                keywords=["mindfulness", "wellness", "mental health"],
                target_demographics=["millennials", "gen_z"],
                seasonal_factors={"january": 1.4, "september": 1.2},
                competition_level="medium",
            ),
        ]

        self.trend_cache = {trend.trend_id: trend for trend in sample_trends}
        self.last_refresh = datetime.now()

        logger.info(f"Refreshed market data with {len(sample_trends)} trends")

    def _filter_trends_by_intent(self, intent_type: str) -> List[MarketTrend]:
        """Filter trends based on user intent"""
        if not self.trend_cache:
            return []

        # Map intents to relevant categories
        intent_categories = {
            "create_book": ["mystery", "romance", "fantasy", "self_help"],
            "market_optimize": ["business", "self_help", "mystery"],
            "explore_ideas": list(self.trend_cache.keys()),
            "set_vibe": ["romance", "fantasy", "mystery"],
        }

        relevant_categories = intent_categories.get(
            intent_type, list(self.trend_cache.keys())
        )

        # Filter and sort by popularity
        relevant_trends = [
            trend
            for trend in self.trend_cache.values()
            if trend.category in relevant_categories or intent_type in ["explore_ideas"]
        ]

        return sorted(relevant_trends, key=lambda t: t.popularity_score, reverse=True)[
            :5
        ]

    async def _generate_target_keywords(
        self, intent_type: str, user_preferences: Optional[Dict]
    ) -> List[str]:
        """Generate target keywords based on intent and preferences"""
        base_keywords = []

        # Add intent-based keywords
        intent_keywords = {
            "create_book": ["new release", "debut author", "indie book"],
            "market_optimize": ["bestseller", "trending", "popular"],
            "explore_ideas": ["creative", "innovative", "unique"],
            "set_vibe": ["atmospheric", "immersive", "engaging"],
        }

        base_keywords.extend(intent_keywords.get(intent_type, []))

        # Add preference-based keywords
        if user_preferences:
            genres = user_preferences.get("genre_preferences", [])
            for genre in genres:
                if hasattr(genre, "value"):
                    base_keywords.append(genre.value.replace("_", " "))

        return base_keywords[:15]  # Limit to top 15 keywords

    async def _analyze_competition(self, trends: List[MarketTrend]) -> Dict[str, any]:
        """Analyze competition for given trends"""
        competition_levels = {"low": 0, "medium": 0, "high": 0}

        for trend in trends:
            competition_levels[trend.competition_level] += 1

        # Calculate overall competition score
        total_trends = len(trends)
        if total_trends == 0:
            competition_score = 0.5
        else:
            competition_score = (
                competition_levels["low"] * 0.2
                + competition_levels["medium"] * 0.5
                + competition_levels["high"] * 0.9
            ) / total_trends

        return {
            "overall_competition_score": competition_score,
            "competition_breakdown": competition_levels,
            "recommended_strategy": self._get_competition_strategy(competition_score),
            "opportunity_gaps": self._identify_opportunity_gaps(trends),
        }

    def _get_competition_strategy(self, score: float) -> str:
        """Get recommended strategy based on competition score"""
        if score < 0.3:
            return "aggressive_entry"
        elif score < 0.6:
            return "differentiated_positioning"
        else:
            return "niche_specialization"

    def _identify_opportunity_gaps(self, trends: List[MarketTrend]) -> List[str]:
        """Identify gaps in the market based on trends"""
        gaps = []

        # Look for underserved categories
        represented_categories = {trend.category for trend in trends}
        all_categories = {
            "mystery",
            "romance",
            "fantasy",
            "business",
            "self_help",
            "science_fiction",
        }

        missing_categories = all_categories - represented_categories
        for category in missing_categories:
            gaps.append(f"underserved_{category}")

        # Look for demographic gaps
        all_demographics = set()
        for trend in trends:
            all_demographics.update(trend.target_demographics)

        if "gen_z" not in all_demographics:
            gaps.append("gen_z_gap")
        if "seniors" not in all_demographics:
            gaps.append("seniors_gap")

        return gaps

    async def _get_pricing_insights(self, trends: List[MarketTrend]) -> Dict[str, any]:
        """Get pricing insights for current trends"""
        # Simulate pricing analysis
        pricing_data = {
            "ebook_price_range": {"min": 2.99, "max": 9.99, "optimal": 4.99},
            "paperback_price_range": {"min": 8.99, "max": 16.99, "optimal": 12.99},
            "pricing_strategy": "value_positioning",
            "seasonal_adjustments": {
                "holiday_season": 0.9,  # 10% discount
                "back_to_school": 1.1,  # 10% premium
                "summer": 0.95,  # 5% discount
            },
        }

        return pricing_data

    async def _analyze_audience_preferences(
        self, trends: List[MarketTrend]
    ) -> Dict[str, any]:
        """Analyze audience preferences from trends"""
        all_demographics = []
        for trend in trends:
            all_demographics.extend(trend.target_demographics)

        # Count demographic frequency
        demo_counts = {}
        for demo in all_demographics:
            demo_counts[demo] = demo_counts.get(demo, 0) + 1

        # Get most common demographics
        primary_demographics = sorted(
            demo_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]

        return {
            "primary_demographics": [demo[0] for demo in primary_demographics],
            "demographic_distribution": demo_counts,
            "content_preferences": {
                "preferred_length": "medium",  # Based on trend analysis
                "preferred_style": "accessible",
                "popular_themes": [
                    "personal_growth",
                    "problem_solving",
                    "entertainment",
                ],
            },
        }

    async def _get_seasonal_opportunities(self) -> Dict[str, any]:
        """Get seasonal publishing opportunities"""
        current_month = datetime.now().month

        seasonal_calendar = {
            1: {"themes": ["new_year_resolutions", "fresh_start"], "boost": 1.3},
            2: {"themes": ["romance", "relationships"], "boost": 1.2},
            3: {"themes": ["spring_cleaning", "productivity"], "boost": 1.1},
            9: {"themes": ["back_to_school", "learning"], "boost": 1.2},
            10: {"themes": ["spooky", "mystery", "halloween"], "boost": 1.4},
            11: {"themes": ["gratitude", "family"], "boost": 1.1},
            12: {"themes": ["reflection", "planning", "holidays"], "boost": 1.3},
        }

        current_season = seasonal_calendar.get(
            current_month, {"themes": ["general"], "boost": 1.0}
        )

        return {
            "current_seasonal_themes": current_season["themes"],
            "seasonal_boost_factor": current_season["boost"],
            "upcoming_opportunities": self._get_upcoming_seasonal_themes(current_month),
        }

    def _get_upcoming_seasonal_themes(self, current_month: int) -> List[Dict[str, any]]:
        """Get upcoming seasonal themes for planning"""
        upcoming = []
        for i in range(1, 4):  # Next 3 months
            future_month = (current_month + i - 1) % 12 + 1
            month_name = datetime(2024, future_month, 1).strftime("%B")

            themes = {
                1: ["new_year_resolutions", "fresh_start"],
                2: ["romance", "relationships"],
                9: ["back_to_school", "learning"],
                10: ["spooky", "mystery"],
                12: ["reflection", "planning"],
            }.get(future_month, ["general"])

            upcoming.append(
                {"month": month_name, "themes": themes, "lead_time_weeks": i * 4}
            )

        return upcoming

    async def _get_platform_optimizations(self) -> Dict[str, any]:
        """Get platform-specific optimization recommendations"""
        return {
            "amazon_kdp": {
                "category_optimization": True,
                "keyword_density": "medium",
                "description_length": "detailed",
                "series_potential": True,
            },
            "social_media": {
                "instagram_visual": True,
                "tiktok_hooks": True,
                "twitter_threads": True,
                "linkedin_professional": False,
            },
            "email_marketing": {
                "launch_sequence": True,
                "reader_magnets": True,
                "cross_promotion": True,
            },
        }


class CreativeContextLibrary:
    """Library of creative patterns and writing structures"""

    def __init__(self):
        self.patterns = self._initialize_creative_patterns()

    async def match_patterns(self, voice_input: VoiceInput) -> CreativeContext:
        """Match creative patterns to voice input"""

        # Analyze voice input for creative indicators
        creative_indicators = self._extract_creative_indicators(voice_input)

        # Find matching patterns
        relevant_patterns = self._find_matching_patterns(creative_indicators)

        # Get genre conventions
        genre_conventions = self._get_genre_conventions(voice_input)

        # Get story structures
        story_structures = self._get_story_structures(voice_input)

        return CreativeContext(
            relevant_patterns=relevant_patterns,
            genre_conventions=genre_conventions,
            story_structures=story_structures,
            character_development=self._get_character_development_guidelines(),
            world_building=self._get_world_building_guidelines(),
            dialogue_patterns=self._get_dialogue_patterns(),
            narrative_techniques=self._get_narrative_techniques(),
            creative_constraints=self._get_creative_constraints(voice_input),
        )

    def _initialize_creative_patterns(self) -> List[CreativePattern]:
        """Initialize library of creative patterns"""
        patterns = []

        # Mystery pattern
        patterns.append(
            CreativePattern(
                pattern_id="cozy_mystery",
                name="Cozy Mystery",
                genre=BookGenre.MYSTERY,
                structure_template={
                    "setup": "Introduce sleuth and setting",
                    "inciting_incident": "Discovery of crime/mystery",
                    "investigation": "Clue gathering and red herrings",
                    "climax": "Revelation and confrontation",
                    "resolution": "Justice and restoration",
                },
                character_archetypes=[
                    "amateur_sleuth",
                    "quirky_sidekick",
                    "suspicious_locals",
                ],
                plot_devices=["red_herrings", "locked_room", "hidden_motive"],
                theme_elements=["justice", "community", "truth"],
                style_guidelines={
                    "tone": "light",
                    "violence": "minimal",
                    "setting": "small_community",
                },
                success_rate=0.75,
            )
        )

        # Romance pattern
        patterns.append(
            CreativePattern(
                pattern_id="enemies_to_lovers",
                name="Enemies to Lovers Romance",
                genre=BookGenre.ROMANCE,
                structure_template={
                    "meet_cute": "Antagonistic first meeting",
                    "forced_proximity": "Circumstances force interaction",
                    "growing_attraction": "Gradual softening and attraction",
                    "black_moment": "Misunderstanding or obstacle",
                    "resolution": "Love confession and HEA",
                },
                character_archetypes=[
                    "stubborn_protagonist",
                    "equally_matched_love_interest",
                ],
                plot_devices=["forced_proximity", "misunderstanding", "grand_gesture"],
                theme_elements=[
                    "love_conquers_all",
                    "personal_growth",
                    "vulnerability",
                ],
                style_guidelines={
                    "tone": "passionate",
                    "steam_level": "variable",
                    "pov": "dual",
                },
                success_rate=0.82,
            )
        )

        return patterns

    def _extract_creative_indicators(self, voice_input: VoiceInput) -> Dict[str, any]:
        """Extract creative indicators from voice input"""
        text = voice_input.text.lower()
        emotions = voice_input.emotions

        indicators = {
            "genre_hints": [],
            "mood_indicators": [],
            "structure_preferences": [],
            "character_types": [],
            "theme_interests": [],
        }

        # Genre detection
        genre_keywords = {
            "mystery": ["mystery", "solve", "clue", "detective", "crime"],
            "romance": ["love", "romance", "relationship", "heart"],
            "fantasy": ["magic", "dragon", "quest", "wizard"],
            "science_fiction": ["future", "space", "technology", "alien"],
        }

        for genre, keywords in genre_keywords.items():
            if any(keyword in text for keyword in keywords):
                indicators["genre_hints"].append(genre)

        # Mood indicators
        if emotions.mood.value in ["playful", "energetic"]:
            indicators["mood_indicators"].append("light_hearted")
        elif emotions.mood.value in ["serious", "contemplative"]:
            indicators["mood_indicators"].append("serious_tone")

        # Structure preferences
        if "quick" in text or "fast" in text:
            indicators["structure_preferences"].append("fast_paced")
        elif "slow" in text or "detailed" in text:
            indicators["structure_preferences"].append("slow_burn")

        return indicators

    def _find_matching_patterns(
        self, indicators: Dict[str, any]
    ) -> List[CreativePattern]:
        """Find patterns that match the creative indicators"""
        matching_patterns = []

        for pattern in self.patterns:
            match_score = 0

            # Check genre match
            if pattern.genre.value in indicators["genre_hints"]:
                match_score += 3

            # Check mood compatibility
            style_tone = pattern.style_guidelines.get("tone", "")
            if (
                "light" in style_tone
                and "light_hearted" in indicators["mood_indicators"]
            ) or (
                "serious" in style_tone
                and "serious_tone" in indicators["mood_indicators"]
            ):
                match_score += 2

            # Consider success rate
            if pattern.success_rate > 0.7:
                match_score += 1

            if match_score > 0:
                matching_patterns.append(pattern)

        # Sort by relevance and success rate
        return sorted(matching_patterns, key=lambda p: p.success_rate, reverse=True)[:3]

    def _get_genre_conventions(self, voice_input: VoiceInput) -> Dict[str, any]:
        """Get genre conventions based on voice input"""
        # Simplified genre conventions
        return {
            "mystery": {
                "required_elements": ["crime", "investigation", "resolution"],
                "optional_elements": ["red_herrings", "suspects", "clues"],
                "avoid": ["graphic_violence", "explicit_content"],
            },
            "romance": {
                "required_elements": [
                    "romantic_relationship",
                    "emotional_journey",
                    "hea_hfn",
                ],
                "optional_elements": ["steam", "secondary_romance", "found_family"],
                "avoid": ["cheating", "unresolved_ending"],
            },
        }

    def _get_story_structures(self, voice_input: VoiceInput) -> Dict[str, any]:
        """Get story structure templates"""
        return {
            "three_act": {
                "act1": "Setup and inciting incident (25%)",
                "act2": "Rising action and midpoint (50%)",
                "act3": "Climax and resolution (25%)",
            },
            "hero_journey": {
                "ordinary_world": "Character in normal situation",
                "call_to_adventure": "Challenge presented",
                "refusal": "Initial hesitation",
                "mentor": "Guidance received",
                "threshold": "Commitment to journey",
                "trials": "Obstacles and growth",
                "revelation": "Major discovery",
                "transformation": "Character changed",
                "return": "Back to world, transformed",
            },
        }

    def _get_character_development_guidelines(self) -> Dict[str, any]:
        """Get character development guidelines"""
        return {
            "protagonist_arc": {
                "flaw": "Character weakness to overcome",
                "want": "Surface-level goal",
                "need": "Deep emotional need",
                "ghost": "Past trauma or event",
                "lie": "False belief about self/world",
                "truth": "What they must learn",
            },
            "supporting_characters": {
                "love_interest": "Emotional counterpart",
                "mentor": "Wisdom provider",
                "antagonist": "Opposition force",
                "sidekick": "Loyal companion",
            },
        }

    def _get_world_building_guidelines(self) -> Dict[str, any]:
        """Get world building guidelines"""
        return {
            "contemporary": {
                "research_requirements": ["location", "culture", "current_events"],
                "authenticity_checks": ["local_customs", "dialect", "landmarks"],
            },
            "fantasy": {
                "magic_system": ["rules", "limitations", "costs"],
                "world_elements": ["geography", "politics", "cultures", "history"],
            },
            "historical": {
                "period_research": ["technology", "social_norms", "language"],
                "accuracy_requirements": ["historical_events", "period_details"],
            },
        }

    def _get_dialogue_patterns(self) -> Dict[str, any]:
        """Get dialogue writing patterns"""
        return {
            "natural_speech": {
                "contractions": "Use contractions for realism",
                "interruptions": "Characters interrupt naturally",
                "subtext": "Characters don't always say what they mean",
            },
            "character_voice": {
                "vocabulary": "Match education and background",
                "speech_patterns": "Unique rhythms and phrases",
                "emotional_state": "Dialogue reflects feelings",
            },
        }

    def _get_narrative_techniques(self) -> List[str]:
        """Get narrative technique options"""
        return [
            "show_dont_tell",
            "sensory_details",
            "internal_monologue",
            "dialogue_tags",
            "scene_transitions",
            "pacing_variation",
            "point_of_view_consistency",
            "active_voice",
        ]

    def _get_creative_constraints(self, voice_input: VoiceInput) -> Dict[str, any]:
        """Get creative constraints based on voice input"""
        return {
            "word_count": {"min": 50000, "max": 90000, "target": 70000},
            "chapter_structure": {"chapters": 15, "avg_length": 4000},
            "pov_constraints": {"maximum_povs": 2, "recommended": "single"},
            "timeline": {"complexity": "linear", "flashbacks": "minimal"},
            "content_rating": {
                "level": "pg13",
                "restrictions": ["minimal_violence", "fade_to_black"],
            },
        }


class PublishingContextEngine:
    """Engine for publishing context and optimization"""

    async def optimize_for_platforms(self, intent_type: str) -> PublishingContext:
        """Optimize context for target publishing platforms"""

        # Get target formats based on intent
        target_formats = self._get_target_formats(intent_type)

        # Get platform requirements
        platform_requirements = self._get_platform_requirements()

        # Get SEO optimizations
        seo_optimizations = self._get_seo_optimizations()

        # Get metadata templates
        metadata_templates = self._get_metadata_templates()

        # Get quality standards
        quality_standards = self._get_quality_standards()

        return PublishingContext(
            target_formats=target_formats,
            platform_requirements=platform_requirements,
            seo_optimizations=seo_optimizations,
            metadata_templates=metadata_templates,
            quality_standards=quality_standards,
            distribution_strategies=self._get_distribution_strategies(),
            monetization_options=self._get_monetization_options(),
        )

    def _get_target_formats(self, intent_type: str) -> List[PublishingFormat]:
        """Get target publishing formats based on intent"""
        formats = []

        # Ebook format (always included)
        formats.append(
            PublishingFormat(
                format_type="ebook",
                platform="amazon_kdp",
                specifications={
                    "file_format": "epub",
                    "max_file_size": "50MB",
                    "image_resolution": "300dpi",
                    "font_requirements": "readable",
                },
                optimization_rules={
                    "toc_required": True,
                    "chapter_breaks": True,
                    "image_optimization": True,
                },
                quality_requirements={
                    "grammar_score": 0.95,
                    "formatting_score": 0.9,
                    "readability_score": 0.8,
                },
            )
        )

        # Add paperback for certain intents
        if intent_type in ["create_book", "market_optimize"]:
            formats.append(
                PublishingFormat(
                    format_type="paperback",
                    platform="amazon_kdp",
                    specifications={
                        "trim_size": "6x9",
                        "paper_type": "white",
                        "cover_finish": "matte",
                        "spine_width": "calculated",
                    },
                    optimization_rules={
                        "margin_requirements": True,
                        "page_numbering": True,
                        "chapter_starts": "right_page",
                    },
                    quality_requirements={
                        "print_resolution": "300dpi",
                        "text_clarity": 0.95,
                        "cover_quality": 0.9,
                    },
                )
            )

        return formats

    def _get_platform_requirements(self) -> Dict[str, any]:
        """Get platform-specific requirements"""
        return {
            "amazon_kdp": {
                "content_guidelines": {
                    "no_illegal_content": True,
                    "no_copyright_violation": True,
                    "quality_standards": True,
                },
                "metadata_requirements": {
                    "title": "required",
                    "description": "required",
                    "categories": "2_max",
                    "keywords": "7_max",
                },
                "pricing_constraints": {
                    "min_ebook_price": 0.99,
                    "max_ebook_price": 200.00,
                    "royalty_tiers": ["35%", "70%"],
                },
            }
        }

    def _get_seo_optimizations(self) -> Dict[str, any]:
        """Get SEO optimization guidelines"""
        return {
            "title_optimization": {
                "length": "60_chars_max",
                "keyword_placement": "front_loaded",
                "subtitle_strategy": "benefit_focused",
            },
            "description_optimization": {
                "hook_first_line": True,
                "benefits_focused": True,
                "call_to_action": True,
                "keyword_density": "natural",
            },
            "category_selection": {
                "primary_category": "highest_relevance",
                "secondary_category": "lower_competition",
                "avoid_oversaturated": True,
            },
            "keyword_strategy": {
                "long_tail_keywords": True,
                "competitor_analysis": True,
                "seasonal_keywords": True,
            },
        }

    def _get_metadata_templates(self) -> Dict[str, any]:
        """Get metadata templates for different genres"""
        return {
            "mystery": {
                "title_pattern": "[Compelling Hook] - A [Setting] Mystery",
                "description_template": "When [protagonist] discovers [inciting incident], they must [main challenge] before [stakes]. But with [obstacles] and [red herrings], can they [resolution goal]?",
                "categories": ["Mystery & Suspense", "Cozy Mystery"],
                "keywords": ["amateur sleuth", "small town mystery", "cozy crime"],
            },
            "romance": {
                "title_pattern": "[Emotional Hook] - A [Subgenre] Romance",
                "description_template": "[Protagonist] never expected [meet cute situation]. But when [conflict arises], they must choose between [internal conflict] and [love]. Will [stakes] keep them apart, or will love [resolution]?",
                "categories": ["Romance", "Contemporary Romance"],
                "keywords": [
                    "enemies to lovers",
                    "second chance",
                    "small town romance",
                ],
            },
        }

    def _get_quality_standards(self) -> Dict[str, any]:
        """Get quality standards for publishing"""
        return {
            "content_quality": {
                "grammar_accuracy": 0.95,
                "spelling_accuracy": 0.98,
                "readability_score": 0.8,
                "consistency_score": 0.9,
            },
            "formatting_quality": {
                "consistent_styling": True,
                "proper_headings": True,
                "clean_layout": True,
                "mobile_friendly": True,
            },
            "cover_quality": {
                "genre_appropriate": True,
                "thumbnail_readable": True,
                "professional_design": True,
                "brand_consistent": True,
            },
        }

    def _get_distribution_strategies(self) -> Dict[str, any]:
        """Get distribution strategies"""
        return {
            "exclusive_kdp": {
                "benefits": ["kdp_select", "kindle_unlimited", "higher_royalties"],
                "restrictions": ["amazon_only"],
                "recommended_for": ["new_authors", "series_books"],
            },
            "wide_distribution": {
                "platforms": ["amazon", "apple", "kobo", "barnes_noble"],
                "benefits": ["broader_reach", "diversified_income"],
                "recommended_for": ["established_authors", "standalone_books"],
            },
        }

    def _get_monetization_options(self) -> Dict[str, any]:
        """Get monetization options"""
        return {
            "direct_sales": {
                "ebook_pricing": {"min": 2.99, "max": 9.99, "sweet_spot": 4.99},
                "paperback_pricing": {"min": 8.99, "max": 16.99, "sweet_spot": 12.99},
            },
            "subscription_models": {
                "kindle_unlimited": "page_reads",
                "author_newsletter": "reader_magnets",
            },
            "additional_revenue": {
                "audiobook": "narrator_partnership",
                "merchandise": "character_based",
                "courses": "writing_expertise",
            },
        }


class ContextSynthesisEngine:
    """Main engine for synthesizing multiple context layers"""

    def __init__(self):
        self.author_builder = AuthorContextBuilder()
        self.market_analyzer = MarketContextAnalyzer()
        self.creative_library = CreativeContextLibrary()
        self.publishing_engine = PublishingContextEngine()
        self.memory_store = ContextMemoryStore()
        self.logger = logging.getLogger(__name__)

    async def synthesize_context(
        self, user_id: str, voice_input: VoiceInput
    ) -> SynthesizedContext:
        """Synthesize comprehensive context from all layers"""

        try:
            session_id = voice_input.session_id

            # Build contexts in parallel for performance
            context_tasks = [
                self.author_builder.build_context(user_id, voice_input),
                self.market_analyzer.get_relevant_context(voice_input.intent.value),
                self.creative_library.match_patterns(voice_input),
                self.publishing_engine.optimize_for_platforms(voice_input.intent.value),
            ]

            author_ctx, market_ctx, creative_ctx, publishing_ctx = await asyncio.gather(
                *context_tasks
            )

            # Calculate synthesis weights based on intent and context
            synthesis_weights = self._calculate_synthesis_weights(
                voice_input, author_ctx
            )

            # Create synthesized context
            synthesized_context = SynthesizedContext(
                session_id=session_id,
                author=author_ctx,
                market=market_ctx,
                creative=creative_ctx,
                publishing=publishing_ctx,
                synthesis_weights=synthesis_weights,
                synthesis_timestamp=datetime.now(),
            )

            # Calculate quality and coherence scores
            synthesized_context.quality_score = await self._calculate_quality_score(
                synthesized_context
            )
            synthesized_context.coherence_score = await self._calculate_coherence_score(
                synthesized_context
            )

            # Generate optimization suggestions
            synthesized_context.optimization_suggestions = (
                await self._generate_optimization_suggestions(synthesized_context)
            )

            # Store synthesis for future reference
            await self._store_synthesis_record(synthesized_context)

            self.logger.info(
                f"Synthesized context for user {user_id} with quality score {synthesized_context.quality_score:.2f}"
            )

            return synthesized_context

        except Exception as e:
            self.logger.error(f"Failed to synthesize context for user {user_id}: {e}")
            # Return minimal context on error
            basic_author_ctx = AuthorContext(user_id=user_id)
            return SynthesizedContext(
                session_id=voice_input.session_id,
                author=basic_author_ctx,
                market=MarketContext(),
                creative=CreativeContext(),
                publishing=PublishingContext(),
            )

    def _calculate_synthesis_weights(
        self, voice_input: VoiceInput, author_ctx: AuthorContext
    ) -> ContextSynthesisWeights:
        """Calculate attention weights for context synthesis"""

        weights = ContextSynthesisWeights()

        # Adjust weights based on user intent
        if voice_input.intent.value == "market_optimize":
            weights.market_weight = 0.4
            weights.author_weight = 0.3
            weights.publishing_weight = 0.2
            weights.creative_weight = 0.1
        elif voice_input.intent.value == "create_book":
            weights.creative_weight = 0.4
            weights.author_weight = 0.35
            weights.market_weight = 0.15
            weights.publishing_weight = 0.1
        elif voice_input.intent.value == "publish_book":
            weights.publishing_weight = 0.4
            weights.market_weight = 0.3
            weights.author_weight = 0.2
            weights.creative_weight = 0.1

        # Adjust based on user experience level
        if author_ctx.total_sessions < 5:  # New user
            weights.author_weight *= 1.2  # Focus more on learning user preferences
            weights.creative_weight *= 1.1  # Provide more creative guidance
        elif author_ctx.total_sessions > 20:  # Experienced user
            weights.market_weight *= 1.1  # Focus more on optimization
            weights.publishing_weight *= 1.1

        # Normalize weights
        weights.normalize()

        return weights

    async def _calculate_quality_score(self, context: SynthesizedContext) -> float:
        """Calculate overall quality score of the synthesized context"""

        quality_factors = []

        # Author context quality
        author_completeness = self._assess_author_completeness(context.author)
        quality_factors.append(
            author_completeness * context.synthesis_weights.author_weight
        )

        # Market context quality
        market_relevance = self._assess_market_relevance(context.market)
        quality_factors.append(
            market_relevance * context.synthesis_weights.market_weight
        )

        # Creative context quality
        creative_richness = self._assess_creative_richness(context.creative)
        quality_factors.append(
            creative_richness * context.synthesis_weights.creative_weight
        )

        # Publishing context quality
        publishing_readiness = self._assess_publishing_readiness(context.publishing)
        quality_factors.append(
            publishing_readiness * context.synthesis_weights.publishing_weight
        )

        return sum(quality_factors)

    def _assess_author_completeness(self, author_ctx: AuthorContext) -> float:
        """Assess completeness of author context"""
        completeness_score = 0.0

        # Check writing style completeness
        if author_ctx.writing_style.tone != "conversational":  # Non-default
            completeness_score += 0.2
        if author_ctx.writing_style.genre_preferences:
            completeness_score += 0.2
        if author_ctx.writing_style.favorite_themes:
            completeness_score += 0.1

        # Check preferences completeness
        if author_ctx.preferences.publishing_goals:
            completeness_score += 0.2
        if author_ctx.preferences.target_audience != "general":  # Non-default
            completeness_score += 0.1

        # Check experience level
        if author_ctx.total_sessions > 0:
            completeness_score += 0.1
        if author_ctx.past_works:
            completeness_score += 0.1

        return min(completeness_score, 1.0)

    def _assess_market_relevance(self, market_ctx: MarketContext) -> float:
        """Assess relevance of market context"""
        relevance_score = 0.0

        if market_ctx.current_trends:
            relevance_score += 0.3
        if market_ctx.target_keywords:
            relevance_score += 0.2
        if market_ctx.competition_analysis:
            relevance_score += 0.2
        if market_ctx.audience_preferences:
            relevance_score += 0.2
        if market_ctx.seasonal_opportunities:
            relevance_score += 0.1

        return min(relevance_score, 1.0)

    def _assess_creative_richness(self, creative_ctx: CreativeContext) -> float:
        """Assess richness of creative context"""
        richness_score = 0.0

        if creative_ctx.relevant_patterns:
            richness_score += 0.4
        if creative_ctx.genre_conventions:
            richness_score += 0.2
        if creative_ctx.story_structures:
            richness_score += 0.2
        if creative_ctx.narrative_techniques:
            richness_score += 0.1
        if creative_ctx.creative_constraints:
            richness_score += 0.1

        return min(richness_score, 1.0)

    def _assess_publishing_readiness(self, publishing_ctx: PublishingContext) -> float:
        """Assess publishing readiness"""
        readiness_score = 0.0

        if publishing_ctx.target_formats:
            readiness_score += 0.3
        if publishing_ctx.quality_standards:
            readiness_score += 0.2
        if publishing_ctx.seo_optimizations:
            readiness_score += 0.2
        if publishing_ctx.metadata_templates:
            readiness_score += 0.2
        if publishing_ctx.distribution_strategies:
            readiness_score += 0.1

        return min(readiness_score, 1.0)

    async def _calculate_coherence_score(self, context: SynthesizedContext) -> float:
        """Calculate coherence between different context layers"""

        coherence_factors = []

        # Check author-creative coherence
        author_creative_coherence = self._check_author_creative_coherence(
            context.author, context.creative
        )
        coherence_factors.append(author_creative_coherence)

        # Check market-publishing coherence
        market_publishing_coherence = self._check_market_publishing_coherence(
            context.market, context.publishing
        )
        coherence_factors.append(market_publishing_coherence)

        # Check author-market coherence
        author_market_coherence = self._check_author_market_coherence(
            context.author, context.market
        )
        coherence_factors.append(author_market_coherence)

        return (
            sum(coherence_factors) / len(coherence_factors)
            if coherence_factors
            else 0.0
        )

    def _check_author_creative_coherence(
        self, author_ctx: AuthorContext, creative_ctx: CreativeContext
    ) -> float:
        """Check coherence between author preferences and creative patterns"""
        coherence = 0.5  # Base coherence

        # Check genre alignment
        author_genres = {g.value for g in author_ctx.writing_style.genre_preferences}
        pattern_genres = {p.genre.value for p in creative_ctx.relevant_patterns}

        if author_genres.intersection(pattern_genres):
            coherence += 0.3

        # Check style alignment
        for pattern in creative_ctx.relevant_patterns:
            pattern_tone = pattern.style_guidelines.get("tone", "")
            if pattern_tone == author_ctx.writing_style.tone:
                coherence += 0.2
                break

        return min(coherence, 1.0)

    def _check_market_publishing_coherence(
        self, market_ctx: MarketContext, publishing_ctx: PublishingContext
    ) -> float:
        """Check coherence between market insights and publishing strategy"""
        coherence = 0.5  # Base coherence

        # Check if publishing formats align with market trends
        if market_ctx.current_trends and publishing_ctx.target_formats:
            coherence += 0.3

        # Check if pricing aligns with market insights
        if market_ctx.pricing_insights and publishing_ctx.monetization_options:
            coherence += 0.2

        return min(coherence, 1.0)

    def _check_author_market_coherence(
        self, author_ctx: AuthorContext, market_ctx: MarketContext
    ) -> float:
        """Check coherence between author goals and market opportunities"""
        coherence = 0.5  # Base coherence

        # Check if author's publishing goals align with market opportunities
        author_goals = set(author_ctx.preferences.publishing_goals)

        if "bestseller" in author_goals and market_ctx.current_trends:
            # Check if author is targeting trending genres
            trending_categories = {
                trend.category for trend in market_ctx.current_trends
            }
            author_genre_names = {
                g.value.replace("_", " ")
                for g in author_ctx.writing_style.genre_preferences
            }

            if trending_categories.intersection(author_genre_names):
                coherence += 0.3

        if "passive_income" in author_goals and market_ctx.audience_preferences:
            coherence += 0.2

        return min(coherence, 1.0)

    async def _generate_optimization_suggestions(
        self, context: SynthesizedContext
    ) -> List[str]:
        """Generate optimization suggestions based on context analysis"""
        suggestions = []

        # Quality-based suggestions
        if context.quality_score < 0.7:
            suggestions.append(
                "Consider providing more information about your writing preferences to improve personalization"
            )

        # Coherence-based suggestions
        if context.coherence_score < 0.6:
            suggestions.append(
                "Your creative preferences and market targets could be better aligned for success"
            )

        # Author context suggestions
        if context.author.total_sessions < 3:
            suggestions.append(
                "Continue using the system to build a more complete author profile"
            )

        # Market context suggestions
        if not context.market.current_trends:
            suggestions.append(
                "Consider market research to identify trending topics in your genre"
            )

        # Creative context suggestions
        if not context.creative.relevant_patterns:
            suggestions.append(
                "Explore different creative patterns to find your unique voice"
            )

        # Publishing context suggestions
        if len(context.publishing.target_formats) < 2:
            suggestions.append("Consider multiple publishing formats to maximize reach")

        return suggestions[:5]  # Limit to top 5 suggestions

    async def _store_synthesis_record(self, context: SynthesizedContext):
        """Store synthesis record for analysis and improvement"""
        try:
            synthesis_data = {
                "session_id": context.session_id,
                "quality_score": context.quality_score,
                "coherence_score": context.coherence_score,
                "synthesis_weights": {
                    "author": context.synthesis_weights.author_weight,
                    "market": context.synthesis_weights.market_weight,
                    "creative": context.synthesis_weights.creative_weight,
                    "publishing": context.synthesis_weights.publishing_weight,
                },
                "optimization_suggestions": context.optimization_suggestions,
            }

            # Store in memory store for analysis
            await self.memory_store.store_success_metric(
                user_id=context.author.user_id,
                session_id=context.session_id,
                metric_type="context_synthesis",
                metric_data=synthesis_data,
            )

        except Exception as e:
            self.logger.error(f"Failed to store synthesis record: {e}")
