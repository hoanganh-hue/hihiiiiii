"""
Enhanced Retry Utility with Exponential Backoff
"""

import asyncio
import random
import time
from typing import Callable, Any, Optional, Dict
from config.config import get_config_instance
from .logger import get_logger


class RetryUtil:
    """Enhanced Retry Utility with Exponential Backoff"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.logger = get_logger()
        self.circuit_breaker_states = {}
    
    async def with_retry(self, operation: Callable, options: Optional[Dict[str, Any]] = None) -> Any:
        """Execute operation with retry logic"""
        options = options or {}
        
        max_attempts = options.get('max_attempts', self.config.processing['retry_max_attempts'])
        base_delay = options.get('base_delay', self.config.processing['retry_base_delay'])
        max_delay = options.get('max_delay', 60000)  # 1 minute max delay
        exponential_base = options.get('exponential_base', 2)
        jitter = options.get('jitter', True)
        retry_condition = options.get('retry_condition', self.should_retry)
        on_retry = options.get('on_retry')
        context = options.get('context', 'operation')
        
        last_error = None
        attempt = 1
        
        while attempt <= max_attempts:
            try:
                self.logger.debug(f'🔄 Attempting {context} (attempt {attempt}/{max_attempts})')
                
                result = await operation(attempt)
                
                if attempt > 1:
                    self.logger.info(f'✅ {context} succeeded on attempt {attempt}')
                
                return result
                
            except Exception as error:
                last_error = error
                
                self.logger.warn(f'❌ {context} failed on attempt {attempt}: {error}')
                
                # Check if we should retry
                if attempt >= max_attempts or not retry_condition(error):
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = self.calculate_delay(base_delay, attempt - 1, exponential_base, max_delay, jitter)
                
                self.logger.info(f'⏳ Retrying {context} in {delay}ms (attempt {attempt + 1}/{max_attempts})')
                
                # Call on_retry callback if provided
                if on_retry:
                    try:
                        await on_retry(error, attempt, delay)
                    except Exception as callback_error:
                        self.logger.error(f'Error in on_retry callback: {callback_error}')
                
                # Wait before retry
                await self.sleep(delay)
                
                attempt += 1
        
        # All attempts failed
        self.logger.error(f'💥 {context} failed after {max_attempts} attempts. Last error: {last_error}')
        raise last_error
    
    def calculate_delay(self, base_delay: int, attempt: int, exponential_base: float, 
                       max_delay: int, jitter: bool) -> int:
        """Calculate delay with exponential backoff and optional jitter"""
        # Exponential backoff: base_delay * (exponential_base ^ attempt)
        delay = base_delay * (exponential_base ** attempt)
        
        # Apply maximum delay cap
        delay = min(delay, max_delay)
        
        # Add jitter to avoid thundering herd problem
        if jitter:
            # Random jitter between 50% and 150% of calculated delay
            jitter_min = 0.5
            jitter_max = 1.5
            delay = delay * (jitter_min + random.random() * (jitter_max - jitter_min))
        
        return int(delay)
    
    def should_retry(self, error: Exception) -> bool:
        """Determine if error should trigger a retry"""
        error_str = str(error).lower()
        
        # Network errors - retry
        if any(code in error_str for code in ['econnreset', 'econnrefused', 'etimedout', 'enotfound']):
            return True
        
        # HTTP errors
        if hasattr(error, 'response'):
            status = getattr(error.response, 'status_code', None)
            if status:
                # Server errors (5xx) - retry
                if 500 <= status < 600:
                    return True
                
                # Rate limiting (429) - retry
                if status == 429:
                    return True
                
                # Request timeout (408) - retry
                if status == 408:
                    return True
                
                # Client errors (4xx except 408, 429) - don't retry
                if 400 <= status < 500:
                    return False
        
        # CAPTCHA specific errors
        if 'captcha' in error_str:
            # CAPTCHA timeout - retry
            if 'timeout' in error_str:
                return True
            
            # CAPTCHA service errors - retry
            if 'service' in error_str or '2captcha' in error_str:
                return True
            
            # CAPTCHA invalid - retry but with lower retry count
            if 'invalid' in error_str:
                return True
        
        # Default: retry for unknown errors
        return True
    
    async def sleep(self, ms: int):
        """Sleep utility"""
        await asyncio.sleep(ms / 1000.0)
    
    async def retry_captcha(self, captcha_operation: Callable, options: Optional[Dict[str, Any]] = None) -> Any:
        """Retry specifically for CAPTCHA operations"""
        options = options or {}
        
        return await self.with_retry(captcha_operation, {
            'max_attempts': 5,  # More attempts for CAPTCHA
            'base_delay': 5000,  # Longer base delay for CAPTCHA
            'max_delay': 120000,  # 2 minutes max delay
            'exponential_base': 1.5,  # Gentler exponential growth
            'context': 'CAPTCHA solving',
            'retry_condition': self._captcha_retry_condition,
            **options
        })
    
    def _captcha_retry_condition(self, error: Exception) -> bool:
        """CAPTCHA specific retry logic"""
        error_str = str(error).lower()
        
        # Don't retry on invalid API key
        if 'invalid key' in error_str or 'wrong key' in error_str:
            return False
        
        # Don't retry on insufficient balance
        if 'insufficient balance' in error_str or 'no balance' in error_str:
            return False
        
        return self.should_retry(error)
    
    async def retry_bhxh_api(self, api_operation: Callable, options: Optional[Dict[str, Any]] = None) -> Any:
        """Retry specifically for BHXH API operations"""
        options = options or {}
        
        return await self.with_retry(api_operation, {
            'max_attempts': 3,
            'base_delay': 2000,
            'max_delay': 30000,
            'context': 'BHXH API call',
            'retry_condition': self._bhxh_retry_condition,
            **options
        })
    
    def _bhxh_retry_condition(self, error: Exception) -> bool:
        """BHXH API specific retry logic"""
        # Don't retry on validation errors (400)
        if hasattr(error, 'response'):
            status = getattr(error.response, 'status_code', None)
            if status == 400:
                return False
        
        return self.should_retry(error)
    
    async def with_circuit_breaker(self, operation: Callable, options: Optional[Dict[str, Any]] = None) -> Any:
        """Retry with circuit breaker pattern"""
        options = options or {}
        
        failure_threshold = options.get('failure_threshold', 5)
        reset_timeout = options.get('reset_timeout', 60000)  # 1 minute
        context = options.get('context', 'circuit-breaker-operation')
        
        # Get or create circuit breaker state
        state = self.circuit_breaker_states.get(context, {
            'failures': 0,
            'last_failure_time': None,
            'state': 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        })
        
        # Check circuit breaker state
        if state['state'] == 'OPEN':
            if time.time() * 1000 - state['last_failure_time'] < reset_timeout:
                raise Exception(f'Circuit breaker is OPEN for {context}')
            else:
                # Transition to HALF_OPEN
                state['state'] = 'HALF_OPEN'
                self.logger.info(f'🔄 Circuit breaker transitioning to HALF_OPEN for {context}')
        
        try:
            result = await self.with_retry(operation, {
                **options,
                'context': f'{context} (circuit-breaker)'
            })
            
            # Success - reset circuit breaker
            if state['failures'] > 0:
                self.logger.info(f'✅ Circuit breaker reset for {context}')
            
            state['failures'] = 0
            state['state'] = 'CLOSED'
            self.circuit_breaker_states[context] = state
            
            return result
            
        except Exception as error:
            # Failure - update circuit breaker state
            state['failures'] += 1
            state['last_failure_time'] = time.time() * 1000
            
            if state['failures'] >= failure_threshold:
                state['state'] = 'OPEN'
                self.logger.error(f'🚫 Circuit breaker OPEN for {context} after {state["failures"]} failures')
            
            self.circuit_breaker_states[context] = state
            raise error


# Singleton instance
_instance: Optional[RetryUtil] = None


def get_retry_util() -> RetryUtil:
    """Get retry util instance"""
    global _instance
    if _instance is None:
        _instance = RetryUtil()
    return _instance