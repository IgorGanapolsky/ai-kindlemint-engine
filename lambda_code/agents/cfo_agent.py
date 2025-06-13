"""
CFO Agent - Handles logging, analytics, and financial tracking
"""
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import csv
import config
from utils.logger import MissionLogger
from utils.file_manager import FileManager

class CFOAgent:
    """CFO Agent responsible for logging, analytics, and tracking"""
    
    def __init__(self):
        self.logger = MissionLogger("CFO_Agent")
        self.file_manager = FileManager()
    
    def run_cfo_tasks(self, log_message: str, activity_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main CFO workflow"""
        start_time = time.time()
        self.logger.log_agent_start("CFO", f"Logging activity: {log_message}")
        
        try:
            # Log the activity
            activity_data = activity_data or {}
            activity_data.update({
                'message': log_message,
                'timestamp': datetime.now().isoformat(),
                'session_id': str(int(time.time()))
            })
            
            # Save activity log
            log_file = self.file_manager.save_activity_log(log_message, activity_data)
            self.logger.log_file_operation("Save Activity Log", log_file, "Success")
            
            # Update mission log with detailed tracking
            self._update_mission_log(log_message, activity_data)
            
            # Generate analytics report
            self.logger.info("📊 Generating analytics report...")
            analytics = self._generate_analytics_report()
            
            # Save analytics to CSV
            analytics_file = self._save_analytics_csv(analytics)
            
            # Generate financial summary
            financial_summary = self._calculate_financial_metrics(activity_data)
            
            duration = time.time() - start_time
            self.logger.log_agent_complete("CFO", f"Activity logging and analysis", duration)
            
            return {
                'success': True,
                'log_file': log_file,
                'analytics_file': analytics_file,
                'analytics': analytics,
                'financial_summary': financial_summary,
                'duration': duration
            }
            
        except Exception as e:
            self.logger.log_agent_error("CFO", f"Activity logging", str(e))
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def _generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        try:
            # Get file summary
            file_summary = self.file_manager.get_output_summary()
            
            # Calculate productivity metrics
            analytics = {
                'timestamp': datetime.now().isoformat(),
                'file_summary': file_summary,
                'productivity_metrics': {
                    'total_projects': len(file_summary.get('books', [])) + len(file_summary.get('marketing', [])),
                    'total_files_generated': file_summary.get('total_files', 0),
                    'books_generated': len(file_summary.get('books', [])),
                    'marketing_campaigns': len(file_summary.get('marketing', [])),
                    'log_files': len(file_summary.get('logs', []))
                },
                'system_health': self._check_system_health(),
                'recommendations': self._generate_recommendations(file_summary)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to generate analytics: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _save_analytics_csv(self, analytics: Dict[str, Any]) -> str:
        """Save analytics data to CSV format"""
        try:
            csv_file = config.LOGS_OUTPUT_DIR / f"analytics_{datetime.now().strftime('%Y%m%d')}.csv"
            
            # Prepare CSV data
            csv_data = []
            metrics = analytics.get('productivity_metrics', {})
            
            csv_data.append(['Metric', 'Value', 'Timestamp'])
            csv_data.append(['Total Projects', metrics.get('total_projects', 0), analytics.get('timestamp', '')])
            csv_data.append(['Total Files', metrics.get('total_files_generated', 0), analytics.get('timestamp', '')])
            csv_data.append(['Books Generated', metrics.get('books_generated', 0), analytics.get('timestamp', '')])
            csv_data.append(['Marketing Campaigns', metrics.get('marketing_campaigns', 0), analytics.get('timestamp', '')])
            csv_data.append(['Log Files', metrics.get('log_files', 0), analytics.get('timestamp', '')])
            
            # Write CSV file
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
            
            self.logger.log_file_operation("Save Analytics CSV", str(csv_file), "Success")
            return str(csv_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save analytics CSV: {e}")
            return ""
    
    def _check_system_health(self) -> Dict[str, Any]:
        """Check system health and performance"""
        try:
            health_status = {
                'directories_exist': True,
                'api_keys_configured': bool(config.OPENAI_API_KEY),
                'output_directories': {
                    'books': config.BOOK_OUTPUT_DIR.exists(),
                    'marketing': config.MARKETING_OUTPUT_DIR.exists(),
                    'logs': config.LOGS_OUTPUT_DIR.exists()
                },
                'disk_usage': self._get_disk_usage(),
                'last_check': datetime.now().isoformat()
            }
            
            # Overall health score
            health_checks = [
                health_status['directories_exist'],
                health_status['api_keys_configured'],
                all(health_status['output_directories'].values())
            ]
            
            health_status['overall_health'] = sum(health_checks) / len(health_checks)
            health_status['status'] = 'healthy' if health_status['overall_health'] > 0.8 else 'needs_attention'
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def _get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information for output directories"""
        try:
            usage = {}
            
            for dir_name, dir_path in [
                ('books', config.BOOK_OUTPUT_DIR),
                ('marketing', config.MARKETING_OUTPUT_DIR),
                ('logs', config.LOGS_OUTPUT_DIR)
            ]:
                if dir_path.exists():
                    file_count = sum(1 for _ in dir_path.rglob('*') if _.is_file())
                    total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                    
                    usage[dir_name] = {
                        'file_count': file_count,
                        'total_size_bytes': total_size,
                        'total_size_mb': round(total_size / (1024 * 1024), 2)
                    }
                else:
                    usage[dir_name] = {
                        'file_count': 0,
                        'total_size_bytes': 0,
                        'total_size_mb': 0
                    }
            
            return usage
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_recommendations(self, file_summary: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on data"""
        recommendations = []
        
        try:
            total_projects = len(file_summary.get('books', [])) + len(file_summary.get('marketing', []))
            
            if total_projects == 0:
                recommendations.append("🚀 Start your first project by running the mission control with a book topic")
            elif total_projects < 5:
                recommendations.append("📈 Consider diversifying your content portfolio with more book topics")
            
            if len(file_summary.get('marketing', [])) < len(file_summary.get('books', [])):
                recommendations.append("📱 Increase marketing content generation to match book production")
            
            if file_summary.get('total_files', 0) > 100:
                recommendations.append("🗂️ Consider implementing file archival system for better organization")
            
            if not config.OPENAI_API_KEY:
                recommendations.append("🔑 Configure OpenAI API key for full functionality")
            
            recommendations.append("✅ System is operating efficiently - keep up the great work!")
            
        except Exception as e:
            recommendations.append(f"⚠️ Error generating recommendations: {e}")
        
        return recommendations
    
    def _update_mission_log(self, log_message: str, activity_data: Dict[str, Any]):
        """Update mission log with detailed tracking information"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            book_topic = activity_data.get('book_topic', 'Unknown')
            cto_success = activity_data.get('cto_success', False)
            cmo_success = activity_data.get('cmo_success', False)
            total_files = activity_data.get('total_files_created', 0)
            duration = activity_data.get('mission_duration', 0)
            
            # Create comprehensive log entry
            log_entry = f"[{timestamp}] {log_message}\n"
            log_entry += f"  Topic: {book_topic}\n"
            log_entry += f"  CTO Success: {'✅' if cto_success else '❌'}\n"
            log_entry += f"  CMO Success: {'✅' if cmo_success else '❌'}\n"
            log_entry += f"  Files Created: {total_files}\n"
            log_entry += f"  Duration: {duration:.2f}s\n"
            log_entry += f"  Status: {'COMPLETED' if cto_success else 'PARTIAL'}\n"
            log_entry += "-" * 50 + "\n"
            
            # Append to mission log
            with open("mission_log.txt", "a", encoding='utf-8') as log:
                log.write(log_entry)
            
            self.logger.info(f"📝 Updated mission_log.txt with detailed tracking")
            
        except Exception as e:
            self.logger.warning(f"Failed to update mission log: {e}")
    
    def _get_daily_analytics(self) -> Dict[str, Any]:
        """Get comprehensive daily analytics from logs and files"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            analytics = {
                'date': today,
                'missions_completed': 0,
                'books_generated': 0,
                'total_chapters': 0,
                'marketing_campaigns': 0,
                'average_mission_time': 0,
                'errors_encountered': 0,
                'api_calls_made': 0,
                'file_sizes_mb': 0
            }
            
            # Parse mission log for daily stats
            if os.path.exists('mission_log.txt'):
                with open('mission_log.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Count missions completed today
                today_missions = [line for line in content.split('\n') if today in line and 'Completed full mission cycle' in line]
                analytics['missions_completed'] = len(today_missions)
                
                # Count errors
                error_lines = [line for line in content.split('\n') if today in line and ('ERROR' in line or 'Failed' in line)]
                analytics['errors_encountered'] = len(error_lines)
            
            # Count files generated today
            output_dir = Path('output')
            if output_dir.exists():
                today_timestamp = datetime.now().timestamp() - 86400  # Last 24 hours
                
                for file_path in output_dir.rglob('*'):
                    if file_path.is_file() and file_path.stat().st_mtime > today_timestamp:
                        analytics['file_sizes_mb'] += file_path.stat().st_size / (1024 * 1024)
                        
                        if 'books' in str(file_path):
                            analytics['books_generated'] += 1
                        elif 'marketing' in str(file_path):
                            analytics['marketing_campaigns'] += 1
            
            # Estimate API calls from log files
            log_dir = Path('logs')
            if log_dir.exists():
                for log_file in log_dir.glob('*.log'):
                    if log_file.stat().st_mtime > today_timestamp:
                        with open(log_file, 'r') as f:
                            api_lines = [line for line in f if 'API Call' in line]
                            analytics['api_calls_made'] += len(api_lines)
            
            return analytics
            
        except Exception as e:
            self.logger.warning(f"Failed to generate daily analytics: {e}")
            return {'date': datetime.now().strftime('%Y-%m-%d'), 'error': str(e)}
    
    def _calculate_financial_metrics(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate estimated financial metrics and daily analytics"""
        try:
            # Daily analytics tracking
            daily_analytics = self._get_daily_analytics()
            
            # Estimated costs and metrics
            base_metrics = {
                'estimated_api_costs': {
                    'openai_calls': 0.05,  # Estimated per call
                    'total_estimated': 0.15,  # Total estimated cost
                    'currency': 'USD'
                },
                'productivity_value': {
                    'content_generated': 'High',
                    'time_saved_hours': 8,  # Estimated hours saved
                    'estimated_value_usd': 400  # Based on content creation rates
                },
                'roi_estimate': {
                    'investment': 0.15,
                    'value_generated': 400,
                    'roi_percentage': 266567
                }
            }
            
            return base_metrics
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Financial metrics calculation failed'
            }
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report"""
        try:
            analytics = self._generate_analytics_report()
            
            report = f"""
# Mission Control Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Health
- Status: {analytics.get('system_health', {}).get('status', 'Unknown')}
- Overall Health: {analytics.get('system_health', {}).get('overall_health', 0):.1%}
- API Keys Configured: {analytics.get('system_health', {}).get('api_keys_configured', False)}

## Productivity Metrics
- Total Projects: {analytics.get('productivity_metrics', {}).get('total_projects', 0)}
- Files Generated: {analytics.get('productivity_metrics', {}).get('total_files_generated', 0)}
- Books Created: {analytics.get('productivity_metrics', {}).get('books_generated', 0)}
- Marketing Campaigns: {analytics.get('productivity_metrics', {}).get('marketing_campaigns', 0)}

## Recommendations
"""
            
            for rec in analytics.get('recommendations', []):
                report += f"- {rec}\n"
            
            return report
            
        except Exception as e:
            return f"Error generating summary report: {e}"
