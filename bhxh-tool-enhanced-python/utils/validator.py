"""
Enhanced Input Validator with Sanitization
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from config.config import get_config_instance


class Validator:
    """Enhanced Input Validator with Sanitization"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.setup_schemas()
    
    def setup_schemas(self):
        """Setup validation schemas"""
        # CCCD/CMND regex
        self.cccd_regex = re.compile(self.config.validation['cccd']['regex'])
        self.cccd_min_length = self.config.validation['cccd']['min_length']
        self.cccd_max_length = self.config.validation['cccd']['max_length']
        
        # Name regex
        self.name_regex = re.compile(self.config.validation['name']['regex'])
        self.name_min_length = self.config.validation['name']['min_length']
        self.name_max_length = self.config.validation['name']['max_length']
        
        # Phone regex
        self.phone_regex = re.compile(r'^[\d\s\-\+\(\)]*$')
    
    def validate_cccd(self, cccd: str) -> Dict[str, Any]:
        """Validate and sanitize CCCD"""
        try:
            # Sanitize: remove all non-digit characters
            sanitized = re.sub(r'\D', '', str(cccd))
            
            # Validate
            if not sanitized:
                return {
                    'is_valid': False,
                    'error': 'Số CCCD/CMND là bắt buộc',
                    'sanitized': None
                }
            
            if len(sanitized) < self.cccd_min_length:
                return {
                    'is_valid': False,
                    'error': f'Số CCCD/CMND phải có ít nhất {self.cccd_min_length} chữ số',
                    'sanitized': None
                }
            
            if len(sanitized) > self.cccd_max_length:
                return {
                    'is_valid': False,
                    'error': f'Số CCCD/CMND không được vượt quá {self.cccd_max_length} chữ số',
                    'sanitized': None
                }
            
            if not self.cccd_regex.match(sanitized):
                return {
                    'is_valid': False,
                    'error': 'Số CCCD/CMND phải chứa từ 9-12 chữ số',
                    'sanitized': None
                }
            
            return {
                'is_valid': True,
                'error': None,
                'sanitized': sanitized
            }
            
        except Exception:
            return {
                'is_valid': False,
                'error': 'Lỗi xử lý số CCCD/CMND',
                'sanitized': None
            }
    
    def validate_name(self, name: str) -> Dict[str, Any]:
        """Validate and sanitize name"""
        try:
            # Sanitize: trim and normalize spaces
            sanitized = str(name).strip()
            sanitized = re.sub(r'\s+', ' ', sanitized)  # Replace multiple spaces with single space
            sanitized = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđĐ]', '', sanitized)
            
            # Validate
            if not sanitized:
                return {
                    'is_valid': False,
                    'error': 'Họ tên là bắt buộc',
                    'sanitized': None
                }
            
            if len(sanitized) < self.name_min_length:
                return {
                    'is_valid': False,
                    'error': f'Họ tên phải có ít nhất {self.name_min_length} ký tự',
                    'sanitized': None
                }
            
            if len(sanitized) > self.name_max_length:
                return {
                    'is_valid': False,
                    'error': f'Họ tên không được vượt quá {self.name_max_length} ký tự',
                    'sanitized': None
                }
            
            if not self.name_regex.match(sanitized):
                return {
                    'is_valid': False,
                    'error': 'Họ tên chỉ được chứa ký tự tiếng Việt và khoảng trắng',
                    'sanitized': None
                }
            
            return {
                'is_valid': True,
                'error': None,
                'sanitized': sanitized
            }
            
        except Exception:
            return {
                'is_valid': False,
                'error': 'Lỗi xử lý họ tên',
                'sanitized': None
            }
    
    def validate_address(self, address: str) -> Dict[str, Any]:
        """Validate and sanitize address"""
        try:
            # Sanitize: trim and clean
            sanitized = str(address).strip() if address else ''
            sanitized = re.sub(r'\s+', ' ', sanitized)  # Replace multiple spaces with single space
            sanitized = re.sub(r'[<>]', '', sanitized)  # Remove potential HTML characters
            
            # Validate
            if len(sanitized) > 500:
                return {
                    'is_valid': False,
                    'error': 'Địa chỉ không được vượt quá 500 ký tự',
                    'sanitized': None
                }
            
            return {
                'is_valid': True,
                'error': None,
                'sanitized': sanitized
            }
            
        except Exception:
            return {
                'is_valid': False,
                'error': 'Lỗi xử lý địa chỉ',
                'sanitized': None
            }
    
    def validate_phone(self, phone: str) -> Dict[str, Any]:
        """Validate and sanitize phone number"""
        try:
            # Sanitize: keep only digits, spaces, and common phone characters
            sanitized = str(phone).strip() if phone else ''
            sanitized = re.sub(r'[^\d\s\-\+\(\)]', '', sanitized)
            
            # Validate
            if len(sanitized) > 20:
                return {
                    'is_valid': False,
                    'error': 'Số điện thoại không được vượt quá 20 ký tự',
                    'sanitized': None
                }
            
            if sanitized and not self.phone_regex.match(sanitized):
                return {
                    'is_valid': False,
                    'error': 'Số điện thoại không hợp lệ',
                    'sanitized': None
                }
            
            return {
                'is_valid': True,
                'error': None,
                'sanitized': sanitized
            }
            
        except Exception:
            return {
                'is_valid': False,
                'error': 'Lỗi xử lý số điện thoại',
                'sanitized': None
            }
    
    def validate_record(self, record: Dict[str, Any], record_index: int) -> Dict[str, Any]:
        """Validate complete record"""
        errors = []
        sanitized = {}
        is_valid = True
        
        # Validate each field
        fields = [
            {'name': 'soCCCD', 'validator': 'validate_cccd', 'required': True},
            {'name': 'hoVaTen', 'validator': 'validate_name', 'required': True},
            {'name': 'diaChi', 'validator': 'validate_address', 'required': False},
            {'name': 'soDienThoai', 'validator': 'validate_phone', 'required': False}
        ]
        
        for field in fields:
            value = record.get(field['name'])
            
            # Check required fields
            if field['required'] and (not value or str(value).strip() == ''):
                errors.append(f'Dòng {record_index + 1}: Thiếu {field["name"]}')
                is_valid = False
                continue
            
            # Validate field
            validation = getattr(self, field['validator'])(value)
            
            if not validation['is_valid']:
                errors.append(f'Dòng {record_index + 1}: {validation["error"]}')
                is_valid = False
            else:
                sanitized[field['name']] = validation['sanitized']
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'sanitized': sanitized if is_valid else None
        }
    
    def validate_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch validate records"""
        results = []
        valid_records = []
        invalid_records = []
        
        for i, record in enumerate(records):
            validation = self.validate_record(record, i)
            
            results.append({
                'index': i,
                'is_valid': validation['is_valid'],
                'errors': validation['errors'],
                'original': record,
                'sanitized': validation['sanitized']
            })
            
            if validation['is_valid']:
                valid_records.append({
                    'index': i,
                    'data': validation['sanitized']
                })
            else:
                invalid_records.append({
                    'index': i,
                    'data': record,
                    'errors': validation['errors']
                })
        
        return {
            'results': results,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'total_records': len(records),
            'valid_count': len(valid_records),
            'invalid_count': len(invalid_records)
        }
    
    def sanitize_error_message(self, message: str) -> str:
        """Sanitize error messages for logging"""
        # Remove potential sensitive information from error messages
        message = re.sub(r'\d{9,12}', '***', message)  # Hide CCCD numbers
        message = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '***@***.***', message)  # Hide emails
        return message


# Singleton instance
_instance: Optional[Validator] = None


def get_validator() -> Validator:
    """Get validator instance"""
    global _instance
    if _instance is None:
        _instance = Validator()
    return _instance