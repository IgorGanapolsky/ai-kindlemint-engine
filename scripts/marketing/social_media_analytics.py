#!/usr/bin/env python3
"""
Social Media Analytics - Track BookTok ROI and Performance
Measures social media impact on book sales and engagement
"""

import json
import csv
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from typing import Dict, List, Any
import sys
from dataclasses import dataclass, asdict

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

@dataclass
class SocialMediaMetrics:
    """Social media performance metrics"""
    platform: str
    date: str
    views: int
    likes: int
    shares: int
    comments: int
    clicks: int
    followers_gained: int
    engagement_rate: float
    reach: int
    impressions: int

@dataclass
class BookSalesMetrics:
    """Book sales metrics from social media traffic"""
    date: str
    amazon_clicks: int
    conversions: int
    revenue: float
    conversion_rate: float
    cost_per_acquisition: float
    return_on_ad_spend: float

class SocialMediaAnalytics:
    """Track and analyze social media performance for BookTok strategy"""
    
    def __init__(self, data_directory: str = "data/analytics"):
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Analytics files
        self.social_metrics_file = self.data_dir / "social_media_metrics.json"
        self.sales_metrics_file = self.data_dir / "book_sales_metrics.json"
        self.performance_report_file = self.data_dir / "weekly_performance_report.md"
        
        # UTM tracking codes for social media traffic
        self.utm_codes = {
            "tiktok": "utm_source=tiktok&utm_medium=social&utm_campaign=booktok",
            "pinterest": "utm_source=pinterest&utm_medium=social&utm_campaign=puzzle_pins",
            "instagram": "utm_source=instagram&utm_medium=social&utm_campaign=reels",
            "facebook": "utm_source=facebook&utm_medium=social&utm_campaign=groups"
        }
        
        # Performance benchmarks
        self.benchmarks = {
            "tiktok": {
                "good_engagement_rate": 0.06,  # 6%
                "viral_threshold": 100000,      # 100K views
                "follower_growth_target": 50    # per week
            },
            "pinterest": {
                "good_engagement_rate": 0.02,  # 2%
                "monthly_impressions_target": 10000,
                "click_through_rate_target": 0.01  # 1%
            }
        }
    
    def track_tiktok_performance(self, video_data: Dict[str, Any]) -> SocialMediaMetrics:
        """Track TikTok video performance"""
        return SocialMediaMetrics(
            platform="tiktok",
            date=datetime.now().strftime("%Y-%m-%d"),
            views=video_data.get("views", 0),
            likes=video_data.get("likes", 0),
            shares=video_data.get("shares", 0),
            comments=video_data.get("comments", 0),
            clicks=video_data.get("clicks", 0),
            followers_gained=video_data.get("followers_gained", 0),
            engagement_rate=self._calculate_engagement_rate(video_data),
            reach=video_data.get("reach", 0),
            impressions=video_data.get("impressions", 0)
        )
    
    def track_pinterest_performance(self, pin_data: Dict[str, Any]) -> SocialMediaMetrics:
        """Track Pinterest pin performance"""
        return SocialMediaMetrics(
            platform="pinterest",
            date=datetime.now().strftime("%Y-%m-%d"),
            views=pin_data.get("impressions", 0),
            likes=pin_data.get("saves", 0),  # Pinterest uses saves instead of likes
            shares=pin_data.get("pin_clicks", 0),
            comments=pin_data.get("comments", 0),
            clicks=pin_data.get("outbound_clicks", 0),
            followers_gained=pin_data.get("followers_gained", 0),
            engagement_rate=self._calculate_pinterest_engagement_rate(pin_data),
            reach=pin_data.get("reach", 0),
            impressions=pin_data.get("impressions", 0)
        )
    
    def _calculate_engagement_rate(self, data: Dict[str, Any]) -> float:
        """Calculate engagement rate for TikTok"""
        views = data.get("views", 0)
        if views == 0:
            return 0.0
        
        engagements = (
            data.get("likes", 0) + 
            data.get("comments", 0) + 
            data.get("shares", 0)
        )
        return round(engagements / views, 4)
    
    def _calculate_pinterest_engagement_rate(self, data: Dict[str, Any]) -> float:
        """Calculate engagement rate for Pinterest"""
        impressions = data.get("impressions", 0)
        if impressions == 0:
            return 0.0
        
        engagements = (
            data.get("saves", 0) + 
            data.get("pin_clicks", 0) + 
            data.get("comments", 0)
        )
        return round(engagements / impressions, 4)
    
    def track_amazon_sales(self, sales_data: Dict[str, Any]) -> BookSalesMetrics:
        """Track book sales from social media traffic"""
        return BookSalesMetrics(
            date=datetime.now().strftime("%Y-%m-%d"),
            amazon_clicks=sales_data.get("amazon_clicks", 0),
            conversions=sales_data.get("conversions", 0),
            revenue=sales_data.get("revenue", 0.0),
            conversion_rate=self._calculate_conversion_rate(sales_data),
            cost_per_acquisition=sales_data.get("cost_per_acquisition", 0.0),
            return_on_ad_spend=self._calculate_roas(sales_data)
        )
    
    def _calculate_conversion_rate(self, sales_data: Dict[str, Any]) -> float:
        """Calculate conversion rate from clicks to sales"""
        clicks = sales_data.get("amazon_clicks", 0)
        conversions = sales_data.get("conversions", 0)
        
        if clicks == 0:
            return 0.0
        
        return round(conversions / clicks, 4)
    
    def _calculate_roas(self, sales_data: Dict[str, Any]) -> float:
        """Calculate Return on Ad Spend"""
        revenue = sales_data.get("revenue", 0.0)
        ad_spend = sales_data.get("ad_spend", 0.0)
        
        if ad_spend == 0:
            return 0.0
        
        return round(revenue / ad_spend, 2)
    
    def save_metrics(self, metrics: SocialMediaMetrics) -> None:
        """Save social media metrics to file"""
        # Load existing metrics
        existing_metrics = []
        if self.social_metrics_file.exists():
            with open(self.social_metrics_file, 'r') as f:
                existing_metrics = json.load(f)
        
        # Add new metrics
        existing_metrics.append(asdict(metrics))
        
        # Save updated metrics
        with open(self.social_metrics_file, 'w') as f:
            json.dump(existing_metrics, f, indent=2)
        
        print(f"✅ Saved {metrics.platform} metrics for {metrics.date}")
    
    def save_sales_metrics(self, metrics: BookSalesMetrics) -> None:
        """Save book sales metrics to file"""
        # Load existing metrics
        existing_metrics = []
        if self.sales_metrics_file.exists():
            with open(self.sales_metrics_file, 'r') as f:
                existing_metrics = json.load(f)
        
        # Add new metrics
        existing_metrics.append(asdict(metrics))
        
        # Save updated metrics
        with open(self.sales_metrics_file, 'w') as f:
            json.dump(existing_metrics, f, indent=2)
        
        print(f"✅ Saved sales metrics for {metrics.date}")
    
    def generate_weekly_report(self) -> None:
        """Generate weekly performance report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Load metrics
        social_metrics = self._load_metrics_for_period(
            self.social_metrics_file, start_date, end_date
        )
        sales_metrics = self._load_metrics_for_period(
            self.sales_metrics_file, start_date, end_date
        )
        
        # Generate report
        report = self._create_performance_report(social_metrics, sales_metrics, start_date, end_date)
        
        # Save report
        with open(self.performance_report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ Generated weekly report: {self.performance_report_file}")
    
    def _load_metrics_for_period(self, file_path: Path, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Load metrics for specific time period"""
        if not file_path.exists():
            return []
        
        with open(file_path, 'r') as f:
            all_metrics = json.load(f)
        
        # Filter by date range
        filtered_metrics = []
        for metric in all_metrics:
            metric_date = datetime.strptime(metric["date"], "%Y-%m-%d")
            if start_date <= metric_date <= end_date:
                filtered_metrics.append(metric)
        
        return filtered_metrics
    
    def _create_performance_report(self, social_metrics: List[Dict], sales_metrics: List[Dict], 
                                 start_date: datetime, end_date: datetime) -> str:
        """Create comprehensive performance report"""
        
        # Calculate totals and averages
        total_views = sum(m.get("views", 0) for m in social_metrics)
        total_engagement = sum(m.get("likes", 0) + m.get("comments", 0) + m.get("shares", 0) for m in social_metrics)
        total_clicks = sum(m.get("clicks", 0) for m in social_metrics)
        total_followers_gained = sum(m.get("followers_gained", 0) for m in social_metrics)
        
        total_amazon_clicks = sum(m.get("amazon_clicks", 0) for m in sales_metrics)
        total_conversions = sum(m.get("conversions", 0) for m in sales_metrics)
        total_revenue = sum(m.get("revenue", 0) for m in sales_metrics)
        
        avg_engagement_rate = sum(m.get("engagement_rate", 0) for m in social_metrics) / len(social_metrics) if social_metrics else 0
        avg_conversion_rate = sum(m.get("conversion_rate", 0) for m in sales_metrics) / len(sales_metrics) if sales_metrics else 0
        
        # Platform breakdown
        platform_stats = {}
        for metric in social_metrics:
            platform = metric.get("platform", "unknown")
            if platform not in platform_stats:
                platform_stats[platform] = {"views": 0, "engagement": 0, "followers": 0}
            
            platform_stats[platform]["views"] += metric.get("views", 0)
            platform_stats[platform]["engagement"] += (
                metric.get("likes", 0) + metric.get("comments", 0) + metric.get("shares", 0)
            )
            platform_stats[platform]["followers"] += metric.get("followers_gained", 0)
        
        # Performance analysis
        performance_insights = self._analyze_performance(social_metrics, sales_metrics)
        
        report = f"""# BookTok Performance Report
**Period:** {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 Social Media Overview
- **Total Views:** {total_views:,}
- **Total Engagement:** {total_engagement:,}
- **Total Clicks:** {total_clicks:,}
- **New Followers:** {total_followers_gained:,}
- **Average Engagement Rate:** {avg_engagement_rate:.2%}

## 💰 Sales Performance
- **Amazon Clicks:** {total_amazon_clicks:,}
- **Conversions:** {total_conversions:,}
- **Revenue:** ${total_revenue:.2f}
- **Conversion Rate:** {avg_conversion_rate:.2%}
- **Revenue per Click:** ${(total_revenue / total_amazon_clicks if total_amazon_clicks > 0 else 0):.2f}

## 📱 Platform Breakdown
"""
        
        for platform, stats in platform_stats.items():
            report += f"""
### {platform.title()}
- Views: {stats['views']:,}
- Engagement: {stats['engagement']:,}
- New Followers: {stats['followers']:,}
"""
        
        report += f"""
## 🎯 Performance Insights
{performance_insights}

## 📈 Key Metrics Trends
- **Best Performing Content:** {self._get_best_performing_content(social_metrics)}
- **Peak Engagement Times:** {self._get_peak_engagement_times(social_metrics)}
- **Top Converting Platforms:** {self._get_top_converting_platforms(social_metrics, sales_metrics)}

## 🚀 Recommendations
{self._generate_recommendations(social_metrics, sales_metrics)}

## 📋 Action Items for Next Week
- [ ] Create more content similar to best performers
- [ ] Post during peak engagement times
- [ ] Focus budget on top converting platforms
- [ ] A/B test new content formats
- [ ] Engage more with comments and community

---
*Report generated by AI-KindleMint Social Media Analytics*
"""
        
        return report
    
    def _analyze_performance(self, social_metrics: List[Dict], sales_metrics: List[Dict]) -> str:
        """Analyze performance against benchmarks"""
        insights = []
        
        # TikTok analysis
        tiktok_metrics = [m for m in social_metrics if m.get("platform") == "tiktok"]
        if tiktok_metrics:
            avg_engagement = sum(m.get("engagement_rate", 0) for m in tiktok_metrics) / len(tiktok_metrics)
            benchmark = self.benchmarks["tiktok"]["good_engagement_rate"]
            
            if avg_engagement >= benchmark:
                insights.append(f"✅ TikTok engagement rate ({avg_engagement:.2%}) exceeds benchmark ({benchmark:.2%})")
            else:
                insights.append(f"⚠️ TikTok engagement rate ({avg_engagement:.2%}) below benchmark ({benchmark:.2%})")
        
        # Sales analysis
        if sales_metrics:
            total_revenue = sum(m.get("revenue", 0) for m in sales_metrics)
            if total_revenue > 0:
                insights.append(f"✅ Generated ${total_revenue:.2f} in revenue from social media")
            else:
                insights.append("⚠️ No revenue generated from social media traffic yet")
        
        return "\n".join(insights) if insights else "No significant insights available yet."
    
    def _get_best_performing_content(self, social_metrics: List[Dict]) -> str:
        """Identify best performing content"""
        if not social_metrics:
            return "No data available"
        
        best_metric = max(social_metrics, key=lambda x: x.get("views", 0))
        return f"{best_metric.get('platform', 'Unknown')} content with {best_metric.get('views', 0):,} views"
    
    def _get_peak_engagement_times(self, social_metrics: List[Dict]) -> str:
        """Identify peak engagement times"""
        # This would require timestamp data - placeholder for now
        return "Analysis requires timestamp data (to be implemented)"
    
    def _get_top_converting_platforms(self, social_metrics: List[Dict], sales_metrics: List[Dict]) -> str:
        """Identify platforms with highest conversion rates"""
        if not sales_metrics:
            return "No conversion data available"
        
        # This would require platform-specific sales tracking
        return "Platform-specific conversion tracking (to be implemented)"
    
    def _generate_recommendations(self, social_metrics: List[Dict], sales_metrics: List[Dict]) -> str:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not social_metrics:
            recommendations.append("- Start tracking social media metrics consistently")
            recommendations.append("- Implement UTM codes for better attribution")
        
        if social_metrics:
            total_views = sum(m.get("views", 0) for m in social_metrics)
            if total_views < 10000:
                recommendations.append("- Focus on increasing content volume and consistency")
                recommendations.append("- Experiment with trending hashtags and sounds")
        
        if not sales_metrics or sum(m.get("revenue", 0) for m in sales_metrics) == 0:
            recommendations.append("- Add clear call-to-actions in social media content")
            recommendations.append("- Create compelling Amazon product links")
            recommendations.append("- Consider offering limited-time discounts")
        
        return "\n".join(recommendations) if recommendations else "Continue current strategy and monitor performance."
    
    def generate_utm_links(self, base_amazon_url: str) -> Dict[str, str]:
        """Generate UTM-tracked Amazon links for each platform"""
        utm_links = {}
        
        for platform, utm_params in self.utm_codes.items():
            if "?" in base_amazon_url:
                utm_links[platform] = f"{base_amazon_url}&{utm_params}"
            else:
                utm_links[platform] = f"{base_amazon_url}?{utm_params}"
        
        return utm_links
    
    def export_data_for_analysis(self, output_file: str = "social_media_data_export.csv") -> None:
        """Export all data to CSV for external analysis"""
        export_file = self.data_dir / output_file
        
        # Load all metrics
        social_metrics = []
        sales_metrics = []
        
        if self.social_metrics_file.exists():
            with open(self.social_metrics_file, 'r') as f:
                social_metrics = json.load(f)
        
        if self.sales_metrics_file.exists():
            with open(self.sales_metrics_file, 'r') as f:
                sales_metrics = json.load(f)
        
        # Combine data for export
        export_data = []
        
        # Add social metrics
        for metric in social_metrics:
            export_data.append({
                "date": metric["date"],
                "type": "social",
                "platform": metric["platform"],
                "views": metric.get("views", 0),
                "likes": metric.get("likes", 0),
                "shares": metric.get("shares", 0),
                "comments": metric.get("comments", 0),
                "clicks": metric.get("clicks", 0),
                "followers_gained": metric.get("followers_gained", 0),
                "engagement_rate": metric.get("engagement_rate", 0),
                "revenue": 0,
                "conversions": 0
            })
        
        # Add sales metrics
        for metric in sales_metrics:
            export_data.append({
                "date": metric["date"],
                "type": "sales",
                "platform": "amazon",
                "views": 0,
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "clicks": metric.get("amazon_clicks", 0),
                "followers_gained": 0,
                "engagement_rate": 0,
                "revenue": metric.get("revenue", 0),
                "conversions": metric.get("conversions", 0)
            })
        
        # Write to CSV
        if export_data:
            with open(export_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            
            print(f"✅ Exported data to: {export_file}")
        else:
            print("⚠️ No data to export")

def main():
    parser = argparse.ArgumentParser(description="Social Media Analytics for BookTok Strategy")
    parser.add_argument("--data-dir", default="data/analytics", help="Analytics data directory")
    parser.add_argument("--generate-report", action="store_true", help="Generate weekly report")
    parser.add_argument("--export-data", action="store_true", help="Export data to CSV")
    parser.add_argument("--utm-links", help="Generate UTM links for Amazon URL")
    
    args = parser.parse_args()
    
    analytics = SocialMediaAnalytics(args.data_dir)
    
    if args.generate_report:
        analytics.generate_weekly_report()
    
    if args.export_data:
        analytics.export_data_for_analysis()
    
    if args.utm_links:
        utm_links = analytics.generate_utm_links(args.utm_links)
        print("UTM-tracked links:")
        for platform, link in utm_links.items():
            print(f"{platform}: {link}")
    
    if not any([args.generate_report, args.export_data, args.utm_links]):
        print("Social Media Analytics initialized.")
        print(f"Data directory: {analytics.data_dir}")
        print("Use --help for available commands.")

if __name__ == "__main__":
    main()
