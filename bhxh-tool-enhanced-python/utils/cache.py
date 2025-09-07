"""
Enhanced Cache Utility
"""

import hashlib
import time
from typing import Dict, Any, Optional
from cachetools import TTLCache
from config.config import get_config_instance
from .logger import get_logger


class CacheUtil:
    """Enhanced Cache Utility"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.logger = get_logger()
        self.setup_cache()
    
    def setup_cache(self):
        """Setup cache instances"""
        if not self.config.cache['enabled']:
            self.logger.info('Cache is disabled')
            return
        
        # Main cache for BHXH results
        self.bhxh_cache = TTLCache(
            maxsize=1000,
            ttl=self.config.cache['std_ttl']
        )
        
        # Cache for province mappings
        self.province_cache = TTLCache(
            maxsize=1000,
            ttl=86400  # 24 hours for province mappings
        )
        
        # Cache for CAPTCHA solutions (short-lived)
        self.captcha_cache = TTLCache(
            maxsize=100,
            ttl=300  # 5 minutes
        )
        
        self.logger.info('✅ Cache initialized', {
            'bhxhTTL': self.config.cache['std_ttl'],
            'checkPeriod': self.config.cache['check_period']
        })
    
    def generate_bhxh_key(self, cccd: str, ho_ten: str, dia_chi: str = '') -> str:
        """Generate cache key for BHXH lookup"""
        data = f'{cccd}|{ho_ten}|{dia_chi}'.lower()
        return hashlib.md5(data.encode()).hexdigest()
    
    def get_bhxh_result(self, cccd: str, ho_ten: str, dia_chi: str = '') -> Optional[Dict[str, Any]]:
        """Get BHXH result from cache"""
        if not self.config.cache['enabled']:
            return None
        
        try:
            key = self.generate_bhxh_key(cccd, ho_ten, dia_chi)
            result = self.bhxh_cache.get(key)
            
            if result:
                self.logger.debug('🎯 BHXH cache hit', {
                    'cccd': self.sanitize_cccd(cccd),
                    'key': self.sanitize_key(key)
                })
                return result
            
            return None
        except Exception as e:
            self.logger.error('Cache get error', {'error': str(e)})
            return None
    
    def set_bhxh_result(self, cccd: str, ho_ten: str, dia_chi: str, result: Dict[str, Any]) -> bool:
        """Set BHXH result to cache"""
        if not self.config.cache['enabled']:
            return False
        
        try:
            key = self.generate_bhxh_key(cccd, ho_ten, dia_chi)
            
            # Don't cache error results or empty results
            if result.get('status') == 'error' or result.get('soKetQua', 0) == 0:
                return False
            
            self.bhxh_cache[key] = result
            
            self.logger.debug('💾 BHXH result cached', {
                'cccd': self.sanitize_cccd(cccd),
                'key': self.sanitize_key(key),
                'soKetQua': result.get('soKetQua', 0)
            })
            
            return True
        except Exception as e:
            self.logger.error('Cache set error', {'error': str(e)})
            return False
    
    def generate_province_key(self, address: str) -> str:
        """Generate cache key for province mapping"""
        return hashlib.md5(address.lower().encode()).hexdigest()
    
    def get_province_code(self, address: str) -> Optional[Dict[str, Any]]:
        """Get province code from cache"""
        if not self.config.cache['enabled'] or not address:
            return None
        
        try:
            key = self.generate_province_key(address)
            result = self.province_cache.get(key)
            
            if result:
                self.logger.debug('🗺️ Province cache hit', {
                    'address': address[:20] + '...',
                    'key': self.sanitize_key(key)
                })
                return result
            
            return None
        except Exception as e:
            self.logger.error('Province cache get error', {'error': str(e)})
            return None
    
    def set_province_code(self, address: str, province_data: Dict[str, Any]) -> bool:
        """Set province code to cache"""
        if not self.config.cache['enabled'] or not address:
            return False
        
        try:
            key = self.generate_province_key(address)
            self.province_cache[key] = province_data
            
            self.logger.debug('🗺️ Province mapping cached', {
                'address': address[:20] + '...',
                'province': province_data.get('name', ''),
                'key': self.sanitize_key(key)
            })
            
            return True
        except Exception as e:
            self.logger.error('Province cache set error', {'error': str(e)})
            return False
    
    def set_captcha_solution(self, website_url: str, solution: str) -> bool:
        """Cache CAPTCHA solution temporarily"""
        if not self.config.cache['enabled']:
            return False
        
        try:
            key = hashlib.md5(website_url.encode()).hexdigest()
            self.captcha_cache[key] = solution
            
            self.logger.debug('🔐 CAPTCHA solution cached', {
                'url': website_url,
                'key': self.sanitize_key(key)
            })
            
            return True
        except Exception as e:
            self.logger.error('CAPTCHA cache set error', {'error': str(e)})
            return False
    
    def get_captcha_solution(self, website_url: str) -> Optional[str]:
        """Get cached CAPTCHA solution"""
        if not self.config.cache['enabled']:
            return None
        
        try:
            key = hashlib.md5(website_url.encode()).hexdigest()
            result = self.captcha_cache.get(key)
            
            if result:
                self.logger.debug('🔐 CAPTCHA cache hit', {
                    'url': website_url,
                    'key': self.sanitize_key(key)
                })
                return result
            
            return None
        except Exception as e:
            self.logger.error('CAPTCHA cache get error', {'error': str(e)})
            return None
    
    def clear_all(self):
        """Clear all caches"""
        if not self.config.cache['enabled']:
            return
        
        try:
            self.bhxh_cache.clear()
            self.province_cache.clear()
            self.captcha_cache.clear()
            
            self.logger.info('🗑️ All caches cleared')
        except Exception as e:
            self.logger.error('Cache clear error', {'error': str(e)})
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.config.cache['enabled']:
            return {'enabled': False}
        
        try:
            return {
                'enabled': True,
                'bhxh': {
                    'size': len(self.bhxh_cache),
                    'maxsize': self.bhxh_cache.maxsize,
                    'ttl': self.bhxh_cache.ttl
                },
                'province': {
                    'size': len(self.province_cache),
                    'maxsize': self.province_cache.maxsize,
                    'ttl': self.province_cache.ttl
                },
                'captcha': {
                    'size': len(self.captcha_cache),
                    'maxsize': self.captcha_cache.maxsize,
                    'ttl': self.captcha_cache.ttl
                }
            }
        except Exception as e:
            self.logger.error('Cache stats error', {'error': str(e)})
            return {'enabled': True, 'error': str(e)}
    
    def warm_up_province_cache(self, provinces: list):
        """Warm up cache with common province mappings"""
        if not self.config.cache['enabled'] or not provinces:
            return
        
        try:
            common_addresses = [
                'Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng',
                'Cần Thơ', 'Biên Hòa', 'Nha Trang', 'Huế'
            ]
            
            warmed_count = 0
            
            for address in common_addresses:
                province = next((p for p in provinces if 
                               address.lower() in p['name'].lower() or
                               p['name'].lower() in address.lower()), None)
                
                if province:
                    self.set_province_code(address, province)
                    warmed_count += 1
            
            self.logger.info(f'🔥 Province cache warmed up with {warmed_count} entries')
        except Exception as e:
            self.logger.error('Province cache warmup error', {'error': str(e)})
    
    def sanitize_key(self, key: str) -> str:
        """Sanitize cache key for logging"""
        return f'{key[:8]}...' if key else 'unknown'
    
    def sanitize_cccd(self, cccd: str) -> str:
        """Sanitize CCCD for logging"""
        if not cccd or len(cccd) < 6:
            return '***'
        first_three = cccd[:3]
        last_three = cccd[-3:]
        middle = '*' * (len(cccd) - 6)
        return f'{first_three}{middle}{last_three}'
    
    def health_check(self) -> Dict[str, Any]:
        """Check cache health"""
        if not self.config.cache['enabled']:
            return {'healthy': True, 'enabled': False}
        
        try:
            # Test cache operations
            test_key = 'health_check'
            test_value = {'test': time.time()}
            
            self.bhxh_cache[test_key] = test_value
            retrieved = self.bhxh_cache.get(test_key)
            del self.bhxh_cache[test_key]
            
            healthy = retrieved and retrieved['test'] == test_value['test']
            
            return {
                'healthy': healthy,
                'enabled': True,
                'stats': self.get_stats()
            }
        except Exception as e:
            return {
                'healthy': False,
                'enabled': True,
                'error': str(e)
            }


# Singleton instance
_instance: Optional[CacheUtil] = None


def get_cache_util() -> CacheUtil:
    """Get cache util instance"""
    global _instance
    if _instance is None:
        _instance = CacheUtil()
    return _instance