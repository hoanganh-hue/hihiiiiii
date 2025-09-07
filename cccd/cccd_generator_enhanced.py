#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCCD Generator Enhanced - Phiên bản cải tiến với tỷ lệ chính xác cao
Tích hợp tính toán checksum tự động và validation đầy đủ
"""

from __future__ import annotations

import random
import time
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import calendar

from .cccd_config import CCCDConfig
from .performance_optimizer import CCCDPerformanceOptimizer
from .province_data import ProvinceData
from .checksum import calculate_checksum, is_checksum_valid


class CCCDGeneratorEnhanced:
    """
    CCCD Generator Enhanced - Phiên bản cải tiến với tỷ lệ chính xác cao
    
    Tính năng chính:
    - Tích hợp tính toán checksum tự động (100% tuân thủ Thông tư 07/2016/TT-BCA)
    - Logic gender-century khớp 100% với năm sinh
    - Validation đầy đủ để tránh tạo CCCD không hợp lệ
    - Cải thiện logic tạo ngày sinh (bao gồm năm nhuận)
    - Cơ chế kiểm tra trùng lặp số thứ tự
    - Tối ưu hóa phân phối ngẫu nhiên gần với thực tế
    """

    def __init__(self) -> None:
        self.provinces: Dict[str, Dict[str, str]] = ProvinceData.get_all_provinces()
        self.province_codes: List[str] = list(self.provinces.keys())
        self.gender_century_codes: Dict[int, Dict[str, Any]] = CCCDConfig.getGenderCenturyCodes()
        self.performance_optimizer = CCCDPerformanceOptimizer()
        self.performance_optimizer.preload_province_data()
        
        # Cache để tránh trùng lặp số thứ tự trong cùng tỉnh/ngày
        self.sequence_cache: Dict[str, Set[str]] = {}
        
        # Thống kê hiệu suất
        self.stats = {
            "total_generated": 0,
            "valid_cccd": 0,
            "invalid_cccd": 0,
            "checksum_errors": 0,
            "date_errors": 0,
            "gender_century_errors": 0,
            "duplicate_sequences": 0
        }

    def _get_gender_century_code(self, birth_year: int, gender: Optional[str] = None) -> int:
        """
        Tính toán mã thế kỷ và giới tính một cách chính xác 100%.
        Hỗ trợ các thế kỷ 20, 21, 22, 23, 24.
        """
        if not (CCCDConfig.MIN_BIRTH_YEAR <= birth_year <= CCCDConfig.MAX_BIRTH_YEAR):
            raise ValueError(f"Năm sinh {birth_year} nằm ngoài khoảng cho phép ({CCCDConfig.MIN_BIRTH_YEAR}-{CCCDConfig.MAX_BIRTH_YEAR})")
        
        century_val = (birth_year // 100) + 1
        base_code = (century_val - 20) * 2

        # Lọc ra các mã hợp lệ cho thế kỷ này
        valid_codes = [k for k, v in self.gender_century_codes.items() if v["century"] == century_val]
        if not valid_codes:
            raise ValueError(f"Không tìm thấy mã hợp lệ cho thế kỷ {century_val}")

        if gender == "Nam":
            return base_code
        elif gender == "Nữ":
            return base_code + 1
        else:
            # Nếu không chỉ định giới tính, chọn ngẫu nhiên từ các mã hợp lệ
            return random.choice(valid_codes)

    def _generate_valid_date(self, birth_year: int) -> Tuple[int, int]:
        """
        Tạo ngày sinh hợp lệ, bao gồm xử lý năm nhuận.
        """
        # Tạo tháng ngẫu nhiên
        birth_month = random.randint(1, 12)
        
        # Tạo ngày hợp lệ cho tháng đó
        if birth_month in [1, 3, 5, 7, 8, 10, 12]:
            # Tháng có 31 ngày
            birth_day = random.randint(1, 31)
        elif birth_month in [4, 6, 9, 11]:
            # Tháng có 30 ngày
            birth_day = random.randint(1, 30)
        else:  # birth_month == 2
            # Tháng 2 - xử lý năm nhuận
            if calendar.isleap(birth_year):
                birth_day = random.randint(1, 29)
            else:
                birth_day = random.randint(1, 28)
        
        return birth_month, birth_day

    def _generate_unique_sequence(self, province_code: str, birth_year: int, 
                                birth_month: int, birth_day: int) -> str:
        """
        Tạo số thứ tự duy nhất cho tỉnh/ngày cụ thể.
        """
        # Tạo key duy nhất cho tỉnh/ngày
        date_key = f"{province_code}_{birth_year:04d}{birth_month:02d}{birth_day:02d}"
        
        # Khởi tạo cache nếu chưa có
        if date_key not in self.sequence_cache:
            self.sequence_cache[date_key] = set()
        
        # Tìm số thứ tự chưa được sử dụng
        max_attempts = 100  # Tránh vòng lặp vô hạn
        for _ in range(max_attempts):
            sequence_num = random.randint(1, 99)
            sequence_code = str(sequence_num).zfill(2)
            
            if sequence_code not in self.sequence_cache[date_key]:
                self.sequence_cache[date_key].add(sequence_code)
                return sequence_code
        
        # Nếu không tìm được số duy nhất, sử dụng timestamp
        timestamp = int(time.time() * 1000) % 100
        sequence_code = str(timestamp).zfill(2)
        self.sequence_cache[date_key].add(sequence_code)
        self.stats["duplicate_sequences"] += 1
        
        return sequence_code

    def _generate_cccd_with_checksum(self, province_code: str, birth_year: int,
                                   birth_month: int, birth_day: int, 
                                   gender: Optional[str] = None) -> Dict[str, Any]:
        """
        Tạo CCCD với checksum tự động và validation đầy đủ.
        """
        try:
            # Tính toán mã giới tính-thế kỷ
            gender_century_code = self._get_gender_century_code(birth_year, gender)
            
            # Tạo các mã thành phần
            year_code = str(birth_year % 100).zfill(2)
            month_code = str(birth_month).zfill(2)
            day_code = str(birth_day).zfill(2)
            
            # Tạo số thứ tự duy nhất
            sequence_code = self._generate_unique_sequence(
                province_code, birth_year, birth_month, birth_day
            )
            
            # Tạo chuỗi đầy đủ 12 chữ số
            full_digits = f"{province_code}{gender_century_code}{year_code}{month_code}{day_code}{sequence_code}"
            
            # Lấy 11 chữ số đầu để tính checksum
            eleven_digits = full_digits[:11]
            
            # Tính checksum tự động
            checksum_digit = calculate_checksum(eleven_digits)
            
            # Tạo CCCD hoàn chỉnh
            cccd = f"{eleven_digits}{checksum_digit}"
            
            # Validation cuối cùng
            if not is_checksum_valid(cccd):
                self.stats["checksum_errors"] += 1
                raise ValueError("Checksum không hợp lệ sau khi tính toán")
            
            # Lấy thông tin giới tính
            gender_info = self.gender_century_codes.get(gender_century_code, {})
            gender_text = gender_info.get("gender", "Không xác định")
            century_text = gender_info.get("century", "Không xác định")
            
            self.stats["valid_cccd"] += 1
            
            return {
                "cccd_number": cccd,
                "province_code": province_code,
                "province_name": self.provinces.get(province_code, {}).get("name", "Unknown"),
                "gender": gender_text,
                "birth_year": birth_year,
                "birth_month": birth_month,
                "birth_day": birth_day,
                "birth_date": f"{birth_day:02d}/{birth_month:02d}/{birth_year}",
                "century": century_text,
                "gender_century_code": gender_century_code,
                "sequence_number": sequence_code,
                "checksum_digit": checksum_digit,
                "valid": True,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.stats["invalid_cccd"] += 1
            if "năm sinh" in str(e):
                self.stats["date_errors"] += 1
            elif "thế kỷ" in str(e):
                self.stats["gender_century_errors"] += 1
            
            return {
                "cccd_number": None,
                "error": str(e),
                "valid": False,
                "generated_at": datetime.now().isoformat()
            }

    def generate_cccd_list_enhanced(
        self,
        province_codes: Optional[List[str]] = None,
        gender: Optional[str] = None,
        birth_year_range: Optional[Tuple[int, int]] = None,
        quantity: int = 10,
        validate_output: bool = True
    ) -> Dict[str, Any]:
        """
        Tạo danh sách CCCD với tỷ lệ chính xác cao.
        
        Args:
            province_codes: Danh sách mã tỉnh/thành
            gender: Giới tính ('Nam', 'Nữ', hoặc None để random)
            birth_year_range: Khoảng năm sinh (min_year, max_year)
            quantity: Số lượng CCCD cần tạo
            validate_output: Có validate kết quả đầu ra không
            
        Returns:
            Dict chứa danh sách CCCD và thống kê
        """
        start_time = time.time()
        
        # Validation đầu vào
        input_validation = CCCDConfig.validateInputLimit("generation_single", quantity)
        if not input_validation["valid"]:
            return {
                "success": False,
                "error": input_validation["error"],
                "maxLimit": input_validation["maxLimit"],
                "requested": input_validation["requested"],
            }

        max_quantity = input_validation["maxLimit"]
        actual_quantity = min(quantity, max_quantity)
        
        # Chuẩn bị tham số
        target_province_codes = province_codes or self.province_codes
        
        if birth_year_range:
            start_year, end_year = birth_year_range
            if start_year > end_year:
                start_year, end_year = end_year, start_year
        else:
            start_year, end_year = 1990, 2000

        # Tạo danh sách CCCD
        results: List[Dict[str, Any]] = []
        
        for i in range(actual_quantity):
            # Chọn tỉnh ngẫu nhiên
            province_code = random.choice(target_province_codes)
            
            # Tạo năm sinh ngẫu nhiên
            birth_year = random.randint(start_year, end_year)
            
            # Tạo ngày sinh hợp lệ
            birth_month, birth_day = self._generate_valid_date(birth_year)
            
            # Tạo CCCD với checksum
            cccd_data = self._generate_cccd_with_checksum(
                province_code, birth_year, birth_month, birth_day, gender
            )
            
            results.append(cccd_data)
            
            # Log progress cho batch lớn
            if actual_quantity > 1000 and (i + 1) % 1000 == 0:
                progress = (i + 1) / actual_quantity * 100
                print(f"Generated {i + 1}/{actual_quantity} CCCD ({progress:.1f}%)")

        # Validation đầu ra
        if validate_output:
            results = self._validate_results(results)
        
        # Cập nhật thống kê
        self.stats["total_generated"] += len(results)
        
        end_time = time.time()
        
        # Tính toán KPIs
        kpis = self._calculate_kpis(results, end_time - start_time)
        
        return {
            "success": True,
            "data": results,
            "metadata": {
                "input_limit": input_validation["maxLimit"],
                "requested_quantity": quantity,
                "actual_quantity": len(results),
                "generation_time": end_time - start_time,
                "kpis": kpis,
                "stats": self.stats.copy()
            }
        }

    def _validate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate kết quả và loại bỏ các CCCD không hợp lệ.
        """
        valid_results = []
        
        for result in results:
            if result.get("valid", False) and result.get("cccd_number"):
                # Kiểm tra lại checksum
                if is_checksum_valid(result["cccd_number"]):
                    valid_results.append(result)
                else:
                    result["valid"] = False
                    result["error"] = "Checksum không hợp lệ trong validation"
            else:
                valid_results.append(result)  # Giữ lại để báo lỗi
        
        return valid_results

    def _calculate_kpis(self, results: List[Dict[str, Any]], generation_time: float) -> Dict[str, Any]:
        """
        Tính toán các chỉ số KPI.
        """
        total_results = len(results)
        valid_results = sum(1 for r in results if r.get("valid", False))
        
        if total_results == 0:
            return {
                "coverage_rate": 0.0,
                "rpn": 0.0,
                "reliability_index": 0.0,
                "accuracy_rate": 0.0,
                "generation_speed": 0.0
            }
        
        # Coverage Rate - Tỷ lệ bao phủ (số CCCD hợp lệ / tổng số)
        coverage_rate = (valid_results / total_results) * 100
        
        # RPN (Risk Priority Number) - Chỉ số ưu tiên rủi ro
        # RPN = Severity × Occurrence × Detection
        severity = 10 if coverage_rate < 95 else 5 if coverage_rate < 99 else 1
        occurrence = 10 if self.stats["invalid_cccd"] > 0 else 1
        detection = 5  # Giả định có hệ thống phát hiện lỗi
        rpn = severity * occurrence * detection
        
        # Reliability Index - Chỉ số độ tin cậy
        reliability_index = min(100, coverage_rate - (rpn / 10))
        
        # Accuracy Rate - Tỷ lệ chính xác
        accuracy_rate = coverage_rate
        
        # Generation Speed - Tốc độ tạo (CCCD/giây)
        generation_speed = total_results / generation_time if generation_time > 0 else 0
        
        return {
            "coverage_rate": round(coverage_rate, 2),
            "rpn": rpn,
            "reliability_index": round(reliability_index, 2),
            "accuracy_rate": round(accuracy_rate, 2),
            "generation_speed": round(generation_speed, 2),
            "valid_count": valid_results,
            "invalid_count": total_results - valid_results
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê hiệu suất.
        """
        return {
            "stats": self.stats.copy(),
            "cache_size": sum(len(sequences) for sequences in self.sequence_cache.values()),
            "province_coverage": len(self.province_codes),
            "supported_centuries": list(set(info["century"] for info in self.gender_century_codes.values()))
        }

    def clear_cache(self) -> None:
        """
        Xóa cache để giải phóng bộ nhớ.
        """
        self.sequence_cache.clear()
        print("Cache đã được xóa")

    def batch_generate_optimized(
        self,
        province_codes: Optional[List[str]] = None,
        gender: Optional[str] = None,
        birth_year_range: Optional[Tuple[int, int]] = None,
        quantity: int = 10000
    ) -> Dict[str, Any]:
        """
        Tạo batch lớn với tối ưu hóa hiệu suất.
        """
        if quantity <= 1000:
            return self.generate_cccd_list_enhanced(
                province_codes, gender, birth_year_range, quantity
            )
        
        # Tối ưu hóa cho batch lớn
        config = self.performance_optimizer.optimize_cccd_generation(
            quantity=quantity,
            province_codes=province_codes or self.province_codes,
            gender=gender,
            birth_year_range=birth_year_range
        )
        
        batch_size = config['batch_size']
        all_results = []
        
        for i in range(0, quantity, batch_size):
            current_batch_size = min(batch_size, quantity - i)
            
            batch_result = self.generate_cccd_list_enhanced(
                province_codes, gender, birth_year_range, current_batch_size, False
            )
            
            if batch_result["success"]:
                all_results.extend(batch_result["data"])
            
            # Log progress
            if (i + current_batch_size) % (batch_size * 10) == 0:
                progress = (i + current_batch_size) / quantity * 100
                print(f"Batch progress: {i + current_batch_size}/{quantity} ({progress:.1f}%)")
        
        # Validation cuối cùng
        all_results = self._validate_results(all_results)
        
        return {
            "success": True,
            "data": all_results,
            "metadata": {
                "total_quantity": quantity,
                "actual_quantity": len(all_results),
                "batch_size": batch_size,
                "kpis": self._calculate_kpis(all_results, 0)
            }
        }


# Test functions
if __name__ == "__main__":
    # Test generator enhanced
    generator = CCCDGeneratorEnhanced()
    
    print("=== Test CCCD Generator Enhanced ===")
    
    # Test tạo 10 CCCD
    result = generator.generate_cccd_list_enhanced(
        province_codes=["001", "079"],  # Hà Nội, TP.HCM
        gender=None,  # Random
        birth_year_range=(1990, 2000),
        quantity=10
    )
    
    if result["success"]:
        print(f"Tạo thành công {len(result['data'])} CCCD")
        print(f"KPIs: {result['metadata']['kpis']}")
        
        # Hiển thị một vài CCCD mẫu
        for i, cccd_data in enumerate(result["data"][:3]):
            if cccd_data.get("valid"):
                print(f"CCCD {i+1}: {cccd_data['cccd_number']} - {cccd_data['gender']} - {cccd_data['birth_date']} - {cccd_data['province_name']}")
    else:
        print(f"Lỗi: {result.get('error')}")
    
    # Test performance stats
    stats = generator.get_performance_stats()
    print(f"\nPerformance Stats: {stats}")