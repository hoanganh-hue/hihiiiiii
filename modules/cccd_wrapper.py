#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCCD Module Wrapper - PRODUCTION
Wrapper Python để tương tác với các module CCCD thuần Python.
Triển khai thực tế với dữ liệu thật từ API chính thức.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Thêm đường dẫn đến thư mục gốc của dự án và thư mục cccd
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'cccd'))

try:
    from cccd.cccd_generator_service import CCCDGeneratorService
    from cccd.cccd_generator_enhanced import CCCDGeneratorEnhanced
    from cccd.cccd_analyzer_service import CCCDAnalyzerService
except ImportError:
    print("Error: Không thể import CCCD services.")
    print("Vui lòng đảm bảo thư mục cccd tồn tại và có thể truy cập.")
    class CCCDGeneratorService:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("CCCDGeneratorService không thể được khởi tạo.")
    class CCCDGeneratorEnhanced:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("CCCDGeneratorEnhanced không thể được khởi tạo.")
    class CCCDAnalyzerService:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("CCCDAnalyzerService không thể được khởi tạo.")

class CCCDWrapper:
    """
    Wrapper class để tương tác với các module CCCD bằng Python thuần.
    """
    
    def __init__(self, use_enhanced: bool = True):
        """
        Khởi tạo CCCD Wrapper.
        
        Args:
            use_enhanced: Sử dụng generator enhanced (True) hay generator cũ (False)
        """
        try:
            if use_enhanced:
                self.generator = CCCDGeneratorEnhanced()
                self.generator_type = "enhanced"
            else:
                self.generator = CCCDGeneratorService()
                self.generator_type = "standard"
            
            self.analyzer = CCCDAnalyzerService()
        except Exception as e:
            print(f"Lỗi khi khởi tạo các service CCCD: {e}")
            self.generator = None
            self.analyzer = None
            self.generator_type = None

    def generate_cccd_list(self, 
                          province_codes: List[str] = None, 
                          quantity: int = 10,
                          gender: str = None,
                          birth_year_range: tuple = None,
                          use_enhanced: bool = None) -> Dict:
        """
        Tạo danh sách số CCCD.
        
        Args:
            province_codes: Danh sách mã tỉnh/thành (VD: ['001', '079'])
            quantity: Số lượng CCCD cần tạo
            gender: Giới tính ('Nam' hoặc 'Nữ', None để random)
            birth_year_range: Khoảng năm sinh (tuple: (min_year, max_year))
            use_enhanced: Sử dụng generator enhanced (None = dùng generator hiện tại)
            
        Returns:
            Dict chứa danh sách các số CCCD đã tạo (dạng List[str]).
        """
        if not self.generator:
            return {"success": False, "error": "CCCD Generator không được khởi tạo."}

        try:
            # Sử dụng generator enhanced nếu được yêu cầu
            if use_enhanced is True and self.generator_type != "enhanced":
                self.generator = CCCDGeneratorEnhanced()
                self.generator_type = "enhanced"
            elif use_enhanced is False and self.generator_type != "standard":
                self.generator = CCCDGeneratorService()
                self.generator_type = "standard"

            if self.generator_type == "enhanced":
                # Sử dụng generator enhanced
                result = self.generator.generate_cccd_list_enhanced(
                    province_codes=province_codes,
                    gender=gender,
                    birth_year_range=birth_year_range,
                    quantity=quantity,
                    validate_output=True
                )
                
                if result["success"]:
                    # Trích xuất danh sách CCCD numbers
                    cccd_numbers = [item['cccd_number'] for item in result["data"] if item.get("valid")]
                    
                    return {
                        "success": True, 
                        "data": cccd_numbers,
                        "metadata": result.get("metadata", {}),
                        "generator_type": "enhanced"
                    }
                else:
                    return {"success": False, "error": result.get("error", "Unknown error")}
            else:
                # Sử dụng generator standard
                birth_year_list = list(birth_year_range) if birth_year_range else None

                detailed_results = self.generator.generateCccdList(
                    provinceCodes=province_codes,
                    quantity=quantity,
                    gender=gender,
                    birthYearRange=birth_year_list
                )

                # Xử lý trường hợp service trả về lỗi
                if isinstance(detailed_results, dict) and 'error' in detailed_results:
                     return {"success": False, "error": detailed_results['error']}

                # Trích xuất ra danh sách các số CCCD (List[str]) để tương thích với main.py
                cccd_numbers = [item['cccd_number'] for item in detailed_results]

                return {
                    "success": True, 
                    "data": cccd_numbers,
                    "generator_type": "standard"
                }

        except Exception as e:
            return {"success": False, "error": f"Lỗi không xác định trong CCCDWrapper: {e}"}

    def analyze_cccd(self, cccd: str, detailed: bool = True) -> Dict:
        """
        Phân tích cấu trúc số CCCD.
        """
        if not self.analyzer:
            return {"success": False, "error": "CCCDAnalyzerService không được khởi tạo."}
        
        try:
            analysis = self.analyzer.analyzeCccdStructure(cccd, detailed=detailed)
            return {"success": True, "data": analysis}
        except Exception as e:
            return {"success": False, "error": f"Lỗi khi phân tích CCCD: {e}"}
    
    def validate_cccd(self, cccd: str) -> Dict:
        """
        Kiểm tra tính hợp lệ của số CCCD.
        """
        if not self.analyzer:
            return {"success": False, "error": "CCCDAnalyzerService không được khởi tạo."}
        
        try:
            validation = self.analyzer.validateCccdFormat(cccd)
            return {"success": True, "data": validation}
        except Exception as e:
            return {"success": False, "error": f"Lỗi khi validate CCCD: {e}"}
    
    def get_performance_stats(self) -> Dict:
        """
        Lấy thống kê hiệu suất (chỉ có với generator enhanced).
        """
        if self.generator_type == "enhanced" and hasattr(self.generator, 'get_performance_stats'):
            try:
                return {"success": True, "data": self.generator.get_performance_stats()}
            except Exception as e:
                return {"success": False, "error": f"Lỗi khi lấy thống kê: {e}"}
        else:
            return {"success": False, "error": "Chức năng chỉ có với generator enhanced"}

# Test functions
if __name__ == "__main__":
    try:
        print("▶️  Bắt đầu kiểm tra CCCDWrapper...")
        cccd_wrapper = CCCDWrapper()
        
        if not cccd_wrapper.generator:
            raise RuntimeError("Không thể khởi tạo CCCDGeneratorService.")

        print("\n=== Test: Tạo 3 CCCD ở Hà Nội ===")
        result = cccd_wrapper.generate_cccd_list(province_codes=['001'], quantity=3)
        if result['success']:
            cccd_list = result['data']
            print(f"✅ Thành công! Tạo được {len(cccd_list)} số CCCD:")
            for cccd_number in cccd_list:
                print(f"   - {cccd_number}")
        else:
            print(f"❌ Thất bại: {result.get('error')}")
                
    except Exception as e:
        print(f"\n🚨 Lỗi nghiêm trọng khi kiểm tra wrapper: {e}")