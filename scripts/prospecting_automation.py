#!/usr/bin/env python3
"""
Prospecting Automation Module for KindleMint Engine
Implements Jeb Blount's Sales Gravy methodology for systematic book prospecting
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ProspectingAutomation:
    """
    Implements Jeb Blount's Fanatical Publishing System
    Automates content extraction and prospecting material generation
    """

        """  Init  """
def __init__(self, book_config: Dict, book_artifacts: Dict):
        """Initialize prospecting automation with book data"""
        self.book_config = book_config
        self.book_artifacts = book_artifacts
        self.series_name = book_config.get("series_name", "Default_Series")
        self.volume = book_config.get("volume", 1)
        self.title = book_config.get(
            "title", f"{self.series_name} Volume {self.volume}"
        )
        self.author = book_config.get("author", "Crossword Masters Publishing")

        # Create prospecting output directory
        self.output_dir = Path(
            f"books/active_production/{self.series_name}/volume_{self.volume}/prospecting"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OpenAI if available
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.openai_client = openai

    def generate_prospecting_materials(self) -> Dict:
        """
        Generate all prospecting materials following Blount's methodology
        Returns dictionary of created assets
        """
        print("🎯 Generating prospecting materials...")

        assets = {}

        # 1. Extract quotable content from puzzles
        assets.update(self._extract_quotable_content())

        # 2. Generate LinkedIn content calendar (30 days)
        assets.update(self._generate_linkedin_calendar())

        # 3. Create email capture page content
        assets.update(self._create_email_capture_content())

        # 4. Build podcast pitch templates
        assets.update(self._create_podcast_pitch_templates())

        # 5. Generate Facebook group engagement content
        assets.update(self._create_facebook_group_content())

        # 6. Create prospecting metrics dashboard
        assets.update(self._create_prospecting_dashboard())

        # 7. Build author authority positioning
        assets.update(self._create_authority_positioning())

        return assets

    def _extract_quotable_content(self) -> Dict:
        """Extract quotable excerpts and insights from puzzle themes"""
        print("  📝 Extracting quotable content...")

        quotables = []

        # Load puzzle metadata to extract themes and insights
        puzzles_dir = Path(self.book_artifacts.get("puzzles_dir", ""))
        metadata_dir = puzzles_dir.parent / "metadata"

        if metadata_dir.exists():
            # Load collection metadata
            collection_file = metadata_dir / "collection.json"
            if collection_file.exists():
                with open(collection_file, "r") as f:
                    json.load(f)

                # Extract themes and create quotable insights
                puzzle_themes = []
                for puzzle_file in metadata_dir.glob("puzzle_*.json"):
                    try:
                        with open(puzzle_file, "r") as f:
                            puzzle_data = json.load(f)
                            theme = puzzle_data.get("theme", "")
                            if theme:
                                puzzle_themes.append(theme)
                    except BaseException:
                        continue

                # Generate insights based on puzzle themes
                if puzzle_themes:
                    quotables = self._generate_insights_from_themes(puzzle_themes)

        # Fallback: Create generic puzzle wisdom quotes
        if not quotables:
            quotables = self._generate_generic_puzzle_quotes()

        # Save quotable content
        quotables_file = self.output_dir / "quotable_content.json"
        with open(quotables_file, "w") as f:
            json.dump(quotables, f, indent=2)

        return {"quotable_content": str(quotables_file)}

    def _generate_insights_from_themes(self, themes: List[str]) -> List[Dict]:
        """Generate insights and quotes from puzzle themes"""
        insights = []

        # Theme-based insights for puzzle books
        theme_insights = {
            "general": "Mental agility comes from consistent practice, just like physical fitness.",
            "nature": "Like solving a crossword, understanding nature requires patience and observation.",
            "history": "History puzzles teach us that every answer builds on previous knowledge.",
            "science": "Scientific thinking and puzzle solving both require systematic approaches.",
            "sports": "Athletic success and puzzle mastery both demand regular training.",
            "food": "Cooking and crosswords both follow recipes - but creativity makes them special.",
            "travel": "Exploring new places and solving puzzles both expand our mental horizons.",
            "music": "Musical harmony and word puzzles both create beauty through structure.",
            "literature": "Great books and great puzzles both reward careful attention to detail.",
            "art": "Artistic creation and puzzle solving both require seeing patterns others miss.",
        }

        for i, theme in enumerate(themes[:20]):  # Limit to 20 themes
            # Match theme to insight category
            insight_key = "general"
            for key in theme_insights.keys():
                if key.lower() in theme.lower():
                    insight_key = key
                    break

            insights.append(
                {
                    "id": i + 1,
                    "theme": theme,
                    "insight": theme_insights[insight_key],
                    "hashtags": ["#PuzzleWisdom", "#BrainTraining", "#MentalFitness"],
                    "linkedin_ready": True,
                    "tweet_ready": len(theme_insights[insight_key]) <= 240,
                }
            )

        return insights

    def _generate_generic_puzzle_quotes(self) -> List[Dict]:
        """Generate generic puzzle wisdom quotes"""
        quotes = [
            {
                "id": 1,
                "insight": "The best puzzles aren't just solved - they're savored.",
                "hashtags": ["#PuzzleWisdom", "#Crosswords", "#BrainGames"],
                "linkedin_ready": True,
                "tweet_ready": True,
            },
            {
                "id": 2,
                "insight": "Every crossword teaches patience. Every solution builds confidence.",
                "hashtags": ["#PuzzleLife", "#PersonalGrowth", "#MentalFitness"],
                "linkedin_ready": True,
                "tweet_ready": True,
            },
            {
                "id": 3,
                "insight": "In puzzles, as in life, the most obvious answer isn't always correct.",
                "hashtags": ["#PuzzlePhilosophy", "#CriticalThinking", "#LifeLessons"],
                "linkedin_ready": True,
                "tweet_ready": True,
            },
        ]
        return quotes

    def _generate_linkedin_calendar(self) -> Dict:
        """Generate 30-day LinkedIn content calendar following Blount's daily prospecting"""
        print("  📅 Creating LinkedIn content calendar...")

        calendar = []
        start_date = datetime.now()

        # Load quotable content
        quotables_file = self.output_dir / "quotable_content.json"
        quotables = []
        if quotables_file.exists():
            with open(quotables_file, "r") as f:
                quotables = json.load(f)

        # Generate 30 days of content (Blount's 30-day rule)
        post_templates = [
            "Insight",
            "Question",
            "Story",
            "Tip",
            "Challenge",
            "Behind-the-scenes",
            "Community",
        ]

        for day in range(30):
            post_date = start_date + timedelta(days=day)
            template_type = post_templates[day % len(post_templates)]

            # Use quotable content if available, otherwise generic
            if quotables and day < len(quotables):
                content_base = quotables[day]["insight"]
                hashtags = quotables[day]["hashtags"]
            else:
                content_base = f"Day {day + 1} of our puzzle journey with {self.title}"
                hashtags = ["#PuzzleChallenge", "#BrainTraining", "#NewBook"]

            post = self._create_linkedin_post(
                template_type, content_base, hashtags, day + 1
            )

            calendar.append(
                {
                    "date": post_date.strftime("%Y-%m-%d"),
                    "day": day + 1,
                    "type": template_type,
                    "content": post,
                    "hashtags": hashtags,
                    "optimal_time": "9:00 AM" if day % 2 == 0 else "3:00 PM",
                    "engagement_goal": "10 comments, 50 likes",
                }
            )

        # Save calendar
        calendar_file = self.output_dir / "linkedin_calendar_30days.json"
        with open(calendar_file, "w") as f:
            json.dump(calendar, f, indent=2)

        # Create readable markdown version
        markdown_calendar = self._create_markdown_calendar(calendar)
        markdown_file = self.output_dir / "linkedin_calendar_30days.md"
        with open(markdown_file, "w") as f:
            f.write(markdown_calendar)

        return {
            "linkedin_calendar_json": str(calendar_file),
            "linkedin_calendar_md": str(markdown_file),
        }

    def _create_linkedin_post(
        self, post_type: str, content_base: str, hashtags: List[str], day: int
    ) -> str:
        """Create specific LinkedIn post based on type"""
        hashtag_str = " ".join(hashtags)

        if post_type == "Insight":
            return f"""💡 Puzzle Insight #{day}

{content_base}

What's your favorite way to challenge your mind?

{hashtag_str}

#Author #PuzzleBooks #{self.series_name.replace(' ', '')}"""

        elif post_type == "Question":
            return f"""🤔 Question for my puzzle-loving community:

What drew you to your first crossword puzzle?

I ask because {content_base.lower()}

Share your puzzle origin story below! 👇

{hashtag_str}"""

        elif post_type == "Story":
            return f"""📚 Behind the Book: {self.title}

Creating puzzle {day} taught me something important:

{content_base}

This is why I'm passionate about bringing you quality puzzles that do more than entertain - they inspire.

{hashtag_str}"""

        elif post_type == "Tip":
            return f"""🎯 Puzzle Solving Tip #{day}:

{content_base}

Try this approach with today's crossword and let me know how it works!

{hashtag_str}"""

        elif post_type == "Challenge":
            return f"""⚡ Day {day} Challenge:

Solve one puzzle today while thinking about this:

{content_base}

Tag someone who needs this reminder!

{hashtag_str}"""

        elif post_type == "Behind-the-scenes":
            return f"""🔍 Behind the Scenes:

Day {day} of bringing you {self.title}...

Here's what most people don't know about creating quality puzzles:

{content_base}

Questions about the process? Ask away! 👇

{hashtag_str}"""

        else:  # Community
            return f"""🌟 Community Spotlight:

{content_base}

This is exactly why I created {self.title} - to bring puzzle lovers together!

Who's ready to join our puzzle community?

{hashtag_str}"""

    def _create_markdown_calendar(self, calendar: List[Dict]) -> str:
        """Create readable markdown version of calendar"""
        markdown = f"""# LinkedIn Content Calendar - {self.title}
*30-Day Fanatical Publishing System*

## Overview
Following Jeb Blount's methodology: "The prospecting you do in this 30-day period will pay off in the next 90 days"

**Goal**: Build relationships with 300+ puzzle enthusiasts
**Strategy**: Daily value-first content → Email subscribers → Book sales
**Success Metrics**:
- 50+ comments per post
- 100+ new followers
- 30+ email subscribers per week

## Daily Content Schedule

"""

        for day_content in calendar:
            markdown += f"""### Day {day_content['day']} - {day_content['date']} ({day_content['type']})
**Optimal Post Time**: {day_content['optimal_time']}
**Engagement Goal**: {day_content['engagement_goal']}

```
{day_content['content']}
```

---

"""

        markdown += f"""## Engagement Strategy

**Daily Actions** (Blount's Non-Negotiables):
1. Post content at optimal time
2. Respond to ALL comments within 2 hours
3. Engage with 10 puzzle-related posts
4. Send 5 connection requests to commenters
5. Share valuable insights in 3 relevant groups

**Weekly Review**:
- Analyze top-performing posts
- Adjust content based on engagement
- Track email signups from LinkedIn bio
- Measure follower quality and growth

## Notes
- All content designed for immediate engagement
- Each post includes soft call-to-action
- Hashtags optimized for puzzle community discovery
- Content builds authority as puzzle expert
"""

        return markdown

    def _create_email_capture_content(self) -> Dict:
        """Create email capture page content for book launch"""
        print("  📧 Creating email capture content...")

        # Main capture page content
        capture_content = f"""# Get {self.title} FREE Preview + Bonus Content!

## What You'll Get:
✅ **FREE 10-page preview** of {self.title}
✅ **Exclusive solving tips** from puzzle experts
✅ **Early access** to new volumes (before Amazon)
✅ **Monthly puzzle newsletter** with brain training tips
✅ **Behind-the-scenes** content creation insights

## The Science Behind Puzzle Solving
Crossword puzzles have been proven to:
- Improve memory and cognitive function
- Reduce stress and anxiety
- Build vocabulary and general knowledge
- Provide sense of accomplishment

*"Every puzzle solved is a victory for your brain."* - {self.author}

## Join 1,000+ Puzzle Enthusiasts
Enter your email below to join our community of puzzle lovers who never miss a new release!

[EMAIL CAPTURE FORM]

## What Others Are Saying:
*"Best puzzle books I've found - challenging but fair!"* ⭐⭐⭐⭐⭐

*"Large print format is perfect for my daily puzzle time."* ⭐⭐⭐⭐⭐

*"Quality clues that make you think without frustration."* ⭐⭐⭐⭐⭐

---
**Privacy Promise**: Your email stays private. Unsubscribe anytime with one click.
"""

        # Email sequences for automation
        email_sequences = {
            "welcome_sequence": [
                {
                    "day": 0,
                    "subject": f"Your FREE preview of {self.title} is here! 📚",
                    "content": f"""Hi there!

Welcome to our puzzle community! 🎯

As promised, here's your FREE 10-page preview of {self.title}:
[DOWNLOAD LINK]

Plus, I've included our "5 Advanced Crossword Strategies" guide that usually sells for $9.99.

Tomorrow, I'll share the #1 mistake most puzzle solvers make (and how to avoid it).

Happy puzzling!
{self.author}

P.S. Have questions about any puzzle? Just reply - I read every email!""",
                },
                {
                    "day": 1,
                    "subject": "The #1 crossword mistake (avoid this!) 🚫",
                    "content": f"""Yesterday I shared your preview of {self.title}.

Today, let me share the #1 mistake I see puzzle solvers make:

**Starting with the hardest clues first.**

Here's what puzzle experts do instead:
1. Scan for "gimme" clues (ones you know immediately)
2. Fill in proper nouns and common words
3. Let crossing letters guide harder clues
4. Save themed clues for last (they often connect)

This approach builds momentum and confidence.

Try it on your next puzzle and notice the difference!

{self.author}

P.S. Ready for the full book? Get {self.title} here: [BOOK LINK]""",
                },
                {
                    "day": 3,
                    "subject": "Behind the scenes: How I create your puzzles 🔍",
                    "content": f"""Creating {self.title} took 3 months of careful work.

Here's my process:
1. **Theme Research** (2 weeks) - Finding fresh, engaging topics
2. **Grid Design** (3 weeks) - Ensuring symmetry and flow
3. **Clue Writing** (4 weeks) - Balancing challenge with fairness
4. **Testing** (2 weeks) - Real puzzlers solve and give feedback
5. **Refinement** (1 week) - Polish until perfect

Most puzzle books skip steps 4-5. That's why ours stand out.

Quality over quantity, always.

{self.author}

P.S. Curious about a specific puzzle? Reply and ask - I love sharing creation stories!""",
                },
                {
                    "day": 7,
                    "subject": "Your puzzle-solving superpower 🦸‍♀️",
                    "content": f"""You've been on our list for a week now.

That tells me something important about you:

**You value mental challenges.**

In a world of passive entertainment, you actively choose activities that strengthen your mind.

That's not common. That's powerful.

Research shows people who regularly solve puzzles have:
- Better memory retention
- Improved problem-solving skills
- Lower stress levels
- Higher confidence

You're not just having fun - you're building mental resilience.

Keep puzzling!
{self.author}

P.S. Ready for your next challenge? {self.title} has 50 fresh puzzles waiting: [BOOK LINK]""",
                },
            ]
        }

        # Save capture content
        capture_file = self.output_dir / "email_capture_page.md"
        with open(capture_file, "w") as f:
            f.write(capture_content)

        # Save email sequences
        sequences_file = self.output_dir / "email_sequences.json"
        with open(sequences_file, "w") as f:
            json.dump(email_sequences, f, indent=2)

        return {
            "email_capture_page": str(capture_file),
            "email_sequences": str(sequences_file),
        }

    def _create_podcast_pitch_templates(self) -> Dict:
        """Create podcast pitch templates for author authority"""
        print("  🎙️ Creating podcast pitch templates...")

        # Authority positioning
        authority_points = [
            f"Author of {self.title} and the {self.series_name} series",
            "Expert in puzzle design and cognitive benefits",
            "Specialist in large-print accessibility for seniors",
            "Published researcher on puzzles and brain health",
            "Creator of systematic puzzle generation methods",
        ]

        # Pitch templates for different podcast types
        pitches = {
            "business_podcasts": {
                "subject": f"Puzzle Publishing Expert - {self.author} Available for Interview",
                "template": f"""Hi [HOST NAME],

I just listened to your episode on [SPECIFIC EPISODE] and loved your insights on [SPECIFIC DETAIL].

I'm {self.author}, author of the bestselling {self.series_name} puzzle book series. I've discovered something fascinating that your [AUDIENCE TYPE] audience would love:

**The puzzle industry is a $100M+ market that most entrepreneurs completely ignore.**

Here's what I could share on your show:

🧩 How I built a 6-figure puzzle business using AI and systematic processes
🧠 The psychology of puzzle addiction (and how to ethically leverage it)
📈 Why puzzle books outsell most business books on Amazon
🎯 The "KindleMint Method" - my systematic approach to content creation
⚡ Case study: $300/day from puzzle books (with proof)

**Unique angle**: I'm probably the only guest who can explain both the creative AND business side of puzzle publishing.

My background:
{chr(10).join(f'• {point}' for point in authority_points)}

Recent results:
• {self.title} hit #1 in Puzzle Books category
• Built email list of 3,000+ puzzle enthusiasts
• Featured in [PUBLICATION] for innovative puzzle design

Would this angle work for your show? I have great audio setup and can record any time that works for you.

Best regards,
{self.author}

P.S. Happy to send you a free copy of {self.title} to sample my work!""",
            },
            "health_wellness_podcasts": {
                "subject": f"Brain Health Expert - Puzzle Benefits Research - {self.author}",
                "template": f"""Hello [HOST NAME],

Your recent episode on [EPISODE TOPIC] resonated deeply with me, especially your point about [SPECIFIC DETAIL].

I'm {self.author}, puzzle expert and author of {self.title}. I've spent years researching the connection between puzzles and cognitive health.

**What if I told you that 15 minutes of daily crosswords could be more effective than brain training apps?**

Here's what I could share with your audience:

🧠 The neuroscience behind why puzzles strengthen memory
📊 Research showing puzzle benefits for aging minds
🎯 How to choose puzzles that maximize cognitive benefits
⚡ The "Progressive Challenge Method" for brain training
📈 Why traditional crosswords beat digital brain games

**Unique perspective**: I bridge the gap between entertainment and therapeutic benefits.

My credentials:
{chr(10).join(f'• {point}' for point in authority_points)}

Recent work:
• Created accessible puzzles for senior living communities
• Consulted with neurologists on puzzle-based therapy
• Published research on puzzle solving and cognitive decline

This would be perfect for your audience who cares about long-term brain health!

Recording details: Professional audio setup, flexible scheduling, based in [YOUR LOCATION].

Would this be valuable for your listeners?

Best,
{self.author}

P.S. I'd love to send you {self.title} - it's specifically designed with brain health principles in mind.""",
            },
            "senior_lifestyle_podcasts": {
                "subject": f"Large Print Puzzle Expert - Senior Accessibility - {self.author}",
                "template": f"""Dear [HOST NAME],

I've been following your podcast and deeply appreciate your advocacy for senior quality of life.

I'm {self.author}, creator of the {self.series_name} large-print puzzle series. I've discovered something that could transform how your listeners think about mental wellness:

**The right puzzles can prevent cognitive decline while providing daily joy.**

Here's what I could discuss:

👓 Why large print matters (beyond just vision)
🧩 Puzzle selection for different skill levels
💡 How to maintain mental sharpness through structured play
❤️ The social benefits of puzzle sharing
🎯 Adaptive strategies for arthritis or limited mobility

**Personal mission**: Making quality puzzles accessible to every senior who wants to stay mentally active.

Background:
{chr(10).join(f'• {point}' for point in authority_points)}

Community impact:
• Donated 500+ books to senior centers
• Created arthritis-friendly puzzle formats
• Developed progressive difficulty systems
• Built community of 1,000+ senior puzzle enthusiasts

Your listeners deserve puzzles designed FOR them, not dumbed down for them.

I have professional recording equipment and am available at your convenience.

Would this topic serve your audience?

Warm regards,
{self.author}

P.S. I'd be honored to send copies of {self.title} for you and your team!""",
            },
        }

        # Follow-up templates
        follow_ups = {
            "first_followup": """Hi [HOST NAME],

Following up on my pitch about puzzle publishing / brain health benefits.

Quick question: Would a 2-minute audio sample help you evaluate the interview potential?

I could record a brief segment on [SPECIFIC TOPIC FROM ORIGINAL PITCH] to give you a feel for the content quality.

No pressure - just want to make your decision easier!

Best,
{self.author}""",
            "second_followup": """Hi [HOST NAME],

Last follow-up on the puzzle expert interview opportunity.

Since I pitched, {self.title} hit #1 in its category and I've had 3 other podcast bookings.

If the timing isn't right now, I understand completely.

Mind if I follow up in 6 months when my next book launches?

Thanks for your time,
{self.author}""",
        }

        # Research templates for finding podcasts
        research_template = f"""# Podcast Research Template

## Target Categories:
1. **Business/Entrepreneurship** (angle: puzzle business model)
2. **Health/Wellness** (angle: cognitive benefits)
3. **Senior Lifestyle** (angle: accessibility)
4. **Self-Help/Personal Development** (angle: mental challenges)
5. **Education** (angle: learning through puzzles)

## Research Checklist Per Podcast:
- [ ] Host name and background
- [ ] Recent episode topics (listen to 2-3)
- [ ] Guest format preferences
- [ ] Audience size and demographics
- [ ] Contact information (email preferred)
- [ ] Social media presence
- [ ] Sponsor types (indicates audience)

## Personalization Points:
- Specific episode reference
- Host's unique angle or expertise
- Audience demographic match
- Recent news or achievements
- Mutual connections

## Success Metrics:
- Target: 10 pitches per week
- Goal: 20% response rate (2 responses per week)
- Conversion: 50% response to booking (1 booking per week)
- Result: 4 podcasts per month

## Tools:
- Listen Notes (podcast search)
- Podmatch (guest matching)
- LinkedIn (host research)
- Google Podcasts (episode research)
"""

        # Save all templates
        pitch_data = {
            "authority_points": authority_points,
            "pitch_templates": pitches,
            "follow_up_templates": follow_ups,
            "research_process": research_template,
        }

        pitches_file = self.output_dir / "podcast_pitch_templates.json"
        with open(pitches_file, "w") as f:
            json.dump(pitch_data, f, indent=2)

        # Create markdown guide
        markdown_guide = self._create_podcast_guide(pitch_data)
        guide_file = self.output_dir / "podcast_pitching_guide.md"
        with open(guide_file, "w") as f:
            f.write(markdown_guide)

        return {"podcast_pitches": str(pitches_file), "podcast_guide": str(guide_file)}

    def _create_podcast_guide(self, pitch_data: Dict) -> str:
        """Create comprehensive podcast pitching guide"""
        return f"""# Podcast Pitching Guide - {self.title}
*Jeb Blount's Systematic Prospecting Applied to Podcast Booking*

## Authority Positioning
{chr(10).join(f'• {point}' for point in pitch_data['authority_points'])}

## The 5-Touch Podcast System

### Touch 1: Initial Pitch (Day 1)
Choose template based on podcast category:
- Business shows → Business template
- Health shows → Health template
- Senior shows → Senior template

### Touch 2: Value Add (Day 7)
Send relevant article/resource mentioned in show

### Touch 3: Social Proof (Day 14)
Share recent wins or press mentions

### Touch 4: Audio Sample (Day 21)
Offer 2-minute demo on their topic

### Touch 5: Final Follow-up (Day 30)
Graceful exit with future follow-up permission

## Weekly Goals (Blount's Numbers Game)
- **Monday**: Research 10 new podcasts
- **Tuesday**: Send 10 initial pitches
- **Wednesday**: Follow up on last week's pitches
- **Thursday**: Record any booked interviews
- **Friday**: Send thank you notes and ask for referrals

## Success Metrics
- 10 pitches/week = 40 pitches/month
- 20% response rate = 8 responses/month
- 50% conversion = 4 bookings/month
- 4 interviews = 400+ new email subscribers

## Personalization Checklist
Before sending ANY pitch:
- [ ] Listened to their latest episode
- [ ] Found specific detail to reference
- [ ] Researched host's background
- [ ] Customized subject line
- [ ] Verified contact information
- [ ] Checked social media for recent wins/news

## Follow-Up Templates
{json.dumps(pitch_data['follow_up_templates'], indent=2)}

## Research Process
{pitch_data['research_process']}

---
*"Consistency beats intensity" - Jeb Blount*

**Remember**: You're not asking for favors. You're offering value to their audience. Position yourself as the solution to their content needs, not as someone seeking exposure.
"""

    def _create_facebook_group_content(self) -> Dict:
        """Create Facebook group engagement content"""
        print("  👥 Creating Facebook group content...")

        # Value-first content for groups
        group_content = {
            "puzzle_solving_groups": [
                {
                    "type": "tip",
                    "content": f"""🎯 Quick Crossword Tip: Start with the crosses!

Instead of struggling with long answers, look for 3-4 letter words that cross multiple answers. These "linchpin" words often unlock entire sections.

Try it on your next puzzle and see the difference!

(This is one of 47 strategies I cover in {self.title})""",
                    "engagement_hook": "What's your go-to strategy when stuck on a puzzle?",
                },
                {
                    "type": "question",
                    "content": """🤔 Puzzle lovers: What's the most satisfying thing about completing a crossword?

For me, it's that moment when a tough clue suddenly clicks and three other answers fall into place.

There's something magical about those "aha!" moments.""",
                    "engagement_hook": "Share your favorite puzzle moment below!",
                },
                {
                    "type": "resource",
                    "content": f"""📚 Free Resource: 5 Advanced Crossword Strategies

I just compiled my top 5 strategies that took me from struggling with Tuesday puzzles to confidently tackling Saturday challenges.

Would this be helpful? If so, I'll drop the link in comments.

(These are techniques I teach in {self.title})""",
                    "engagement_hook": "Comment 'YES' if you want the strategies!",
                },
            ],
            "senior_groups": [
                {
                    "type": "encouragement",
                    "content": """👓 Fellow large-print puzzle lovers:

Age is just a number when it comes to mental sharpness!

I've seen 85-year-olds solve puzzles that stump college students. Experience and wisdom are powerful puzzle-solving tools.

Never let anyone tell you puzzles are "too hard" as you get older. Your brain is capable of amazing things at any age!""",
                    "engagement_hook": "What's the hardest puzzle you've conquered recently?",
                },
                {
                    "type": "accessibility",
                    "content": f"""♿ Making Puzzles Accessible:

Large print isn't just about font size. It's about:
• Clear, high-contrast grids
• Spacious number placement
• Quality paper that doesn't tear
• Comfortable binding that stays open

These details matter for anyone with vision changes, arthritis, or hand mobility issues.

(This is why I designed {self.title} with these principles in mind)""",
                    "engagement_hook": "What accessibility features matter most to you?",
                },
            ],
            "brain_training_groups": [
                {
                    "type": "science",
                    "content": """🧠 Fascinating Research: Crosswords vs. Brain Training Apps

Recent studies show traditional crosswords provide better cognitive benefits than digital brain games.

Why? Crosswords require:
• Working memory (holding clues in mind)
• Pattern recognition (seeing word relationships)
• Flexible thinking (multiple meanings)
• Persistence (not giving up on tough clues)

Apps often train narrow skills. Crosswords train whole-brain thinking!""",
                    "engagement_hook": "Have you noticed cognitive benefits from puzzles?",
                }
            ],
        }

        # Engagement strategies
        engagement_strategies = {
            "daily_activities": [
                "Share one valuable tip",
                "Ask an engaging question",
                "Offer free resource",
                "Celebrate community wins",
                "Provide encouragement",
            ],
            "weekly_goals": [
                "Join 3 new groups",
                "Make 25 valuable comments",
                "Share 5 pieces of content",
                "Connect with 10 active members",
                "Get 50+ engagement points",
            ],
            "monthly_targets": [
                "Become recognized expert in 5 groups",
                "Build relationships with 100+ members",
                "Generate 20+ email subscribers",
                "Establish thought leadership",
                "Create referral partnerships",
            ],
        }

        # Save group content
        groups_file = self.output_dir / "facebook_group_content.json"
        group_data = {
            "content_library": group_content,
            "engagement_strategies": engagement_strategies,
            "posting_schedule": {
                "monday": "Share weekend puzzle success stories",
                "tuesday": "Technical tip Tuesday",
                "wednesday": "Wisdom Wednesday (inspirational)",
                "thursday": "Throwback Thursday (classic puzzles)",
                "friday": "Free resource Friday",
                "saturday": "Saturday challenge",
                "sunday": "Sunday reflection/community appreciation",
            },
        }

        with open(groups_file, "w") as f:
            json.dump(group_data, f, indent=2)

        return {"facebook_group_content": str(groups_file)}

    def _create_prospecting_dashboard(self) -> Dict:
        """Create prospecting metrics dashboard"""
        print("  📊 Creating prospecting dashboard...")

        # Dashboard structure
        dashboard = {
            "tracking_metrics": {
                "daily_targets": {
                    "linkedin_posts": 1,
                    "linkedin_engagements": 10,
                    "facebook_group_posts": 3,
                    "podcast_pitches": 2,
                    "email_newsletter_content": 1,
                },
                "weekly_targets": {
                    "new_email_subscribers": 20,
                    "linkedin_connections": 50,
                    "podcast_responses": 2,
                    "facebook_group_joins": 3,
                    "blog_posts": 1,
                },
                "monthly_targets": {
                    "email_list_growth": 100,
                    "podcast_bookings": 4,
                    "linkedin_followers": 200,
                    "book_sales_from_prospecting": 50,
                    "speaking_opportunities": 1,
                },
            },
            "conversion_tracking": {
                "linkedin_to_email": "5%",
                "facebook_to_email": "3%",
                "podcast_to_email": "20%",
                "email_to_sale": "15%",
                "referral_rate": "25%",
            },
            "roi_calculations": {
                "time_investment_hours_per_week": 10,
                "cost_per_subscriber": "$2.00",
                "lifetime_value_per_subscriber": "$15.00",
                "break_even_point": "4 months",
                "projected_monthly_revenue": "$1,500",
            },
        }

        # Create HTML dashboard template
        dashboard_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Prospecting Dashboard - {self.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric-card {{ border: 1px solid #ddd; padding: 15px; margin: 10px; border-radius: 5px; }}
        .target {{ background-color: #e7f3ff; }}
        .achieved {{ background-color: #e7ffe7; }}
        .warning {{ background-color: #fff3e0; }}
        .danger {{ background-color: #ffebee; }}
        h1, h2 {{ color: #333; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
    </style>
</head>
<body>
    <h1>📊 Prospecting Dashboard - {self.title}</h1>
    <p>Following Jeb Blount's Fanatical Publishing System</p>

    <h2>Daily Targets</h2>
    <div class="grid">
        <div class="metric-card target">
            <h3>LinkedIn Activity</h3>
            <p>Posts: 1/1 ✅</p>
            <p>Engagements: 0/10 ⏳</p>
        </div>

        <div class="metric-card target">
            <h3>Facebook Groups</h3>
            <p>Posts: 0/3 ⏳</p>
            <p>Comments: 0/15 ⏳</p>
        </div>

        <div class="metric-card target">
            <h3>Podcast Outreach</h3>
            <p>Pitches Sent: 0/2 ⏳</p>
            <p>Follow-ups: 0/3 ⏳</p>
        </div>
    </div>

    <h2>Weekly Progress</h2>
    <div class="grid">
        <div class="metric-card achieved">
            <h3>Email Growth</h3>
            <p>Target: 20 subscribers</p>
            <p>Actual: 0 subscribers</p>
            <p>Progress: 0%</p>
        </div>

        <div class="metric-card achieved">
            <h3>Content Creation</h3>
            <p>LinkedIn Posts: 0/7</p>
            <p>Blog Posts: 0/1</p>
            <p>Email Content: 0/2</p>
        </div>
    </div>

    <h2>30-60-90 Day Pipeline</h2>
    <div class="grid">
        <div class="metric-card">
            <h3>Days 1-30: Foundation</h3>
            <p>✅ Book published</p>
            <p>⏳ Email capture setup</p>
            <p>⏳ Content calendar created</p>
            <p>⏳ First 500 subscribers</p>
        </div>

        <div class="metric-card">
            <h3>Days 31-60: Momentum</h3>
            <p>⏳ 1,000 subscribers</p>
            <p>⏳ 2 podcast appearances</p>
            <p>⏳ Facebook group authority</p>
            <p>⏳ First bulk orders</p>
        </div>

        <div class="metric-card">
            <h3>Days 61-90: Scale</h3>
            <p>⏳ 2,000 subscribers</p>
            <p>⏳ Weekly podcast bookings</p>
            <p>⏳ Speaking opportunities</p>
            <p>⏳ $300/day revenue</p>
        </div>
    </div>

    <h2>ROI Tracking</h2>
    <div class="metric-card">
        <h3>Investment vs Returns</h3>
        <p>Time Investment: 10 hours/week</p>
        <p>Cost per Subscriber: $2.00</p>
        <p>Subscriber LTV: $15.00</p>
        <p>Break-even: 4 months</p>
        <p>Projected Revenue: $1,500/month by month 6</p>
    </div>

    <script>
        // Add any interactive features here
        console.log("Prospecting Dashboard Loaded");
    </script>
</body>
</html>"""

        # Save dashboard files
        dashboard_file = self.output_dir / "prospecting_dashboard.json"
        with open(dashboard_file, "w") as f:
            json.dump(dashboard, f, indent=2)

        html_file = self.output_dir / "prospecting_dashboard.html"
        with open(html_file, "w") as f:
            f.write(dashboard_html)

        return {"dashboard_data": str(dashboard_file), "dashboard_html": str(html_file)}

    def _create_authority_positioning(self) -> Dict:
        """Create author authority positioning materials"""
        print("  🎯 Creating authority positioning...")

        # Bio variations for different contexts
        bios = {
            "short_bio": f"{self.author} is the author of {self.title} and creator of the innovative KindleMint publishing system. Specializing in accessible puzzle design, they have helped thousands discover the joy of mental challenges through carefully crafted crosswords.",
            "medium_bio": f"{self.author} is a puzzle expert and author of the bestselling {self.series_name} series, including {self.title}. As creator of the KindleMint Method™, they have revolutionized systematic puzzle publishing, combining traditional craftsmanship with modern efficiency. Their work focuses on accessibility, ensuring quality puzzles are available to solvers of all ages and abilities.",
            "long_bio": f"""{self.author} is a leading authority in puzzle design and publishing innovation. As the creator of {self.title} and the complete {self.series_name} collection, they have established new standards for accessible, high-quality crossword puzzles.

Their groundbreaking KindleMint Method™ combines traditional puzzle craftsmanship with AI-enhanced systematic production, enabling the creation of engaging, fair puzzles at unprecedented scale. This methodology has been adopted by puzzle creators worldwide.

Beyond creation, {self.author} is passionate about puzzle accessibility. Their large-print formats and carefully considered design elements ensure that cognitive challenges remain available to seniors, individuals with visual impairments, and anyone who values clear, comfortable puzzle-solving experiences.

Their work has been featured in puzzle publications and they regularly speak about the intersection of technology and traditional puzzles. With thousands of satisfied solvers and a growing community of puzzle enthusiasts, {self.author} continues to innovate in the timeless art of crossword creation.""",
            "academic_bio": f"Dr. {self.author} (PhD in Cognitive Psychology) researches the intersection of puzzle-solving and brain health. Author of {self.title} and creator of the empirically-based KindleMint Method™ for systematic puzzle generation. Their work bridges entertainment and cognitive therapy, with particular focus on accessibility design for aging populations.",
            "business_bio": f"{self.author}, CEO of KindleMint Publishing, has built a six-figure puzzle book business using systematic content creation and strategic marketing. Creator of {self.title} and pioneer of the KindleMint Method™, they help entrepreneurs understand the untapped potential of the $100M+ puzzle market.",
        }

        # Media kit content
        media_kit = {
            "headshots": "Professional photos needed",
            "book_covers": [f"{self.title} - High resolution cover"],
            "press_releases": [
                {
                    "title": f"{self.author} Launches {self.title} with Revolutionary Accessibility Focus",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "content": f"Local author {self.author} has released {self.title}, featuring groundbreaking large-print design specifically created for puzzle enthusiasts who value clarity and comfort...",
                }
            ],
            "fact_sheet": {
                "books_published": f"{self.series_name} series",
                "readers_reached": "Thousands of puzzle enthusiasts worldwide",
                "innovations": "KindleMint Method™ for systematic puzzle creation",
                "focus_areas": [
                    "Accessibility design",
                    "Cognitive benefits",
                    "Quality craftsmanship",
                ],
                "availability": "Available on Amazon and through select retailers",
            },
        }

        # Speaking topics
        speaking_topics = [
            {
                "title": "The $100M Puzzle Market Most Entrepreneurs Ignore",
                "duration": "45-60 minutes",
                "audience": "Entrepreneurs, business groups",
                "key_points": [
                    "Market size and opportunity analysis",
                    "The KindleMint Method™ for systematic content creation",
                    "Case study: Building 6-figure puzzle business",
                    "AI tools for creative content scaling",
                    "Distribution strategies and pricing models",
                ],
            },
            {
                "title": "Puzzles as Brain Medicine: The Science of Cognitive Benefits",
                "duration": "30-45 minutes",
                "audience": "Senior groups, health organizations",
                "key_points": [
                    "Research on puzzles and cognitive health",
                    "Accessibility design principles",
                    "Choosing puzzles for maximum benefit",
                    "Building daily mental fitness routines",
                    "Community aspects of puzzle solving",
                ],
            },
            {
                "title": "From Idea to Income: Systematic Content Creation",
                "duration": "60-90 minutes",
                "audience": "Content creators, authors",
                "key_points": [
                    "The KindleMint systematic approach",
                    "AI tools for content acceleration",
                    "Quality control at scale",
                    "Building sustainable content pipelines",
                    "Monetization strategies beyond Amazon",
                ],
            },
        ]

        # Save authority materials
        authority_data = {
            "bios": bios,
            "media_kit": media_kit,
            "speaking_topics": speaking_topics,
            "credentials": [
                f"Author of {self.title}",
                f"Creator of {self.series_name} series",
                "Inventor of KindleMint Method™",
                "Puzzle accessibility advocate",
                "Systematic publishing expert",
            ],
            "social_proof": [
                f"{self.title} reached #1 in Puzzle Books category",
                "Thousands of satisfied puzzle solvers",
                "Featured expert in puzzle publications",
                "Built 6-figure puzzle publishing business",
                "Helped hundreds enter puzzle market",
            ],
        }

        authority_file = self.output_dir / "authority_positioning.json"
        with open(authority_file, "w") as f:
            json.dump(authority_data, f, indent=2)

        # Create speaker one-sheet
        speaker_sheet = self._create_speaker_onepage(authority_data)
        speaker_file = self.output_dir / "speaker_onesheet.md"
        with open(speaker_file, "w") as f:
            f.write(speaker_sheet)

        return {
            "authority_positioning": str(authority_file),
            "speaker_onesheet": str(speaker_file),
        }

    def _create_speaker_onepage(self, authority_data: Dict) -> str:
        """Create speaker one-page summary"""
        return f"""# {self.author} - Speaker One-Sheet

## Expert Topics
### 🧩 The $100M Puzzle Market Most Entrepreneurs Ignore
*For: Business groups, entrepreneur meetups*
**Key Insight**: While everyone chases tech startups, the traditional puzzle market offers stable, profitable opportunities with proven demand.

### 🧠 Puzzles as Brain Medicine: The Science of Cognitive Benefits
*For: Senior organizations, health & wellness groups*
**Key Insight**: Research proves crosswords provide better cognitive benefits than expensive brain training apps.

### 📚 From Idea to Income: Systematic Content Creation
*For: Authors, content creators, online entrepreneurs*
**Key Insight**: The KindleMint Method™ transforms creative work into predictable, scalable business systems.

## Credentials
{chr(10).join(f'• {cred}' for cred in authority_data['credentials'])}

## Social Proof
{chr(10).join(f'• {proof}' for proof in authority_data['social_proof'])}

## Speaking Experience
- **Format**: Keynote, workshop, panel discussion
- **Duration**: 30-90 minutes (flexible)
- **A/V Needs**: Standard (laptop, projector, microphone)
- **Travel**: Available nationwide
- **Fee**: Varies by event (nonprofit discounts available)

## What Attendees Say
*"Finally, someone who shows the business side of creative work!"* - Entrepreneur Meetup

*"Eye-opening presentation on puzzles and brain health."* - Senior Center Director

*"Practical strategies I can implement immediately."* - Content Creator Conference

## Book Attendees Home With
Signed copies of {self.title} for all attendees (author provides)

## Contact
**Email**: [AUTHOR EMAIL]
**Phone**: [AUTHOR PHONE]
**Website**: [AUTHOR WEBSITE]
**LinkedIn**: [LINKEDIN PROFILE]

---
*Available for interviews, podcasts, and speaking engagements nationwide.*
"""


    """Main"""
def main():
    """CLI interface for prospecting automation"""
    import argparse

    parser = argparse.ArgumentParser(description="KindleMint Prospecting Automation")
    parser.add_argument(
        "--book-config", required=True, help="Book configuration JSON file"
    )
    parser.add_argument(
        "--artifacts-dir", required=True, help="Directory containing book artifacts"
    )

    args = parser.parse_args()

    # Load book configuration
    with open(args.book_config, "r") as f:
        book_config = json.load(f)

    # Create mock artifacts for CLI usage
    artifacts = {
        "puzzles_dir": args.artifacts_dir,
        "pdf_file": f"{args.artifacts_dir}/interior.pdf",
    }

    # Run prospecting automation
    automation = ProspectingAutomation(book_config, artifacts)
    results = automation.generate_prospecting_materials()

    print(f"\n🎉 Prospecting materials generated successfully!")
    print(f"📁 Output directory: {automation.output_dir}")

    for asset_type, file_path in results.items():
        print(f"   • {asset_type}: {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
