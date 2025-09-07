#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Configuration Management
Quản lý cấu hình hệ thống tập trung
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class SystemConfig:
    """
    Class quản lý cấu hình hệ thống
    """
    
    def __init__(self, env_file: str = None):
        """
        Khởi tạo system config
        
        Args:
            env_file: Đường dẫn đến file .env
        """
        self.project_root = Path.cwd()
        
        # Load environment variables
        if env_file:
            load_dotenv(env_file)
        else:
            # Tìm file .env trong thư mục hiện tại
            env_path = self.project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path)
        
        self._load_configuration()
    
    def _load_configuration(self):
        """
        Load và validate cấu hình từ environment variables
        """
        # BHXH Configuration
        self.captcha_api_key = os.getenv('CAPTCHA_API_KEY', '')
        self.captcha_website_key = os.getenv('CAPTCHA_WEBSITE_KEY', '6Lcey5QUAAAAADcB0m7xYLj8W8HHi8ur4JQrTCUY')
        self.captcha_website_url = os.getenv('CAPTCHA_WEBSITE_URL', 'https://baohiemxahoi.gov.vn')
        self.bhxh_api_url = os.getenv('BHXH_API_URL', 'https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx')
        
        # Doanh Nghiep API Configuration
        self.doanh_nghiep_api_url = os.getenv('DOANH_NGHIEP_API_URL', 'https://thongtindoanhnghiep.co')
        
        # System Configuration
        self.max_concurrent_processing = int(os.getenv('MAX_CONCURRENT_PROCESSING', '5'))
        self.retry_max_attempts = int(os.getenv('RETRY_MAX_ATTEMPTS', '3'))
        self.retry_base_delay = int(os.getenv('RETRY_BASE_DELAY', '2000'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30000'))
        
        # CCCD Generation Configuration
        self.cccd_count = int(os.getenv('CCCD_COUNT', '100'))
        self.cccd_province_code = os.getenv('CCCD_PROVINCE_CODE', '001')
        self.cccd_gender = os.getenv('CCCD_GENDER', '')
        self.cccd_birth_year_from = int(os.getenv('CCCD_BIRTH_YEAR_FROM', '1990'))
        self.cccd_birth_year_to = int(os.getenv('CCCD_BIRTH_YEAR_TO', '2000'))
        self.cccd_random_seed = int(os.getenv('CCCD_RANDOM_SEED', '42'))
        
        # Excel Configuration
        self.excel_output_file = os.getenv('EXCEL_OUTPUT_FILE', 'output.xlsx')
        self.batch_write_size = int(os.getenv('BATCH_WRITE_SIZE', '10'))
        
        # Logging Configuration
        self.log_level = os.getenv('LOG_LEVEL', 'info').upper()
        self.log_file = os.getenv('LOG_FILE', 'logs/system.log')
        
        # Environment Mode
        self.node_env = os.getenv('NODE_ENV', 'production')
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
        # Cache Configuration
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('CACHE_TTL', '300000'))
        
        # Paths Configuration
        self.modules_path = self.project_root / "modules"
        self.output_path = self.project_root / "output"
        self.logs_path = self.project_root / "logs"
        self.config_path = self.project_root / "config"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """
        Tạo các thư mục cần thiết nếu chưa tồn tại
        """
        directories = [
            self.output_path,
            self.logs_path,
            self.config_path
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
    
    def get_module_path(self, module_name: str) -> Path:
        """
        Lấy đường dẫn đến module cụ thể
        
        Args:
            module_name: Tên module ('cccd', 'doanh-nghiep', 'bhxh')
            
        Returns:
            Path đến thư mục module
        """
        return self.modules_path / module_name
    
    def get_output_file_path(self, filename: str) -> Path:
        """
        Lấy đường dẫn đầy đủ cho file output
        
        Args:
            filename: Tên file
            
        Returns:
            Path đầy đủ đến file
        """
        return self.output_path / filename
    
    def get_log_file_path(self, filename: str = None) -> Path:
        """
        Lấy đường dẫn đầy đủ cho file log
        
        Args:
            filename: Tên file log (nếu None sẽ dùng config mặc định)
            
        Returns:
            Path đầy đủ đến file log
        """
        if filename:
            return self.logs_path / filename
        else:
            return self.project_root / self.log_file
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Kiểm tra tính hợp lệ của cấu hình
        
        Returns:
            Dict chứa kết quả validation
        """
        errors = []
        warnings = []
        
        # Kiểm tra CAPTCHA API key
        if not self.captcha_api_key or self.captcha_api_key == 'your_2captcha_api_key_here':
            warnings.append("CAPTCHA_API_KEY chưa được cấu hình - Module BHXH sẽ không hoạt động")
        
        # Kiểm tra số lượng CCCD hợp lý
        if self.cccd_count <= 0 or self.cccd_count > 100000:
            errors.append(f"CCCD_COUNT không hợp lệ: {self.cccd_count} (phải từ 1-100,000)")
        
        # Kiểm tra năm sinh
        if self.cccd_birth_year_from < 1900 or self.cccd_birth_year_from > 2024:
            errors.append(f"CCCD_BIRTH_YEAR_FROM không hợp lệ: {self.cccd_birth_year_from} (phải từ 1900-2024)")
        
        if self.cccd_birth_year_to < 1900 or self.cccd_birth_year_to > 2024:
            errors.append(f"CCCD_BIRTH_YEAR_TO không hợp lệ: {self.cccd_birth_year_to} (phải từ 1900-2024)")
        
        if self.cccd_birth_year_from > self.cccd_birth_year_to:
            errors.append(f"CCCD_BIRTH_YEAR_FROM ({self.cccd_birth_year_from}) phải nhỏ hơn hoặc bằng CCCD_BIRTH_YEAR_TO ({self.cccd_birth_year_to})")
        
        # Kiểm tra mã tỉnh
        if len(self.cccd_province_code) != 3 or not self.cccd_province_code.isdigit():
            errors.append(f"CCCD_PROVINCE_CODE không hợp lệ: {self.cccd_province_code} (phải là 3 chữ số)")
        
        # Kiểm tra thư mục modules
        if not self.modules_path.exists():
            errors.append(f"Thư mục modules không tồn tại: {self.modules_path}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def print_configuration_summary(self):
        """
        In tóm tắt cấu hình hệ thống
        """
        print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
        print("┃                CẤU HÌNH HỆ THỐNG                      ┃")
        print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
        
        print(f"📋 CCCD Generation:")
        print(f"  - Số lượng: {self.cccd_count}")
        print(f"  - Mã tỉnh: {self.cccd_province_code}")
        
        print(f"\n🏢 APIs:")
        print(f"  - Doanh Nghiệp: {self.doanh_nghiep_api_url}")
        print(f"  - BHXH: {'Cấu hình' if self.captcha_api_key else 'Chưa cấu hình'}")
        
        print(f"\n📊 Processing:")
        print(f"  - Max concurrent: {self.max_concurrent_processing}")
        print(f"  - Retry attempts: {self.retry_max_attempts}")
        
        print(f"\n📝 Output:")
        print(f"  - Excel file: {self.excel_output_file}")
        print(f"  - Output path: {self.output_path}")
        print(f"  - Logs path: {self.logs_path}")
        
        print(f"\n⚙️ System:")
        print(f"  - Environment: {self.node_env}")
        print(f"  - Debug mode: {self.debug_mode}")
        print(f"  - Log level: {self.log_level}")
        print()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Chuyển đổi cấu hình thành dictionary
        
        Returns:
            Dict chứa toàn bộ cấu hình
        """
        return {
            "captcha_api_key": "***" if self.captcha_api_key else None,
            "captcha_website_key": self.captcha_website_key,
            "captcha_website_url": self.captcha_website_url,
            "bhxh_api_url": self.bhxh_api_url,
            "doanh_nghiep_api_url": self.doanh_nghiep_api_url,
            "max_concurrent_processing": self.max_concurrent_processing,
            "retry_max_attempts": self.retry_max_attempts,
            "retry_base_delay": self.retry_base_delay,
            "request_timeout": self.request_timeout,
            "cccd_count": self.cccd_count,
            "cccd_province_code": self.cccd_province_code,
            "cccd_random_seed": self.cccd_random_seed,
            "excel_output_file": self.excel_output_file,
            "batch_write_size": self.batch_write_size,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "node_env": self.node_env,
            "debug_mode": self.debug_mode,
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self.cache_ttl
        }


# Singleton instance
_config_instance = None

def get_config(env_file: str = None) -> SystemConfig:
    """
    Lấy singleton instance của SystemConfig
    
    Args:
        env_file: Đường dẫn đến file .env
        
    Returns:
        SystemConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = SystemConfig(env_file)
    return _config_instance


if __name__ == "__main__":
    # Test configuration
    config = get_config()
    config.print_configuration_summary()
    
    validation = config.validate_configuration()
    if validation['valid']:
        print("✅ Cấu hình hợp lệ")
    else:
        print("❌ Lỗi cấu hình:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("\n⚠️ Cảnh báo:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
