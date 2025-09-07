"""
Enhanced Province Service with Optimized Mapping
"""

import json
import os
import re
from typing import Dict, Any, List, Optional
from config.config import get_config_instance
from utils.logger import get_logger
from utils.cache import get_cache_util


class ProvinceService:
    """Enhanced Province Service with Optimized Mapping"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.logger = get_logger()
        self.cache = get_cache_util()
        self.provinces = []
        self.mapping_index = {}  # For faster lookups
        self.load_provinces()
    
    def load_provinces(self):
        """Load provinces data from JSON file"""
        try:
            province_path = self.config.files['provinces_json']
            
            if not os.path.exists(province_path):
                raise FileNotFoundError(f'Province data file not found: {province_path}')
            
            with open(province_path, 'r', encoding='utf-8') as f:
                self.provinces = json.load(f)
            
            if not isinstance(self.provinces, list) or len(self.provinces) == 0:
                raise ValueError('Invalid province data format')
            
            # Build mapping index for faster lookups
            self.build_mapping_index()
            
            # Warm up cache
            self.cache.warm_up_province_cache(self.provinces)
            
            self.logger.info(f'✅ Loaded {len(self.provinces)} provinces')
            
        except Exception as error:
            self.logger.error(f'❌ Error loading provinces: {error}')
            raise error
    
    def build_mapping_index(self):
        """Build optimized mapping index"""
        try:
            self.mapping_index.clear()
            
            # Sort provinces by name length (descending) for better matching
            sorted_provinces = sorted(self.provinces, key=lambda x: len(x['name']), reverse=True)
            
            for province in sorted_provinces:
                # Index by full name
                self.mapping_index[province['name'].lower()] = province
                
                # Index by alternative names and keywords
                alternatives = self.generate_alternative_names(province['name'])
                for alt in alternatives:
                    if alt.lower() not in self.mapping_index:
                        self.mapping_index[alt.lower()] = province
            
            self.logger.debug(f'🗺️ Built province mapping index with {len(self.mapping_index)} entries')
            
        except Exception as error:
            self.logger.error(f'❌ Error building province mapping index: {error}')
            raise error
    
    def generate_alternative_names(self, province_name: str) -> List[str]:
        """Generate alternative names for province"""
        alternatives = []
        
        # Common prefixes to remove/add
        prefixes = ['Tỉnh', 'Thành phố', 'TP.', 'TP']
        common_replacements = {
            'TP. Hồ Chí Minh': ['Hồ Chí Minh', 'TPHCM', 'Sài Gòn', 'Saigon'],
            'Thừa Thiên Huế': ['Huế', 'Thừa Thiên-Huế'],
            'Bà Rịa - Vũng Tàu': ['Bà Rịa-Vũng Tàu', 'Vũng Tàu', 'Ba Ria Vung Tau'],
            'Đắk Lắk': ['Dak Lak', 'Đăk Lăk'],
            'Đắk Nông': ['Dak Nong', 'Đăk Nông']
        }
        
        # Add original name
        alternatives.append(province_name)
        
        # Add name without prefixes
        name_without_prefix = province_name
        for prefix in prefixes:
            if province_name.startswith(prefix):
                name_without_prefix = province_name.replace(prefix, '').strip()
                alternatives.append(name_without_prefix)
                break
        
        # Add name with different prefixes
        for prefix in prefixes:
            if not province_name.startswith(prefix):
                alternatives.append(f'{prefix} {name_without_prefix}')
        
        # Add common replacements
        if province_name in common_replacements:
            alternatives.extend(common_replacements[province_name])
        
        # Add normalized versions (remove diacritics for fuzzy matching)
        alternatives.append(self.remove_diacritics(province_name))
        alternatives.append(self.remove_diacritics(name_without_prefix))
        
        return list(set(alternatives))  # Remove duplicates
    
    def remove_diacritics(self, text: str) -> str:
        """Remove Vietnamese diacritics"""
        diacritics_map = {
            'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
            'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
            'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
            'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
            'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
            'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
            'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
            'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
            'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
            'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
            'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
            'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
            'đ': 'd', 'Đ': 'D'
        }
        
        return ''.join(diacritics_map.get(char, char) for char in text)
    
    def find_province_code(self, address: str) -> Optional[Dict[str, Any]]:
        """Find province code from address with enhanced algorithm"""
        if not address or not isinstance(address, str):
            return None
        
        # Check cache first
        cached = self.cache.get_province_code(address)
        if cached:
            return cached
        
        try:
            result = self.find_province_code_internal(address)
            
            # Cache the result if found
            if result:
                self.cache.set_province_code(address, result)
            
            return result
            
        except Exception as error:
            self.logger.error(f'❌ Error finding province code: {error}', {
                'address': address[:50]
            })
            return None
    
    def find_province_code_internal(self, address: str) -> Optional[Dict[str, Any]]:
        """Internal province finding logic"""
        normalized_address = address.lower().strip()
        
        # Strategy 1: Exact match in mapping index
        if normalized_address in self.mapping_index:
            province = self.mapping_index[normalized_address]
            self.logger.debug(f'🎯 Exact match found: {province["name"]}', {
                'strategy': 'exact_match',
                'address': address[:30]
            })
            return {'code': province['code'], 'name': province['name']}
        
        # Strategy 2: Word boundary match (most reliable)
        for key, province in self.mapping_index.items():
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, normalized_address, re.IGNORECASE):
                self.logger.debug(f'🎯 Word boundary match: {province["name"]}', {
                    'strategy': 'word_boundary',
                    'address': address[:30]
                })
                return {'code': province['code'], 'name': province['name']}
        
        # Strategy 3: Address parts exact match
        address_parts = [part.strip() for part in re.split(r'[,;]', normalized_address)]
        for part in address_parts:
            if part in self.mapping_index:
                province = self.mapping_index[part]
                self.logger.debug(f'🎯 Address part match: {province["name"]}', {
                    'strategy': 'address_part',
                    'matched_part': part,
                    'address': address[:30]
                })
                return {'code': province['code'], 'name': province['name']}
        
        # Strategy 4: Ends with province name
        for key, province in self.mapping_index.items():
            if normalized_address.endswith(key):
                self.logger.debug(f'🎯 Ends with match: {province["name"]}', {
                    'strategy': 'ends_with',
                    'address': address[:30]
                })
                return {'code': province['code'], 'name': province['name']}
        
        # Strategy 5: Contains match (less reliable, use sorted order)
        sorted_entries = sorted(self.mapping_index.items(), key=lambda x: len(x[0]), reverse=True)
        
        for key, province in sorted_entries:
            if key in normalized_address and len(key) >= 4:  # Minimum 4 characters
                self.logger.debug(f'🎯 Contains match: {province["name"]}', {
                    'strategy': 'contains',
                    'matched_key': key,
                    'address': address[:30]
                })
                return {'code': province['code'], 'name': province['name']}
        
        # Strategy 6: Fuzzy match without diacritics
        normalized_without_diacritics = self.remove_diacritics(normalized_address)
        for key, province in self.mapping_index.items():
            key_without_diacritics = self.remove_diacritics(key)
            if (key_without_diacritics in normalized_without_diacritics and 
                len(key_without_diacritics) >= 4):
                self.logger.debug(f'🎯 Fuzzy match: {province["name"]}', {
                    'strategy': 'fuzzy',
                    'address': address[:30]
                })
                return {'code': province['code'], 'name': province['name']}
        
        self.logger.warn(f'⚠️ No province found for address: {address[:50]}')
        return None
    
    def get_all_provinces(self) -> List[Dict[str, Any]]:
        """Get all provinces"""
        return self.provinces.copy()
    
    def get_province_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get province by code"""
        return next((p for p in self.provinces if p['code'] == code), None)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get province statistics"""
        return {
            'total_provinces': len(self.provinces),
            'mapping_index_size': len(self.mapping_index),
            'cache_stats': self.cache.get_stats().get('province', {})
        }
    
    def validate_province_data(self) -> Dict[str, Any]:
        """Validate province data"""
        issues = []
        
        # Check for duplicate codes
        codes = [p['code'] for p in self.provinces]
        duplicate_codes = [code for code in set(codes) if codes.count(code) > 1]
        if duplicate_codes:
            issues.append(f'Duplicate codes: {", ".join(duplicate_codes)}')
        
        # Check for empty names or codes
        invalid_provinces = [p for p in self.provinces if not p.get('name') or not p.get('code')]
        if invalid_provinces:
            issues.append(f'{len(invalid_provinces)} provinces with missing name or code')
        
        # Check code format
        invalid_codes = [p for p in self.provinces if not re.match(r'^\d{2}TTT$', p['code'])]
        if invalid_codes:
            issues.append(f'{len(invalid_codes)} provinces with invalid code format')
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    def test_mapping(self) -> Dict[str, Any]:
        """Test province mapping with sample addresses"""
        test_addresses = [
            'Số 1, Đường ABC, Quận 1, TP. Hồ Chí Minh',
            'Thôn Cổ Điển, Xã Hải Bối, Huyện Đông Anh, Hà Nội',
            'Phường Hải Châu 1, Quận Hải Châu, Đà Nẵng',
            'Xã Tân An, Huyện Vĩnh Cửu, Đồng Nai',
            'Huyện Phú Quốc, Kiên Giang',
            'Can Tho',  # Short form
            'Hue',  # Without diacritics
            'TPHCM'  # Abbreviation
        ]
        
        results = []
        
        for address in test_addresses:
            result = self.find_province_code(address)
            results.append({
                'address': address,
                'found': bool(result),
                'province': result['name'] if result else None,
                'code': result['code'] if result else None
            })
        
        success_rate = (len([r for r in results if r['found']]) / len(results)) * 100
        
        self.logger.info(f'🧪 Province mapping test completed: {success_rate}% success rate')
        
        return {
            'results': results,
            'success_rate': success_rate,
            'total_tests': len(results),
            'successful': len([r for r in results if r['found']])
        }


# Singleton instance
_instance: Optional[ProvinceService] = None


def get_province_service() -> ProvinceService:
    """Get province service instance"""
    global _instance
    if _instance is None:
        _instance = ProvinceService()
    return _instance