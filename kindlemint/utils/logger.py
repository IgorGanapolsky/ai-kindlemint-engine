"""
Centralized logging configuration with automatic rotation for KindleMint Engine.
Handles log rotation when files reach 10MB or after 7 days, with compressed backups.
"""
import logging
import logging.handlers
from pathlib import Path
import os
from datetime import datetime

class KindleMintLogger:
    """Centralized logger with rotation capabilities."""
    
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KindleMintLogger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Create logs directory
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Main log file path
        self.main_log_file = self.log_dir / "kindlemint.log"
        
        # Set up main logger
        self._setup_main_logger()
        self._initialized = True
    
    def _setup_main_logger(self):
        """Set up the main KindleMint logger with rotation."""
        # Remove any existing handlers
        root_logger = logging.getLogger('kindlemint')
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create rotating file handler
        # Rotates when file reaches 10MB or after 7 days
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=self.main_log_file,
            when='midnight',
            interval=7,  # Every 7 days
            backupCount=4,  # Keep 4 weeks of logs
            encoding='utf-8'
        )
        
        # Also add size-based rotation (10MB limit)
        size_handler = logging.handlers.RotatingFileHandler(
            filename=str(self.main_log_file).replace('.log', '_size.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        size_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Configure main logger
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(size_handler)
        root_logger.addHandler(console_handler)
        
        # Store reference
        self._loggers['main'] = root_logger
    
    def get_logger(self, name: str = 'kindlemint') -> logging.Logger:
        """Get a logger instance with automatic rotation."""
        if name in self._loggers:
            return self._loggers[name]
        
        # Create child logger
        logger = logging.getLogger(f'kindlemint.{name}')
        logger.setLevel(logging.INFO)
        
        # Child loggers inherit from parent, so no need for additional handlers
        self._loggers[name] = logger
        return logger
    
    def cleanup_old_logs(self):
        """Clean up old log files and compress them."""
        try:
            import gzip
            import shutil
            
            # Find old log files
            for log_file in self.log_dir.glob("*.log.*"):
                if not log_file.name.endswith('.gz'):
                    # Compress old log files
                    compressed_name = f"{log_file}.gz"
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_name, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # Remove original
                    log_file.unlink()
                    
            # Clean up any duplicate log directories
            self._consolidate_log_files()
            
        except Exception as e:
            logging.error(f"Failed to cleanup old logs: {e}")
    
    def _consolidate_log_files(self):
        """Consolidate duplicate log files from different directories."""
        try:
            # Find all kindlemint.log files
            duplicate_logs = []
            
            # Check lambda/logs directory
            lambda_log_dir = Path("lambda/logs")
            if lambda_log_dir.exists():
                lambda_log = lambda_log_dir / "kindlemint.log"
                if lambda_log.exists():
                    duplicate_logs.append(lambda_log)
            
            # Move content from duplicate logs to main log
            if duplicate_logs:
                main_logger = self.get_logger()
                main_logger.info("🔄 Consolidating duplicate log files...")
                
                for dup_log in duplicate_logs:
                    try:
                        # Read content and append to main log
                        with open(dup_log, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if content.strip():
                                main_logger.info(f"--- Consolidated from {dup_log} ---")
                                # Write raw content to avoid double formatting
                                with open(self.main_log_file, 'a', encoding='utf-8') as main_f:
                                    main_f.write(f"\n--- Logs from {dup_log} ---\n")
                                    main_f.write(content)
                                    main_f.write(f"\n--- End logs from {dup_log} ---\n")
                        
                        # Remove duplicate log
                        dup_log.unlink()
                        main_logger.info(f"✅ Consolidated and removed: {dup_log}")
                        
                        # Remove empty directory if it exists
                        if dup_log.parent.exists() and not any(dup_log.parent.iterdir()):
                            dup_log.parent.rmdir()
                            
                    except Exception as e:
                        main_logger.error(f"Failed to consolidate {dup_log}: {e}")
                        
        except Exception as e:
            logging.error(f"Failed to consolidate log files: {e}")

# Global logger instance
_logger_instance = KindleMintLogger()

def get_logger(name: str = 'kindlemint') -> logging.Logger:
    """Get a KindleMint logger with automatic rotation."""
    return _logger_instance.get_logger(name)

def setup_logging():
    """Set up logging for the entire application."""
    logger = get_logger()
    logger.info("🔧 KindleMint centralized logging initialized")
    
    # Clean up old logs on startup
    _logger_instance.cleanup_old_logs()
    
    return logger

def rotate_logs():
    """Manually trigger log rotation and cleanup."""
    _logger_instance.cleanup_old_logs()
    logger = get_logger()
    logger.info("🔄 Manual log rotation completed")

# Convenience functions
def info(message: str, logger_name: str = 'kindlemint'):
    """Log info message."""
    get_logger(logger_name).info(message)

def error(message: str, logger_name: str = 'kindlemint'):
    """Log error message."""
    get_logger(logger_name).error(message)

def warning(message: str, logger_name: str = 'kindlemint'):
    """Log warning message."""
    get_logger(logger_name).warning(message)

def debug(message: str, logger_name: str = 'kindlemint'):
    """Log debug message."""
    get_logger(logger_name).debug(message)