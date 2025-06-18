"""
Autonomous Niche Research Agent - Continuous opportunity discovery
Runs independently to find profitable niches and populate portfolio
"""
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Niche Research Agent Lambda handler.
    Runs daily to discover new profitable opportunities.
    """
    try:
        logger.info("🔍 NICHE RESEARCH AGENT ACTIVATED")
        logger.info(f"Event received: {json.dumps(event, indent=2)}")
        
        # Import dependencies
        from kindlemint.intelligence.market_scout import MarketScout
        from kindlemint.portfolio.portfolio_manager import PortfolioManager
        
        # Initialize components
        scout = MarketScout()
        portfolio = PortfolioManager()
        
        # Configuration
        max_opportunities = event.get('max_opportunities', 3)
        research_source = event.get('source', 'scheduled_daily')
        
        logger.info(f"🎯 Research parameters:")
        logger.info(f"   Max opportunities: {max_opportunities}")
        logger.info(f"   Source: {research_source}")
        
        # Execute niche discovery
        logger.info("🔍 Scanning market for profitable opportunities...")
        opportunities = scout.discover_profitable_micro_niches(max_niches=max_opportunities)
        
        # Process each opportunity
        results = []
        for opportunity in opportunities:
            try:
                # Enhance opportunity data
                enhanced_opportunity = {
                    **opportunity,
                    'research_date': datetime.utcnow().isoformat(),
                    'research_source': research_source,
                    'market_intelligence_version': '3.0'
                }
                
                # Add to portfolio tracker
                series_id = portfolio.add_new_opportunity(enhanced_opportunity)
                
                results.append({
                    'series_id': series_id,
                    'niche': opportunity['niche'],
                    'topic': opportunity['topic'],
                    'market_score': opportunity.get('market_score', 0),
                    'estimated_revenue': opportunity.get('estimated_revenue', 0),
                    'status': 'AWAITING_APPROVAL'
                })
                
                logger.info(f"✅ Added opportunity: {opportunity['niche']} (Score: {opportunity.get('market_score', 0)})")
                
            except Exception as e:
                logger.error(f"Failed to process opportunity {opportunity.get('niche', 'Unknown')}: {e}")
                continue
        
        # Send notification to CEO about new opportunities
        if results:
            send_ceo_notification(results)
        
        logger.info(f"✅ Niche research completed: {len(results)} opportunities added")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': f'Niche research completed successfully',
                'opportunities_found': len(results),
                'results': results,
                'research_source': research_source,
                'version': '3.0'
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Niche research failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Niche research failed: {str(e)}',
                'research_source': event.get('source', 'unknown'),
                'version': '3.0'
            })
        }

def send_ceo_notification(opportunities: list):
    """Send Slack notification about new opportunities."""
    try:
        import requests
        
        slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
        if not slack_webhook:
            logger.warning("No Slack webhook configured")
            return
        
        # Format opportunities for CEO review
        opportunity_text = "\n".join([
            f"• *{opp['niche']}*: {opp['topic']} (Score: {opp['market_score']}, Est: ${opp['estimated_revenue']}/day)"
            for opp in opportunities
        ])
        
        message = {
            "text": "🔍 NEW PROFITABLE OPPORTUNITIES DISCOVERED",
            "attachments": [
                {
                    "color": "good",
                    "fields": [
                        {
                            "title": f"🎯 {len(opportunities)} New Opportunities Awaiting Approval",
                            "value": opportunity_text,
                            "short": False
                        },
                        {
                            "title": "Next Action",
                            "value": "Review and approve profitable series for production",
                            "short": True
                        },
                        {
                            "title": "Research Date", 
                            "value": datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(slack_webhook, json=message, timeout=10)
        if response.status_code == 200:
            logger.info("✅ CEO notification sent successfully")
        else:
            logger.warning(f"Slack notification failed: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Failed to send CEO notification: {e}")

if __name__ == "__main__":
    # For local testing
    test_event = {
        "max_opportunities": 2,
        "source": "manual_test"
    }
    
    class MockContext:
        def __init__(self):
            self.function_name = "niche-research-agent"
            self.memory_limit_in_mb = 512
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))