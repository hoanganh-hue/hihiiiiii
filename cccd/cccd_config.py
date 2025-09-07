import os
from pathlib import Path
from typing import Dict, List, Any


class CCCDConfig:
    """Cấu hình cho module phân tích và tạo CCCD (Python).

    Port từ phiên bản JavaScript sang Python để thống nhất ngôn ngữ.
    """

    # Cấu hình cơ bản
    DEFAULT_QUANTITY_LIMIT: int = 100
    MAX_QUANTITY_LIMIT: int = 100000  # Tăng giới hạn lên 100,000
    MIN_BIRTH_YEAR: int = 1900
    MAX_BIRTH_YEAR: int = 2399 # Hỗ trợ đến hết thế kỷ 24

    # Cấu hình giới hạn số lượng CCCD (đã tăng giới hạn)
    INPUT_LIMITS: Dict[str, int] = {
        "single_analysis": 1,          # Phân tích đơn lẻ
        "batch_analysis": 1000,        # Phân tích hàng loạt (tăng từ 50)
        "generation_single": 10000,    # Tạo đơn lẻ (tăng từ 100)
        "generation_batch": 50000,     # Tạo hàng loạt (tăng từ 500)
        "verification_single": 1,      # Xác minh đơn lẻ
        "verification_batch": 1000,    # Xác minh hàng loạt (tăng từ 20)
    }

    OUTPUT_LIMITS: Dict[str, int] = {
        "max_results_per_request": 100000,  # Tối đa kết quả trả về (tăng từ 1000)
        "max_export_records": 100000,      # Tối đa bản ghi xuất file (tăng từ 10000)
        "max_cache_entries": 10000,        # Tối đa bản ghi cache (tăng từ 1000)
        "max_log_entries": 50000,          # Tối đa bản ghi log (tăng từ 5000)
    }

    # Cấu hình API (tham chiếu, không dùng trực tiếp trong Python module này)
    API_ENDPOINTS: Dict[str, str] = {
        "analyze": "/api/analyze-cccd",
        "generate": "/api/generate-cccd",
        "generate_legacy": "/api/generate/cccd",
        "options": "/api/generate/cccd/interactive",
    }

    # Cấu hình validation
    VALIDATION_RULES: Dict[str, int] = {
        "cccd_length": 12,
        "province_code_length": 3,
        "gender_century_code_length": 1,
        "birth_year_code_length": 2,
        "birth_month_code_length": 2,
        "birth_day_code_length": 2,
        "sequence_code_length": 2,
    }

    # Cấu hình file export
    EXPORT_CONFIG: Dict[str, Any] = {
        "allowed_formats": ["json", "csv", "xlsx", "txt"],
        "default_format": "json",
        "max_file_size_mb": 10,
        "output_directory": "output/cccd",
    }

    # Cấu hình logging
    LOGGING_CONFIG: Dict[str, Any] = {
        "log_level": "INFO",
        "log_file": "logs/cccd_analysis.log",
        "max_log_size_mb": 10,
        "backup_count": 5,
    }

    # Cấu hình cache
    CACHE_CONFIG: Dict[str, Any] = {
        "enabled": True,
        "ttl_seconds": 3600,  # 1 hour
        "max_entries": 1000,
    }

    # Cấu hình bảo mật
    SECURITY_CONFIG: Dict[str, Any] = {
        "rate_limit_per_minute": 60,
        "max_requests_per_hour": 1000,
        "allowed_origins": ["*"],
        "require_auth": True,
    }

    # Cấu hình database (nếu có)
    DATABASE_CONFIG: Dict[str, Any] = {
        "enabled": False,
        "connection_string": "",
        "table_name": "cccd_analysis_log",
        "batch_size": 100,
    }

    @staticmethod
    def getProvinceCodes() -> Dict[str, str]:
        """Lấy danh sách mã tỉnh thành.
        
        @deprecated Sẽ được thay thế bởi province_data.py để tập trung hóa dữ liệu.
        """
        return {
            "001": "Hà Nội", "002": "Hà Giang", "004": "Cao Bằng", "006": "Bắc Kạn",
            "008": "Tuyên Quang", "010": "Lào Cai", "011": "Điện Biên", "012": "Lai Châu",
            "014": "Sơn La", "015": "Yên Bái", "017": "Hoà Bình", "019": "Thái Nguyên",
            "020": "Lạng Sơn", "022": "Quảng Ninh", "024": "Bắc Giang", "025": "Phú Thọ",
            "026": "Vĩnh Phúc", "027": "Bắc Ninh", "030": "Hải Dương", "031": "Hải Phòng",
            "033": "Hưng Yên", "034": "Thái Bình", "035": "Hà Nam", "036": "Nam Định",
            "037": "Ninh Bình", "038": "Thanh Hóa", "040": "Nghệ An", "042": "Hà Tĩnh",
            "044": "Quảng Bình", "045": "Quảng Trị", "046": "Thừa Thiên Huế",
            "048": "Đà Nẵng", "049": "Quảng Nam", "051": "Quảng Ngãi", "052": "Bình Định",
            "054": "Phú Yên", "056": "Khánh Hòa", "058": "Ninh Thuận", "060": "Bình Thuận",
            "062": "Kon Tum", "064": "Gia Lai", "066": "Đắk Lắk", "067": "Đắk Nông",
            "068": "Lâm Đồng", "070": "Bình Phước", "072": "Tây Ninh", "074": "Bình Dương",
            "075": "Đồng Nai", "077": "Bà Rịa - Vũng Tàu", "079": "Thành phố Hồ Chí Minh",
            "080": "Long An", "082": "Tiền Giang", "083": "Bến Tre", "084": "Trà Vinh",
            "086": "Vĩnh Long", "087": "Đồng Tháp", "089": "An Giang", "091": "Kiên Giang",
            "092": "Cần Thơ", "093": "Hậu Giang", "094": "Sóc Trăng", "095": "Bạc Liêu",
            "096": "Cà Mau",
        }

    @staticmethod
    def getGenderCenturyCodes() -> Dict[int, Dict[str, Any]]:
        """
        Lấy mã giới tính và thế kỷ - ĐÃ SỬA THEO QUY ĐỊNH CHÍNH THỨC
        Quy tắc: Nam = Số chẵn, Nữ = Số lẻ
        """
        return {
            0: {"gender": "Nam", "century": 20, "description": "Nam, sinh thế kỷ 20 (1900-1999)"},
            1: {"gender": "Nữ", "century": 20, "description": "Nữ, sinh thế kỷ 20 (1900-1999)"},
            2: {"gender": "Nam", "century": 21, "description": "Nam, sinh thế kỷ 21 (2000-2099)"},
            3: {"gender": "Nữ", "century": 21, "description": "Nữ, sinh thế kỷ 21 (2000-2099)"},
            4: {"gender": "Nam", "century": 22, "description": "Nam, sinh thế kỷ 22 (2100-2199)"},
            5: {"gender": "Nữ", "century": 22, "description": "Nữ, sinh thế kỷ 22 (2100-2199)"},
            6: {"gender": "Nam", "century": 23, "description": "Nam, sinh thế kỷ 23 (2200-2299)"},
            7: {"gender": "Nữ", "century": 23, "description": "Nữ, sinh thế kỷ 23 (2200-2299)"},
            8: {"gender": "Nam", "century": 24, "description": "Nam, sinh thế kỷ 24 (2300-2399)"},
            9: {"gender": "Nữ", "century": 24, "description": "Nữ, sinh thế kỷ 24 (2300-2399)"},
        }

    @staticmethod
    def getRegionMapping() -> Dict[str, List[str]]:
        """Lấy mapping vùng miền theo mã tỉnh.
        
        @deprecated Sẽ được thay thế bởi province_data.py để tập trung hóa dữ liệu.
        """
        return {
            "Miền Bắc": [
                "001", "002", "004", "006", "008", "010", "011", "012", "014", "015",
                "017", "019", "020", "022", "024", "025", "026", "027", "030", "031",
                "033", "034", "035", "036", "037", "038", "040", "042",
            ],
            "Miền Trung": [
                "044", "045", "046", "048", "049", "051", "052", "054", "056", "058",
                "060", "062", "064", "066", "067", "068",
            ],
            "Miền Nam": [
                "070", "072", "074", "075", "077", "079", "080", "082", "083", "084",
                "086", "087", "089", "091", "092", "093", "094", "095", "096",
            ],
        }

    @staticmethod
    def getLegalBasis() -> Dict[str, str]:
        """Lấy cơ sở pháp lý."""
        return {
            "decree": "Nghị định số 137/2015/NĐ-CP",
            "circular": "Thông tư số 07/2016/TT-BCA",
            "description": "Quy định về số định danh cá nhân và cấu trúc CCCD",
            "effective_date": "01/01/2016",
        }

    @staticmethod
    def getStructureBreakdown() -> Dict[str, str]:
        """Lấy mô tả cấu trúc CCCD."""
        return {
            "positions_1_3": "Mã tỉnh/thành phố nơi đăng ký khai sinh",
            "position_4": "Mã thế kỷ và giới tính",
            "positions_5_6": "Hai số cuối của năm sinh",
            "positions_7_8": "Tháng sinh (MM)",
            "positions_9_10": "Ngày sinh (DD)",
            "positions_11_12": "Số thứ tự ngẫu nhiên",
        }

    @staticmethod
    def validateConfig() -> Dict[str, Any]:
        """Validate cấu hình, tạo thư mục cần thiết nếu thiếu."""
        validation_result: Dict[str, Any] = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Kiểm tra output directory
        output_dir = Path(CCCDConfig.EXPORT_CONFIG["output_directory"]).expanduser()
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
                validation_result["warnings"].append(f"Created output directory: {output_dir}")
            except Exception as exc:  # noqa: BLE001 - keep broad for config validation
                validation_result["valid"] = False
                validation_result["errors"].append(f"Cannot create output directory: {exc}")

        # Kiểm tra log directory
        log_file = Path(CCCDConfig.LOGGING_CONFIG["log_file"]).expanduser()
        log_dir = log_file.parent
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                validation_result["warnings"].append(f"Created log directory: {log_dir}")
            except Exception as exc:  # noqa: BLE001
                validation_result["valid"] = False
                validation_result["errors"].append(f"Cannot create log directory: {exc}")

        # Kiểm tra giới hạn
        if CCCDConfig.DEFAULT_QUANTITY_LIMIT > CCCDConfig.MAX_QUANTITY_LIMIT:
            validation_result["valid"] = False
            validation_result["errors"].append(
                "Default quantity limit cannot be greater than max limit",
            )

        if CCCDConfig.MIN_BIRTH_YEAR >= CCCDConfig.MAX_BIRTH_YEAR:
            validation_result["valid"] = False
            validation_result["errors"].append(
                "Min birth year must be less than max birth year",
            )

        return validation_result

    @staticmethod
    def getInputLimits() -> Dict[str, int]:
        """Lấy giới hạn đầu vào."""
        return CCCDConfig.INPUT_LIMITS.copy()

    @staticmethod
    def getOutputLimits() -> Dict[str, int]:
        """Lấy giới hạn đầu ra."""
        return CCCDConfig.OUTPUT_LIMITS.copy()

    @staticmethod
    def validateInputLimit(operationType: str, count: int) -> Dict[str, Any]:
        """Validate giới hạn đầu vào."""
        limits = CCCDConfig.getInputLimits()
        max_limit = limits[operationType] if operationType in limits else 1

        if count > max_limit:
            return {
                "valid": False,
                "error": f"Số lượng vượt quá giới hạn cho phép. Tối đa: {max_limit}",
                "maxLimit": max_limit,
                "requested": count,
            }

        return {
            "valid": True,
            "maxLimit": max_limit,
            "requested": count,
        }

    @staticmethod
    def validateOutputLimit(outputType: str, count: int) -> Dict[str, Any]:
        """Validate giới hạn đầu ra."""
        limits = CCCDConfig.getOutputLimits()
        max_limit = limits[outputType] if outputType in limits else 1000

        if count > max_limit:
            return {
                "valid": False,
                "error": f"Số lượng kết quả vượt quá giới hạn. Tối đa: {max_limit}",
                "maxLimit": max_limit,
                "requested": count,
            }

        return {
            "valid": True,
            "maxLimit": max_limit,
            "requested": count,
        }

    @staticmethod
    def getConfigSummary() -> Dict[str, Any]:
        """Lấy tóm tắt cấu hình."""
        return {
            "module": "CCCD Analysis & Generation",
            "version": "1.0.0",
            "totalProvinces": len(CCCDConfig.getProvinceCodes().keys()),
            "quantityLimits": {
                "default": CCCDConfig.DEFAULT_QUANTITY_LIMIT,
                "max": CCCDConfig.MAX_QUANTITY_LIMIT,
            },
            "birthYearRange": {
                "min": CCCDConfig.MIN_BIRTH_YEAR,
                "max": CCCDConfig.MAX_BIRTH_YEAR,
            },
            "inputLimits": CCCDConfig.getInputLimits(),
            "outputLimits": CCCDConfig.getOutputLimits(),
            "features": {
                "analysis": True,
                "generation": True,
                "validation": True,
                "export": True,
                "caching": CCCDConfig.CACHE_CONFIG["enabled"],
                "database": CCCDConfig.DATABASE_CONFIG["enabled"],
            },
            "apiEndpoints": list(CCCDConfig.API_ENDPOINTS.values()),
            "legalCompliance": CCCDConfig.getLegalBasis(),
        }
