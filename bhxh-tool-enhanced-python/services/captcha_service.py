"""
Enhanced CAPTCHA Service with 2captcha Integration
"""

import asyncio
import time
from typing import Dict, Any, Optional
import httpx
from config.config import get_config_instance
from utils.logger import get_logger
from utils.retry import get_retry_util
from utils.cache import get_cache_util


class CaptchaService:
    """Enhanced CAPTCHA Service with 2captcha Integration"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.logger = get_logger()
        self.retry = get_retry_util()
        self.cache = get_cache_util()
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=20)
        )
        
        self.stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0
        }
    
    async def solve_recaptcha(self, log_prefix: str = '') -> str:
        """Solve reCAPTCHA with enhanced error handling"""
        start_time = time.time()
        self.stats['total_attempts'] += 1
        
        try:
            self.logger.info(f'🔐 Starting CAPTCHA solving {log_prefix}')
            
            # Check cache first (very short-lived cache)
            cached = self.cache.get_captcha_solution(self.config.captcha['website_url'])
            if cached:
                self.logger.info(f'🎯 Using cached CAPTCHA solution {log_prefix}')
                self.stats['successful'] += 1
                return cached
            
            result = await self.retry.retry_captcha(
                lambda attempt: self.solve_captcha_internal(log_prefix, attempt)
            )
            
            duration = int((time.time() - start_time) * 1000)
            self.stats['successful'] += 1
            self.stats['total_time'] += duration
            
            # Cache the solution for a very short time
            self.cache.set_captcha_solution(self.config.captcha['website_url'], result)
            
            self.logger.info(f'✅ CAPTCHA solved successfully in {duration}ms {log_prefix}')
            return result
            
        except Exception as error:
            duration = int((time.time() - start_time) * 1000)
            self.stats['failed'] += 1
            self.stats['total_time'] += duration
            
            self.logger.error(f'❌ CAPTCHA solving failed after {duration}ms {log_prefix}: {error}')
            raise error
    
    async def solve_captcha_internal(self, log_prefix: str, attempt_number: int) -> str:
        """Internal CAPTCHA solving logic"""
        # Step 1: Submit CAPTCHA to 2captcha
        captcha_id = await self.submit_captcha(log_prefix, attempt_number)
        
        # Step 2: Poll for solution
        solution = await self.poll_captcha_solution(captcha_id, log_prefix, attempt_number)
        
        return solution
    
    async def submit_captcha(self, log_prefix: str, attempt_number: int) -> str:
        """Submit CAPTCHA to 2captcha service"""
        try:
            self.logger.debug(f'📤 Submitting CAPTCHA to 2captcha {log_prefix} (attempt {attempt_number})')
            
            submit_data = {
                'key': self.config.captcha['api_key'],
                'method': 'userrecaptcha',
                'googlekey': self.config.captcha['website_key'],
                'pageurl': self.config.captcha['website_url'],
                'json': 1
            }
            
            response = await self.client.post(
                self.config.captcha['submit_url'],
                data=submit_data,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': self.config.bhxh['user_agent']
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            self.logger.debug(f'📤 Submit response {log_prefix}: {data}')
            
            if data.get('status') == 1:
                captcha_id = data['request']
                self.logger.info(f'✅ CAPTCHA submitted successfully {log_prefix}, ID: {captcha_id}')
                return captcha_id
            else:
                error_message = data.get('error_text', 'Unknown submit error')
                raise Exception(f'CAPTCHA submit failed: {error_message}')
            
        except httpx.HTTPStatusError as error:
            self.logger.error(f'📤 Submit HTTP error {log_prefix}: {error.response.status_code}')
            raise Exception(f'CAPTCHA submit HTTP error: {error.response.status_code}')
        except httpx.TimeoutException:
            raise Exception('CAPTCHA submit timeout')
        except Exception as error:
            self.logger.error(f'📤 Submit error {log_prefix}: {error}')
            raise Exception(f'CAPTCHA submit error: {error}')
    
    async def poll_captcha_solution(self, captcha_id: str, log_prefix: str, attempt_number: int) -> str:
        """Poll for CAPTCHA solution"""
        try:
            self.logger.debug(f'⏳ Polling CAPTCHA solution {log_prefix}, ID: {captcha_id}')
            
            max_attempts = self.config.captcha['max_attempts']
            poll_interval = self.config.captcha['poll_interval']
            poll_attempt = 0
            
            while poll_attempt < max_attempts:
                poll_attempt += 1
                
                # Wait before first poll and between polls
                if poll_attempt == 1:
                    await asyncio.sleep(poll_interval / 1000.0)  # Initial delay
                else:
                    await asyncio.sleep(poll_interval / 1000.0)
                
                try:
                    result_data = {
                        'key': self.config.captcha['api_key'],
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    }
                    
                    response = await self.client.post(
                        self.config.captcha['result_url'],
                        data=result_data,
                        headers={
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'User-Agent': self.config.bhxh['user_agent']
                        }
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    progress = int((poll_attempt / max_attempts) * 100)
                    self.logger.debug(f'⏳ Poll {poll_attempt}/{max_attempts} ({progress}%) {log_prefix}: {data}')
                    
                    if data.get('status') == 1:
                        solution = data['request']
                        self.logger.info(f'✅ CAPTCHA solution received {log_prefix} after {poll_attempt} polls')
                        return solution
                    
                    if data.get('error_text'):
                        error_text = data['error_text']
                        
                        # Handle specific errors
                        if 'CAPCHA_NOT_READY' in error_text:
                            continue  # Keep polling
                        elif 'ERROR_CAPTCHA_UNSOLVABLE' in error_text:
                            raise Exception('CAPTCHA unsolvable')
                        elif 'ERROR_WRONG_USER_KEY' in error_text:
                            raise Exception('Invalid 2captcha API key')
                        elif 'ERROR_ZERO_BALANCE' in error_text:
                            raise Exception('2captcha account has zero balance')
                        else:
                            raise Exception(f'CAPTCHA error: {error_text}')
                    
                except httpx.TimeoutException:
                    self.logger.warn(f'⚠️ Poll timeout {log_prefix}, attempt {poll_attempt}/{max_attempts}')
                    continue  # Try next poll
                except Exception as poll_error:
                    raise poll_error
            
            # Max attempts reached
            raise Exception(f'CAPTCHA polling timeout after {max_attempts} attempts')
            
        except Exception as error:
            self.logger.error(f'❌ CAPTCHA polling failed {log_prefix}: {error}')
            raise error
    
    def get_stats(self) -> Dict[str, Any]:
        """Get CAPTCHA service statistics"""
        avg_time = (self.stats['total_time'] // self.stats['total_attempts'] 
                   if self.stats['total_attempts'] > 0 else 0)
        
        success_rate = (int((self.stats['successful'] / self.stats['total_attempts']) * 100) 
                       if self.stats['total_attempts'] > 0 else 0)
        
        return {
            'total_attempts': self.stats['total_attempts'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'success_rate': success_rate,
            'average_time_ms': avg_time,
            'total_time_ms': self.stats['total_time']
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_attempts': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0
        }
        
        self.logger.info('📊 CAPTCHA statistics reset')
    
    async def test_service(self) -> Dict[str, Any]:
        """Test CAPTCHA service"""
        try:
            self.logger.info('🧪 Testing CAPTCHA service...')
            
            start_time = time.time()
            solution = await self.solve_recaptcha('[TEST]')
            duration = int((time.time() - start_time) * 1000)
            
            is_valid = solution and isinstance(solution, str) and len(solution) > 50
            
            self.logger.info(f'🧪 CAPTCHA test completed in {duration}ms', {
                'success': is_valid,
                'solution_length': len(solution) if solution else 0
            })
            
            return {
                'success': is_valid,
                'duration': duration,
                'solution': 'valid' if is_valid else 'invalid',
                'solution_length': len(solution) if solution else 0
            }
            
        except Exception as error:
            self.logger.error(f'🧪 CAPTCHA test failed: {error}')
            return {
                'success': False,
                'error': str(error)
            }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration"""
        issues = []
        
        if (not self.config.captcha['api_key'] or 
            self.config.captcha['api_key'] == 'your_2captcha_api_key_here'):
            issues.append('CAPTCHA API key not configured')
        
        if not self.config.captcha['website_key']:
            issues.append('CAPTCHA website key not configured')
        
        if not self.config.captcha['website_url']:
            issues.append('CAPTCHA website URL not configured')
        
        if self.config.captcha['max_attempts'] < 10:
            issues.append('CAPTCHA max attempts too low (recommended: >= 10)')
        
        if self.config.captcha['poll_interval'] < 3000:
            issues.append('CAPTCHA poll interval too low (recommended: >= 3000ms)')
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    async def get_balance(self) -> float:
        """Get 2captcha account balance"""
        try:
            response = await self.client.post(
                self.config.captcha['result_url'],
                data={
                    'key': self.config.captcha['api_key'],
                    'action': 'getbalance',
                    'json': 1
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 1:
                balance = float(data['request'])
                self.logger.info(f'💰 2captcha balance: ${balance}')
                return balance
            else:
                raise Exception(data.get('error_text', 'Failed to get balance'))
            
        except Exception as error:
            self.logger.error(f'❌ Error getting 2captcha balance: {error}')
            raise error
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_instance: Optional[CaptchaService] = None


def get_captcha_service() -> CaptchaService:
    """Get CAPTCHA service instance"""
    global _instance
    if _instance is None:
        _instance = CaptchaService()
    return _instance