#!/usr/bin/env python3
"""
Enhanced BHXH Tool - Main Application
Version: 2.0.0

Improvements:
- Enhanced Security: Environment variables, input validation, sanitization  
- Improved Performance: Batch Excel writing, optimized province mapping, better memory management
- Enhanced Data Collection: Complete BHXH data extraction with multiple strategies
- Fixed Output Formatting: Clean data presentation, standardized date format
- Better Error Handling: Retry mechanisms, comprehensive logging, graceful degradation
"""

import asyncio
import os
import signal
import sys
import time
from typing import Dict, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Import our modules
from config.config import get_config_instance
from utils.logger import get_logger
from utils.validator import get_validator
from utils.cache import get_cache_util
from services.excel_service import get_excel_service
from services.province_service import get_province_service
from services.captcha_service import get_captcha_service
from services.bhxh_service import get_bhxh_service


class EnhancedBhxhTool:
    """Enhanced BHXH Tool Main Class"""
    
    def __init__(self):
        self.config = get_config_instance()
        self.logger = get_logger()
        self.validator = get_validator()
        self.cache = get_cache_util()
        self.excel = get_excel_service()
        self.province = get_province_service()
        self.captcha = get_captcha_service()
        self.bhxh = get_bhxh_service()
        
        self.stats = {
            'total_records': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None,
            'errors': {}
        }
        
        self.console = Console()
    
    async def initialize(self):
        """Initialize application"""
        try:
            self.logger.info('🚀 Initializing Enhanced BHXH Tool v2.0.0')
            
            # Print configuration summary
            self.config.print_summary()
            
            # Validate configurations
            await self.validate_configurations()
            
            # Setup graceful shutdown
            self.setup_graceful_shutdown()
            
            self.logger.info('✅ Application initialized successfully')
            
        except Exception as error:
            self.logger.error(f'❌ Initialization failed: {error}')
            sys.exit(1)
    
    async def validate_configurations(self):
        """Validate all configurations"""
        self.logger.info('🔧 Validating configurations...')
        
        # Validate CAPTCHA configuration
        captcha_validation = self.captcha.validate_config()
        if not captcha_validation['is_valid']:
            raise Exception(f"CAPTCHA configuration invalid: {', '.join(captcha_validation['issues'])}")
        
        # Validate province data
        province_validation = self.province.validate_province_data()
        if not province_validation['is_valid']:
            self.logger.warn(f"⚠️ Province data issues: {', '.join(province_validation['issues'])}")
        
        # Validate input file exists
        if not os.path.exists(self.config.files['input_excel']):
            raise Exception(f"Input file not found: {self.config.files['input_excel']}")
        
        # Validate Excel format
        excel_validation = self.excel.validate_excel_format(self.config.files['input_excel'])
        if not excel_validation['valid']:
            raise Exception(f"Input Excel format invalid: {excel_validation['error']}")
        
        # Test cache health
        cache_health = self.cache.health_check()
        if not cache_health['healthy']:
            self.logger.warn(f"⚠️ Cache health check failed: {cache_health.get('error', 'Unknown error')}")
        
        self.logger.info('✅ Configuration validation completed')
    
    async def process(self):
        """Main processing function"""
        try:
            self.stats['start_time'] = time.time()
            
            self.logger.info('🔄 Starting BHXH processing...')
            
            # Step 1: Read input Excel file
            excel_data = await self.excel.read_excel_file()
            sheet_names = list(excel_data.keys())
            
            if not sheet_names:
                raise Exception('No sheets found in Excel file')
            
            # Process first sheet (or all sheets)
            sheet_name = sheet_names[0]
            sheet_data = excel_data[sheet_name]
            records = sheet_data['data']
            
            # Apply optional record limit for quick runs
            if hasattr(self.config, 'processing') and self.config.processing.get('limit_records'):
                limit = self.config.processing['limit_records']
                if isinstance(limit, int):
                    records = records[:limit]
            
            self.stats['total_records'] = len(records)
            
            if not records:
                raise Exception('No data records found in Excel file')
            
            self.logger.info(f'📊 Processing {len(records)} records from sheet "{sheet_name}"')
            
            # Step 2: Validate input records
            validation = self.validator.validate_records(records)
            
            if validation['invalid_count'] > 0:
                self.logger.warn(f"⚠️ Found {validation['invalid_count']} invalid records:")
                for i, invalid in enumerate(validation['invalid_records'][:5]):  # Show first 5
                    self.logger.warn(f"  - Row {invalid['index'] + 1}: {'; '.join(invalid['errors'])}")
                
                if validation['valid_count'] == 0:
                    raise Exception('No valid records found to process')
            
            self.logger.info(f"✅ Validation completed: {validation['valid_count']} valid, {validation['invalid_count']} invalid records")
            
            # Step 3: Create backup of existing output file
            await self.excel.create_backup()
            
            # Step 4: Process valid records
            await self.process_records(validation['valid_records'])
            
            # Step 5: Process invalid records (add to output with error status)
            await self.process_invalid_records(validation['invalid_records'])
            
            # Step 6: Finalize processing
            await self.finalize_processing()
            
        except Exception as error:
            self.logger.error(f'❌ Processing failed: {error}')
            raise error
    
    async def process_records(self, valid_records: list):
        """Process valid records with concurrency control"""
        semaphore = asyncio.Semaphore(self.config.processing['max_concurrent'])
        
        self.logger.info(f"🔄 Processing {len(valid_records)} valid records with {self.config.processing['max_concurrent']} concurrent threads")
        
        # Create progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Processing records...", total=len(valid_records))
            
            async def process_record_with_semaphore(record_info):
                async with semaphore:
                    return await self.process_record(record_info, progress, task)
            
            # Process all records concurrently
            tasks = [process_record_with_semaphore(record_info) for record_info in valid_records]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Analyze results
            successful = 0
            failed = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed += 1
                    self.logger.error(f'❌ Task {i + 1} failed: {result}')
                elif result and result.get('success'):
                    successful += 1
                else:
                    failed += 1
            
            self.stats['successful'] = successful
            self.stats['failed'] = failed
            self.stats['processed'] = len(valid_records)
            
            self.logger.info(f'📊 Record processing completed: {successful} successful, {failed} failed')
    
    async def process_record(self, record_info: dict, progress: Optional[Progress] = None, 
                           task: Optional[Any] = None) -> Dict[str, Any]:
        """Process a single record"""
        index, data = record_info['index'], record_info['data']
        start_time = time.time()
        
        try:
            log_prefix = f'[Record {index + 1}]'
            
            self.logger.debug(f'🔄 Processing record {index + 1}', {
                'cccd': self.sanitize_cccd(data['soCCCD']),
                'hoTen': data['hoVaTen'][:10] + '...'
            })
            
            # Step 1: Find province code
            province_result = self.province.find_province_code(data.get('diaChi', ''))
            if not province_result:
                raise Exception('Không tìm thấy mã tỉnh từ địa chỉ')
            
            # Step 2: Solve CAPTCHA
            captcha_token = await self.captcha.solve_recaptcha(log_prefix)
            
            # Step 3: Query BHXH
            bhxh_result = await self.bhxh.query_bhxh({
                'cccd': data['soCCCD'],
                'hoTen': data['hoVaTen'],
                'diaChi': data.get('diaChi', ''),
                'maTinh': province_result['code']
            }, captcha_token, log_prefix)
            
            # Step 4: Write to Excel (batch)
            processing_time = int((time.time() - start_time) * 1000)
            await self.excel.add_to_batch(data, bhxh_result, processing_time)
            
            # Update progress
            if progress and task is not None:
                progress.update(task, advance=1)
            
            self.logger.info(f'✅ Record {index + 1} processed successfully in {processing_time}ms', {
                'cccd': self.sanitize_cccd(data['soCCCD']),
                'status': bhxh_result.get('status'),
                'soKetQua': bhxh_result.get('soKetQua', 0)
            })
            
            return {'success': True, 'result': bhxh_result, 'duration': processing_time}
            
        except Exception as error:
            processing_time = int((time.time() - start_time) * 1000)
            
            # Create error result
            error_result = {
                'status': 'error',
                'message': self.sanitize_error_message(str(error)),
                'soKetQua': 0,
                'thongTinHoGiaDinh': []
            }
            
            # Write error result to Excel
            await self.excel.add_to_batch(data, error_result, processing_time)
            
            # Update progress
            if progress and task is not None:
                progress.update(task, advance=1)
            
            # Track error types
            error_type = self.categorize_error(error)
            self.stats['errors'][error_type] = self.stats['errors'].get(error_type, 0) + 1
            
            self.logger.error(f'❌ Record {index + 1} failed after {processing_time}ms: {error}', {
                'cccd': self.sanitize_cccd(data['soCCCD']),
                'error_type': error_type
            })
            
            return {'success': False, 'error': str(error), 'duration': processing_time}
    
    async def process_invalid_records(self, invalid_records: list):
        """Process invalid records (add to output with error status)"""
        if not invalid_records:
            return
        
        self.logger.info(f'📝 Adding {len(invalid_records)} invalid records to output')
        
        for invalid_record in invalid_records:
            error_result = {
                'status': 'error',
                'message': f"Dữ liệu không hợp lệ: {'; '.join(invalid_record['errors'])}",
                'soKetQua': 0,
                'thongTinHoGiaDinh': []
            }
            
            await self.excel.add_to_batch(invalid_record['data'], error_result, 0)
    
    async def finalize_processing(self):
        """Finalize processing"""
        try:
            # Flush remaining Excel records
            await self.excel.finalize_excel()
            
            # Calculate final statistics
            self.stats['end_time'] = time.time()
            total_duration = int((self.stats['end_time'] - self.stats['start_time']) * 1000)
            avg_time_per_record = (total_duration // self.stats['processed'] 
                                 if self.stats['processed'] > 0 else 0)
            
            final_stats = {
                'total_records': self.stats['total_records'],
                'processed': self.stats['processed'],
                'successful': self.stats['successful'],
                'failed': self.stats['failed'],
                'success_rate': int((self.stats['successful'] / self.stats['processed']) * 100) 
                              if self.stats['processed'] > 0 else 0,
                'total_duration_ms': total_duration,
                'total_duration_formatted': self.format_duration(total_duration),
                'avg_time_per_record_ms': avg_time_per_record,
                'errors': self.stats['errors'],
                'captcha_stats': self.captcha.get_stats(),
                'bhxh_stats': self.bhxh.get_stats(),
                'cache_stats': self.cache.get_stats()
            }
            
            # Log final statistics
            self.logger.log_processing_complete(final_stats)
            
            # Print summary to console
            self.print_final_summary(final_stats)
            
            self.logger.info('🎉 Processing completed successfully')
            
        except Exception as error:
            self.logger.error(f'❌ Error finalizing processing: {error}')
            raise error
    
    def print_final_summary(self, stats: Dict[str, Any]):
        """Print final summary to console"""
        self.console.print('\n' + '=' * 80)
        self.console.print('🎉 ENHANCED BHXH TOOL - PROCESSING SUMMARY', style='bold green')
        self.console.print('=' * 80)
        
        # Create summary table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        table.add_row("📊 Records Processed", f"{stats['processed']}/{stats['total_records']}")
        table.add_row("✅ Successful", f"{stats['successful']} ({stats['success_rate']}%)")
        table.add_row("❌ Failed", f"{stats['failed']} ({100 - stats['success_rate']}%)")
        table.add_row("⏱️ Total Duration", stats['total_duration_formatted'])
        table.add_row("📈 Avg Time/Record", f"{stats['avg_time_per_record_ms']}ms")
        
        self.console.print(table)
        
        if stats['errors']:
            self.console.print('\n🚨 Error Breakdown:', style='bold red')
            for error_type, count in stats['errors'].items():
                self.console.print(f"   {error_type}: {count}")
        
        self.console.print(f'\n🔐 CAPTCHA Stats:', style='bold blue')
        self.console.print(f"   Success Rate: {stats['captcha_stats']['success_rate']}%")
        self.console.print(f"   Avg Solve Time: {stats['captcha_stats']['average_time_ms']}ms")
        
        self.console.print(f'\n🌐 BHXH API Stats:', style='bold blue')
        self.console.print(f"   Success Rate: {stats['bhxh_stats']['success_rate']}%")
        self.console.print(f"   Avg Response Time: {stats['bhxh_stats']['average_time_ms']}ms")
        
        self.console.print(f'\n📁 Output File: {self.config.files["output_excel"]}')
        self.console.print(f'📋 Log File: {self.config.files["log_file"]}')
        self.console.print('=' * 80)
    
    def setup_graceful_shutdown(self):
        """Setup graceful shutdown handlers"""
        def signal_handler(signum, frame):
            self.logger.info(f'📴 Received signal {signum}. Shutting down gracefully...')
            
            try:
                # Print current stats
                if self.stats['start_time']:
                    current_duration = int((time.time() - self.stats['start_time']) * 1000)
                    self.logger.info(f"📊 Shutdown Stats: {self.stats['processed']}/{self.stats['total_records']} processed in {self.format_duration(current_duration)}")
                
                self.logger.info('✅ Graceful shutdown completed')
                sys.exit(0)
            except Exception as error:
                self.logger.error(f'❌ Error during shutdown: {error}')
                sys.exit(1)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def categorize_error(self, error: Exception) -> str:
        """Categorize errors for statistics"""
        error_str = str(error).lower()
        
        if 'captcha' in error_str:
            return 'CAPTCHA_ERROR'
        elif 'mã tỉnh' in error_str or 'province' in error_str:
            return 'PROVINCE_ERROR'
        elif 'api' in error_str or 'http' in error_str:
            return 'API_ERROR'
        elif 'timeout' in error_str:
            return 'TIMEOUT_ERROR'
        elif 'network' in error_str or 'connection' in error_str:
            return 'NETWORK_ERROR'
        elif 'parsing' in error_str or 'html' in error_str:
            return 'PARSING_ERROR'
        else:
            return 'UNKNOWN_ERROR'
    
    def sanitize_error_message(self, message: str) -> str:
        """Sanitize error messages"""
        if not message:
            return 'Unknown error'
        
        import re
        return (message
                .replace(re.sub(r'\d{9,12}', '***', message), '***')  # Hide CCCD numbers
                .replace(re.sub(r'key=[a-zA-Z0-9]+', 'key=***', message), 'key=***')  # Hide API keys
                .replace(re.sub(r'token=[a-zA-Z0-9]+', 'token=***', message), 'token=***'))  # Hide tokens
    
    def sanitize_cccd(self, cccd: str) -> str:
        """Sanitize CCCD for logging"""
        if not cccd or len(cccd) < 6:
            return '***'
        first_three = cccd[:3]
        last_three = cccd[-3:]
        middle = '*' * (len(cccd) - 6)
        return f'{first_three}{middle}{last_three}'
    
    def format_duration(self, ms: int) -> str:
        """Format duration in human readable format"""
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        
        if hours > 0:
            return f'{hours}h {minutes % 60}m {seconds % 60}s'
        elif minutes > 0:
            return f'{minutes}m {seconds % 60}s'
        else:
            return f'{seconds}s'
    
    async def run_diagnostics(self):
        """Run diagnostic tests"""
        self.logger.info('🧪 Running diagnostic tests...')
        
        diagnostics = {
            'config': True,
            'cache': False,
            'captcha': False,
            'provinces': False,
            'excel': False
        }
        
        try:
            # Test cache
            cache_health = self.cache.health_check()
            diagnostics['cache'] = cache_health['healthy']
            
            # Test CAPTCHA service
            captcha_test = await self.captcha.test_service()
            diagnostics['captcha'] = captcha_test['success']
            
            # Test province mapping
            province_test = self.province.test_mapping()
            diagnostics['provinces'] = province_test['success_rate'] >= 80
            
            # Test Excel file
            excel_validation = self.excel.validate_excel_format(self.config.files['input_excel'])
            diagnostics['excel'] = excel_validation['valid']
            
            self.logger.info('🧪 Diagnostic results:', diagnostics)
            
            all_passed = all(diagnostics.values())
            if all_passed:
                self.logger.info('✅ All diagnostics passed')
            else:
                self.logger.warn('⚠️ Some diagnostics failed')
            
            return diagnostics
            
        except Exception as error:
            self.logger.error(f'❌ Diagnostic tests failed: {error}')
            raise error


@click.command()
@click.option('--input', '-i', help='Override input Excel path')
@click.option('--output', '-o', help='Override output Excel path')
@click.option('--limit', '-l', type=int, help='Process only first N records')
@click.option('--test', '-t', is_flag=True, help='Run diagnostic tests')
@click.option('--help', '-h', is_flag=True, help='Show help message')
def main(input: Optional[str], output: Optional[str], limit: Optional[int], 
         test: bool, help: bool):
    """Enhanced BHXH Tool v2.0.0 - Social Insurance lookup tool"""
    
    if help:
        print_help()
        return
    
    async def run():
        try:
            # Create tool
            tool = EnhancedBhxhTool()
            
            # CLI overrides for input/output files
            if input:
                tool.config.files['input_excel'] = input
            if output:
                tool.config.files['output_excel'] = output
            if limit:
                tool.config.processing['limit_records'] = limit
            
            if test:
                await tool.initialize()
                await tool.run_diagnostics()
                return
            
            # Initialize and run
            await tool.initialize()
            await tool.process()
            
        except Exception as error:
            console = Console()
            console.print('\n❌ Application failed:', style='bold red')
            console.print(str(error), style='red')
            
            if os.getenv('DEBUG_MODE') == 'true':
                console.print('\nStack trace:', style='bold red')
                import traceback
                console.print(traceback.format_exc(), style='red')
            
            console.print('\n💡 Troubleshooting:', style='bold yellow')
            console.print('1. Check your .env configuration')
            console.print('2. Ensure input Excel file exists and is valid')
            console.print('3. Verify 2captcha API key and balance')
            console.print('4. Run with --test flag to diagnose issues')
            
            sys.exit(1)
    
    # Run the async main function
    asyncio.run(run())


def print_help():
    """Print help information"""
    console = Console()
    console.print("""
🔧 Enhanced BHXH Tool v2.0.0
=================================

Usage: python main.py [options]

Options:
  -h, --help    Show this help message
  -t, --test    Run diagnostic tests
  -i, --input   Override input Excel path
  -o, --output  Override output Excel path
  -l, --limit   Process only first N records
  
Environment Variables:
  Set in .env file (see .env.template)
  
Files Required:
  - data-input.xlsx     Input Excel file with CCCD data
  - tinh-thanh.json    Province mapping data
  - .env               Environment configuration
  
Features:
  ✅ Enhanced Security with environment variables
  ✅ Improved Performance with batch processing
  ✅ Enhanced Data Collection with multiple extraction strategies
  ✅ Fixed Output Formatting with clean data presentation
  ✅ Better Error Handling with retry mechanisms
  
For more information, see README.md
""", style='cyan')


if __name__ == '__main__':
    main()