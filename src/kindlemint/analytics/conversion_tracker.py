"""
Conversion Tracking and Analytics System

Tracks user journey from landing page to purchase:
1. Landing page visits
2. Email signups
3. Lead magnet downloads
4. Email engagement (opens/clicks)
5. Sales conversions
6. Revenue attribution
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import hashlib


class ConversionTracker:
    """Track conversions and generate analytics for email funnel"""
    
    def __init__(self, data_dir: str = "data/analytics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tracking files
        self.events_file = self.data_dir / "conversion_events.json"
        self.users_file = self.data_dir / "user_journeys.json"
        self.revenue_file = self.data_dir / "revenue_tracking.json"
        
        # Load existing data
        self.events = self._load_json(self.events_file, default=[])
        self.users = self._load_json(self.users_file, default={})
        self.revenue = self._load_json(self.revenue_file, default={})
    
    def _load_json(self, file_path: Path, default=None):
        """Load JSON file or return default"""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return default if default is not None else {}
    
    def _save_json(self, data: Any, file_path: Path):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _get_user_id(self, email: str) -> str:
        """Generate consistent user ID from email"""
        return hashlib.sha256(email.lower().encode()).hexdigest()[:12]
    
    def track_event(self, event_type: str, email: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Track a conversion event"""
        user_id = self._get_user_id(email)
        
        event = {
            "event_id": f"{event_type}_{user_id}_{datetime.now().timestamp()}",
            "event_type": event_type,
            "user_id": user_id,
            "email": email,
            "timestamp": datetime.now().isoformat(),
            "data": data or {}
        }
        
        # Add to events list
        self.events.append(event)
        self._save_json(self.events, self.events_file)
        
        # Update user journey
        if user_id not in self.users:
            self.users[user_id] = {
                "user_id": user_id,
                "email": email,
                "first_seen": datetime.now().isoformat(),
                "events": [],
                "status": "visitor",
                "lifetime_value": 0
            }
        
        self.users[user_id]["events"].append({
            "type": event_type,
            "timestamp": event["timestamp"],
            "data": data
        })
        
        # Update user status based on event
        self._update_user_status(user_id, event_type)
        self._save_json(self.users, self.users_file)
        
        return {"success": True, "event": event}
    
    def _update_user_status(self, user_id: str, event_type: str):
        """Update user status based on latest event"""
        status_progression = {
            "page_view": "visitor",
            "signup": "subscriber",
            "lead_magnet_download": "engaged",
            "email_open": "engaged",
            "email_click": "interested",
            "purchase": "customer"
        }
        
        current_status = self.users[user_id]["status"]
        new_status = status_progression.get(event_type, current_status)
        
        # Only update if it's a progression
        status_levels = ["visitor", "subscriber", "engaged", "interested", "customer"]
        if status_levels.index(new_status) > status_levels.index(current_status):
            self.users[user_id]["status"] = new_status
    
    def track_page_view(self, session_id: str, referrer: Optional[str] = None) -> Dict[str, Any]:
        """Track landing page view"""
        return self.track_event(
            "page_view",
            f"anonymous_{session_id}",
            {
                "session_id": session_id,
                "referrer": referrer,
                "page": "landing_page"
            }
        )
    
    def track_signup(self, email: str, first_name: str, source: str = "landing_page") -> Dict[str, Any]:
        """Track email signup"""
        return self.track_event(
            "signup",
            email,
            {
                "first_name": first_name,
                "source": source,
                "lead_magnet": "5_free_puzzles"
            }
        )
    
    def track_email_open(self, email: str, email_type: str, sequence_day: int) -> Dict[str, Any]:
        """Track email open"""
        return self.track_event(
            "email_open",
            email,
            {
                "email_type": email_type,
                "sequence_day": sequence_day
            }
        )
    
    def track_email_click(self, email: str, link_type: str, email_type: str, sequence_day: int) -> Dict[str, Any]:
        """Track email click"""
        return self.track_event(
            "email_click",
            email,
            {
                "link_type": link_type,
                "email_type": email_type,
                "sequence_day": sequence_day
            }
        )
    
    def track_purchase(self, email: str, product: str, amount: float, currency: str = "USD") -> Dict[str, Any]:
        """Track purchase conversion"""
        user_id = self._get_user_id(email)
        
        # Track event
        result = self.track_event(
            "purchase",
            email,
            {
                "product": product,
                "amount": amount,
                "currency": currency
            }
        )
        
        # Update revenue tracking
        month_key = datetime.now().strftime("%Y-%m")
        if month_key not in self.revenue:
            self.revenue[month_key] = {
                "total": 0,
                "purchases": [],
                "products": defaultdict(int)
            }
        
        self.revenue[month_key]["total"] += amount
        self.revenue[month_key]["purchases"].append({
            "user_id": user_id,
            "product": product,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
        self.revenue[month_key]["products"][product] += amount
        
        # Update user lifetime value
        self.users[user_id]["lifetime_value"] += amount
        
        self._save_json(self.revenue, self.revenue_file)
        self._save_json(self.users, self.users_file)
        
        return result
    
    def get_funnel_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Calculate funnel conversion metrics"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Count events by type
        event_counts = defaultdict(int)
        for event in self.events:
            event_date = datetime.fromisoformat(event["timestamp"])
            if event_date >= cutoff_date:
                event_counts[event["event_type"]] += 1
        
        # Calculate unique users at each stage
        stage_users = defaultdict(set)
        for user_id, user_data in self.users.items():
            for event in user_data["events"]:
                event_date = datetime.fromisoformat(event["timestamp"])
                if event_date >= cutoff_date:
                    stage_users[event["type"]].add(user_id)
        
        # Calculate conversion rates
        visitors = len(stage_users.get("page_view", set()))
        signups = len(stage_users.get("signup", set()))
        engaged = len(stage_users.get("email_open", set()) | stage_users.get("email_click", set()))
        customers = len(stage_users.get("purchase", set()))
        
        metrics = {
            "period_days": days,
            "funnel_stages": {
                "visitors": visitors,
                "signups": signups,
                "engaged": engaged,
                "customers": customers
            },
            "conversion_rates": {
                "visitor_to_signup": round(signups / visitors * 100, 2) if visitors > 0 else 0,
                "signup_to_engaged": round(engaged / signups * 100, 2) if signups > 0 else 0,
                "engaged_to_customer": round(customers / engaged * 100, 2) if engaged > 0 else 0,
                "overall": round(customers / visitors * 100, 2) if visitors > 0 else 0
            },
            "event_counts": dict(event_counts)
        }
        
        return metrics
    
    def get_revenue_metrics(self, months: int = 3) -> Dict[str, Any]:
        """Get revenue metrics for specified months"""
        metrics = {
            "total_revenue": 0,
            "monthly_revenue": {},
            "top_products": defaultdict(float),
            "average_order_value": 0,
            "total_purchases": 0
        }
        
        # Get last N months
        current_date = datetime.now()
        for i in range(months):
            month_date = current_date - timedelta(days=30*i)
            month_key = month_date.strftime("%Y-%m")
            
            if month_key in self.revenue:
                month_data = self.revenue[month_key]
                metrics["monthly_revenue"][month_key] = month_data["total"]
                metrics["total_revenue"] += month_data["total"]
                metrics["total_purchases"] += len(month_data["purchases"])
                
                for product, amount in month_data["products"].items():
                    metrics["top_products"][product] += amount
        
        # Calculate average order value
        if metrics["total_purchases"] > 0:
            metrics["average_order_value"] = round(
                metrics["total_revenue"] / metrics["total_purchases"], 2
            )
        
        # Sort top products
        metrics["top_products"] = dict(
            sorted(metrics["top_products"].items(), key=lambda x: x[1], reverse=True)
        )
        
        return metrics
    
    def get_email_performance(self) -> Dict[str, Any]:
        """Analyze email sequence performance"""
        email_stats = defaultdict(lambda: {"sent": 0, "opens": 0, "clicks": 0})
        
        for event in self.events:
            if event["event_type"] == "email_sent":
                email_type = event["data"].get("email_type", "unknown")
                email_stats[email_type]["sent"] += 1
            elif event["event_type"] == "email_open":
                email_type = event["data"].get("email_type", "unknown")
                email_stats[email_type]["opens"] += 1
            elif event["event_type"] == "email_click":
                email_type = event["data"].get("email_type", "unknown")
                email_stats[email_type]["clicks"] += 1
        
        # Calculate rates
        performance = {}
        for email_type, stats in email_stats.items():
            performance[email_type] = {
                "sent": stats["sent"],
                "opens": stats["opens"],
                "clicks": stats["clicks"],
                "open_rate": round(stats["opens"] / stats["sent"] * 100, 2) if stats["sent"] > 0 else 0,
                "click_rate": round(stats["clicks"] / stats["opens"] * 100, 2) if stats["opens"] > 0 else 0
            }
        
        return performance
    
    def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        return {
            "generated_at": datetime.now().isoformat(),
            "funnel_metrics": {
                "last_7_days": self.get_funnel_metrics(7),
                "last_30_days": self.get_funnel_metrics(30),
                "last_90_days": self.get_funnel_metrics(90)
            },
            "revenue_metrics": self.get_revenue_metrics(3),
            "email_performance": self.get_email_performance(),
            "user_segments": self._get_user_segments(),
            "recommendations": self._generate_recommendations()
        }
    
    def _get_user_segments(self) -> Dict[str, int]:
        """Segment users by status"""
        segments = defaultdict(int)
        for user in self.users.values():
            segments[user["status"]] += 1
        return dict(segments)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on metrics"""
        recommendations = []
        
        # Get current metrics
        metrics = self.get_funnel_metrics(30)
        
        # Analyze conversion rates
        if metrics["conversion_rates"]["visitor_to_signup"] < 10:
            recommendations.append(
                "Landing page conversion is below 10%. Consider A/B testing headlines "
                "or adding more social proof."
            )
        
        if metrics["conversion_rates"]["signup_to_engaged"] < 50:
            recommendations.append(
                "Email engagement is low. Review subject lines and send times. "
                "Consider personalizing content."
            )
        
        if metrics["conversion_rates"]["engaged_to_customer"] < 5:
            recommendations.append(
                "Purchase conversion needs improvement. Test different pricing, "
                "add urgency, or improve product positioning."
            )
        
        # Check email performance
        email_perf = self.get_email_performance()
        for email_type, stats in email_perf.items():
            if stats.get("open_rate", 0) < 20:
                recommendations.append(
                    f"{email_type} emails have low open rates. Improve subject lines."
                )
        
        return recommendations
    
    def export_analytics_dashboard(self, output_file: str = "analytics_dashboard.html") -> str:
        """Export analytics as HTML dashboard"""
        report = self.generate_analytics_report()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>KindleMint Analytics Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #2E3440; }}
        .metric-label {{ color: #666; }}
        .funnel {{ margin: 20px 0; }}
        .funnel-stage {{ display: inline-block; width: 20%; text-align: center; padding: 20px; margin: 5px; background: #E5E9F0; border-radius: 4px; }}
        .recommendation {{ background: #FFF4E6; padding: 10px; margin: 5px 0; border-left: 4px solid #FFA500; }}
        h1, h2 {{ color: #2E3440; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #E5E9F0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 KindleMint Analytics Dashboard</h1>
        <p>Generated: {report['generated_at']}</p>
        
        <div class="card">
            <h2>🎯 30-Day Funnel Performance</h2>
            <div class="funnel">
                <div class="funnel-stage">
                    <div class="metric-value">{report['funnel_metrics']['last_30_days']['funnel_stages']['visitors']}</div>
                    <div class="metric-label">Visitors</div>
                </div>
                <div class="funnel-stage">
                    <div class="metric-value">{report['funnel_metrics']['last_30_days']['funnel_stages']['signups']}</div>
                    <div class="metric-label">Signups</div>
                    <div style="color: #666; font-size: 14px;">{report['funnel_metrics']['last_30_days']['conversion_rates']['visitor_to_signup']}%</div>
                </div>
                <div class="funnel-stage">
                    <div class="metric-value">{report['funnel_metrics']['last_30_days']['funnel_stages']['engaged']}</div>
                    <div class="metric-label">Engaged</div>
                    <div style="color: #666; font-size: 14px;">{report['funnel_metrics']['last_30_days']['conversion_rates']['signup_to_engaged']}%</div>
                </div>
                <div class="funnel-stage">
                    <div class="metric-value">{report['funnel_metrics']['last_30_days']['funnel_stages']['customers']}</div>
                    <div class="metric-label">Customers</div>
                    <div style="color: #666; font-size: 14px;">{report['funnel_metrics']['last_30_days']['conversion_rates']['engaged_to_customer']}%</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>💰 Revenue Metrics</h2>
            <div class="metric">
                <div class="metric-value">${report['revenue_metrics']['total_revenue']}</div>
                <div class="metric-label">Total Revenue (3 months)</div>
            </div>
            <div class="metric">
                <div class="metric-value">${report['revenue_metrics']['average_order_value']}</div>
                <div class="metric-label">Average Order Value</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report['revenue_metrics']['total_purchases']}</div>
                <div class="metric-label">Total Purchases</div>
            </div>
        </div>
        
        <div class="card">
            <h2>📧 Email Performance</h2>
            <table>
                <tr>
                    <th>Email Type</th>
                    <th>Sent</th>
                    <th>Opens</th>
                    <th>Open Rate</th>
                    <th>Clicks</th>
                    <th>Click Rate</th>
                </tr>
                {"".join([f'''
                <tr>
                    <td>{email_type}</td>
                    <td>{stats['sent']}</td>
                    <td>{stats['opens']}</td>
                    <td>{stats['open_rate']}%</td>
                    <td>{stats['clicks']}</td>
                    <td>{stats['click_rate']}%</td>
                </tr>
                ''' for email_type, stats in report['email_performance'].items()])}
            </table>
        </div>
        
        <div class="card">
            <h2>💡 Recommendations</h2>
            {"".join([f'<div class="recommendation">{rec}</div>' for rec in report['recommendations']])}
        </div>
    </div>
</body>
</html>
        """
        
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return str(output_path)


def main():
    """Test conversion tracking"""
    tracker = ConversionTracker()
    
    # Simulate some events
    print("🧪 Testing Conversion Tracker")
    print("=" * 60)
    
    # Track page view
    tracker.track_page_view("session_123", "google.com")
    print("✓ Tracked page view")
    
    # Track signup
    tracker.track_signup("test@example.com", "John", "landing_page")
    print("✓ Tracked signup")
    
    # Track email opens
    tracker.track_email_open("test@example.com", "welcome", 0)
    tracker.track_email_click("test@example.com", "cta_button", "welcome", 0)
    print("✓ Tracked email engagement")
    
    # Track purchase
    tracker.track_purchase("test@example.com", "Sudoku Masters Vol 1", 8.99)
    print("✓ Tracked purchase")
    
    # Generate report
    report = tracker.generate_analytics_report()
    print("\n📊 Analytics Report:")
    print(json.dumps(report, indent=2))
    
    # Export dashboard
    dashboard_path = tracker.export_analytics_dashboard()
    print(f"\n📈 Dashboard exported to: {dashboard_path}")


if __name__ == "__main__":
    main()