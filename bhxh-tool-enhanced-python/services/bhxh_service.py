"""
Enhanced BHXH API Service with Improved Data Collection
"""

import re
import time
from typing import Dict, Any, List, Optional
import httpx
from bs4 import BeautifulSoup
from config.config import get_config_instance
from utils.logger import get_logger
from utils.retry import get_retry_util
from utils.cache import get_cache_util


class BhxhService:
    """Enhanced BHXH API Service with Improved Data Collection"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.logger = get_logger()
        self.retry = get_retry_util()
        self.cache = get_cache_util()
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=self.config.bhxh['timeout'] / 1000.0,
            limits=httpx.Limits(max_keepalive_connections=50, max_connections=50)
        )
        
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0,
            'errors_by_type': {}
        }
    
    async def query_bhxh(self, params: Dict[str, Any], captcha_token: str, 
                        log_prefix: str = '') -> Dict[str, Any]:
        """Query BHXH with enhanced data collection"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        try:
            self.logger.info(f'🔍 Querying BHXH API {log_prefix}', {
                'cccd': self.sanitize_cccd(params['cccd']),
                'hoTen': params['hoTen'][:10] + '...'
            })
            
            # Check cache first
            cached = self.cache.get_bhxh_result(params['cccd'], params['hoTen'], params.get('diaChi', ''))
            if cached:
                self.logger.info(f'🎯 Using cached BHXH result {log_prefix}')
                self.stats['successful'] += 1
                return cached
            
            result = await self.retry.retry_bhxh_api(
                lambda attempt: self.query_bhxh_internal(params, captcha_token, log_prefix, attempt)
            )
            
            duration = int((time.time() - start_time) * 1000)
            self.stats['successful'] += 1
            self.stats['total_time'] += duration
            
            # Cache successful results
            if result.get('status') == 'success' and result.get('soKetQua', 0) > 0:
                self.cache.set_bhxh_result(params['cccd'], params['hoTen'], params.get('diaChi', ''), result)
            
            self.logger.info(f'✅ BHXH query completed in {duration}ms {log_prefix}', {
                'status': result.get('status'),
                'soKetQua': result.get('soKetQua', 0)
            })
            
            return result
            
        except Exception as error:
            duration = int((time.time() - start_time) * 1000)
            self.stats['failed'] += 1
            self.stats['total_time'] += duration
            
            # Track error types
            error_type = self.categorize_error(error)
            self.stats['errors_by_type'][error_type] = self.stats['errors_by_type'].get(error_type, 0) + 1
            
            self.logger.error(f'❌ BHXH query failed after {duration}ms {log_prefix}: {error}', {
                'error_type': error_type,
                'cccd': self.sanitize_cccd(params['cccd'])
            })
            
            return {
                'status': 'error',
                'message': self.sanitize_error_message(str(error)),
                'soKetQua': 0,
                'thongTinHoGiaDinh': [],
                'error': error_type
            }
    
    async def query_bhxh_internal(self, params: Dict[str, Any], captcha_token: str, 
                                 log_prefix: str, attempt_number: int) -> Dict[str, Any]:
        """Internal BHXH query logic"""
        try:
            # Prepare form data
            form_data = {
                'matinh': params['maTinh'],
                'tennhankhau': params['hoTen'],
                'cmnd': params['cccd'],
                'tokenRecaptch': captcha_token,
                'typetext': 'CoDau'
            }
            
            self.logger.debug(f'🌐 Making BHXH API request {log_prefix} (attempt {attempt_number})', {
                'matinh': params['maTinh'],
                'cccd': self.sanitize_cccd(params['cccd']),
                'hoTen': params['hoTen'][:10] + '...'
            })
            
            # Make HTTP request
            response = await self.client.post(
                self.config.bhxh['api_url'],
                data=form_data,
                headers={
                    'User-Agent': self.config.bhxh['user_agent'],
                    'Referer': 'https://baohiemxahoi.gov.vn',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                },
                follow_redirects=True
            )
            
            self.logger.debug(f'📥 BHXH API response received {log_prefix}', {
                'status': response.status_code,
                'content_length': len(response.content),
                'content_type': response.headers.get('content-type', '')
            })
            
            if response.status_code != 200:
                raise Exception(f'BHXH API returned status {response.status_code}')
            
            # Parse HTML response
            return self.parse_html_response(response.text, {
                'cccd': params['cccd'],
                'hoTen': params['hoTen']
            }, log_prefix)
            
        except httpx.HTTPStatusError as error:
            self.logger.error(f'🌐 BHXH API HTTP error {log_prefix}: {error.response.status_code}')
            raise Exception(f'BHXH API HTTP {error.response.status_code}: {error.response.reason_phrase}')
        except httpx.TimeoutException:
            raise Exception('BHXH API timeout')
        except httpx.ConnectError:
            raise Exception('BHXH API connection failed')
        except Exception as error:
            self.logger.error(f'🌐 BHXH API error {log_prefix}: {error}')
            raise error
    
    def parse_html_response(self, html_content: str, input_data: Dict[str, Any], 
                           log_prefix: str) -> Dict[str, Any]:
        """Parse HTML response with enhanced data extraction"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            self.logger.debug(f'📄 Parsing HTML response {log_prefix}')
            
            # Check for specific error messages
            error_messages = self.check_for_errors(soup)
            if error_messages:
                self.logger.warn(f'⚠️ BHXH API returned errors {log_prefix}: {error_messages}')
                return {
                    'status': 'error',
                    'message': '; '.join(error_messages),
                    'soKetQua': 0,
                    'thongTinHoGiaDinh': [],
                    'inputData': input_data
                }
            
            # Enhanced data extraction
            extracted_data = self.extract_bhxh_data(soup, log_prefix)
            
            self.logger.debug(f'📊 Extracted BHXH data {log_prefix}: {len(extracted_data)} records')
            
            return {
                'status': 'success',
                'message': 'Tìm thấy thông tin BHXH' if extracted_data else 'Không tìm thấy thông tin BHXH',
                'soKetQua': len(extracted_data),
                'thongTinHoGiaDinh': extracted_data,
                'inputData': input_data
            }
            
        except Exception as error:
            self.logger.error(f'❌ Error parsing HTML response {log_prefix}: {error}')
            raise Exception(f'HTML parsing error: {error}')
    
    def check_for_errors(self, soup: BeautifulSoup) -> List[str]:
        """Check for error messages in HTML response"""
        errors = []
        
        # Common error message selectors
        error_selectors = [
            '.error-message',
            '.alert-danger',
            '.validation-summary-errors',
            '#lblError',
            '.message-error'
        ]
        
        for selector in error_selectors:
            elements = soup.select(selector)
            for element in elements:
                error_text = element.get_text().strip()
                if error_text and error_text not in errors:
                    errors.append(error_text)
        
        # Check for specific Vietnamese error messages in content
        content = soup.get_text().lower()
        vietnamese_errors = [
            'không tìm thấy',
            'không có dữ liệu',
            'lỗi hệ thống',
            'vui lòng thử lại',
            'captcha không đúng',
            'thông tin không chính xác'
        ]
        
        for error_pattern in vietnamese_errors:
            if error_pattern in content:
                errors.append(f'Detected error: {error_pattern}')
        
        return errors
    
    def extract_bhxh_data(self, soup: BeautifulSoup, log_prefix: str) -> List[Dict[str, Any]]:
        """Extract BHXH data with enhanced field collection"""
        results = []
        
        # Try multiple selectors for data extraction
        data_selectors = [
            '#contentChiTietHGD tr',
            '.data-table tr',
            'table tr',
            '.result-row'
        ]
        
        for selector in data_selectors:
            rows = soup.select(selector)
            
            if rows:
                self.logger.debug(f'📋 Found {len(rows)} rows with selector: {selector} {log_prefix}')
                
                for index, row in enumerate(rows):
                    # Skip header rows
                    if index == 0 or row.find('th'):
                        continue
                    
                    cells = row.find_all('td')
                    if len(cells) >= 5:
                        extracted_record = self.extract_record_data(cells, log_prefix)
                        if extracted_record and extracted_record.get('maBHXH'):
                            results.append(extracted_record)
                
                # If we found results with this selector, break
                if results:
                    break
        
        # If no results found with table selectors, try alternative extraction
        if not results:
            alternative_data = self.extract_alternative_data(soup, log_prefix)
            if alternative_data:
                results.append(alternative_data)
        
        return results
    
    def extract_record_data(self, cells: List, log_prefix: str) -> Optional[Dict[str, Any]]:
        """Extract data from table row cells"""
        try:
            data = {
                'maBHXH': self.clean_text(cells[1].get_text()) if len(cells) > 1 else '',
                'hoTen': self.clean_text(cells[2].get_text()) if len(cells) > 2 else '',
                'gioiTinh': self.clean_text(cells[3].get_text()) if len(cells) > 3 else '',
                'ngaySinh': self.clean_text(cells[4].get_text()) if len(cells) > 4 else '',
                'diaChi': self.clean_text(cells[5].get_text()) if len(cells) > 5 else '',
                'trangThai': self.clean_text(cells[6].get_text()) if len(cells) > 6 else ''
            }
            
            # Clean and validate data
            data['maBHXH'] = self.clean_text(data['maBHXH'])
            data['hoTen'] = self.clean_text(data['hoTen'])
            data['gioiTinh'] = self.normalize_gender(data['gioiTinh'])
            data['ngaySinh'] = self.format_date(data['ngaySinh'])
            data['diaChi'] = self.clean_text(data['diaChi'])
            data['trangThai'] = self.normalize_bhxh_status(data['trangThai'])
            
            self.logger.debug(f'📝 Extracted record data {log_prefix}: {data["maBHXH"]}')
            
            return data
            
        except Exception as error:
            self.logger.error(f'❌ Error extracting record data {log_prefix}: {error}')
            return None
    
    def extract_alternative_data(self, soup: BeautifulSoup, log_prefix: str) -> Optional[Dict[str, Any]]:
        """Alternative data extraction for different HTML structures"""
        try:
            # Try to find data in different formats
            alternatives = [
                lambda: self.extract_from_divs(soup),
                lambda: self.extract_from_spans(soup),
                lambda: self.extract_from_labels(soup)
            ]
            
            for extractor in alternatives:
                result = extractor()
                if result and result.get('maBHXH'):
                    self.logger.debug(f'📝 Alternative extraction successful {log_prefix}')
                    return result
            
            return None
            
        except Exception as error:
            self.logger.error(f'❌ Error in alternative extraction {log_prefix}: {error}')
            return None
    
    def extract_from_divs(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract from div elements"""
        data = {}
        
        # Common patterns for div-based layouts
        field_labels = soup.select('.field-label')
        for element in field_labels:
            label = element.get_text().strip().lower()
            value_element = element.find_next(class_='field-value')
            value = value_element.get_text().strip() if value_element else ''
            
            if 'mã bảo hiểm' in label or 'mã bhxh' in label:
                data['maBHXH'] = self.clean_text(value)
            elif 'họ tên' in label or 'tên' in label:
                data['hoTen'] = self.clean_text(value)
            elif 'giới tính' in label:
                data['gioiTinh'] = self.normalize_gender(value)
            elif 'ngày sinh' in label:
                data['ngaySinh'] = self.format_date(value)
            elif 'địa chỉ' in label:
                data['diaChi'] = self.clean_text(value)
            elif 'trạng thái' in label:
                data['trangThai'] = self.normalize_bhxh_status(value)
        
        return data if data else None
    
    def extract_from_spans(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract from span elements"""
        data = {}
        
        spans = soup.select('span[id*="lblMa"], span[id*="lblTen"], span[id*="lblGioiTinh"]')
        for element in spans:
            element_id = element.get('id', '')
            value = element.get_text().strip()
            
            if 'lblMa' in element_id or 'bhxh' in element_id.lower():
                data['maBHXH'] = self.clean_text(value)
            elif 'lblTen' in element_id or 'lblHoTen' in element_id:
                data['hoTen'] = self.clean_text(value)
            elif 'lblGioiTinh' in element_id:
                data['gioiTinh'] = self.normalize_gender(value)
            elif 'lblNgaySinh' in element_id:
                data['ngaySinh'] = self.format_date(value)
        
        return data if data else None
    
    def extract_from_labels(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extract from label elements"""
        data = {}
        
        labels = soup.select('label')
        for element in labels:
            label_text = element.get_text().strip().lower()
            for_attr = element.get('for')
            
            if for_attr:
                target_element = soup.find(id=for_attr)
                value = target_element.get('value', '') if target_element else target_element.get_text().strip() if target_element else ''
                
                if 'mã bảo hiểm' in label_text or 'mã bhxh' in label_text:
                    data['maBHXH'] = self.clean_text(value)
                elif 'họ tên' in label_text:
                    data['hoTen'] = self.clean_text(value)
                elif 'giới tính' in label_text:
                    data['gioiTinh'] = self.normalize_gender(value)
                elif 'ngày sinh' in label_text:
                    data['ngaySinh'] = self.format_date(value)
        
        return data if data else None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ''
        
        return (text.strip()
                .replace('\n', ' ')  # Replace newlines with spaces
                .replace('\r', ' ')  # Replace carriage returns with spaces
                .replace('\t', ' ')  # Replace tabs with spaces
                .replace('  ', ' ')  # Replace multiple spaces with single space
                .strip())
    
    def normalize_gender(self, gender: str) -> str:
        """Normalize gender values"""
        if not gender:
            return ''
        
        normalized = gender.lower().strip()
        
        if 'nam' in normalized or normalized in ['m', 'male']:
            return 'Nam'
        elif 'nữ' in normalized or 'nu' in normalized or normalized in ['f', 'female']:
            return 'Nữ'
        
        return self.clean_text(gender)
    
    def format_date(self, date_str: str) -> str:
        """Format date to standard format"""
        if not date_str:
            return ''
        
        cleaned = self.clean_text(date_str)
        
        # Try to detect and normalize date formats
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',      # DD/MM/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',       # DD-MM-YYYY
            r'(\d{4})/(\d{1,2})/(\d{1,2})',     # YYYY/MM/DD
            r'(\d{4})-(\d{1,2})-(\d{1,2})'        # YYYY-MM-DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, cleaned)
            if match:
                if pattern.startswith(r'(\d{4})'):  # YYYY format
                    year, month, day = match.groups()
                    return f'{day.zfill(2)}/{month.zfill(2)}/{year}'
                else:  # DD format
                    day, month, year = match.groups()
                    return f'{day.zfill(2)}/{month.zfill(2)}/{year}'
        
        return cleaned
    
    def normalize_bhxh_status(self, status: str) -> str:
        """Normalize BHXH status"""
        if not status:
            return ''
        
        cleaned = self.clean_text(status).lower()
        
        if 'đang tham gia' in cleaned or 'hoạt động' in cleaned:
            return 'Đang tham gia BHXH'
        elif 'tạm dừng' in cleaned or 'ngưng' in cleaned:
            return 'Tạm dừng tham gia'
        elif 'chưa tham gia' in cleaned or 'chưa đăng ký' in cleaned:
            return 'Chưa tham gia BHXH'
        elif 'hết hiệu lực' in cleaned:
            return 'Hết hiệu lực'
        
        return self.clean_text(status)
    
    def categorize_error(self, error: Exception) -> str:
        """Categorize errors for statistics"""
        error_str = str(error).lower()
        
        if 'timeout' in error_str or 'econnaborted' in error_str:
            return 'TIMEOUT'
        elif 'econnreset' in error_str or 'econnrefused' in error_str:
            return 'CONNECTION'
        elif '404' in error_str or 'not found' in error_str:
            return 'NOT_FOUND'
        elif '500' in error_str or 'server error' in error_str:
            return 'SERVER_ERROR'
        elif 'captcha' in error_str:
            return 'CAPTCHA_ERROR'
        elif 'parsing' in error_str or 'html' in error_str:
            return 'PARSING_ERROR'
        else:
            return 'UNKNOWN'
    
    def sanitize_error_message(self, message: str) -> str:
        """Sanitize error messages"""
        if not message:
            return 'Unknown error'
        
        # Remove sensitive information
        message = re.sub(r'\d{9,12}', '***', message)  # Hide CCCD numbers
        message = re.sub(r'key=[a-zA-Z0-9]+', 'key=***', message)  # Hide API keys
        message = re.sub(r'token=[a-zA-Z0-9]+', 'token=***', message)  # Hide tokens
        return message
    
    def sanitize_cccd(self, cccd: str) -> str:
        """Sanitize CCCD for logging"""
        if not cccd or len(cccd) < 6:
            return '***'
        first_three = cccd[:3]
        last_three = cccd[-3:]
        return f'{first_three}***{last_three}'
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        avg_time = (self.stats['total_time'] // self.stats['total_requests'] 
                   if self.stats['total_requests'] > 0 else 0)
        
        success_rate = (int((self.stats['successful'] / self.stats['total_requests']) * 100) 
                       if self.stats['total_requests'] > 0 else 0)
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'success_rate': success_rate,
            'average_time_ms': avg_time,
            'total_time_ms': self.stats['total_time'],
            'errors_by_type': self.stats['errors_by_type'].copy()
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'total_time': 0,
            'errors_by_type': {}
        }
        
        self.logger.info('📊 BHXH API statistics reset')
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
_instance: Optional[BhxhService] = None


def get_bhxh_service() -> BhxhService:
    """Get BHXH service instance"""
    global _instance
    if _instance is None:
        _instance = BhxhService()
    return _instance