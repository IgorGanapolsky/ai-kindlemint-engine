"""
Email Automation System for KindleMint

Manages automated email sequences, triggers, and subscriber lifecycle
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .sendgrid_client import SendGridClient
from ..analytics import ConversionTracker

logger = logging.getLogger(__name__)


class EmailAutomation:
    """Automated email sequence manager"""
    
    def __init__(self, sendgrid_client: Optional[SendGridClient] = None):
        """
        Initialize email automation
        
        Args:
            sendgrid_client: SendGrid client instance
        """
        self.sendgrid = sendgrid_client or SendGridClient()
        self.sequences = self._load_sequences()
        self.subscriber_db = Path('/tmp/email_automation.json')
        self.tracker = ConversionTracker()
        
        # Initialize subscriber database
        if not self.subscriber_db.exists():
            self._init_subscriber_db()
        
        logger.info("📧 Email automation system initialized")
    
    def _init_subscriber_db(self):
        """Initialize subscriber database"""
        data = {
            'subscribers': {},
            'sequences': {},
            'stats': {
                'total_subscribers': 0,
                'emails_sent': 0,
                'conversions': 0
            }
        }
        with open(self.subscriber_db, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_sequences(self) -> Dict[str, Dict]:
        """Load email sequence definitions"""
        return {
            'sudoku_lead_magnet': {
                'name': 'Sudoku Lead Magnet Nurture',
                'trigger': 'subscription',
                'emails': [
                    {
                        'day': 0,
                        'type': 'lead_magnet',
                        'subject': 'Your FREE Brain-Boosting Puzzles Are Here!'
                    },
                    {
                        'day': 1,
                        'type': 'nurture',
                        'subject': 'Did you try puzzle #3 yet? (It\'s the tricky one)'
                    },
                    {
                        'day': 3,
                        'type': 'bonus',
                        'subject': 'Here are 5 MORE free puzzles for you!'
                    },
                    {
                        'day': 7,
                        'type': 'sales',
                        'subject': 'Ready for 100 more brain-boosting puzzles?'
                    },
                    {
                        'day': 14,
                        'type': 'testimonial',
                        'subject': 'How Margaret solved 100 puzzles in 2 weeks'
                    },
                    {
                        'day': 21,
                        'type': 'final_offer',
                        'subject': 'Last chance: 30% off Large Print Sudoku Masters'
                    }
                ]
            }
        }
    
    def add_subscriber(
        self, 
        email: str, 
        first_name: str,
        sequence: str = 'sudoku_lead_magnet',
        tags: List[str] = None,
        lead_magnet_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add subscriber and start email sequence
        
        Args:
            email: Subscriber email
            first_name: Subscriber first name
            sequence: Email sequence to enroll in
            tags: Additional tags
            lead_magnet_path: Path to lead magnet file
            
        Returns:
            Dict with success status
        """
        try:
            # Load database
            with open(self.subscriber_db, 'r') as f:
                db = json.load(f)
            
            # Check if already subscribed
            if email in db['subscribers']:
                return {
                    'success': False,
                    'error': 'Already subscribed'
                }
            
            # Add subscriber
            subscriber_data = {
                'email': email,
                'first_name': first_name,
                'subscribed_at': datetime.now().isoformat(),
                'sequence': sequence,
                'sequence_started': datetime.now().isoformat(),
                'tags': tags or ['sudoku_lead_magnet'],
                'emails_sent': [],
                'conversions': [],
                'status': 'active'
            }
            
            db['subscribers'][email] = subscriber_data
            db['stats']['total_subscribers'] += 1
            
            # Save database
            with open(self.subscriber_db, 'w') as f:
                json.dump(db, f, indent=2)
            
            # Send welcome email with lead magnet
            if lead_magnet_path and self.sendgrid:
                result = self.sendgrid.send_lead_magnet(
                    email=email,
                    first_name=first_name,
                    lead_magnet_path=lead_magnet_path
                )
                
                if result['success']:
                    self._record_email_sent(email, 'lead_magnet', 0)
                    logger.info(f"✅ Lead magnet sent to {email}")
                else:
                    logger.error(f"❌ Failed to send lead magnet: {result.get('error')}")
            
            return {
                'success': True,
                'subscriber': subscriber_data
            }
            
        except Exception as e:
            logger.error(f"Failed to add subscriber: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_sequences(self) -> Dict[str, Any]:
        """
        Process all active email sequences
        
        This should be run daily to send scheduled emails
        
        Returns:
            Dict with processing results
        """
        results = {
            'processed': 0,
            'emails_sent': 0,
            'errors': []
        }
        
        try:
            # Load database
            with open(self.subscriber_db, 'r') as f:
                db = json.load(f)
            
            # Process each active subscriber
            for email, subscriber in db['subscribers'].items():
                if subscriber['status'] != 'active':
                    continue
                
                results['processed'] += 1
                
                # Get sequence definition
                sequence_name = subscriber['sequence']
                if sequence_name not in self.sequences:
                    continue
                
                sequence = self.sequences[sequence_name]
                
                # Calculate days since subscription
                subscribed_date = datetime.fromisoformat(subscriber['subscribed_at'])
                days_since = (datetime.now() - subscribed_date).days
                
                # Check which emails to send
                for email_def in sequence['emails']:
                    email_day = email_def['day']
                    email_type = email_def['type']
                    
                    # Skip if not time yet
                    if days_since < email_day:
                        continue
                    
                    # Skip if already sent
                    email_id = f"{email_type}_{email_day}"
                    if email_id in subscriber.get('emails_sent', []):
                        continue
                    
                    # Send email
                    if self._send_sequence_email(
                        subscriber, 
                        email_def, 
                        days_since
                    ):
                        results['emails_sent'] += 1
                        self._record_email_sent(email, email_type, email_day)
                    else:
                        results['errors'].append(f"Failed to send {email_id} to {email}")
            
            logger.info(f"📧 Processed {results['processed']} subscribers, sent {results['emails_sent']} emails")
            return results
            
        except Exception as e:
            logger.error(f"Failed to process sequences: {e}")
            results['errors'].append(str(e))
            return results
    
    def _send_sequence_email(
        self, 
        subscriber: Dict, 
        email_def: Dict,
        days_since: int
    ) -> bool:
        """Send a specific sequence email"""
        email_type = email_def['type']
        
        if email_type == 'nurture':
            result = self.sendgrid.send_sequence_email(
                email=subscriber['email'],
                first_name=subscriber['first_name'],
                sequence_day=email_def['day']
            )
        elif email_type == 'bonus':
            # Send bonus puzzles
            result = self._send_bonus_puzzles(subscriber, email_def)
        elif email_type == 'sales':
            # Send sales email
            result = self._send_sales_email(subscriber, email_def)
        else:
            # Default sequence email
            result = self.sendgrid.send_sequence_email(
                email=subscriber['email'],
                first_name=subscriber['first_name'],
                sequence_day=email_def['day']
            )
        
        return result.get('success', False)
    
    def _send_bonus_puzzles(self, subscriber: Dict, email_def: Dict) -> Dict:
        """Send bonus puzzle email"""
        # In production, generate new puzzles and attach
        return self.sendgrid.send_sequence_email(
            email=subscriber['email'],
            first_name=subscriber['first_name'],
            sequence_day=email_def['day']
        )
    
    def _send_sales_email(self, subscriber: Dict, email_def: Dict) -> Dict:
        """Send sales email with special offer"""
        return self.sendgrid.send_sequence_email(
            email=subscriber['email'],
            first_name=subscriber['first_name'],
            sequence_day=email_def['day']
        )
    
    def _record_email_sent(self, email: str, email_type: str, day: int):
        """Record that an email was sent"""
        try:
            # Track in analytics system
            self.tracker.track_event(
                "email_sent",
                email,
                {
                    "email_type": email_type,
                    "sequence_day": day
                }
            )
            
            # Also record in local database
            with open(self.subscriber_db, 'r') as f:
                db = json.load(f)
            
            email_id = f"{email_type}_{day}"
            if email in db['subscribers']:
                if 'emails_sent' not in db['subscribers'][email]:
                    db['subscribers'][email]['emails_sent'] = []
                
                db['subscribers'][email]['emails_sent'].append(email_id)
                db['stats']['emails_sent'] += 1
            
            with open(self.subscriber_db, 'w') as f:
                json.dump(db, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to record email sent: {e}")
    
    def record_conversion(self, email: str, product: str, amount: float):
        """Record a conversion from email subscriber"""
        try:
            # Track in analytics system
            self.tracker.track_purchase(email, product, amount)
            
            # Also record in local database
            with open(self.subscriber_db, 'r') as f:
                db = json.load(f)
            
            if email in db['subscribers']:
                if 'conversions' not in db['subscribers'][email]:
                    db['subscribers'][email]['conversions'] = []
                
                db['subscribers'][email]['conversions'].append({
                    'product': product,
                    'amount': amount,
                    'date': datetime.now().isoformat()
                })
                
                db['stats']['conversions'] += 1
            
            with open(self.subscriber_db, 'w') as f:
                json.dump(db, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to record conversion: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get email automation statistics"""
        try:
            with open(self.subscriber_db, 'r') as f:
                db = json.load(f)
            
            stats = db['stats'].copy()
            
            # Calculate additional metrics
            active_subscribers = sum(
                1 for s in db['subscribers'].values() 
                if s['status'] == 'active'
            )
            
            total_conversions_value = sum(
                conv['amount']
                for subscriber in db['subscribers'].values()
                for conv in subscriber.get('conversions', [])
            )
            
            stats.update({
                'active_subscribers': active_subscribers,
                'total_conversions_value': total_conversions_value,
                'avg_conversion_value': (
                    total_conversions_value / stats['conversions'] 
                    if stats['conversions'] > 0 else 0
                )
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}