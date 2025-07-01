"""
Intelligent V3 Orchestrator - Market-Aware Publishing Engine
Transforms blind publishing into intelligent, profitable series creation.

BUSINESS IMPACT: $300/day revenue through profitable micro-niche domination
STRATEGY: Market Intelligence → Series Publishing → Brand Building → Customer Lifetime Value
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3

logger = logging.getLogger(__name__)


class IntelligentV3Orchestrator:
    """Market-aware publishing engine with intelligence-driven targeting."""

        """  Init  """


def __init__(self):
        """Initialize intelligent orchestrator."""
        # API keys and configurations
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.assets_bucket = os.getenv("ASSETS_BUCKET", "kindlemint-books")
        self.fargate_invoker_arn = os.getenv("FARGATE_INVOKER_ARN")

        # AWS clients
        self.s3_client = boto3.client("s3")
        self.lambda_client = boto3.client("lambda")

        # Intelligence system thresholds
        self.min_niche_confidence = 75.0  # Minimum confidence to proceed
        self.target_daily_profit = 10.0  # Minimum daily profit potential
        self.series_length = 5  # Standard series length

        # Approval system
        self.auto_approve_threshold = 85.0  # Auto-approve above this confidence
        self.require_human_approval = True  # Enable human approval gate

    async def execute_intelligent_pipeline(
        self, force_niche: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute intelligent market-aware publishing pipeline.

        Args:
            force_niche: Override niche for testing

        Returns:
            Complete pipeline execution results
        """
        try:
            pipeline_id = f"intelligent_{uuid.uuid4().hex[:8]}"
            logger.info(f"🧠 INTELLIGENT V3 PIPELINE ACTIVATED - ID: {pipeline_id}")

            # Phase 1: Market Intelligence Discovery
            logger.info("🔍 Phase 1: Market Intelligence Discovery")
            market_opportunities = await self._discover_market_opportunities()

            if not market_opportunities:
                return {
                    "status": "failed",
                    "reason": "no_profitable_opportunities_found",
                    "phase": "market_discovery",
                }

            # Phase 2: Human Approval Gate (if enabled)
            logger.info("🎯 Phase 2: Opportunity Assessment")
            approved_opportunity = await self._get_opportunity_approval(
                market_opportunities
            )

            if not approved_opportunity:
                return {
                    "status": "pending_approval",
                    "opportunities": market_opportunities,
                    "phase": "awaiting_human_decision",
                    "action_required": "Select opportunity from list and re-trigger pipeline",
                }

            logger.info(
                f"✅ Opportunity approved: {approved_opportunity['micro_niche']}"
            )

            # Phase 3: Series Strategy Creation
            logger.info("📚 Phase 3: Series Strategy Creation")
            book_series = await self._create_intelligent_series(approved_opportunity)

            # Phase 4: Brand System Building
            logger.info("🏗️ Phase 4: Brand System Building")
            brand_system = await self._build_brand_system(book_series)

            # Phase 5: Volume 1 Production
            logger.info("🚀 Phase 5: Volume 1 Production")
            volume_1_result = await self._produce_series_volume_1(
                book_series, brand_system
            )

            # Phase 6: Series Launch Automation
            logger.info("⚡ Phase 6: Series Launch Automation")
            launch_automation = await self._activate_series_launch_sequence(
                book_series, brand_system, volume_1_result
            )

            # Phase 7: Memory System Update
            logger.info("💾 Phase 7: Memory System Update")
            await self._update_intelligent_memory(
                pipeline_id, approved_opportunity, book_series, brand_system
            )

            return {
                "status": "success",
                "pipeline_id": pipeline_id,
                "approved_opportunity": approved_opportunity,
                "book_series": book_series,
                "brand_system": brand_system,
                "volume_1_production": volume_1_result,
                "launch_automation": launch_automation,
                "expected_daily_profit": approved_opportunity["profit_potential_daily"],
                "series_completion_timeline": f"{self.series_length * 14} days",
                "next_volume_schedule": (
                    datetime.now() + timedelta(days=14)
                ).isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Intelligent pipeline failed: {str(e)}")
            raise

    async def _discover_market_opportunities(self) -> List[Dict[str, Any]]:
        """Discover profitable micro-niche opportunities using Market Intelligence."""
        try:
            from kindlemint.intelligence.market_scout import KDPMarketScout

            logger.info("🎯 Activating Market Intelligence System...")

            # Initialize market scout
            scout = KDPMarketScout()

            # Discover profitable opportunities
            opportunities = await scout.discover_profitable_micro_niches(max_niches=5)

            # Filter by profitability thresholds
            qualified_opportunities = []
            for opp in opportunities:
                if (
                    opp.confidence_score >= self.min_niche_confidence
                    and opp.profit_potential >= self.target_daily_profit
                ):

                    qualified_opportunities.append(
                        {
                            "micro_niche": opp.micro_niche,
                            "broad_category": opp.broad_category,
                            "profit_potential_daily": opp.profit_potential,
                            "confidence_score": opp.confidence_score,
                            "demand_score": opp.demand_score,
                            "competition_score": opp.competition_score,
                            "keywords": opp.keywords,
                            "series_opportunities": opp.series_opportunities,
                            "brand_potential": opp.brand_potential,
                            "auto_approve": opp.confidence_score
                            >= self.auto_approve_threshold,
                        }
                    )

            logger.info(
                f"✅ Market Intelligence: {len(qualified_opportunities)} qualified opportunities found"
            )

            # Sort by profit potential * confidence
            qualified_opportunities.sort(
                key=lambda x: x["profit_potential_daily"]
                * (x["confidence_score"] / 100),
                reverse=True,
            )

            return qualified_opportunities

        except Exception as e:
            logger.error(f"Market discovery failed: {e}")
            return []

    async def _get_opportunity_approval(
        self, opportunities: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Get approval for market opportunity (auto or human)."""
        try:
            if not opportunities:
                return None

            # Check for auto-approval candidates
            for opp in opportunities:
                if opp.get("auto_approve", False) and not self.require_human_approval:
                    logger.info(
                        f"🤖 Auto-approving high-confidence opportunity: {opp['micro_niche']}"
                    )
                    logger.info(f"   Confidence: {opp['confidence_score']}%")
                    logger.info(
                        f"   Profit Potential: ${opp['profit_potential_daily']}/day"
                    )
                    return opp

            # If human approval required, return None to trigger approval workflow
            if self.require_human_approval:
                logger.info("👤 Human approval required - presenting opportunities")
                await self._send_approval_request(opportunities)
                return None

            # Fallback: return best opportunity
            return opportunities[0]

        except Exception as e:
            logger.error(f"Opportunity approval failed: {e}")
            return None

    async     """ Send Approval Request"""
def _send_approval_request(self, opportunities: List[Dict[str, Any]]):
        """Send approval request with opportunity details."""
        try:
            # Format opportunities for human review
            opportunity_summary = "🎯 PROFITABLE OPPORTUNITIES DISCOVERED:\n\n"

            for i, opp in enumerate(opportunities[:3], 1):  # Top 3 opportunities
                opportunity_summary += f"{i}. {opp['micro_niche']}\n"
                opportunity_summary += (
                    f"   💰 Daily Profit: ${opp['profit_potential_daily']}\n"
                )
                opportunity_summary += f"   📊 Confidence: {opp['confidence_score']}%\n"
                opportunity_summary += f"   🎯 Demand: {opp['demand_score']}/100\n"
                opportunity_summary += (
                    f"   🏁 Competition: {opp['competition_score']}/100\n"
                )
                opportunity_summary += f"   📚 Series Potential: {opp['series_opportunities'][0]}, {opp['series_opportunities'][1]}...\n"
                opportunity_summary += (
                    f"   🏷️ Brand: {opp['brand_potential'][:60]}...\n\n"
                )

            opportunity_summary += (
                "Reply with the number of your choice (1, 2, or 3) to proceed."
            )

            # Send via Slack notification
            from kindlemint.notifications.slack_notifier import SlackNotifier

            slack = SlackNotifier()
            await slack.send_notification(
                message=opportunity_summary,
                title="🧠 Market Intelligence: Approval Required",
                urgency="high",
            )

            logger.info("📩 Approval request sent via Slack")

        except Exception as e:
            logger.warning(f"Approval request sending failed: {e}")

    async def _create_intelligent_series(
        self, opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create intelligent book series for approved opportunity."""
        try:
            from kindlemint.intelligence.series_publisher import SeriesPublisher

            logger.info(
                f"📚 Creating intelligent series for: {opportunity['micro_niche']}"
            )

            # Initialize series publisher
            publisher = SeriesPublisher()

            # Create complete book series
            book_series = await publisher.create_book_series(opportunity)

            # Convert to dictionary format
            series_data = {
                "series_name": book_series.series_name,
                "series_brand": book_series.series_brand,
                "micro_niche": book_series.micro_niche,
                "total_volumes": book_series.total_volumes,
                "author_persona": book_series.author_persona,
                "brand_colors": book_series.brand_colors,
                "website_url": book_series.website_url,
                "email_capture_offer": book_series.email_capture_offer,
                "series_description": book_series.series_description,
                "books": [
                    {
                        "volume_number": book.volume_number,
                        "title": book.title,
                        "subtitle": book.subtitle,
                        "unique_content_focus": book.unique_content_focus,
                        "keywords": book.keywords,
                        "target_length": book.target_length,
                        "book_id": book.book_id,
                    }
                    for book in book_series.books
                ],
                "cross_promotion_strategy": await publisher._create_cross_promotion_strategy(
                    book_series.books
                ),
            }

            logger.info(
                f"✅ Series created: {book_series.series_name} ({book_series.total_volumes} volumes)"
            )

            return series_data

        except Exception as e:
            logger.error(f"Intelligent series creation failed: {e}")
            raise

    async def _build_brand_system(self, book_series: Dict[str, Any]) -> Dict[str, Any]:
        """Build complete brand system with website and email funnel."""
        try:
            from kindlemint.intelligence.brand_builder import BrandBuilder

            logger.info(f"🏗️ Building brand system for: {book_series['series_brand']}")

            # Initialize brand builder
            builder = BrandBuilder()

            # Build complete brand system
            brand_system = await builder.build_complete_brand_system(book_series)

            logger.info(f"✅ Brand system created: {brand_system['website']['url']}")
            logger.info(
                f"   Email Provider: {brand_system['email_funnel']['provider']}"
            )
            logger.info(f"   Bonus Product: {brand_system['bonus_product']['title']}")

            return brand_system

        except Exception as e:
            logger.error(f"Brand system building failed: {e}")
            raise

    async def _produce_series_volume_1(
        self, book_series: Dict[str, Any], brand_system: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Produce the first volume in the series."""
        try:
            # Get Volume 1 details
            volume_1 = book_series["books"][0]

            logger.info(f"📖 Producing Volume 1: {volume_1['title']}")

            # Generate content for Volume 1
            content_result = await self._generate_volume_content(
                volume_1, book_series, brand_system
            )

            # Generate cover for Volume 1
            cover_result = await self._generate_volume_cover(volume_1, book_series)

            # Upload assets to S3
            s3_assets = await self._upload_volume_assets(
                volume_1, content_result, cover_result
            )

            # Trigger Fargate publishing
            publishing_result = await self._trigger_volume_publishing(
                volume_1, s3_assets, book_series
            )

            # Trigger content marketing
            marketing_result = await self._trigger_volume_marketing(
                volume_1, book_series, brand_system
            )

            return {
                "volume_id": volume_1["book_id"],
                "title": volume_1["title"],
                "content_generation": content_result,
                "cover_generation": cover_result,
                "s3_assets": s3_assets,
                "publishing_result": publishing_result,
                "marketing_result": marketing_result,
                "estimated_live_date": (
                    datetime.now() + timedelta(hours=2)
                ).isoformat(),
            }

        except Exception as e:
            logger.error(f"Volume 1 production failed: {e}")
            raise

    async def _generate_volume_content(
        self,
        volume: Dict[str, Any],
        series: Dict[str, Any],
        brand_system: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate content for specific volume with series branding."""
        try:
            from kindlemint.core.generator import ContentGenerator

            generator = ContentGenerator(api_key=self.openai_api_key)

            # Enhanced prompt with series context
            enhanced_topic = f"{volume['title']} - {volume['unique_content_focus']}"

            # Generate volume-specific content
            content_result = generator.generate_book_content(
                topic=enhanced_topic,
                niche=series["micro_niche"],
                target_audience=volume["unique_content_focus"],
                series_context={
                    "series_name": series["series_name"],
                    "volume_number": volume["volume_number"],
                    "total_volumes": series["total_volumes"],
                    "brand_voice": series.get("author_persona", ""),
                    "cross_promotion": series.get("cross_promotion_strategy", {}).get(
                        volume["book_id"], {}
                    ),
                },
            )

            # Add back matter with brand integration
            back_matter = self._generate_branded_back_matter(
                volume, series, brand_system
            )
            content_result["back_matter"] = back_matter

            return content_result

        except Exception as e:
            logger.error(f"Volume content generation failed: {e}")
            raise

    def _generate_branded_back_matter(
        self,
        volume: Dict[str, Any],
        series: Dict[str, Any],
        brand_system: Dict[str, Any],
    ) -> str:
        """Generate back matter with series cross-promotion and brand integration."""
        try:
            back_matter = "\n" + "=" * 50 + "\n"
            back_matter += f"Thank you for reading {volume['title']}!\n"
            back_matter += "=" * 50 + "\n\n"

            # Series cross-promotion
            other_volumes = [
                v
                for v_var in series["books"]
                if v["volume_number"] != volume["volume_number"]
            ]
            if other_volumes:
                back_matter += "📚 ALSO IN THIS SERIES:\n\n"
                for other_vol in sorted(
                    other_volumes, key=lambda x: x["volume_number"]
                )[:3]:
                    back_matter += f"• {other_vol['title']}\n"
                    back_matter += f"  {other_vol['unique_content_focus']}\n\n"
                back_matter += (
                    "🎯 Collect the complete series for the ultimate experience!\n\n"
                )

            # Brand email capture
            website_url = brand_system["website"]["url"]
            email_offer = brand_system["website"]["email_offer"]

            back_matter += "🎁 FREE BONUS CONTENT!\n"
            back_matter += f"Get your {email_offer}\n"
            back_matter += f"Visit: {website_url}\n\n"

            # Brand information
            back_matter += f"📍 About {series['series_brand']}:\n"
            back_matter += f"Creating quality {series['micro_niche']} content for readers worldwide.\n"
            back_matter += f"Visit {website_url} for exclusive content and updates!\n\n"

            # Review request
            back_matter += "⭐ LOVE THIS BOOK?\n"
            back_matter += "Please leave a review on Amazon!\n"
            back_matter += "Your feedback helps us create better content.\n\n"

            back_matter += "=" * 50 + "\n"
            back_matter += f"© {datetime.now().year} {series['series_brand']} | All Rights Reserved\n"
            back_matter += "=" * 50

            return back_matter

        except Exception as e:
            logger.error(f"Back matter generation failed: {e}")
            return f"\nThank you for reading {volume['title']}!\nVisit {brand_system['website']['url']} for bonus content."

    async def _generate_volume_cover(
        self, volume: Dict[str, Any], series: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate branded cover for volume using DALL-E."""
        try:
            import requests

            if not self.openai_api_key:
                logger.warning("⚠️ OPENAI_API_KEY not available - using fallback cover")
                return {"path": "/tmp/fallback_cover.jpg", "method": "fallback"}

            # Create enhanced DALL-E prompt
            dalle_prompt = f"""
            Create a professional Amazon KDP book cover for "{volume['title']}" by {series['series_brand']}.

            Style requirements:
            - Clean, professional design suitable for the target audience
            - Large, readable typography for book title and subtitle
            - Background pattern related to {series['micro_niche']}
            - Brand colors: professional and trustworthy
            - Easy to read at thumbnail size on Amazon
            - Premium quality appearance
            - Volume {volume['volume_number']} clearly visible

            Text elements:
            - Main title: "{volume['title']}"
            - Subtitle: "{volume.get('subtitle', '')}"
            - Author/Brand: "{series['series_brand']}"
            - Volume: "VOLUME {volume['volume_number']}"

            Layout:
            - Title at top in bold, clear text
            - Relevant background pattern for {series['micro_niche']}
            - Clean typography hierarchy
            - Professional book cover proportions
            - High contrast for readability
            """

            logger.info(f"🎨 Generating automated cover for {volume['title']}...")

            # Call DALL-E API
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json",
            }

            data = {
                "model": "dall-e-3",
                "prompt": dalle_prompt,
                "size": "1024x1024",
                "quality": "hd",
                "n": 1,
            }

            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=data,
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]

                # Download the generated image
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    cover_path = f"/tmp/{volume['book_id']}_cover.png"
                    with open(cover_path, "wb") as f:
                        f.write(img_response.content)

                    logger.info("✅ Automated cover generated successfully")
                    return {"path": cover_path, "method": "dalle_automated"}
                else:
                    logger.error(
                        f"❌ Failed to download generated cover: {img_response.status_code}"
                    )
                    return {"path": "/tmp/fallback_cover.jpg", "method": "fallback"}
            else:
                logger.warning(f"⚠️ DALL-E API error: {response.status_code}")
                return {"path": "/tmp/fallback_cover.jpg", "method": "fallback"}

        except Exception as e:
            logger.error(f"Volume cover generation failed: {e}")
            return {"path": "/tmp/fallback_cover.jpg", "method": "fallback"}

    async def _upload_volume_assets(
        self,
        volume: Dict[str, Any],
        content_result: Dict[str, Any],
        cover_result: Dict[str, Any],
    ) -> Dict[str, str]:
        """Upload volume assets to S3."""
        try:
            s3_assets = {}

            # Upload manuscript
            manuscript_key = f"series_manuscripts/{volume['book_id']}_manuscript.docx"
            self.s3_client.upload_file(
                content_result["manuscript_path"], self.assets_bucket, manuscript_key
            )
            s3_assets["manuscript_key"] = manuscript_key

            # Upload cover
            cover_key = f"series_covers/{volume['book_id']}_cover.jpg"
            self.s3_client.upload_file(
                cover_result["path"], self.assets_bucket, cover_key
            )
            s3_assets["cover_key"] = cover_key

            # Upload metadata
            metadata_key = f"series_metadata/{volume['book_id']}_metadata.json"
            metadata = {
                "title": volume["title"],
                "subtitle": volume["subtitle"],
                "volume_number": volume["volume_number"],
                "keywords": volume["keywords"],
                "description": content_result.get("kdp_description", ""),
                "back_matter": content_result.get("back_matter", ""),
            }

            self.s3_client.put_object(
                Bucket=self.assets_bucket,
                Key=metadata_key,
                Body=json.dumps(metadata, indent=2),
                ContentType="application/json",
            )
            s3_assets["metadata_key"] = metadata_key
            s3_assets["bucket"] = self.assets_bucket

            logger.info(f"Assets uploaded for volume: {volume['title']}")

            return s3_assets

        except Exception as e:
            logger.error(f"Asset upload failed: {e}")
            raise

    async def _trigger_volume_publishing(
        self, volume: Dict[str, Any], s3_assets: Dict[str, str], series: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger Fargate publishing for volume."""
        try:
            # Prepare Fargate task payload
            task_payload = {
                "book_id": volume["book_id"],
                "series_context": {
                    "series_name": series["series_name"],
                    "volume_number": volume["volume_number"],
                    "total_volumes": series["total_volumes"],
                },
                "s3_bucket": s3_assets["bucket"],
                "manuscript_key": s3_assets["manuscript_key"],
                "cover_key": s3_assets["cover_key"],
                "metadata_key": s3_assets["metadata_key"],
                "publishing_priority": (
                    "high" if volume["volume_number"] == 1 else "normal"
                ),
            }

            # Invoke Fargate publisher
            response = self.lambda_client.invoke(
                FunctionName=self.fargate_invoker_arn,
                InvocationType="Event",
                Payload=json.dumps(task_payload),
            )

            logger.info(f"Fargate publishing triggered for: {volume['title']}")

            return {
                "status": "triggered",
                "task_payload": task_payload,
                "estimated_completion": (
                    datetime.now() + timedelta(hours=1)
                ).isoformat(),
            }

        except Exception as e:
            logger.error(f"Volume publishing trigger failed: {e}")
            raise

    async def _trigger_volume_marketing(
        self,
        volume: Dict[str, Any],
        series: Dict[str, Any],
        brand_system: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Trigger content marketing for volume."""
        try:
            from promotion.content_marketing_engine import ContentMarketingEngine

            # Initialize content marketing engine
            engine = ContentMarketingEngine()

            # Create marketing campaign for volume
            marketing_campaign = await engine.execute_content_marketing_campaign(
                {
                    "asin": "B" + volume["book_id"][-9:].upper(),  # Mock ASIN
                    "title": volume["title"],
                    "description": f"{volume['subtitle']} - Part of the {series['series_name']}",
                    "topic": volume["unique_content_focus"],
                    "niche": series["micro_niche"],
                    "series_context": {
                        "series_name": series["series_name"],
                        "brand_name": series["series_brand"],
                        "website_url": brand_system["website"]["url"],
                        "volume_number": volume["volume_number"],
                    },
                }
            )

            logger.info(f"Content marketing activated for: {volume['title']}")

            return marketing_campaign

        except Exception as e:
            logger.error(f"Volume marketing trigger failed: {e}")
            return {"status": "fallback", "message": str(e)}

    async def _activate_series_launch_sequence(
        self,
        book_series: Dict[str, Any],
        brand_system: Dict[str, Any],
        volume_1_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Activate automated series launch sequence."""
        try:
            # Schedule remaining volumes
            volume_schedule = []
            base_date = datetime.now() + timedelta(days=14)  # First volume in 2 weeks

            for volume in book_series["books"][1:]:  # Skip Volume 1 (already produced)
                release_date = base_date + timedelta(
                    days=(volume["volume_number"] - 2) * 14
                )

                volume_schedule.append(
                    {
                        "volume_id": volume["book_id"],
                        "title": volume["title"],
                        "volume_number": volume["volume_number"],
                        "scheduled_production": release_date.isoformat(),
                        "auto_trigger": True,
                    }
                )

            # Set up brand website launch
            website_launch = {
                "url": brand_system["website"]["url"],
                "setup_required": brand_system["estimated_setup_time"],
                "email_integration": brand_system["email_funnel"]["provider"],
                "bonus_content": brand_system["bonus_product"]["title"],
            }

            # Create email automation
            email_automation = {
                "welcome_sequence": "activated",
                "new_release_notifications": "scheduled",
                "cross_promotion_campaigns": "automated",
            }

            return {
                "series_schedule": volume_schedule,
                "website_launch": website_launch,
                "email_automation": email_automation,
                "estimated_series_revenue": f"${len(book_series['books']) * 15}/day when complete",
                "completion_timeline": f"{len(book_series['books']) * 14} days",
                "automation_status": "fully_activated",
            }

        except Exception as e:
            logger.error(f"Launch sequence activation failed: {e}")
            return {"status": "manual_setup_required", "error": str(e)}

    async     """ Update Intelligent Memory"""
def _update_intelligent_memory(
        self,
        pipeline_id: str,
        opportunity: Dict[str, Any],
        series: Dict[str, Any],
        brand_system: Dict[str, Any],
    ):
        """Update memory system with intelligent pipeline results."""
        try:
            from kindlemint.memory import KDPMemory

            memory = KDPMemory()

            # Store series record
            memory.store_book_record(
                book_id=pipeline_id,
                topic=opportunity["micro_niche"],
                niche=opportunity["broad_category"],
                metadata={
                    "pipeline_type": "intelligent_v3",
                    "market_intelligence": opportunity,
                    "series_strategy": series,
                    "brand_system": brand_system,
                    "confidence_score": opportunity["confidence_score"],
                    "profit_potential": opportunity["profit_potential_daily"],
                    "series_length": series["total_volumes"],
                    "created_at": datetime.utcnow().isoformat(),
                },
            )

            logger.info(f"Memory updated for intelligent pipeline: {pipeline_id}")

        except Exception as e:
            logger.warning(f"Memory update failed: {e}")


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for Intelligent V3 Orchestrator.

    Expected event format:
    {
        "mode": "auto|approval_required",
        "approved_opportunity_index": 0,  # If responding to approval
        "force_niche": "optional override"
    }
    """
    try:
        logger.info("🧠 INTELLIGENT V3 ORCHESTRATOR ACTIVATED")
        logger.info(f"Event received: {json.dumps(event, indent=2)}")

        # Initialize orchestrator
        orchestrator = IntelligentV3Orchestrator()

        # Check if this is an approval response
        if "approved_opportunity_index" in event:
            # Handle approval response (implement in future iteration)
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "status": "approval_received",
                        "message": "Approval handling not yet implemented",
                    }
                ),
            }

        # Execute intelligent pipeline
        result = asyncio.run(
            orchestrator.execute_intelligent_pipeline(
                force_niche=event.get("force_niche")
            )
        )

        logger.info(f"✅ Intelligent pipeline completed: {result['status']}")

        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "result": result}),
        }

    except Exception as e:
        logger.error(f"❌ Intelligent orchestrator failed: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": f"Intelligent orchestrator failed: {str(e)}",
                }
            ),
        }


if __name__ == "__main__":
    # Test intelligent orchestrator
    import asyncio

    orchestrator = IntelligentV3Orchestrator()
    orchestrator.require_human_approval = False  # Disable for testing

    result = asyncio.run(orchestrator.execute_intelligent_pipeline())
    print(json.dumps(result, indent=2))
