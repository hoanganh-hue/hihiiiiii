#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test module cho CCCD Generator Enhanced
Kiểm tra tính chính xác và hiệu suất của generator mới
"""

import unittest
import time
from typing import Dict, List, Any

from .cccd_generator_enhanced import CCCDGeneratorEnhanced
from .cccd_analyzer_service import CCCDAnalyzerService
from .checksum import is_checksum_valid


class TestCCCDGeneratorEnhanced(unittest.TestCase):
    """Test cases cho CCCD Generator Enhanced"""
    
    def setUp(self):
        """Khởi tạo test environment"""
        self.generator = CCCDGeneratorEnhanced()
        self.analyzer = CCCDAnalyzerService()
        
    def test_checksum_accuracy(self):
        """Test tính chính xác của checksum"""
        print("\n=== Test Checksum Accuracy ===")
        
        # Tạo 100 CCCD và kiểm tra checksum
        result = self.generator.generate_cccd_list_enhanced(
            quantity=100,
            validate_output=True
        )
        
        self.assertTrue(result["success"], "Generator should succeed")
        
        valid_count = 0
        checksum_valid_count = 0
        
        for cccd_data in result["data"]:
            if cccd_data.get("valid") and cccd_data.get("cccd_number"):
                valid_count += 1
                cccd = cccd_data["cccd_number"]
                
                # Kiểm tra checksum
                if is_checksum_valid(cccd):
                    checksum_valid_count += 1
                else:
                    print(f"Checksum invalid: {cccd}")
        
        checksum_accuracy = (checksum_valid_count / valid_count * 100) if valid_count > 0 else 0
        
        print(f"Valid CCCD: {valid_count}/100")
        print(f"Checksum accuracy: {checksum_accuracy:.2f}%")
        
        # Yêu cầu checksum accuracy >= 99%
        self.assertGreaterEqual(checksum_accuracy, 99.0, 
                               f"Checksum accuracy should be >= 99%, got {checksum_accuracy:.2f}%")
    
    def test_gender_century_consistency(self):
        """Test tính nhất quán của mã giới tính-thế kỷ"""
        print("\n=== Test Gender-Century Consistency ===")
        
        # Test với các năm cụ thể
        test_cases = [
            (1990, "Nam", 0),   # Thế kỷ 20, Nam
            (1990, "Nữ", 1),    # Thế kỷ 20, Nữ
            (2000, "Nam", 2),   # Thế kỷ 21, Nam
            (2000, "Nữ", 3),    # Thế kỷ 21, Nữ
            (2100, "Nam", 4),   # Thế kỷ 22, Nam
            (2100, "Nữ", 5),    # Thế kỷ 22, Nữ
        ]
        
        for birth_year, gender, expected_code in test_cases:
            result = self.generator.generate_cccd_list_enhanced(
                birth_year_range=(birth_year, birth_year),
                gender=gender,
                quantity=10
            )
            
            self.assertTrue(result["success"], f"Should succeed for {birth_year}, {gender}")
            
            for cccd_data in result["data"]:
                if cccd_data.get("valid"):
                    actual_code = cccd_data["gender_century_code"]
                    self.assertEqual(actual_code, expected_code,
                                   f"Gender-century code mismatch for {birth_year}, {gender}: "
                                   f"expected {expected_code}, got {actual_code}")
        
        print("All gender-century consistency tests passed!")
    
    def test_date_validity(self):
        """Test tính hợp lệ của ngày sinh"""
        print("\n=== Test Date Validity ===")
        
        # Test với năm nhuận
        result = self.generator.generate_cccd_list_enhanced(
            birth_year_range=(2020, 2020),  # Năm nhuận
            quantity=50
        )
        
        self.assertTrue(result["success"], "Should succeed for leap year")
        
        valid_dates = 0
        invalid_dates = 0
        
        for cccd_data in result["data"]:
            if cccd_data.get("valid"):
                # Phân tích CCCD để kiểm tra ngày
                cccd = cccd_data["cccd_number"]
                analysis = self.analyzer.analyzeCccdStructure(cccd)
                
                if analysis.get("valid") and analysis.get("structure", {}).get("birthDate", {}).get("valid"):
                    valid_dates += 1
                else:
                    invalid_dates += 1
                    print(f"Invalid date in CCCD: {cccd}")
        
        date_accuracy = (valid_dates / (valid_dates + invalid_dates) * 100) if (valid_dates + invalid_dates) > 0 else 0
        
        print(f"Valid dates: {valid_dates}")
        print(f"Invalid dates: {invalid_dates}")
        print(f"Date accuracy: {date_accuracy:.2f}%")
        
        # Yêu cầu date accuracy >= 99%
        self.assertGreaterEqual(date_accuracy, 99.0,
                               f"Date accuracy should be >= 99%, got {date_accuracy:.2f}%")
    
    def test_sequence_uniqueness(self):
        """Test tính duy nhất của số thứ tự"""
        print("\n=== Test Sequence Uniqueness ===")
        
        # Tạo nhiều CCCD cho cùng tỉnh/ngày
        result = self.generator.generate_cccd_list_enhanced(
            province_codes=["001"],  # Chỉ Hà Nội
            birth_year_range=(1995, 1995),  # Chỉ năm 1995
            quantity=100
        )
        
        self.assertTrue(result["success"], "Should succeed for sequence uniqueness test")
        
        # Nhóm theo tỉnh/ngày
        date_groups = {}
        for cccd_data in result["data"]:
            if cccd_data.get("valid"):
                key = f"{cccd_data['province_code']}_{cccd_data['birth_date']}"
                if key not in date_groups:
                    date_groups[key] = []
                date_groups[key].append(cccd_data["sequence_number"])
        
        # Kiểm tra tính duy nhất trong mỗi nhóm
        duplicate_count = 0
        for date_key, sequences in date_groups.items():
            unique_sequences = set(sequences)
            if len(unique_sequences) != len(sequences):
                duplicate_count += 1
                print(f"Duplicates found in {date_key}: {len(sequences) - len(unique_sequences)}")
        
        uniqueness_rate = ((len(date_groups) - duplicate_count) / len(date_groups) * 100) if date_groups else 100
        
        print(f"Date groups: {len(date_groups)}")
        print(f"Groups with duplicates: {duplicate_count}")
        print(f"Uniqueness rate: {uniqueness_rate:.2f}%")
        
        # Yêu cầu uniqueness rate >= 95%
        self.assertGreaterEqual(uniqueness_rate, 95.0,
                               f"Uniqueness rate should be >= 95%, got {uniqueness_rate:.2f}%")
    
    def test_performance_metrics(self):
        """Test các chỉ số hiệu suất"""
        print("\n=== Test Performance Metrics ===")
        
        start_time = time.time()
        
        result = self.generator.generate_cccd_list_enhanced(
            quantity=1000,
            validate_output=True
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        self.assertTrue(result["success"], "Should succeed for performance test")
        
        kpis = result["metadata"]["kpis"]
        
        print(f"Generation time: {generation_time:.2f} seconds")
        print(f"Coverage rate: {kpis['coverage_rate']:.2f}%")
        print(f"Accuracy rate: {kpis['accuracy_rate']:.2f}%")
        print(f"Reliability index: {kpis['reliability_index']:.2f}")
        print(f"Generation speed: {kpis['generation_speed']:.2f} CCCD/second")
        
        # Yêu cầu coverage rate >= 99%
        self.assertGreaterEqual(kpis["coverage_rate"], 99.0,
                               f"Coverage rate should be >= 99%, got {kpis['coverage_rate']:.2f}%")
        
        # Yêu cầu accuracy rate >= 99%
        self.assertGreaterEqual(kpis["accuracy_rate"], 99.0,
                               f"Accuracy rate should be >= 99%, got {kpis['accuracy_rate']:.2f}%")
        
        # Yêu cầu generation speed >= 100 CCCD/second
        self.assertGreaterEqual(kpis["generation_speed"], 100.0,
                               f"Generation speed should be >= 100 CCCD/second, got {kpis['generation_speed']:.2f}")
    
    def test_batch_generation(self):
        """Test tạo batch lớn"""
        print("\n=== Test Batch Generation ===")
        
        start_time = time.time()
        
        result = self.generator.batch_generate_optimized(
            quantity=5000,
            province_codes=["001", "079", "048"],  # Hà Nội, TP.HCM, Đà Nẵng
            birth_year_range=(1980, 2010)
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        self.assertTrue(result["success"], "Should succeed for batch generation")
        
        print(f"Batch generation time: {generation_time:.2f} seconds")
        print(f"Total generated: {len(result['data'])}")
        print(f"Batch speed: {len(result['data']) / generation_time:.2f} CCCD/second")
        
        # Kiểm tra một mẫu ngẫu nhiên
        sample_size = min(100, len(result["data"]))
        valid_count = 0
        
        for i in range(0, len(result["data"]), len(result["data"]) // sample_size):
            cccd_data = result["data"][i]
            if cccd_data.get("valid") and cccd_data.get("cccd_number"):
                if is_checksum_valid(cccd_data["cccd_number"]):
                    valid_count += 1
        
        sample_accuracy = (valid_count / sample_size * 100) if sample_size > 0 else 0
        
        print(f"Sample accuracy: {sample_accuracy:.2f}%")
        
        # Yêu cầu sample accuracy >= 99%
        self.assertGreaterEqual(sample_accuracy, 99.0,
                               f"Sample accuracy should be >= 99%, got {sample_accuracy:.2f}%")
    
    def test_all_provinces_coverage(self):
        """Test bao phủ tất cả 63 tỉnh thành"""
        print("\n=== Test All Provinces Coverage ===")
        
        result = self.generator.generate_cccd_list_enhanced(
            quantity=630,  # 10 CCCD per province
            validate_output=True
        )
        
        self.assertTrue(result["success"], "Should succeed for all provinces test")
        
        # Đếm số tỉnh được sử dụng
        used_provinces = set()
        for cccd_data in result["data"]:
            if cccd_data.get("valid"):
                used_provinces.add(cccd_data["province_code"])
        
        total_provinces = len(self.generator.province_codes)
        coverage_rate = (len(used_provinces) / total_provinces * 100)
        
        print(f"Total provinces: {total_provinces}")
        print(f"Used provinces: {len(used_provinces)}")
        print(f"Coverage rate: {coverage_rate:.2f}%")
        
        # Yêu cầu coverage rate >= 90% (do random selection)
        self.assertGreaterEqual(coverage_rate, 90.0,
                               f"Province coverage should be >= 90%, got {coverage_rate:.2f}%")


def run_comprehensive_test():
    """Chạy test toàn diện"""
    print("=" * 60)
    print("CCCD GENERATOR ENHANCED - COMPREHENSIVE TEST")
    print("=" * 60)
    
    # Tạo test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCCCDGeneratorEnhanced)
    
    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Tóm tắt kết quả
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)