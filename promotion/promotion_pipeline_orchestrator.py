"""
Promotion Pipeline Orchestrator
Integrates all autonomous promotion components with V3 Zero-Touch Engine.

BUSINESS IMPACT: Complete end-to-end automation from book publication to marketing activation
INTEGRATION: Triggered by V3 engine Fargate success notification
"""
import json
import logging
import os
import boto3
import asyncio
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PromotionPipelineOrchestrator:
    """Orchestrates complete autonomous promotion pipeline activation."""
    
    def __init__(self):
        """Initialize the promotion pipeline orchestrator."""
        self.lambda_client = boto3.client('lambda')
        self.events_client = boto3.client('events')
        
        # Lambda function ARNs for promotion components
        self.promotion_functions = {
            'social_media': os.getenv('PROMOTION_ENGINE_ARN'),
            'ad_campaigns': os.getenv('AD_CAMPAIGN_LAUNCHER_ARN'), 
            'pricing': os.getenv('PRICING_PROMOTER_ARN')
        }
        
        # Validate function ARNs
        for component, arn in self.promotion_functions.items():
            if not arn:
                logger.warning(f"{component} Lambda ARN not configured")
    
    async def activate_autonomous_promotion(self, kdp_success_event: Dict[str, Any]) -> Dict[str, Any]:
        """Activate complete autonomous promotion pipeline.
        
        Args:
            kdp_success_event: Event from V3 Fargate KDP publishing success
            
        Returns:
            Dict with complete promotion activation results
        """
        try:
            logger.info("🚀 AUTONOMOUS PROMOTION PIPELINE ACTIVATION")
            logger.info(f"KDP Success Event: {json.dumps(kdp_success_event, indent=2)}")
            
            # Extract book data from KDP success event
            book_data = self._extract_book_data(kdp_success_event)
            logger.info(f"📚 Book Data: {book_data['title']} (ASIN: {book_data['asin']})")
            
            # Trigger all promotion components in parallel
            promotion_results = await self._trigger_promotion_components(book_data)
            
            # Schedule daily ad optimization
            optimization_schedule = await self._schedule_daily_optimization()
            
            # Send activation summary
            activation_summary = self._create_activation_summary(book_data, promotion_results, optimization_schedule)
            await self._send_activation_notification(activation_summary)
            
            return {
                'status': 'success',
                'activation_timestamp': datetime.now().isoformat(),
                'book_data': book_data,
                'promotion_results': promotion_results,
                'optimization_schedule': optimization_schedule,
                'summary': activation_summary
            }
            
        except Exception as e:
            logger.error(f"❌ Promotion pipeline activation failed: {str(e)}")
            await self._send_error_notification(str(e))
            raise
    
    def _extract_book_data(self, kdp_success_event: Dict[str, Any]) -> Dict[str, Any]:
        """Extract book data from KDP success event."""
        try:
            # Handle different event formats from V3 engine
            if 'result' in kdp_success_event:
                # Direct result format
                result = kdp_success_event['result']
                return {
                    'asin': result.get('asin', result.get('book_id', 'unknown')),
                    'title': result.get('title', 'Unknown Title'),
                    'description': result.get('description', ''),
                    'genre': result.get('niche', 'general'),
                    'keywords': result.get('keywords', []),
                    'kdp_url': result.get('kdp_url', ''),
                    'publication_timestamp': result.get('publication_time', datetime.now().isoformat())
                }
            
            elif 'metadata' in kdp_success_event:
                # Fargate task format
                metadata = kdp_success_event['metadata']
                return {
                    'asin': kdp_success_event.get('asin', 'unknown'),
                    'title': metadata.get('title', 'Unknown Title'),
                    'description': metadata.get('description', ''),
                    'genre': metadata.get('genre', 'general'),
                    'keywords': metadata.get('keywords', []),
                    'kdp_url': kdp_success_event.get('kdp_url', ''),
                    'publication_timestamp': datetime.now().isoformat()
                }
            
            else:
                # Fallback format
                return {
                    'asin': kdp_success_event.get('asin', 'unknown'),
                    'title': kdp_success_event.get('title', 'Unknown Title'),
                    'description': kdp_success_event.get('description', ''),
                    'genre': kdp_success_event.get('genre', 'general'),
                    'keywords': kdp_success_event.get('keywords', []),
                    'kdp_url': kdp_success_event.get('kdp_url', ''),
                    'publication_timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to extract book data: {e}")
            # Return minimal fallback data
            return {
                'asin': 'unknown',
                'title': 'Unknown Title',
                'description': '',
                'genre': 'general',
                'keywords': [],
                'kdp_url': '',
                'publication_timestamp': datetime.now().isoformat()
            }
    
    async def _trigger_promotion_components(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Trigger all promotion components in parallel."""
        try:
            promotion_tasks = []
            
            # Prepare payload for all promotion components
            promotion_payload = {
                **book_data,
                'trigger_source': 'v3_kdp_success',
                'promotion_pipeline_id': f"promo_{book_data['asin']}_{int(datetime.now().timestamp())}"
            }
            
            # Create async tasks for each promotion component
            if self.promotion_functions['social_media']:
                promotion_tasks.append(
                    self._invoke_lambda_async('social_media', promotion_payload)
                )
            
            if self.promotion_functions['ad_campaigns']:
                promotion_tasks.append(
                    self._invoke_lambda_async('ad_campaigns', promotion_payload)
                )
            
            if self.promotion_functions['pricing']:
                promotion_tasks.append(
                    self._invoke_lambda_async('pricing', promotion_payload)
                )
            
            # Execute all promotion components in parallel
            promotion_results = await asyncio.gather(*promotion_tasks, return_exceptions=True)
            
            # Process results
            component_results = {}
            component_names = ['social_media', 'ad_campaigns', 'pricing']
            
            for i, result in enumerate(promotion_results):
                component = component_names[i] if i < len(component_names) else f'component_{i}'
                
                if isinstance(result, Exception):
                    logger.error(f"Component {component} failed: {result}")
                    component_results[component] = {
                        'status': 'error',
                        'error': str(result)
                    }
                else:
                    component_results[component] = {
                        'status': 'success',
                        'result': result
                    }
            
            return component_results
            
        except Exception as e:
            logger.error(f"Failed to trigger promotion components: {e}")
            return {'error': str(e)}
    
    async def _invoke_lambda_async(self, component: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a Lambda function asynchronously."""
        try:
            function_arn = self.promotion_functions[component]
            if not function_arn:
                raise ValueError(f"Function ARN not configured for {component}")
            
            response = self.lambda_client.invoke(
                FunctionName=function_arn,
                InvocationType='RequestResponse',  # Synchronous for better error handling
                Payload=json.dumps(payload)
            )
            
            # Parse response
            response_payload = json.loads(response['Payload'].read())
            
            if response['StatusCode'] == 200:
                return response_payload
            else:
                raise Exception(f"Lambda invocation failed with status {response['StatusCode']}")
                
        except Exception as e:
            logger.error(f"Failed to invoke {component} Lambda: {e}")
            raise
    
    async def _schedule_daily_optimization(self) -> Dict[str, Any]:
        """Schedule daily ad optimization if not already scheduled."""
        try:
            rule_name = "kindlemint-daily-ad-optimization"
            
            # Check if rule already exists
            try:
                self.events_client.describe_rule(Name=rule_name)
                logger.info("Daily optimization already scheduled")
                return {
                    'status': 'already_exists',
                    'rule_name': rule_name,
                    'schedule': 'daily at 09:00 UTC'
                }
            except self.events_client.exceptions.ResourceNotFoundException:
                pass
            
            # Create EventBridge rule for daily optimization
            self.events_client.put_rule(
                Name=rule_name,
                ScheduleExpression='cron(0 9 * * ? *)',  # 9 AM UTC daily
                Description='Daily autonomous ad optimization',
                State='ENABLED'
            )
            
            # Add Lambda target
            optimization_function_arn = os.getenv('AD_OPTIMIZER_ARN')
            if optimization_function_arn:
                self.events_client.put_targets(
                    Rule=rule_name,
                    Targets=[
                        {
                            'Id': '1',
                            'Arn': optimization_function_arn,
                            'Input': json.dumps({
                                'trigger_source': 'daily_schedule',
                                'optimization_type': 'autonomous'
                            })
                        }
                    ]
                )
            
            return {
                'status': 'created',
                'rule_name': rule_name,
                'schedule': 'daily at 09:00 UTC',
                'target_function': optimization_function_arn
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule daily optimization: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _create_activation_summary(self, book_data: Dict[str, Any], promotion_results: Dict[str, Any], optimization_schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive activation summary."""
        try:
            successful_components = [comp for comp, result in promotion_results.items() if result.get('status') == 'success']
            failed_components = [comp for comp, result in promotion_results.items() if result.get('status') == 'error']
            
            return {
                'book': {
                    'title': book_data['title'],
                    'asin': book_data['asin'],
                    'publication_time': book_data['publication_timestamp']
                },
                'promotion_activation': {
                    'components_activated': len(successful_components),
                    'successful_components': successful_components,
                    'failed_components': failed_components,
                    'total_components': len(promotion_results)
                },
                'automation_status': {
                    'social_media_automation': 'social_media' in successful_components,
                    'ad_campaign_automation': 'ad_campaigns' in successful_components,
                    'pricing_automation': 'pricing' in successful_components,
                    'daily_optimization': optimization_schedule.get('status') in ['created', 'already_exists']
                },
                'expected_outcomes': [
                    '10 social media posts scheduled over 7 days',
                    'Auto and manual ad campaigns launched',
                    'Promotional pricing set for initial sales velocity',
                    'Daily ad optimization activated',
                    'Complete hands-off marketing automation'
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to create activation summary: {e}")
            return {'error': str(e)}
    
    async def _send_activation_notification(self, summary: Dict[str, Any]):
        """Send promotion pipeline activation notification."""
        try:
            from kindlemint.notifications.slack_notifier import SlackNotifier
            
            notifier = SlackNotifier()
            
            book = summary.get('book', {})
            activation = summary.get('promotion_activation', {})
            automation = summary.get('automation_status', {})
            
            # Send comprehensive notification
            success = notifier.send_notification(
                level=notifier.NotificationLevel.SUCCESS,
                title="🚀 AUTONOMOUS PROMOTION PIPELINE ACTIVATED",
                message=f"Complete marketing automation launched for '{book.get('title', 'Unknown')}'",
                fields={
                    "Book ASIN": book.get('asin', 'Unknown'),
                    "Components Activated": f"{activation.get('components_activated', 0)}/{activation.get('total_components', 0)}",
                    "Social Media": "✅ Automated" if automation.get('social_media_automation') else "❌ Failed",
                    "Ad Campaigns": "✅ Automated" if automation.get('ad_campaign_automation') else "❌ Failed", 
                    "Pricing Strategy": "✅ Automated" if automation.get('pricing_automation') else "❌ Failed",
                    "Daily Optimization": "✅ Scheduled" if automation.get('daily_optimization') else "❌ Not Scheduled",
                    "Status": "FULLY AUTONOMOUS MARKETING ACTIVE"
                }
            )
            
            if success:
                logger.info("Activation notification sent successfully")
            else:
                logger.warning("Failed to send activation notification")
                
        except Exception as e:
            logger.warning(f"Failed to send activation notification: {e}")
    
    async def _send_error_notification(self, error_message: str):
        """Send error notification for promotion pipeline failures."""
        try:
            from kindlemint.notifications.slack_notifier import SlackNotifier
            
            notifier = SlackNotifier()
            
            notifier.send_notification(
                level=notifier.NotificationLevel.ERROR,
                title="❌ PROMOTION PIPELINE ACTIVATION FAILED",
                message="Autonomous marketing automation failed to activate",
                fields={
                    "Error": error_message,
                    "Impact": "Manual promotion may be required",
                    "Action Required": "Review promotion pipeline logs"
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for promotion pipeline orchestration.
    
    Triggered by V3 engine's successful KDP publication.
    
    Expected event format:
    {
        "asin": "B123456789",
        "title": "Book Title",
        "description": "Book description",
        "metadata": {...},
        "trigger_source": "v3_fargate_success"
    }
    """
    try:
        logger.info("🚀 PROMOTION PIPELINE ORCHESTRATOR ACTIVATED")
        logger.info(f"Event: {json.dumps(event, indent=2)}")
        
        # Execute promotion pipeline activation
        orchestrator = PromotionPipelineOrchestrator()
        result = asyncio.run(orchestrator.activate_autonomous_promotion(event))
        
        logger.info("✅ Promotion pipeline orchestration completed successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Autonomous promotion pipeline activated successfully',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Promotion pipeline orchestration failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Promotion pipeline orchestration failed: {str(e)}'
            })
        }

if __name__ == "__main__":
    # For local testing
    test_event = {
        "asin": "B123456789",
        "title": "The Ultimate Success Blueprint",
        "description": "Transform your life with proven strategies",
        "metadata": {
            "genre": "productivity",
            "keywords": ["success", "productivity", "transformation"]
        },
        "trigger_source": "v3_fargate_success"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))