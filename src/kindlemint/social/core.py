"""
Core Social Media Marketing Engine

Comprehensive implementation of the Social Media Marketing Podcast Integration
strategy for transforming books into content marketing ecosystems.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List


class ContentType(Enum):
    """Types of atomic content that can be extracted"""

    QUOTE = "quote"
    TIP = "tip"
    STATISTIC = "statistic"
    STORY = "story"
    FRAMEWORK = "framework"
    QUESTION = "question"


class PlatformType(Enum):
    """Supported social media platforms"""

    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


@dataclass
class AtomicContent:
    """Single piece of atomic content extracted from a book"""

    content_type: ContentType
    text: str
    context: str
    chapter: str
    keywords: List[str] = field(default_factory=list)
    hashtags: List[str] = field(default_factory=list)
    engagement_score: float = 0.0
    platform_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizedPost:
    """Platform-optimized social media post"""

    platform: PlatformType
    content: str
    hashtags: List[str]
    call_to_action: str
    estimated_reach: int = 0
    best_time_to_post: str = "9:00 AM"


class ContentAtomizer:
    """
    Breaks down book content into social media-ready atomic pieces.

    Extracts quotes, tips, statistics, stories, frameworks, and questions
    from book content and optimizes them for maximum engagement.
    """

    def __init__(self):


def __init__(self):
        self.extraction_patterns = {
            ContentType.QUOTE: [r'"([^"]+)"', r'"([^"]+)"'],
            ContentType.TIP: [r"(?:Tip|Advice|Pro tip):\s*(.+?)(?:\.|$)"],
            ContentType.STATISTIC: [r"(\d+(?:\.\d+)?%)\s+(?:of|are|have|show)"],
            ContentType.FRAMEWORK: [
                r"(?:The|This)\s+(\w+\s+(?:Framework|Model|System))"
            ],
            ContentType.QUESTION: [r"(.+\?)"],
        }

    def atomize_book(self, book_content: Dict[str, str]) -> List[AtomicContent]:
        """Extract atomic content pieces from entire book"""
        atomic_pieces = []

        for chapter, content in book_content.items():
            for content_type, patterns in self.extraction_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(
                        pattern, content, re.MULTILINE | re.IGNORECASE
                    )
                    for match in matches:
                        text = match.group(1) if match.groups() else match.group(0)
                        if len(text.split()) >= 5:  # Minimum 5 words
                            atomic_pieces.append(
                                AtomicContent(
                                    content_type=content_type,
                                    text=text.strip(),
                                    context=content[
                                        max(0, match.start() - 100) : match.end() + 100
                                    ],
                                    chapter=chapter,
                                    keywords=self._extract_keywords(text),
                                    hashtags=self._generate_hashtags(content_type),
                                    engagement_score=self._calculate_engagement_score(
                                        text, content_type
                                    ),
                                )
                            )

        return sorted(atomic_pieces, key=lambda x: x.engagement_score, reverse=True)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        words = re.findall(r"\b\w{4,}\b", text.lower())
        return list(set(words))[:5]  # Top 5 unique keywords

    def _generate_hashtags(self, content_type: ContentType) -> List[str]:
        """Generate hashtags based on content type"""
        hashtag_map = {
            ContentType.TIP: ["#tips", "#advice", "#growth"],
            ContentType.QUOTE: ["#quotes", "#inspiration", "#wisdom"],
            ContentType.STATISTIC: ["#data", "#facts", "#research"],
            ContentType.FRAMEWORK: ["#framework", "#strategy", "#methodology"],
            ContentType.STORY: ["#story", "#experience", "#journey"],
            ContentType.QUESTION: ["#question", "#discuss", "#thoughts"],
        }
        return hashtag_map.get(content_type, ["#business", "#success"])

    def _calculate_engagement_score(
        self, text: str, content_type: ContentType
    ) -> float:
        """Calculate engagement potential score"""
        base_scores = {
            ContentType.STATISTIC: 0.9,
            ContentType.FRAMEWORK: 0.85,
            ContentType.TIP: 0.8,
            ContentType.QUOTE: 0.75,
            ContentType.STORY: 0.7,
            ContentType.QUESTION: 0.65,
        }

        score = base_scores.get(content_type, 0.5)

        # Adjust for length (optimal: 10-30 words)
        word_count = len(text.split())
        if 10 <= word_count <= 30:
            score += 0.1
        elif word_count < 5 or word_count > 50:
            score -= 0.1

        # Boost for power words
        power_words = ["proven", "secret", "breakthrough", "transform", "ultimate"]
        if any(word in text.lower() for word in power_words):
            score += 0.05

        return min(score, 1.0)


class PlatformOptimizer:
    """Optimizes content for specific social media platforms"""

    def __init__(self):
def __init__(self, platform: PlatformType):
        self.platform = platform
        self.optimization_rules = self._get_platform_rules()

    def _get_platform_rules(self) -> Dict[str, any]:
        """Get platform-specific optimization rules"""
        rules = {
            PlatformType.LINKEDIN: {
                "max_length": 3000,
                "tone": "professional",
                "hashtag_limit": 5,
                "best_times": ["8:00 AM", "12:00 PM", "5:00 PM"],
            },
            PlatformType.TWITTER: {
                "max_length": 280,
                "tone": "conversational",
                "hashtag_limit": 3,
                "best_times": ["9:00 AM", "3:00 PM", "8:00 PM"],
            },
            PlatformType.INSTAGRAM: {
                "max_length": 2200,
                "tone": "visual",
                "hashtag_limit": 30,
                "best_times": ["11:00 AM", "2:00 PM", "7:00 PM"],
            },
        }
        return rules.get(self.platform, rules[PlatformType.LINKEDIN])

    def optimize(self, atomic_content: AtomicContent) -> OptimizedPost:
        """Transform atomic content into platform-optimized post"""

        # Format content based on platform
        formatted_content = self._format_content(atomic_content)

        # Optimize hashtags
        optimized_hashtags = atomic_content.hashtags[
            : self.optimization_rules["hashtag_limit"]
        ]

        # Generate platform-specific CTA
        cta = self._generate_cta(atomic_content.content_type)

        # Calculate estimated reach
        reach = self._estimate_reach(atomic_content.engagement_score)

        return OptimizedPost(
            platform=self.platform,
            content=formatted_content,
            hashtags=optimized_hashtags,
            call_to_action=cta,
            estimated_reach=reach,
            best_time_to_post=self.optimization_rules["best_times"][0],
        )

    def _format_content(self, atomic_content: AtomicContent) -> str:
        """Format content for the platform"""
        text = atomic_content.text
        max_length = self.optimization_rules["max_length"]

        if self.platform == PlatformType.LINKEDIN:
            return f"💡 Insight:\n\n{text}\n\nWhat's your experience with this?"
        elif self.platform == PlatformType.TWITTER:
            return f"🔥 {text[:200]}..." if len(text) > 200 else f"🔥 {text}"
        elif self.platform == PlatformType.INSTAGRAM:
            return f"✨ {text}\n\n💫 Save this post for later!"
        else:
            return text[:max_length]

    def _generate_cta(self, content_type: ContentType) -> str:
        """Generate call-to-action based on content type"""
        cta_map = {
            ContentType.TIP: "What's your experience with this approach?",
            ContentType.QUOTE: "Does this resonate with you?",
            ContentType.STATISTIC: "What do you think about these numbers?",
            ContentType.FRAMEWORK: "Have you tried this methodology?",
            ContentType.STORY: "Can you relate to this experience?",
            ContentType.QUESTION: "Share your thoughts in the comments!",
        }
        return cta_map.get(content_type, "What are your thoughts?")

    def _estimate_reach(self, engagement_score: float) -> int:
        """Estimate post reach based on engagement score"""
        base_reach = {
            PlatformType.LINKEDIN: 1000,
            PlatformType.TWITTER: 500,
            PlatformType.INSTAGRAM: 800,
            PlatformType.FACEBOOK: 400,
            PlatformType.TIKTOK: 1500,
            PlatformType.YOUTUBE: 600,
        }

        return int(base_reach.get(self.platform, 500) * engagement_score)


class SocialMediaMarketing:
    """
    Main orchestrator for the Social Media Marketing system

    Combines content atomization, platform optimization, authority building,
    community engagement, lead generation, and analytics into a unified system.
    """

    def __init__(self):
def __init__(self, author_name: str, expertise_area: str):
        self.author_name = author_name
        self.expertise_area = expertise_area
        self.atomizer = ContentAtomizer()
        self.optimizers = {
            platform: PlatformOptimizer(platform) for platform in PlatformType
        }
        self.content_library: List[AtomicContent] = []
        self.optimized_posts: List[OptimizedPost] = []

    def process_book(
        self, book_content: Dict[str, str], target_platforms: List[PlatformType]
    ) -> Dict[str, any]:
        """Complete book-to-social-media transformation pipeline"""

        # Step 1: Atomize content
        self.content_library = self.atomizer.atomize_book(book_content)

        # Step 2: Optimize for each platform
        self.optimized_posts = []
        for atomic_content in self.content_library[:50]:  # Top 50 pieces
            for platform in target_platforms:
                optimizer = self.optimizers[platform]
                optimized_post = optimizer.optimize(atomic_content)
                self.optimized_posts.append(optimized_post)

        # Step 3: Generate content calendar
        content_calendar = self._create_content_calendar()

        # Step 4: Authority building recommendations
        authority_actions = self._generate_authority_actions()

        return {
            "total_atomic_pieces": len(self.content_library),
            "optimized_posts": len(self.optimized_posts),
            "content_calendar": content_calendar,
            "authority_actions": authority_actions,
            "estimated_total_reach": sum(
                post.estimated_reach for post in self.optimized_posts
            ),
            "top_content": self._get_top_content(10),
        }

    def _create_content_calendar(self, days: int = 30) -> Dict[str, List[Dict]]:
        """Create 30-day content publishing calendar"""
        calendar = {}
        posts_per_day = max(1, len(self.optimized_posts) // days)

        for day in range(days):
            date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
            start_idx = day * posts_per_day
            end_idx = start_idx + posts_per_day

            daily_posts = []
            for post in self.optimized_posts[start_idx:end_idx]:
                daily_posts.append(
                    {
                        "platform": post.platform.value,
                        "content": post.content[:100] + "...",
                        "scheduled_time": post.best_time_to_post,
                        "hashtags": post.hashtags,
                        "estimated_reach": post.estimated_reach,
                    }
                )

            calendar[date] = daily_posts

        return calendar

    def _generate_authority_actions(self) -> List[Dict[str, str]]:
        """Generate authority building action plan"""
        actions = [
            {
                "action": "Share contrarian viewpoint",
                "description": f"Present unique perspective on {self.expertise_area}",
                "frequency": "Weekly",
                "platform": "LinkedIn",
            },
            {
                "action": "Publish case study",
                "description": "Share detailed success story with metrics",
                "frequency": "Bi-weekly",
                "platform": "LinkedIn",
            },
            {
                "action": "Engage with industry leaders",
                "description": "Comment thoughtfully on influencer posts",
                "frequency": "Daily",
                "platform": "All platforms",
            },
            {
                "action": "Host Q&A session",
                "description": "Answer audience questions live",
                "frequency": "Monthly",
                "platform": "Instagram/LinkedIn",
            },
        ]
        return actions

    def _get_top_content(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get top-performing content pieces"""
        top_content = []
        for content in self.content_library[:limit]:
            top_content.append(
                {
                    "type": content.content_type.value,
                    "text": content.text[:100] + "...",
                    "engagement_score": content.engagement_score,
                    "keywords": content.keywords[:3],
                    "chapter": content.chapter,
                }
            )
        return top_content

    def export_results(self, filename: str) -> None:
        """Export complete results to JSON file"""
        data = {
            "author": self.author_name,
            "expertise_area": self.expertise_area,
            "processing_date": datetime.now().isoformat(),
            "content_library": [
                {
                    "type": content.content_type.value,
                    "text": content.text,
                    "engagement_score": content.engagement_score,
                    "keywords": content.keywords,
                    "hashtags": content.hashtags,
                }
                for content in self.content_library
            ],
            "optimized_posts": [
                {
                    "platform": post.platform.value,
                    "content": post.content,
                    "hashtags": post.hashtags,
                    "cta": post.call_to_action,
                    "estimated_reach": post.estimated_reach,
                    "best_time": post.best_time_to_post,
                }
                for post in self.optimized_posts
            ],
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    """Demo Social Media Marketing"""
def demo_social_media_marketing():
    """Demonstration of the Social Media Marketing system"""

    # Sample book content
    sample_book = {
        "Chapter 1: Introduction": """
        Here's a powerful tip: Always start with your customer's biggest pain point.
        Studies show that 73% of successful businesses focus on solving one problem really well.
        "The key to success is simplicity," said Steve Jobs. What if I told you that
        most entrepreneurs overcomplicate everything? The secret framework I use is called
        the Problem-Solution-Market fit model.
        """,
        "Chapter 2: Strategy": """
        Let me share a story about a client who increased revenue by 300% in 6 months.
        The breakthrough came when they realized that customer retention is 5x more
        profitable than acquisition. Here's the question every business owner should ask:
        What would happen if we delighted every single customer?
        """,
    }

    # Initialize the system
    marketing_system = SocialMediaMarketing(
        author_name="John Expert", expertise_area="Business Growth"
    )

    # Process the book
    target_platforms = [
        PlatformType.LINKEDIN,
        PlatformType.TWITTER,
        PlatformType.INSTAGRAM,
    ]
    results = marketing_system.process_book(sample_book, target_platforms)

    # Print results
    print("📚 Social Media Marketing Results:")
    print(f"• Total atomic pieces extracted: {results['total_atomic_pieces']}")
    print(f"• Optimized posts created: {results['optimized_posts']}")
    print(f"• Estimated total reach: {results['estimated_total_reach']:,}")
    print(f"• Authority actions planned: {len(results['authority_actions'])}")

    print("\n🔥 Top Content:")
    for i, content in enumerate(results["top_content"][:3], 1):
        print(f"{i}. [{content['type'].upper()}] {content['text']}")
        print(f"   Score: {content['engagement_score']:.2f}")

    print("\n📅 Sample Content Calendar (Next 3 Days):")
    calendar = results["content_calendar"]
    for date in list(calendar.keys())[:3]:
        print(f"\n{date}:")
        for post in calendar[date][:2]:  # Show 2 posts per day
            print(f"  • {post['platform']}: {post['content']}")
            print(
                f"    Time: {post['scheduled_time']}, Reach: {post['estimated_reach']}"
            )

    print("\n🎯 Authority Building Actions:")
    for action in results["authority_actions"][:3]:
        print(f"• {action['action']} ({action['frequency']}) - {action['platform']}")
        print(f"  {action['description']}")

    # Export results
    marketing_system.export_results("social_media_marketing_results.json")
    print("\n✅ Complete results exported to social_media_marketing_results.json")

    return results


if __name__ == "__main__":
    demo_social_media_marketing()
