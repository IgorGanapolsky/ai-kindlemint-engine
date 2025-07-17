"""
SendGrid Email Client for KindleMint

Handles all email operations including:
- Lead magnet delivery
- Email sequences
- Transactional emails
- Analytics tracking
"""

import os
import base64
import logging
from typing import Dict, Optional, Any

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import (
        Mail, Attachment, FileContent, FileName, 
        FileType, Disposition, Email, Personalization,
        TrackingSettings, ClickTracking, OpenTracking
    )
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    
logger = logging.getLogger(__name__)


class SendGridClient:
    """SendGrid email client for KindleMint"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SendGrid client
        
        Args:
            api_key: SendGrid API key (or use SENDGRID_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        
        if not self.api_key:
            logger.warning("No SendGrid API key provided. Email sending disabled.")
            self.client = None
        elif not SENDGRID_AVAILABLE:
            logger.warning("SendGrid package not installed. Run: pip install sendgrid")
            self.client = None
        else:
            self.client = SendGridAPIClient(self.api_key)
            logger.info("✉️ SendGrid client initialized")
    
    def send_lead_magnet(
        self, 
        email: str, 
        first_name: str,
        lead_magnet_path: str,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send lead magnet email with PDF attachment
        
        Args:
            email: Recipient email
            first_name: Recipient first name
            lead_magnet_path: Path to lead magnet PDF
            template_id: Optional SendGrid template ID
            
        Returns:
            Dict with success status and details
        """
        if not self.client:
            return {
                'success': False,
                'error': 'SendGrid client not initialized'
            }
        
        try:
            # Read the PDF file
            with open(lead_magnet_path, 'rb') as f:
                pdf_data = f.read()
            
            # Create attachment
            encoded_pdf = base64.b64encode(pdf_data).decode()
            attachment = Attachment(
                FileContent(encoded_pdf),
                FileName('5_FREE_Brain_Boosting_Puzzles.pdf'),
                FileType('application/pdf'),
                Disposition('attachment')
            )
            
            # Create email
            if template_id:
                # Use dynamic template
                message = Mail(
                    from_email=Email('puzzles@kindlemint.com', 'KindleMint Puzzles'),
                    to_emails=email
                )
                message.template_id = template_id
                message.dynamic_template_data = {
                    'first_name': first_name,
                    'subject': 'Your FREE Brain-Boosting Puzzles Are Here!'
                }
            else:
                # Use inline content
                message = Mail(
                    from_email=Email('puzzles@kindlemint.com', 'KindleMint Puzzles'),
                    to_emails=email,
                    subject='Your FREE Brain-Boosting Puzzles Are Here!',
                    html_content=self._get_lead_magnet_html(first_name)
                )
            
            # Add attachment
            message.attachment = attachment
            
            # Add tracking
            message.tracking_settings = TrackingSettings(
                click_tracking=ClickTracking(True, True),
                open_tracking=OpenTracking(True)
            )
            
            # Send email
            response = self.client.send(message)
            
            logger.info(f"✅ Lead magnet sent to {email}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send lead magnet: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_sequence_email(
        self,
        email: str,
        first_name: str,
        sequence_day: int,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send email from nurture sequence
        
        Args:
            email: Recipient email
            first_name: Recipient first name
            sequence_day: Day in sequence (1-7)
            template_id: Optional SendGrid template ID
            
        Returns:
            Dict with success status
        """
        if not self.client:
            return {
                'success': False,
                'error': 'SendGrid client not initialized'
            }
        
        try:
            # Get sequence content
            sequence_data = self._get_sequence_content(sequence_day)
            
            if template_id:
                # Use dynamic template
                message = Mail(
                    from_email=Email('puzzles@kindlemint.com', 'KindleMint Puzzles'),
                    to_emails=email
                )
                message.template_id = template_id
                message.dynamic_template_data = {
                    'first_name': first_name,
                    'day': sequence_day,
                    **sequence_data
                }
            else:
                # Use inline content
                message = Mail(
                    from_email=Email('puzzles@kindlemint.com', 'KindleMint Puzzles'),
                    to_emails=email,
                    subject=sequence_data['subject'],
                    html_content=sequence_data['html_content'].format(first_name=first_name)
                )
            
            # Add tracking
            message.tracking_settings = TrackingSettings(
                click_tracking=ClickTracking(True, True),
                open_tracking=OpenTracking(True)
            )
            
            # Send email
            response = self.client.send(message)
            
            logger.info(f"✅ Sequence email day {sequence_day} sent to {email}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id')
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send sequence email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_lead_magnet_html(self, first_name: str) -> str:
        """Get HTML content for lead magnet email"""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2E3440;">Welcome {first_name}!</h2>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Thank you for joining our brain-boosting community. Your 5 FREE 
                large print Sudoku puzzles are attached to this email.
            </p>
            
            <div style="background: #ECEFF4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #5E81AC; margin-top: 0;">What's Included:</h3>
                <ul style="font-size: 16px;">
                    <li>5 carefully selected easy Sudoku puzzles</li>
                    <li>Extra-large 20pt print that's easy on your eyes</li>
                    <li>Clear instructions for beginners</li>
                    <li>Complete solutions for checking your work</li>
                </ul>
            </div>
            
            <p style="font-size: 16px; line-height: 1.6;">
                Print them out, grab your favorite pencil, and enjoy the mental 
                stimulation these puzzles provide!
            </p>
            
            <p style="font-size: 16px; line-height: 1.6;">
                <strong>Tip:</strong> Try to solve one puzzle each morning with 
                your coffee or tea. It's a great way to wake up your brain!
            </p>
            
            <hr style="border: 1px solid #D8DEE9; margin: 30px 0;">
            
            <p style="font-size: 14px; color: #4C566A;">
                Happy solving,<br>
                The KindleMint Puzzles Team
            </p>
            
            <p style="font-size: 12px; color: #4C566A; margin-top: 30px;">
                P.S. Keep an eye on your inbox - I'll be sending you more 
                brain-boosting tips and exclusive puzzle offers over the next few days!
            </p>
        </div>
        """
    
    def _get_sequence_content(self, day: int) -> Dict[str, str]:
        """Get email content for specific day in sequence"""
        sequences = {
            1: {
                'subject': 'Did you try puzzle #3 yet? (It\'s the tricky one)',
                'html_content': """
                <h2>Hi {first_name}!</h2>
                <p>I hope you've had a chance to print out your puzzles.</p>
                <p>Puzzle #3 is my favorite - it looks simple but has a clever twist 
                in the middle section. Let me know if you get stuck!</p>
                <p>By the way, if you're enjoying these puzzles, you'll love our 
                Large Print Sudoku Masters Volume 1 with 100 more brain-boosters.</p>
                <p><a href="#">Check it out here</a> (20% off for email subscribers)</p>
                """
            },
            3: {
                'subject': 'Here are 5 MORE free puzzles for you!',
                'html_content': """
                <h2>Surprise, {first_name}!</h2>
                <p>You've been such an engaged member of our community that I wanted 
                to send you 5 MORE free puzzles as a thank you.</p>
                <p>These are slightly more challenging than the first set - perfect 
                for when you're ready to level up your skills.</p>
                <p><a href="#">Download your bonus puzzles here</a></p>
                """
            },
            7: {
                'subject': 'Ready for 100 more brain-boosting puzzles?',
                'html_content': """
                <h2>{first_name}, you're a puzzle master!</h2>
                <p>You've been part of our community for a week now, and I hope 
                you've been enjoying the mental exercise.</p>
                <p>If you're ready for more, our Large Print Sudoku Masters Volume 1 
                has 100 carefully crafted puzzles waiting for you.</p>
                <p><strong>Special offer:</strong> Use code BRAIN20 for 20% off</p>
                <p><a href="#">Get your copy here</a></p>
                """
            }
        }
        
        return sequences.get(day, sequences[1])