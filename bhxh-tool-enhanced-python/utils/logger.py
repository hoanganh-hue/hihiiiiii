"""
Enhanced Logger with structured logging
"""

import logging
import logging.handlers
import os
import pathlib
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from config.config import get_config_instance


class Logger:
    """Enhanced Logger with structured logging"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logger with multiple handlers"""
        # Ensure logs directory exists
        log_dir = pathlib.Path(self.config.files['log_file']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('bhxh_tool')
        self.logger.setLevel(getattr(logging, self.config.logging['level'].upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatters
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.config.files['log_file'],
            maxBytes=5*1024*1024,  # 5MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, self.config.logging['level'].upper()))
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        if self.config.logging['console']:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.config.logging['level'].upper()))
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # Exception handler
        exception_handler = logging.handlers.RotatingFileHandler(
            log_dir / 'exceptions.log',
            maxBytes=5*1024*1024,
            backupCount=5
        )
        exception_handler.setLevel(logging.ERROR)
        exception_handler.setFormatter(file_formatter)
        self.logger.addHandler(exception_handler)
        
        self.logger.info('✅ Logger initialized')
    
    def child(self, meta: Dict[str, Any]) -> logging.Logger:
        """Create child logger with additional metadata"""
        return self.logger.getChild(str(meta))
    
    def error(self, message: str, meta: Optional[Dict[str, Any]] = None):
        """Log error message"""
        self._log(logging.ERROR, message, meta)
    
    def warn(self, message: str, meta: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        self._log(logging.WARNING, message, meta)
    
    def info(self, message: str, meta: Optional[Dict[str, Any]] = None):
        """Log info message"""
        self._log(logging.INFO, message, meta)
    
    def debug(self, message: str, meta: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        self._log(logging.DEBUG, message, meta)
    
    def _log(self, level: int, message: str, meta: Optional[Dict[str, Any]] = None):
        """Internal log method"""
        if meta:
            # Format metadata as JSON-like string
            meta_str = ' '.join([f'{k}={v}' for k, v in meta.items()])
            message = f'{message} {meta_str}'
        
        self.logger.log(level, message)
    
    def log_processing_start(self, total_records: int):
        """Log processing start"""
        self.info('🚀 Processing Started', {
            'totalRecords': total_records,
            'timestamp': datetime.now().isoformat(),
            'event': 'PROCESSING_START'
        })
    
    def log_processing_complete(self, stats: Dict[str, Any]):
        """Log processing complete"""
        self.info('✅ Processing Complete', {
            **stats,
            'timestamp': datetime.now().isoformat(),
            'event': 'PROCESSING_COMPLETE'
        })
    
    def log_record_processing(self, record_index: int, cccd: str, status: str, duration: Optional[int] = None):
        """Log record processing"""
        meta = {
            'recordIndex': record_index,
            'cccd': self.sanitize_cccd(cccd),
            'status': status,
            'event': 'RECORD_PROCESSED'
        }
        
        if duration:
            meta['duration'] = duration
        
        if status == 'success':
            self.info(f'✓ Record {record_index + 1} processed successfully', meta)
        else:
            self.warn(f'⚠ Record {record_index + 1} failed: {status}', meta)
    
    def log_captcha(self, action: str, meta: Optional[Dict[str, Any]] = None):
        """Log CAPTCHA action"""
        self.debug(f'🔐 CAPTCHA {action}', {
            **(meta or {}),
            'event': 'CAPTCHA_ACTION'
        })
    
    def log_api_call(self, url: str, method: str, status: int, duration: int):
        """Log API call"""
        self.debug(f'🌐 API Call: {method} {url}', {
            'status': status,
            'duration': duration,
            'event': 'API_CALL'
        })
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        self.error(f'❌ Error: {error}', {
            'error': {
                'message': str(error),
                'type': type(error).__name__
            },
            **(context or {}),
            'event': 'ERROR'
        })
    
    def sanitize_cccd(self, cccd: str) -> str:
        """Sanitize CCCD for logging (keep first 3 and last 3 digits)"""
        if not cccd or len(cccd) < 6:
            return '***'
        first_three = cccd[:3]
        last_three = cccd[-3:]
        middle = '*' * (len(cccd) - 6)
        return f'{first_three}{middle}{last_three}'
    
    def create_progress_logger(self, total: int):
        """Create progress logger"""
        processed = 0
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        def update(success: bool = True):
            nonlocal processed, successful, failed
            processed += 1
            if success:
                successful += 1
            else:
                failed += 1
            
            percentage = round((processed / total) * 100)
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            avg_time_per_record = round(elapsed / processed)
            eta = round((total - processed) * avg_time_per_record / 1000)
            
            self.info(f'📊 Progress: {processed}/{total} ({percentage}%)', {
                'processed': processed,
                'successful': successful,
                'failed': failed,
                'total': total,
                'percentage': percentage,
                'avgTimePerRecord': avg_time_per_record,
                'eta': eta,
                'event': 'PROGRESS_UPDATE'
            })
        
        def get_stats():
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            return {
                'processed': processed,
                'successful': successful,
                'failed': failed,
                'total': total,
                'successRate': round((successful / processed) * 100) if processed > 0 else 0,
                'duration': elapsed
            }
        
        return type('ProgressLogger', (), {
            'update': update,
            'get_stats': get_stats
        })()


# Singleton instance
_instance: Optional[Logger] = None


def get_logger() -> Logger:
    """Get logger instance"""
    global _instance
    if _instance is None:
        _instance = Logger()
    return _instance