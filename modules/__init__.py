#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module Wrappers for Integrated CCCD Lookup System

This package provides Python wrappers for JavaScript modules:
- cccd_wrapper: CCCD analysis and generation
- doanh_nghiep_wrapper: Company/business information lookup
- bhxh_wrapper: Social insurance (BHXH) information lookup
"""

from .cccd_wrapper import CCCDWrapper
from .doanh_nghiep_wrapper import DoanhNghiepWrapper
from .bhxh_wrapper import BHXHWrapper

__version__ = "1.0.0"
__author__ = "MiniMax Agent"
__email__ = "agent@minimax.ai"

__all__ = [
    'CCCDWrapper',
    'DoanhNghiepWrapper', 
    'BHXHWrapper'
]

# Module information
MODULE_INFO = {
    "cccd": {
        "name": "CCCD Analyzer & Generator",
        "description": "Phân tích cấu trúc và tạo số Căn cước Công dân Việt Nam",
        "functions": ["generate_cccd_list", "analyze_cccd", "validate_cccd"]
    },
    "doanh_nghiep": {
        "name": "Doanh Nghiep API Client",
        "description": "Tra cứu thông tin doanh nghiệp qua API thongtindoanhnghiep.co",
        "functions": ["get_cities", "search_companies", "get_company_by_mst"]
    },
    "bhxh": {
        "name": "BHXH Lookup Tool",
        "description": "Tra cứu thông tin Bảo hiểm Xã hội với 2captcha",
        "functions": ["lookup_bhxh_info", "test_connection"]
    }
}

def get_module_info():
    """
    Lấy thông tin về các modules
    
    Returns:
        Dict chứa thông tin chi tiết về từng module
    """
    return MODULE_INFO

def print_module_info():
    """
    In thông tin về các modules ra console
    """
    print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃          MODULE WRAPPERS - THÔNG TIN HỆ THỐNG          ┃")
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    
    for module_key, info in MODULE_INFO.items():
        print(f"\n📦 {info['name']}")
        print(f"   {info['description']}")
        print(f"   Functions: {', '.join(info['functions'])}")
    
    print(f"\n🔧 Version: {__version__}")
    print(f"👤 Author: {__author__}")
    print()

if __name__ == "__main__":
    print_module_info()
