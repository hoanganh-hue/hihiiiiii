"""
Environment Variables Validation
"""

import os
import sys
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EnvConfig(BaseModel):
    """Environment configuration schema"""
    
    # 2captcha Configuration
    captcha_api_key: str = Field(..., min_length=32, description='2captcha API key')
    captcha_website_key: str = Field(
        default='6Lcey5QUAAAAADcB0m7xYLj8W8HHi8ur4JQrTCUY',
        description='Google reCAPTCHA site key'
    )
    captcha_website_url: str = Field(
        default='https://baohiemxahoi.gov.vn',
        description='CAPTCHA website URL'
    )
    
    # BHXH API Configuration
    bhxh_api_url: str = Field(
        default='https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx',
        description='BHXH API endpoint'
    )
    
    # Processing Configuration
    max_concurrent_processing: int = Field(
        default=5, ge=1, le=50,
        description='Maximum concurrent processing threads'
    )
    retry_max_attempts: int = Field(
        default=3, ge=1, le=10,
        description='Maximum retry attempts'
    )
    retry_base_delay: int = Field(
        default=2000, ge=100,
        description='Base delay for retry (ms)'
    )
    request_timeout: int = Field(
        default=30000, ge=1000,
        description='HTTP request timeout (ms)'
    )
    
    # Excel Configuration
    excel_input_file: str = Field(
        default='data-input.xlsx',
        description='Input Excel file path'
    )
    excel_output_file: str = Field(
        default='data-output.xlsx',
        description='Output Excel file path'
    )
    batch_write_size: int = Field(
        default=10, ge=1,
        description='Batch size for Excel writing'
    )
    
    # Logging Configuration
    log_level: str = Field(
        default='info',
        description='Logging level'
    )
    log_file: str = Field(
        default='logs/bhxh-tool.log',
        description='Log file path'
    )
    
    # Environment Configuration
    node_env: str = Field(
        default='production',
        description='Node environment'
    )
    debug_mode: bool = Field(
        default=False,
        description='Enable debug mode'
    )
    
    # Cache Configuration
    cache_enabled: bool = Field(
        default=True,
        description='Enable caching'
    )
    cache_ttl: int = Field(
        default=300000, ge=1000,
        description='Cache TTL in milliseconds'
    )
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['error', 'warn', 'info', 'debug']
        if v.lower() not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v.lower()
    
    @validator('node_env')
    def validate_node_env(cls, v):
        valid_envs = ['development', 'production', 'test']
        if v.lower() not in valid_envs:
            raise ValueError(f'Node environment must be one of: {valid_envs}')
        return v.lower()
    
    @validator('captcha_api_key')
    def validate_captcha_api_key(cls, v):
        if not v or v == 'your_2captcha_api_key_here':
            raise ValueError('CAPTCHA API key must be configured')
        return v


def validate_env() -> EnvConfig:
    """Validate environment variables"""
    is_test_env = os.getenv('NODE_ENV') == 'test' or os.getenv('PYTEST_CURRENT_TEST')
    
    try:
        # Map environment variables to config fields
        env_mapping = {
            'captcha_api_key': 'CAPTCHA_API_KEY',
            'captcha_website_key': 'CAPTCHA_WEBSITE_KEY', 
            'captcha_website_url': 'CAPTCHA_WEBSITE_URL',
            'bhxh_api_url': 'BHXH_API_URL',
            'max_concurrent_processing': 'MAX_CONCURRENT_PROCESSING',
            'retry_max_attempts': 'RETRY_MAX_ATTEMPTS',
            'retry_base_delay': 'RETRY_BASE_DELAY',
            'request_timeout': 'REQUEST_TIMEOUT',
            'excel_input_file': 'EXCEL_INPUT_FILE',
            'excel_output_file': 'EXCEL_OUTPUT_FILE',
            'batch_write_size': 'BATCH_WRITE_SIZE',
            'log_level': 'LOG_LEVEL',
            'log_file': 'LOG_FILE',
            'node_env': 'NODE_ENV',
            'debug_mode': 'DEBUG_MODE',
            'cache_enabled': 'CACHE_ENABLED',
            'cache_ttl': 'CACHE_TTL'
        }
        
        # Build config dict from environment
        config_dict = {}
        for field_name, env_name in env_mapping.items():
            env_value = os.getenv(env_name)
            if env_value is not None:
                # Convert string values to appropriate types
                if field_name in ['max_concurrent_processing', 'retry_max_attempts', 
                                'retry_base_delay', 'request_timeout', 'batch_write_size', 'cache_ttl']:
                    config_dict[field_name] = int(env_value)
                elif field_name in ['debug_mode', 'cache_enabled']:
                    config_dict[field_name] = env_value.lower() in ('true', '1', 'yes', 'on')
                else:
                    config_dict[field_name] = env_value
        
        config = EnvConfig(**config_dict)
        
        if not is_test_env:
            print('✅ Environment validation passed')
        
        return config
        
    except Exception as e:
        if is_test_env:
            # Provide safe defaults for tests
            fallback_config = {
                'captcha_api_key': os.getenv('CAPTCHA_API_KEY', 'test_key_32_chars_min_length________'),
            }
            print('⚠️ Environment validation had issues in test mode, using fallbacks')
            return EnvConfig(**fallback_config)
        
        print('❌ Environment validation failed:')
        print(f'  - {str(e)}')
        sys.exit(1)


def get_config() -> EnvConfig:
    """Get validated configuration"""
    return validate_env()


# Auto-validate when required directly
if __name__ == '__main__':
    validate_env()