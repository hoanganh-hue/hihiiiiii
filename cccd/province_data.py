#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dữ liệu 63 tỉnh/thành phố Việt Nam chính xác
Theo quy định của Bộ Nội vụ và Tổng cục Thống kê
"""

from typing import Dict, List, Tuple

class ProvinceData:
    """Dữ liệu tỉnh/thành phố Việt Nam"""
    
    # Dữ liệu 63 tỉnh/thành phố theo mã CCCD chính thức
    PROVINCES: Dict[str, Dict[str, str]] = {
        "001": {
            "name": "Hà Nội",
            "region": "Miền Bắc",
            "type": "Thành phố Trung ương",
            "code_old": "01"
        },
        "002": {
            "name": "Hà Giang", 
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "02"
        },
        "004": {
            "name": "Cao Bằng",
            "region": "Miền Bắc", 
            "type": "Tỉnh",
            "code_old": "04"
        },
        "006": {
            "name": "Bắc Kạn",
            "region": "Miền Bắc",
            "type": "Tỉnh", 
            "code_old": "06"
        },
        "008": {
            "name": "Tuyên Quang",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "08"
        },
        "010": {
            "name": "Lào Cai",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "10"
        },
        "011": {
            "name": "Điện Biên",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "11"
        },
        "012": {
            "name": "Lai Châu",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "12"
        },
        "014": {
            "name": "Sơn La",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "14"
        },
        "015": {
            "name": "Yên Bái",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "15"
        },
        "017": {
            "name": "Hoà Bình",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "17"
        },
        "019": {
            "name": "Thái Nguyên",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "19"
        },
        "020": {
            "name": "Lạng Sơn",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "20"
        },
        "022": {
            "name": "Quảng Ninh",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "22"
        },
        "024": {
            "name": "Bắc Giang",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "24"
        },
        "025": {
            "name": "Phú Thọ",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "25"
        },
        "026": {
            "name": "Vĩnh Phúc",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "26"
        },
        "027": {
            "name": "Bắc Ninh",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "27"
        },
        "030": {
            "name": "Hải Dương",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "30"
        },
        "031": {
            "name": "Hải Phòng",
            "region": "Miền Bắc",
            "type": "Thành phố Trung ương",
            "code_old": "31"
        },
        "033": {
            "name": "Hưng Yên",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "33"
        },
        "034": {
            "name": "Thái Bình",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "34"
        },
        "035": {
            "name": "Hà Nam",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "35"
        },
        "036": {
            "name": "Nam Định",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "36"
        },
        "037": {
            "name": "Ninh Bình",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "37"
        },
        "038": {
            "name": "Thanh Hóa",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "38"
        },
        "040": {
            "name": "Nghệ An",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "40"
        },
        "042": {
            "name": "Hà Tĩnh",
            "region": "Miền Bắc",
            "type": "Tỉnh",
            "code_old": "42"
        },
        "044": {
            "name": "Quảng Bình",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "44"
        },
        "045": {
            "name": "Quảng Trị",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "45"
        },
        "046": {
            "name": "Thừa Thiên Huế",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "46"
        },
        "048": {
            "name": "Đà Nẵng",
            "region": "Miền Trung",
            "type": "Thành phố Trung ương",
            "code_old": "48"
        },
        "049": {
            "name": "Quảng Nam",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "49"
        },
        "051": {
            "name": "Quảng Ngãi",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "51"
        },
        "052": {
            "name": "Bình Định",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "52"
        },
        "054": {
            "name": "Phú Yên",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "54"
        },
        "056": {
            "name": "Khánh Hòa",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "56"
        },
        "058": {
            "name": "Ninh Thuận",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "58"
        },
        "060": {
            "name": "Bình Thuận",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "60"
        },
        "062": {
            "name": "Kon Tum",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "62"
        },
        "064": {
            "name": "Gia Lai",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "64"
        },
        "066": {
            "name": "Đắk Lắk",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "66"
        },
        "067": {
            "name": "Đắk Nông",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "67"
        },
        "068": {
            "name": "Lâm Đồng",
            "region": "Miền Trung",
            "type": "Tỉnh",
            "code_old": "68"
        },
        "070": {
            "name": "Bình Phước",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "70"
        },
        "072": {
            "name": "Tây Ninh",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "72"
        },
        "074": {
            "name": "Bình Dương",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "74"
        },
        "075": {
            "name": "Đồng Nai",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "75"
        },
        "077": {
            "name": "Bà Rịa - Vũng Tàu",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "77"
        },
        "079": {
            "name": "Thành phố Hồ Chí Minh",
            "region": "Miền Nam",
            "type": "Thành phố Trung ương",
            "code_old": "79"
        },
        "080": {
            "name": "Long An",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "80"
        },
        "082": {
            "name": "Tiền Giang",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "82"
        },
        "083": {
            "name": "Bến Tre",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "83"
        },
        "084": {
            "name": "Trà Vinh",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "84"
        },
        "086": {
            "name": "Vĩnh Long",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "86"
        },
        "087": {
            "name": "Đồng Tháp",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "87"
        },
        "089": {
            "name": "An Giang",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "89"
        },
        "091": {
            "name": "Kiên Giang",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "91"
        },
        "092": {
            "name": "Cần Thơ",
            "region": "Miền Nam",
            "type": "Thành phố Trung ương",
            "code_old": "92"
        },
        "093": {
            "name": "Hậu Giang",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "93"
        },
        "094": {
            "name": "Sóc Trăng",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "94"
        },
        "095": {
            "name": "Bạc Liêu",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "95"
        },
        "096": {
            "name": "Cà Mau",
            "region": "Miền Nam",
            "type": "Tỉnh",
            "code_old": "96"
        }
    }
    
    @classmethod
    def get_all_provinces(cls) -> Dict[str, Dict[str, str]]:
        """Lấy tất cả thông tin tỉnh/thành phố"""
        return cls.PROVINCES.copy()
    
    @classmethod
    def get_province_codes(cls) -> List[str]:
        """Lấy danh sách mã tỉnh/thành phố"""
        return list(cls.PROVINCES.keys())
    
    @classmethod
    def get_province_names(cls) -> List[str]:
        """Lấy danh sách tên tỉnh/thành phố"""
        return [info["name"] for info in cls.PROVINCES.values()]
    
    @classmethod
    def get_provinces_by_region(cls, region: str) -> Dict[str, Dict[str, str]]:
        """Lấy danh sách tỉnh/thành phố theo vùng miền"""
        return {
            code: info for code, info in cls.PROVINCES.items() 
            if info["region"] == region
        }
    
    @classmethod
    def get_provinces_by_type(cls, province_type: str) -> Dict[str, Dict[str, str]]:
        """Lấy danh sách tỉnh/thành phố theo loại"""
        return {
            code: info for code, info in cls.PROVINCES.items() 
            if info["type"] == province_type
        }
    
    @classmethod
    def get_province_info(cls, code: str) -> Dict[str, str]:
        """Lấy thông tin chi tiết của một tỉnh/thành phố"""
        return cls.PROVINCES.get(code, {})
    
    @classmethod
    def get_province_name(cls, code: str) -> str:
        """Lấy tên tỉnh/thành phố theo mã"""
        return cls.PROVINCES.get(code, {}).get("name", "Không xác định")
    
    @classmethod
    def search_provinces(cls, keyword: str) -> Dict[str, Dict[str, str]]:
        """Tìm kiếm tỉnh/thành phố theo từ khóa"""
        keyword = keyword.lower()
        return {
            code: info for code, info in cls.PROVINCES.items()
            if keyword in info["name"].lower()
        }
    
    @classmethod
    def get_region_statistics(cls) -> Dict[str, int]:
        """Lấy thống kê số lượng tỉnh/thành phố theo vùng miền"""
        stats = {}
        for info in cls.PROVINCES.values():
            region = info["region"]
            stats[region] = stats.get(region, 0) + 1
        return stats
    
    @classmethod
    def get_type_statistics(cls) -> Dict[str, int]:
        """Lấy thống kê số lượng tỉnh/thành phố theo loại"""
        stats = {}
        for info in cls.PROVINCES.values():
            province_type = info["type"]
            stats[province_type] = stats.get(province_type, 0) + 1
        return stats
    
    @classmethod
    def validate_province_code(cls, code: str) -> bool:
        """Kiểm tra tính hợp lệ của mã tỉnh/thành phố"""
        return code in cls.PROVINCES
    
    @classmethod
    def get_dropdown_options(cls) -> List[Tuple[str, str]]:
        """Lấy danh sách options cho dropdown (code, name)"""
        return [(code, info["name"]) for code, info in cls.PROVINCES.items()]
    
    @classmethod
    def get_autocomplete_data(cls) -> List[Dict[str, str]]:
        """Lấy dữ liệu cho autocomplete"""
        return [
            {
                "code": code,
                "name": info["name"],
                "region": info["region"],
                "type": info["type"],
                "display": f"{code} - {info['name']} ({info['region']})"
            }
            for code, info in cls.PROVINCES.items()
        ]


# Test functions
if __name__ == "__main__":
    # Test các chức năng
    print("=== Test Province Data ===")
    
    # Test lấy tất cả tỉnh/thành phố
    all_provinces = ProvinceData.get_all_provinces()
    print(f"Tổng số tỉnh/thành phố: {len(all_provinces)}")
    
    # Test lấy theo vùng miền
    northern_provinces = ProvinceData.get_provinces_by_region("Miền Bắc")
    print(f"Số tỉnh/thành phố miền Bắc: {len(northern_provinces)}")
    
    # Test lấy theo loại
    cities = ProvinceData.get_provinces_by_type("Thành phố Trung ương")
    print(f"Số thành phố trung ương: {len(cities)}")
    
    # Test tìm kiếm
    search_results = ProvinceData.search_provinces("Hà")
    print(f"Tìm thấy {len(search_results)} tỉnh/thành phố có chứa 'Hà'")
    
    # Test thống kê
    region_stats = ProvinceData.get_region_statistics()
    print("Thống kê theo vùng miền:", region_stats)
    
    # Test dropdown options
    dropdown_options = ProvinceData.get_dropdown_options()
    print(f"Dropdown options: {len(dropdown_options)} items")
    print("Ví dụ:", dropdown_options[:3])