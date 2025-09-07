"""
Enhanced BHXH Tool Configuration
"""

import os
import pathlib
from typing import Optional
from .validate_env import get_config


class Config:
    """Enhanced BHXH Tool Configuration"""
    
    def __init__(self):
        # Load and validate environment variables
        self.env = get_config()
        
        # CAPTCHA Configuration
        self.captcha = {
            'api_key': self.env.captcha_api_key,
            'website_key': self.env.captcha_website_key,
            'website_url': self.env.captcha_website_url,
            'submit_url': 'https://2captcha.com/in.php',
            'result_url': 'https://2captcha.com/res.php',
            'max_attempts': 36,
            'poll_interval': 5000,
            'timeout': 180000
        }
        
        # BHXH API Configuration
        self.bhxh = {
            'api_url': self.env.bhxh_api_url,
            'timeout': self.env.request_timeout,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Processing Configuration
        self.processing = {
            'max_concurrent': self.env.max_concurrent_processing,
            'retry_max_attempts': self.env.retry_max_attempts,
            'retry_base_delay': self.env.retry_base_delay,
            'batch_write_size': self.env.batch_write_size
        }
        
        # File Paths
        self.files = {
            'input_excel': self._resolve_file_path(self.env.excel_input_file),
            'output_excel': self._resolve_output_path(self.env.excel_output_file),
            'provinces_json': self._resolve_provinces_path(),
            'log_file': self._resolve_log_path(self.env.log_file)
        }
        
        # Logging Configuration
        self.logging = {
            'level': self.env.log_level,
            'file': self.files['log_file'],
            'console': True,
            'colorize': self.env.node_env == 'development',
            'timestamp': True
        }
        
        # Cache Configuration
        self.cache = {
            'enabled': self.env.cache_enabled,
            'ttl': self.env.cache_ttl,
            'std_ttl': self.env.cache_ttl // 1000,  # seconds
            'check_period': self.env.cache_ttl // 10000  # 10% of TTL
        }
        
        # Development Configuration
        self.dev = {
            'debug': self.env.debug_mode,
            'node_env': self.env.node_env
        }
        
        # Validation Rules
        self.validation = {
            'cccd': {
                'regex': r'^\d{9,12}$',
                'min_length': 9,
                'max_length': 12
            },
            'name': {
                'regex': r'^[a-zA-ZàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ\s]+$',
                'min_length': 2,
                'max_length': 100
            }
        }
        
        # Error Codes
        self.error_codes = {
            'VALIDATION_ERROR': 'VALIDATION_ERROR',
            'CAPTCHA_ERROR': 'CAPTCHA_ERROR',
            'API_ERROR': 'API_ERROR',
            'PARSING_ERROR': 'PARSING_ERROR',
            'FILE_ERROR': 'FILE_ERROR',
            'NETWORK_ERROR': 'NETWORK_ERROR'
        }
    
    def get(self, module: str) -> Optional[dict]:
        """Get configuration for a specific module"""
        return getattr(self, module, None)
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.env.node_env == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.env.node_env == 'production'
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.dev['debug']
    
    def print_summary(self):
        """Print configuration summary (without sensitive data)"""
        print('🔧 Configuration Summary:')
        print(f'   Environment: {self.env.node_env}')
        print(f'   Log Level: {self.logging["level"]}')
        print(f'   Max Concurrent: {self.processing["max_concurrent"]}')
        print(f'   Batch Write Size: {self.processing["batch_write_size"]}')
        print(f'   Cache Enabled: {self.cache["enabled"]}')
        print(f'   Debug Mode: {self.dev["debug"]}')
        print(f'   CAPTCHA Service: {"✅ Configured" if self.captcha["api_key"] else "❌ Not configured"}')
        print(f'   Input Excel: {self.files["input_excel"]}')
        print(f'   Output Excel: {self.files["output_excel"]}')
    
    def _resolve_file_path(self, file_path: str) -> str:
        """Resolve a file path so it works whether you run from repo root or backend folder"""
        if not file_path:
            return file_path
        
        # Absolute path stays as-is
        if pathlib.Path(file_path).is_absolute():
            return file_path
        
        # Try a few candidate locations
        candidates = [
            pathlib.Path.cwd() / file_path,  # current working directory
            pathlib.Path.cwd().parent / file_path,  # one level up
            pathlib.Path.cwd().parent.parent / file_path  # two levels up
        ]
        
        for candidate in candidates:
            try:
                if candidate.exists():
                    return str(candidate)
            except Exception:
                # ignore
                pass
        
        # Fallback to CWD join
        return str(pathlib.Path.cwd() / file_path)
    
    def _resolve_output_path(self, file_path: str) -> str:
        """Resolve output file path"""
        if pathlib.Path(file_path).is_absolute():
            return file_path
        return str(pathlib.Path.cwd() / file_path)
    
    def _resolve_provinces_path(self) -> str:
        """Resolve province JSON path"""
        return str(pathlib.Path(__file__).parent.parent / 'tinh-thanh.json')
    
    def _resolve_log_path(self, file_path: str) -> str:
        """Resolve log file path"""
        return str(pathlib.Path.cwd() / file_path)


# Singleton instance
_instance: Optional[Config] = None


def get_config_instance() -> Config:
    """Get configuration instance"""
    global _instance
    if _instance is None:
        _instance = Config()
    return _instance