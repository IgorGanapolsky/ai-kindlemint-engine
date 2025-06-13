"""
Logging utilities for Mission Control system
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
import config

class MissionLogger:
    """Enhanced logging system for Mission Control"""
    
    def __init__(self, name: str = "mission_control"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers"""
        # File handler
        log_file = config.LOGS_DIR / f"mission_control_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
    
    def log_agent_start(self, agent_name: str, task: str):
        """Log agent task start"""
        self.info(f"🚀 {agent_name}: Starting task - {task}")
    
    def log_agent_complete(self, agent_name: str, task: str, duration: float):
        """Log agent task completion"""
        self.info(f"✅ {agent_name}: Completed task - {task} (Duration: {duration:.2f}s)")
    
    def log_agent_error(self, agent_name: str, task: str, error: str):
        """Log agent error"""
        self.error(f"❌ {agent_name}: Failed task - {task} | Error: {error}")
    
    def log_api_call(self, api: str, endpoint: str, status: str):
        """Log API call"""
        self.info(f"🔗 API Call: {api} - {endpoint} | Status: {status}")
    
    def log_file_operation(self, operation: str, file_path: str, status: str):
        """Log file operation"""
        self.info(f"📁 File Operation: {operation} - {file_path} | Status: {status}")
