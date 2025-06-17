"""
Autonomous KDP Ad Campaign Launcher
Automatically creates and launches Amazon KDP ad campaigns the moment a book goes live.

BUSINESS IMPACT: Immediate advertising activation, zero manual setup required
INTEGRATION: Triggered by V3 engine KDP success notification
"""
import json
import logging
import os
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

class AutonomousAdCampaignLauncher:
    """Automatically launches KDP ad campaigns using Amazon Advertising API."""
    
    def __init__(self):
        """Initialize the ad campaign launcher."""
        # Amazon Advertising API credentials
        self.client_id = os.getenv('AMAZON_ADS_CLIENT_ID')
        self.client_secret = os.getenv('AMAZON_ADS_CLIENT_SECRET') 
        self.refresh_token = os.getenv('AMAZON_ADS_REFRESH_TOKEN')
        self.profile_id = os.getenv('AMAZON_ADS_PROFILE_ID')
        
        # Campaign configuration
        self.default_budget = float(os.getenv('DEFAULT_AD_BUDGET', '10.0'))
        self.default_bid = float(os.getenv('DEFAULT_KEYWORD_BID', '0.35'))
        
        # Validate required credentials
        required_vars = [
            'AMAZON_ADS_CLIENT_ID', 'AMAZON_ADS_CLIENT_SECRET', 
            'AMAZON_ADS_REFRESH_TOKEN', 'AMAZON_ADS_PROFILE_ID'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                raise ValueError(f"Required environment variable {var} not set")
        
        self.access_token = None
        self.headers = None
    
    async def launch_autonomous_campaigns(self, book_data: Dict[str, Any]) -> Dict[str, Any]:
        """Launch complete autonomous ad campaign suite.
        
        Args:
            book_data: Dict containing asin, title, genre/keywords
            
        Returns:
            Dict with campaign creation results
        """
        try:
            asin = book_data['asin']
            title = book_data['title']
            genre = book_data.get('genre', 'general')
            keywords = book_data.get('keywords', [])
            
            logger.info(f"🎯 AUTONOMOUS AD CAMPAIGN LAUNCH for ASIN: {asin}")
            
            # Step 1: Authenticate with Amazon Advertising API
            await self._authenticate_amazon_ads_api()
            logger.info("🔐 Amazon Advertising API authenticated")
            
            # Step 2: Create Auto Campaign
            auto_campaign = await self._create_auto_campaign(asin, title)
            logger.info(f"🤖 Auto campaign created: {auto_campaign['campaign_id']}")
            
            # Step 3: Create Manual Keyword Campaign
            manual_campaign = await self._create_manual_campaign(asin, title, genre, keywords)
            logger.info(f"🎯 Manual campaign created: {manual_campaign['campaign_id']}")
            
            # Step 4: Log campaigns for optimization agent
            await self._log_campaigns_for_optimization([auto_campaign, manual_campaign])
            
            return {
                'status': 'success',
                'asin': asin,
                'campaigns_created': [auto_campaign, manual_campaign],
                'total_daily_budget': auto_campaign['daily_budget'] + manual_campaign['daily_budget'],
                'optimization_enabled': True,
                'next_optimization': (datetime.now() + timedelta(days=1)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Autonomous ad campaign launch failed: {str(e)}")
            raise
    
    async def _authenticate_amazon_ads_api(self):
        """Authenticate with Amazon Advertising API and get access token."""
        try:
            token_url = "https://api.amazon.com/auth/o2/token"
            
            payload = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(token_url, data=payload, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Set up headers for API requests
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Amazon-Advertising-API-ClientId': self.client_id,
                'Amazon-Advertising-API-Scope': self.profile_id
            }
            
        except Exception as e:
            logger.error(f"Amazon Ads API authentication failed: {e}")
            raise
    
    async def _create_auto_campaign(self, asin: str, title: str) -> Dict[str, Any]:
        """Create automatic targeting campaign."""
        try:
            campaign_name = f"AUTO_{asin}_{datetime.now().strftime('%Y%m%d')}"
            
            # Create campaign
            campaign_payload = {
                'name': campaign_name,
                'campaignType': 'sponsoredProducts',
                'targetingType': 'auto',
                'state': 'enabled',
                'dailyBudget': self.default_budget,
                'startDate': datetime.now().strftime('%Y%m%d'),
                'bidding': {
                    'strategy': 'legacyForSales'
                }
            }
            
            campaign_url = "https://advertising-api.amazon.com/v2/sp/campaigns"
            campaign_response = requests.post(
                campaign_url, 
                headers=self.headers, 
                json=campaign_payload,
                timeout=30
            )
            campaign_response.raise_for_status()
            campaign_data = campaign_response.json()
            
            campaign_id = campaign_data['campaignId']
            
            # Create ad group
            ad_group_payload = {
                'name': f"{campaign_name}_AdGroup",
                'campaignId': campaign_id,
                'defaultBid': self.default_bid,
                'state': 'enabled'
            }
            
            ad_group_url = "https://advertising-api.amazon.com/v2/sp/adGroups"
            ad_group_response = requests.post(
                ad_group_url,
                headers=self.headers,
                json=ad_group_payload,
                timeout=30
            )
            ad_group_response.raise_for_status()
            ad_group_data = ad_group_response.json()
            
            ad_group_id = ad_group_data['adGroupId']
            
            # Create product ad
            product_ad_payload = {
                'campaignId': campaign_id,
                'adGroupId': ad_group_id,
                'asin': asin,
                'state': 'enabled'
            }
            
            product_ad_url = "https://advertising-api.amazon.com/v2/sp/productAds"
            product_ad_response = requests.post(
                product_ad_url,
                headers=self.headers,
                json=product_ad_payload,
                timeout=30
            )
            product_ad_response.raise_for_status()
            
            # Create auto targeting
            auto_targeting_payload = {
                'campaignId': campaign_id,
                'adGroupId': ad_group_id,
                'state': 'enabled',
                'expressionType': 'auto',
                'expression': [{'type': 'asinCategorySameAs', 'value': asin}]
            }
            
            targeting_url = "https://advertising-api.amazon.com/v2/sp/targets"
            requests.post(
                targeting_url,
                headers=self.headers,
                json=auto_targeting_payload,
                timeout=30
            )
            
            return {
                'campaign_id': campaign_id,
                'campaign_name': campaign_name,
                'campaign_type': 'auto',
                'daily_budget': self.default_budget,
                'ad_group_id': ad_group_id,
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Auto campaign creation failed: {e}")
            raise
    
    async def _create_manual_campaign(self, asin: str, title: str, genre: str, keywords: List[str]) -> Dict[str, Any]:
        """Create manual keyword targeting campaign."""
        try:
            campaign_name = f"MANUAL_{asin}_{datetime.now().strftime('%Y%m%d')}"
            
            # Generate starter keywords based on genre
            starter_keywords = self._get_starter_keywords(genre, keywords)
            
            # Create campaign
            campaign_payload = {
                'name': campaign_name,
                'campaignType': 'sponsoredProducts',
                'targetingType': 'manual',
                'state': 'enabled',
                'dailyBudget': self.default_budget * 1.5,  # Higher budget for manual
                'startDate': datetime.now().strftime('%Y%m%d'),
                'bidding': {
                    'strategy': 'legacyForSales'
                }
            }
            
            campaign_url = "https://advertising-api.amazon.com/v2/sp/campaigns"
            campaign_response = requests.post(
                campaign_url,
                headers=self.headers,
                json=campaign_payload,
                timeout=30
            )
            campaign_response.raise_for_status()
            campaign_data = campaign_response.json()
            
            campaign_id = campaign_data['campaignId']
            
            # Create ad group
            ad_group_payload = {
                'name': f"{campaign_name}_AdGroup",
                'campaignId': campaign_id,
                'defaultBid': self.default_bid,
                'state': 'enabled'
            }
            
            ad_group_url = "https://advertising-api.amazon.com/v2/sp/adGroups"
            ad_group_response = requests.post(
                ad_group_url,
                headers=self.headers,
                json=ad_group_payload,
                timeout=30
            )
            ad_group_response.raise_for_status()
            ad_group_data = ad_group_response.json()
            
            ad_group_id = ad_group_data['adGroupId']
            
            # Create product ad
            product_ad_payload = {
                'campaignId': campaign_id,
                'adGroupId': ad_group_id,
                'asin': asin,
                'state': 'enabled'
            }
            
            product_ad_url = "https://advertising-api.amazon.com/v2/sp/productAds"
            requests.post(
                product_ad_url,
                headers=self.headers,
                json=product_ad_payload,
                timeout=30
            )
            
            # Create keywords
            created_keywords = []
            for keyword in starter_keywords:
                keyword_payload = {
                    'campaignId': campaign_id,
                    'adGroupId': ad_group_id,
                    'keywordText': keyword,
                    'matchType': 'broad',
                    'state': 'enabled',
                    'bid': self.default_bid
                }
                
                keyword_url = "https://advertising-api.amazon.com/v2/sp/keywords"
                keyword_response = requests.post(
                    keyword_url,
                    headers=self.headers,
                    json=keyword_payload,
                    timeout=30
                )
                
                if keyword_response.status_code == 200:
                    created_keywords.append(keyword)
            
            return {
                'campaign_id': campaign_id,
                'campaign_name': campaign_name,
                'campaign_type': 'manual',
                'daily_budget': self.default_budget * 1.5,
                'ad_group_id': ad_group_id,
                'keywords_added': len(created_keywords),
                'keywords': created_keywords,
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Manual campaign creation failed: {e}")
            raise
    
    def _get_starter_keywords(self, genre: str, existing_keywords: List[str]) -> List[str]:
        """Get starter keywords based on book genre."""
        genre_keywords = {
            'productivity': [
                'productivity book', 'time management', 'success book', 'efficiency guide',
                'business productivity', 'work optimization', 'goal achievement',
                'personal development', 'self improvement', 'success strategies'
            ],
            'finance': [
                'money management', 'financial planning', 'investing guide', 'wealth building',
                'personal finance', 'budgeting book', 'financial freedom', 'money book',
                'investment strategy', 'financial literacy'
            ],
            'health': [
                'health guide', 'wellness book', 'fitness guide', 'healthy living',
                'nutrition book', 'exercise guide', 'mental health', 'self care',
                'healthy habits', 'lifestyle book'
            ],
            'self-help': [
                'self help book', 'personal growth', 'motivation book', 'mindset book',
                'life improvement', 'success mindset', 'positive thinking', 'life guide',
                'transformation book', 'empowerment book'
            ],
            'business': [
                'business book', 'entrepreneurship', 'startup guide', 'business strategy',
                'leadership book', 'management guide', 'business success', 'entrepreneur guide',
                'business growth', 'marketing book'
            ]
        }
        
        # Get genre-specific keywords or general ones
        starter_keywords = genre_keywords.get(genre.lower(), genre_keywords['productivity'])
        
        # Add existing keywords
        all_keywords = starter_keywords + existing_keywords
        
        # Remove duplicates and limit to 20 keywords
        unique_keywords = list(set(all_keywords))[:20]
        
        return unique_keywords
    
    async def _log_campaigns_for_optimization(self, campaigns: List[Dict[str, Any]]):
        """Log campaign IDs for use by optimization agent."""
        try:
            # Store campaign data in DynamoDB for optimization agent
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table('KDP_Ad_Campaigns')  # Create this table
            
            for campaign in campaigns:
                table.put_item(
                    Item={
                        'campaign_id': campaign['campaign_id'],
                        'asin': campaign.get('asin'),
                        'campaign_type': campaign['campaign_type'],
                        'daily_budget': campaign['daily_budget'],
                        'created_date': datetime.now().isoformat(),
                        'status': 'active',
                        'optimization_enabled': True
                    }
                )
            
            logger.info(f"Logged {len(campaigns)} campaigns for optimization")
            
        except Exception as e:
            logger.warning(f"Failed to log campaigns for optimization: {e}")

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Lambda handler for autonomous ad campaign launch.
    
    Triggered by V3 engine's successful KDP publication.
    
    Expected event format:
    {
        "asin": "B123456789",
        "title": "Book Title",
        "genre": "productivity",
        "keywords": ["keyword1", "keyword2"],
        "trigger_source": "v3_kdp_success"
    }
    """
    try:
        logger.info("🎯 AUTONOMOUS AD CAMPAIGN LAUNCHER ACTIVATED")
        logger.info(f"Event: {json.dumps(event, indent=2)}")
        
        # Validate required fields
        if 'asin' not in event:
            raise ValueError("ASIN is required")
        
        # Execute autonomous ad campaign launch
        launcher = AutonomousAdCampaignLauncher()
        result = launcher.launch_autonomous_campaigns(event)
        
        logger.info("✅ Autonomous ad campaigns launched successfully")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': 'Autonomous ad campaigns launched successfully',
                'result': result
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Autonomous ad campaign launch failed: {str(e)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'message': f'Autonomous ad campaign launch failed: {str(e)}'
            })
        }

if __name__ == "__main__":
    # For local testing
    test_event = {
        "asin": "B123456789",
        "title": "The Ultimate Productivity Guide",
        "genre": "productivity",
        "keywords": ["productivity", "success", "efficiency"],
        "trigger_source": "v3_kdp_success"
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))