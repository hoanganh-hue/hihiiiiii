from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

from .cccd_config import CCCDConfig
from .performance_optimizer import CCCDPerformanceOptimizer
from .province_data import ProvinceData


class CCCDGeneratorService:
    """Simple CCCD generator (Python port)."""

    def __init__(self) -> None:
        self.provinces: Dict[str, Dict[str, str]] = ProvinceData.get_all_provinces()
        self.province_codes: List[str] = list(self.provinces.keys())
        self.gender_century_codes: Dict[int, Dict[str, Any]] = CCCDConfig.getGenderCenturyCodes()
        self.performance_optimizer = CCCDPerformanceOptimizer()
        self.performance_optimizer.preload_province_data()

    def _get_gender_century_code(self, birth_year: int, gender: Optional[str] = None) -> int:
        """
        Tính toán mã thế kỷ và giới tính một cách tự động.
        Hỗ trợ các thế kỷ 20, 21, 22, 23, 24.
        """
        century_val = (birth_year // 100) + 1
        base_code = (century_val - 20) * 2

        # Lọc ra các mã hợp lệ cho thế kỷ này
        valid_codes = [k for k, v in self.gender_century_codes.items() if v["century"] == century_val]
        if not valid_codes:
            # Fallback cho các năm không được hỗ trợ, mặc dù logic trên đã bao quát
            return random.choice([0, 1])

        if gender == "Nam":
            return base_code
        if gender == "Nữ":
            return base_code + 1
        
        # Nếu không chỉ định giới tính, chọn ngẫu nhiên từ các mã hợp lệ
        return random.choice(valid_codes)

    def generateCccdList(
        self,
        provinceCodes: Optional[List[str]] = None,
        gender: Optional[str] = None,
        birthYearRange: Optional[List[int]] = None,
        genderRatio: Optional[Any] = None,  # not used, kept for API parity
        quantity: int = 10,
    ) -> Any:
        input_validation = CCCDConfig.validateInputLimit("generation_single", quantity)
        if not input_validation["valid"]:
            return {
                "error": input_validation["error"],
                "maxLimit": input_validation["maxLimit"],
                "requested": input_validation["requested"],
            }

        max_quantity = input_validation["maxLimit"]
        actual_quantity = min(quantity, max_quantity)

        # Tối ưu hóa hiệu suất cho số lượng lớn
        if actual_quantity > 1000:
            return self._generate_cccd_list_optimized(
                provinceCodes, gender, birthYearRange, actual_quantity
            )

        results: List[Dict[str, Any]] = []
        
        target_province_codes = provinceCodes or self.province_codes

        for _ in range(actual_quantity):
            province_code = random.choice(target_province_codes)

            start_year = birthYearRange[0] if birthYearRange else 1990
            end_year = birthYearRange[1] if birthYearRange else 2000
            if start_year > end_year:
                start_year, end_year = end_year, start_year
            birth_year = random.randint(start_year, end_year)

            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28) # Giữ an toàn để tránh lỗi ngày không hợp lệ

            gender_century_code = self._get_gender_century_code(birth_year, gender)
            
            year_code = str(birth_year % 100).zfill(2)
            month_code = str(birth_month).zfill(2)
            day_code = str(birth_day).zfill(2)

            sequence_code = str(random.randint(1, 99)).zfill(2)

            cccd = f"{province_code}{gender_century_code}{year_code}{month_code}{day_code}{sequence_code}"

            gender_info = self.gender_century_codes.get(gender_century_code, {})
            gender_text = gender_info.get("gender", "Không xác định")
            century_text = gender_info.get("century", "Không xác định")

            results.append(
                {
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
                }
            )

        output_validation = CCCDConfig.validateOutputLimit("max_results_per_request", len(results))
        if not output_validation["valid"]:
            results = results[: output_validation["maxLimit"]]

        if results:
            results[0]["_metadata"] = {
                "input_limit": input_validation["maxLimit"],
                "output_limit": output_validation["maxLimit"],
                "requested_quantity": quantity,
                "actual_quantity": len(results),
                "truncated": quantity > input_validation["maxLimit"] or len(results) > output_validation["maxLimit"],
            }

        return results

    def _generate_cccd_list_optimized(self,
                                    provinceCodes: Optional[List[str]] = None,
                                    gender: Optional[str] = None,
                                    birthYearRange: Optional[List[int]] = None,
                                    quantity: int = 1000) -> List[Dict[str, Any]]:
        """
        Tạo danh sách CCCD với tối ưu hóa hiệu suất cho số lượng lớn
        """
        start_time = time.time()
        
        # Lấy cấu hình tối ưu
        config = self.performance_optimizer.optimize_cccd_generation(
            quantity=quantity,
            province_codes=provinceCodes or self.province_codes,
            gender=gender,
            birth_year_range=tuple(birthYearRange) if birthYearRange else None
        )
        
        # Tạo dữ liệu theo batch
        results = []
        batch_size = config['batch_size']
        
        for i in range(0, quantity, batch_size):
            current_batch_size = min(batch_size, quantity - i)
            batch_results = self._generate_cccd_batch(
                provinceCodes, gender, birthYearRange, current_batch_size
            )
            results.extend(batch_results)
            
            # Log progress cho batch lớn
            if quantity > 10000 and (i + current_batch_size) % (batch_size * 10) == 0:
                progress = (i + current_batch_size) / quantity * 100
                print(f"Generated {i + current_batch_size}/{quantity} CCCD ({progress:.1f}%)")
        
        end_time = time.time()
        print(f"Generated {quantity} CCCD in {end_time - start_time:.2f} seconds")
        
        return results

    def _generate_cccd_batch(self,
                           provinceCodes: Optional[List[str]] = None,
                           gender: Optional[str] = None,
                           birthYearRange: Optional[List[int]] = None,
                           batch_size: int = 1000) -> List[Dict[str, Any]]:
        """
        Tạo một batch CCCD
        """
        results = []
        target_province_codes = provinceCodes or self.province_codes
        
        for _ in range(batch_size):
            province_code = random.choice(target_province_codes)

            start_year = birthYearRange[0] if birthYearRange else 1990
            end_year = birthYearRange[1] if birthYearRange else 2000
            if start_year > end_year:
                start_year, end_year = end_year, start_year
            birth_year = random.randint(start_year, end_year)

            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)

            gender_century_code = self._get_gender_century_code(birth_year, gender)

            year_code = str(birth_year % 100).zfill(2)
            month_code = str(birth_month).zfill(2)
            day_code = str(birth_day).zfill(2)

            sequence_code = str(random.randint(1, 99)).zfill(2)

            cccd = f"{province_code}{gender_century_code}{year_code}{month_code}{day_code}{sequence_code}"

            gender_info = self.gender_century_codes.get(gender_century_code, {})
            gender_text = gender_info.get("gender", "Không xác định")
            century_text = gender_info.get("century", "Không xác định")

            results.append(
                {
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
                }
            )
        
        return results

    def saveToFile(self, results: List[Dict[str, Any]], filename: str) -> None:
        # Giữ behavior đơn giản như JS: chỉ in ra console
        print(f"Saving {len(results)} results to {filename}")
