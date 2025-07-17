
import json
import boto3

def lambda_handler(event, context):
    '''
    Auto-responds to B2B inquiries with puzzle samples
    Runs on AWS Lambda - you're already paying for AWS
    '''
    
    # Extract email from S3 event or API Gateway
    email = event.get('email')
    
    # Auto-response template
    response_text = '''
    Thank you for your interest in our large-print puzzle program!
    
    I'm attaching your FREE 2-week trial pack which includes:
    - 20 large-print puzzles
    - Activity implementation guide
    - Progress tracking sheets
    
    These puzzles have helped facilities:
    • Increase activity participation by 40%
    • Reduce resident anxiety
    • Save 5+ hours/week in planning time
    
    To get started:
    1. Print the puzzles (they're already large-print optimized)
    2. Try them with 5-10 residents
    3. Track engagement using our sheets
    
    After your trial, our full program is just $197/month for 50 puzzles
    or $497/month for 200 puzzles with white-label options.
    
    Questions? Just reply to this email.
    
    Best regards,
    The Puzzle Team
    '''
    
    # Use SES (you have AWS already) to send email
    ses = boto3.client('ses', region_name='us-east-1')
    
    ses.send_email(
        Source='puzzles@your-domain.com',
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Your Free Puzzle Trial Pack is Here!'},
            'Body': {'Text': {'Data': response_text}}
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully')
    }
