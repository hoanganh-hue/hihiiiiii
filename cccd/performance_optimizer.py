#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Optimizer cho module CCCD
Tối ưu hóa hiệu suất xử lý dữ liệu lớn
"""

import time
import threading
import multiprocessing
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import gc

class PerformanceOptimizer:
    """Class tối ưu hóa hiệu suất cho xử lý dữ liệu lớn"""
    
    def __init__(self, max_workers: int = None):
        """
        Khởi tạo Performance Optimizer
        
        Args:
            max_workers: Số worker tối đa (mặc định = CPU count)
        """
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        
        # Performance metrics
        self.metrics = {
            'total_processed': 0,
            'total_time': 0,
            'avg_time_per_item': 0,
            'memory_usage': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Cache for frequently accessed data
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def batch_process(self, 
                     items: List[Any], 
                     process_func: Callable,
                     batch_size: int = 1000,
                     use_multiprocessing: bool = False) -> List[Any]:
        """
        Xử lý dữ liệu theo batch để tối ưu hiệu suất
        
        Args:
            items: Danh sách items cần xử lý
            process_func: Hàm xử lý
            batch_size: Kích thước batch
            use_multiprocessing: Sử dụng multiprocessing thay vì threading
            
        Returns:
            Danh sách kết quả đã xử lý
        """
        start_time = time.time()
        results = []
        
        # Chia items thành các batch
        batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
        
        if use_multiprocessing and len(batches) > 1:
            # Sử dụng multiprocessing cho batch lớn
            with ProcessPoolExecutor(max_workers=min(self.max_workers, len(batches))) as executor:
                future_to_batch = {
                    executor.submit(self._process_batch, batch, process_func): batch 
                    for batch in batches
                }
                
                for future in future_to_batch:
                    try:
                        batch_results = future.result(timeout=300)  # 5 minutes timeout
                        results.extend(batch_results)
                    except Exception as e:
                        print(f"Error processing batch: {e}")
        else:
            # Sử dụng threading cho batch nhỏ
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch = {
                    executor.submit(self._process_batch, batch, process_func): batch 
                    for batch in batches
                }
                
                for future in future_to_batch:
                    try:
                        batch_results = future.result(timeout=300)
                        results.extend(batch_results)
                    except Exception as e:
                        print(f"Error processing batch: {e}")
        
        # Cập nhật metrics
        end_time = time.time()
        self.metrics['total_processed'] += len(items)
        self.metrics['total_time'] += (end_time - start_time)
        self.metrics['avg_time_per_item'] = (
            self.metrics['total_time'] / self.metrics['total_processed'] 
            if self.metrics['total_processed'] > 0 else 0
        )
        
        return results
    
    def _process_batch(self, batch: List[Any], process_func: Callable) -> List[Any]:
        """
        Xử lý một batch items
        
        Args:
            batch: Batch items
            process_func: Hàm xử lý
            
        Returns:
            Kết quả xử lý batch
        """
        results = []
        for item in batch:
            try:
                result = process_func(item)
                results.append(result)
            except Exception as e:
                print(f"Error processing item {item}: {e}")
                results.append(None)
        
        return results
    
    def memory_optimized_generation(self, 
                                  generator_func: Callable,
                                  quantity: int,
                                  chunk_size: int = 1000) -> List[Any]:
        """
        Tạo dữ liệu với tối ưu hóa bộ nhớ
        
        Args:
            generator_func: Hàm tạo dữ liệu
            quantity: Số lượng cần tạo
            chunk_size: Kích thước chunk
            
        Returns:
            Danh sách dữ liệu đã tạo
        """
        results = []
        
        for i in range(0, quantity, chunk_size):
            chunk_quantity = min(chunk_size, quantity - i)
            
            # Tạo chunk
            chunk_results = generator_func(chunk_quantity)
            results.extend(chunk_results)
            
            # Force garbage collection sau mỗi chunk
            gc.collect()
            
            # Log progress
            if (i + chunk_quantity) % (chunk_size * 10) == 0:
                print(f"Generated {i + chunk_quantity}/{quantity} items")
        
        return results
    
    def cache_get(self, key: str) -> Optional[Any]:
        """
        Lấy dữ liệu từ cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached data hoặc None
        """
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                self.metrics['cache_hits'] += 1
                return data
            else:
                # Cache expired
                del self.cache[key]
        
        self.metrics['cache_misses'] += 1
        return None
    
    def cache_set(self, key: str, data: Any) -> None:
        """
        Lưu dữ liệu vào cache
        
        Args:
            key: Cache key
            data: Data to cache
        """
        self.cache[key] = (data, time.time())
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Lấy metrics hiệu suất
        
        Returns:
            Dict chứa metrics
        """
        return {
            'total_processed': self.metrics['total_processed'],
            'total_time': self.metrics['total_time'],
            'avg_time_per_item': self.metrics['avg_time_per_item'],
            'items_per_second': (
                self.metrics['total_processed'] / self.metrics['total_time'] 
                if self.metrics['total_time'] > 0 else 0
            ),
            'cache_hit_rate': (
                self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100
                if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
            ),
            'cache_size': len(self.cache),
            'max_workers': self.max_workers
        }
    
    def optimize_for_quantity(self, quantity: int) -> Dict[str, Any]:
        """
        Tối ưu hóa cấu hình dựa trên số lượng
        
        Args:
            quantity: Số lượng items cần xử lý
            
        Returns:
            Dict chứa cấu hình tối ưu
        """
        if quantity <= 100:
            return {
                'batch_size': 50,
                'use_multiprocessing': False,
                'chunk_size': 100,
                'max_workers': 2
            }
        elif quantity <= 1000:
            return {
                'batch_size': 200,
                'use_multiprocessing': False,
                'chunk_size': 500,
                'max_workers': 4
            }
        elif quantity <= 10000:
            return {
                'batch_size': 1000,
                'use_multiprocessing': True,
                'chunk_size': 2000,
                'max_workers': 8
            }
        else:
            return {
                'batch_size': 2000,
                'use_multiprocessing': True,
                'chunk_size': 5000,
                'max_workers': self.max_workers
            }
    
    def cleanup(self):
        """Dọn dẹp resources"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        self.cache.clear()
        gc.collect()


class CCCDPerformanceOptimizer(PerformanceOptimizer):
    """Performance Optimizer chuyên biệt cho CCCD"""
    
    def __init__(self):
        super().__init__()
        self.province_cache = {}
        self.gender_cache = {}
    
    def optimize_cccd_generation(self, 
                               quantity: int,
                               province_codes: List[str],
                               gender: Optional[str] = None,
                               birth_year_range: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Tối ưu hóa cho việc tạo CCCD
        
        Args:
            quantity: Số lượng CCCD cần tạo
            province_codes: Danh sách mã tỉnh
            gender: Giới tính
            birth_year_range: Khoảng năm sinh
            
        Returns:
            Cấu hình tối ưu
        """
        config = self.optimize_for_quantity(quantity)
        
        # Tối ưu hóa dựa trên số lượng tỉnh
        if len(province_codes) > 10:
            config['batch_size'] = min(config['batch_size'], 500)
        
        # Tối ưu hóa dựa trên khoảng năm sinh
        if birth_year_range:
            year_range = birth_year_range[1] - birth_year_range[0]
            if year_range > 50:
                config['chunk_size'] = min(config['chunk_size'], 1000)
        
        return config
    
    def preload_province_data(self):
        """Preload dữ liệu tỉnh/thành phố"""
        try:
            from cccd.province_data import ProvinceData
            self.cache_set('provinces', ProvinceData.get_all_provinces())
            self.cache_set('province_codes', ProvinceData.get_province_codes())
            self.cache_set('province_names', ProvinceData.get_province_names())
        except ImportError:
            pass
    
    def get_optimized_batch_size(self, quantity: int) -> int:
        """
        Lấy batch size tối ưu cho số lượng
        
        Args:
            quantity: Số lượng
            
        Returns:
            Batch size tối ưu
        """
        if quantity <= 100:
            return 50
        elif quantity <= 1000:
            return 200
        elif quantity <= 10000:
            return 1000
        else:
            return 2000


# Test functions
if __name__ == "__main__":
    # Test Performance Optimizer
    optimizer = CCCDPerformanceOptimizer()
    
    print("🧪 Test Performance Optimizer")
    print("=" * 50)
    
    # Test optimization configs
    test_quantities = [50, 500, 5000, 50000]
    
    for quantity in test_quantities:
        config = optimizer.optimize_cccd_generation(
            quantity=quantity,
            province_codes=["001", "079"],
            gender="Nam",
            birth_year_range=(1990, 2000)
        )
        
        print(f"Quantity: {quantity:,}")
        print(f"  Batch size: {config['batch_size']}")
        print(f"  Use multiprocessing: {config['use_multiprocessing']}")
        print(f"  Chunk size: {config['chunk_size']}")
        print(f"  Max workers: {config['max_workers']}")
        print()
    
    # Test metrics
    metrics = optimizer.get_performance_metrics()
    print("Performance Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Cleanup
    optimizer.cleanup()
    print("\n✅ Performance Optimizer test completed!")