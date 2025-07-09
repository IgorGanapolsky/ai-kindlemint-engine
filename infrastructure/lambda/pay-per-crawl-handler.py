import json
import boto3
from datetime import datetime

# AI crawler user agents
AI_CRAWLERS = [
    'GPTBot', 'ChatGPT-User', 'Claude-Web', 'Bard',
    'bingbot', 'Googlebot', 'facebookexternalhit', 'Twitterbot'
]

def lambda_handler(event, context):
    """Handle Pay-Per-Crawl detection and analytics"""
    
    # Get user agent from CloudFront headers
    headers = event.get('headers', {})
    user_agent = headers.get('user-agent', [''])[0] if isinstance(headers.get('user-agent'), list) else headers.get('user-agent', '')
    
    # Check if AI crawler
    is_ai_crawler = any(bot.lower() in user_agent.lower() for bot in AI_CRAWLERS)
    
    # Determine payment status (will integrate with Cloudflare later)
    is_paying = False  # Default to free tier
    
    if is_ai_crawler:
        # Log crawler visit to DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('KindleMint-Crawler-Analytics')
        
        try:
            table.put_item(
                Item={
                    'timestamp': datetime.utcnow().isoformat(),
                    'crawler_type': next((bot for bot in AI_CRAWLERS if bot.lower() in user_agent.lower()), 'Unknown'),
                    'user_agent': user_agent,
                    'payment_status': 'paid' if is_paying else 'free',
                    'path': event.get('path', '/'),
                    'revenue': 0.05 if is_paying else 0
                }
            )
        except:
            pass  # Don't fail request if analytics fails
    
    # Return appropriate response
    if event.get('path') == '/api/crawler-analytics':
        # Analytics endpoint
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'totalCrawlers': 0,  # Will implement aggregation
                'revenue': {
                    'today': 0,
                    'month': 0,
                    'total': 0
                },
                'crawlerTypes': {},
                'message': 'Analytics endpoint active'
            })
        }
    
    # For content requests, add crawler info headers
    response_headers = {
        'X-Is-AI-Crawler': str(is_ai_crawler).lower(),
        'X-Crawler-Payment': 'paid' if is_paying else 'free',
        'X-Crawler-Type': next((bot for bot in AI_CRAWLERS if bot.lower() in user_agent.lower()), 'none'),
        'Cache-Control': 'no-cache' if is_ai_crawler else 'public, max-age=3600'
    }
    
    return {
        'statusCode': 200,
        'headers': response_headers,
        'body': json.dumps({
            'isAICrawler': is_ai_crawler,
            'isPaying': is_paying,
            'message': 'Pay-Per-Crawl detection active'
        })
    }