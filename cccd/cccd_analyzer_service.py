from __future__ import annotations

from datetime import date
from typing import Dict, Any, List

from .cccd_config import CCCDConfig
from .province_data import ProvinceData
from .checksum import is_checksum_valid


class CCCDAnalyzerService:
    """Phân tích cấu trúc và ý nghĩa của số CCCD Việt Nam (Python).

    Port từ phiên bản JavaScript sang Python để thống nhất ngôn ngữ.
    """

    def __init__(self) -> None:
        self.provinces: Dict[str, Dict[str, str]] = ProvinceData.get_all_provinces()
        self.genderCenturyCodes: Dict[int, Dict[str, Any]] = CCCDConfig.getGenderCenturyCodes()

    def validateCccdFormat(self, cccd: str) -> Dict[str, Any]:
        if not cccd:
            return {"valid": False, "error": "CCCD không được để trống"}

        if not cccd.isdigit():
            return {"valid": False, "error": "CCCD chỉ được chứa chữ số"}

        if len(cccd) != 12:
            return {"valid": False, "error": "CCCD phải có đúng 12 chữ số"}

        if not is_checksum_valid(cccd):
            return {"valid": False, "error": "CCCD có checksum không hợp lệ"}

        return {"valid": True, "error": None}

    def analyzeCccdStructure(self, cccd: str, detailed: bool = True, location: bool = True) -> Dict[str, Any]:
        format_check = self.validateCccdFormat(cccd)
        if not format_check["valid"]:
            return {"valid": False, "error": format_check["error"], "structure": None}

        province_code = cccd[0:3]
        gender_century_code = int(cccd[3:4])
        birth_year_code = cccd[4:6]
        # Các mã tháng và ngày không được sử dụng trực tiếp trong phiên bản mới
        # birth_month_code = cccd[6:8]
        # birth_day_code = cccd[8:10]
        sequence_code = cccd[10:12]

        structure = {
            "province": self._analyzeProvince(province_code),
            "genderCentury": self._analyzeGenderCentury(gender_century_code),
            "birthDate": self._analyzeBirthDate(birth_year_code, cccd[6:8], cccd[8:10], gender_century_code),
            "sequence": self._analyzeSequence(sequence_code),
        }

        analysis: Dict[str, Any] = {
            "cccd": cccd,
            "valid": True,
            "structure": structure,
            "summary": {},
            "validation": {},
        }

        analysis["summary"] = self._createSummary(structure)
        analysis["validation"] = self._validateCccd(structure)
        analysis["valid"] = analysis["validation"]["overallValid"]

        if detailed:
            analysis["detailedAnalysis"] = self._createDetailedAnalysis(structure)

        if location:
            analysis["locationInfo"] = self._createLocationInfo(structure["province"])

        return analysis

    def _analyzeProvince(self, province_code: str) -> Dict[str, Any]:
        province_info = ProvinceData.get_province_info(province_code)
        is_valid = bool(province_info)
        return {
            "code": province_code,
            "name": province_info.get("name", "Không xác định"),
            "valid": is_valid,
            "description": "Mã tỉnh/thành phố nơi đăng ký khai sinh",
            "region": province_info.get("region", "Không xác định"),
            "type": province_info.get("type", "Không xác định"),
        }

    def _analyzeGenderCentury(self, gender_century_code: int) -> Dict[str, Any]:
        gender_info = self.genderCenturyCodes.get(
            gender_century_code,
            {"gender": "Không xác định", "century": None, "description": "Mã không hợp lệ"},
        )
        return {
            "code": gender_century_code,
            "gender": gender_info.get("gender"),
            "century": gender_info.get("century"),
            "valid": gender_century_code in self.genderCenturyCodes,
            "description": gender_info.get("description"),
        }

    def _analyzeBirthDate(self, year_code: str, month_code: str, day_code: str, gender_century_code: int) -> Dict[str, Any]:
        year = int(year_code)
        month = int(month_code)
        day = int(day_code)

        gender_info = self.genderCenturyCodes.get(gender_century_code, {})
        century = gender_info.get("century")

        full_year = -1
        if century:
            full_year = (century - 1) * 100 + year

        is_valid_date = self._validateDate(full_year, month, day) if century else False
        current_age = self._calculateAge(full_year, month, day) if is_valid_date else -1

        return {
            "yearCode": year_code,
            "monthCode": month_code,
            "dayCode": day_code,
            "fullYear": full_year if is_valid_date else None,
            "month": month,
            "day": day,
            "formattedDate": f"{day:02d}/{month:02d}/{full_year}" if is_valid_date else "Invalid Date",
            "valid": is_valid_date,
            "currentAge": current_age,
            "description": f"Ngày sinh: {day:02d}/{month:02d}/{full_year}" if is_valid_date else "Ngày sinh không hợp lệ",
        }

    def _analyzeSequence(self, sequence_code: str) -> Dict[str, Any]:
        try:
            sequence_num = int(sequence_code)
        except ValueError:
            sequence_num = None
        return {
            "code": sequence_code,
            "number": sequence_num,
            "valid": True,
            "description": "Số thứ tự ngẫu nhiên để đảm bảo tính duy nhất",
        }

    def _validateDate(self, year: int, month: int, day: int) -> bool:
        if not (CCCDConfig.MIN_BIRTH_YEAR <= year <= CCCDConfig.MAX_BIRTH_YEAR):
            return False
        try:
            date(year, month, day)
            return True
        except ValueError:
            return False

    def _calculateAge(self, birth_year: int, birth_month: int, birth_day: int) -> int:
        today = date.today()
        age = today.year - birth_year
        if (today.month, today.day) < (birth_month, birth_day):
            age -= 1
        return max(0, age)

    def _createSummary(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        province = structure["province"]
        gender_century = structure["genderCentury"]
        birth_date = structure["birthDate"]
        
        if not birth_date["valid"]:
            return {
                "error": "Không thể tạo tóm tắt do ngày sinh không hợp lệ."
            }

        return {
            "provinceName": province["name"],
            "gender": gender_century["gender"],
            "birthDate": birth_date["formattedDate"],
            "currentAge": birth_date["currentAge"],
            "description": f"{gender_century.get('gender', '')} sinh ngày {birth_date['formattedDate']} tại {province['name']}, hiện {birth_date['currentAge']} tuổi",
        }

    def _validateGenderCenturyConsistency(self, gender_century_code: int, birth_year: int) -> bool:
        """Kiểm tra mã gender-century có khớp với năm sinh."""
        if not (CCCDConfig.MIN_BIRTH_YEAR <= birth_year <= CCCDConfig.MAX_BIRTH_YEAR):
            return False
            
        century = (birth_year // 100) + 1
        
        # This logic is derived from CCCDGeneratorService._get_gender_century_code
        expected_base_code = (century - 20) * 2
        
        # Nam (even code)
        if gender_century_code % 2 == 0:
            return gender_century_code == expected_base_code
        # Nữ (odd code)
        else:
            return gender_century_code == expected_base_code + 1

    def _validateCccd(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        province_valid = structure["province"]["valid"]
        gender_century_valid = structure["genderCentury"]["valid"]
        birth_date_valid = structure["birthDate"]["valid"]
        sequence_valid = structure["sequence"]["valid"]

        # New validation for gender-century consistency
        gender_century_code = structure["genderCentury"]["code"]
        birth_year = structure["birthDate"]["fullYear"]
        
        gender_century_consistent = False
        if birth_year:
             gender_century_consistent = self._validateGenderCenturyConsistency(gender_century_code, birth_year)

        # Checksum is validated in `analyzeCccdStructure` via `validateCccdFormat`,
        # so we don't need to re-check it here, but we should reflect it in the score.
        
        all_validations = [
            province_valid, 
            gender_century_valid, 
            birth_date_valid, 
            sequence_valid,
            gender_century_consistent
        ]
        
        overall_valid = all(all_validations)
        
        validation_score = (sum(all_validations) / len(all_validations)) * 100

        return {
            "provinceValid": province_valid,
            "genderCenturyValid": gender_century_valid,
            "birthDateValid": birth_date_valid,
            "sequenceValid": sequence_valid,
            "genderCenturyConsistent": gender_century_consistent, # Added field
            "overallValid": overall_valid,
            "validationScore": validation_score,
        }

    def _createDetailedAnalysis(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "legalBasis": CCCDConfig.getLegalBasis(),
            "structureBreakdown": CCCDConfig.getStructureBreakdown(),
            "accuracyNotes": [
                "Cấu trúc tuân thủ quy định pháp luật",
                "Mã tỉnh được xác thực theo bảng mã chính thức của Bộ Công an",
                "Mã giới tính và thế kỷ đúng theo quy tắc",
                "Ngày sinh được kiểm tra tính hợp lệ (bao gồm năm nhuận)",
            ],
        }

    def _createLocationInfo(self, province_info: Dict[str, Any]) -> Dict[str, Any]:
        if not province_info["valid"]:
            return {"error": "Mã tỉnh không hợp lệ"}
        return {
            "provinceCode": province_info["code"],
            "provinceName": province_info["name"],
            "region": province_info.get("region", "Không xác định"),
            "description": f"Tỉnh/thành phố {province_info['name']} - nơi đăng ký khai sinh",
        }

    def _getRegionByProvince(self, province_code: str) -> str:
        # This method is now redundant as region is part of _analyzeProvince
        province_info = ProvinceData.get_province_info(province_code)
        return province_info.get("region", "Không xác định")

    def batchAnalyze(self, cccd_list: List[str]) -> Dict[str, Any]:
        input_validation = CCCDConfig.validateInputLimit("batch_analysis", len(cccd_list))
        if not input_validation["valid"]:
            return {
                "error": input_validation["error"],
                "maxLimit": input_validation["maxLimit"],
                "requested": input_validation["requested"],
            }

        limited_list = cccd_list[: input_validation["maxLimit"]]

        results: List[Dict[str, Any]] = []
        valid_count = 0
        invalid_count = 0

        for cccd in limited_list:
            analysis = self.analyzeCccdStructure(cccd, detailed=False, location=False)
            results.append(analysis)
            if analysis["valid"]:
                valid_count += 1
            else:
                invalid_count += 1

        output_validation = CCCDConfig.validateOutputLimit("max_results_per_request", len(results))
        if not output_validation["valid"]:
            # This logic needs to re-calculate counts if truncated
            results = results[: output_validation["maxLimit"]]
            valid_count = sum(1 for r in results if r.get("valid"))
            invalid_count = len(results) - valid_count

        return {
            "totalAnalyzed": len(limited_list),
            "validCount": valid_count,
            "invalidCount": invalid_count,
            "validityRate": (valid_count / len(limited_list) * 100) if limited_list else 0,
            "results": results,
            "limits": {
                "inputLimit": input_validation["maxLimit"],
                "outputLimit": output_validation["maxLimit"],
                "truncated": len(cccd_list) > input_validation["maxLimit"] or len(results) > output_validation["maxLimit"],
            },
            "summary": {
                "mostCommonProvince": self._getMostCommonProvince(results),
                "ageDistribution": self._getAgeDistribution(results),
                "genderDistribution": self._getGenderDistribution(results),
            },
        }

    def _getMostCommonProvince(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        province_count: Dict[str, int] = {}
        for result in results:
            if result.get("valid"):
                province = result.get("structure", {}).get("province", {}).get("name")
                if province and province != "Không xác định":
                    province_count[province] = province_count.get(province, 0) + 1
        if not province_count:
            return {"name": "Không có", "count": 0}
        most_common = max(province_count.items(), key=lambda item: item[1])
        return {"name": most_common[0], "count": most_common[1]}

    def _getAgeDistribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        age_groups: Dict[str, int] = {"0-17": 0, "18-30": 0, "31-45": 0, "46-60": 0, "61+": 0}
        for result in results:
            if result.get("valid"):
                age = result.get("summary", {}).get("currentAge")
                if age is not None and isinstance(age, int):
                    if age <= 17:
                        age_groups["0-17"] += 1
                    elif age <= 30:
                        age_groups["18-30"] += 1
                    elif age <= 45:
                        age_groups["31-45"] += 1
                    elif age <= 60:
                        age_groups["46-60"] += 1
                    else:
                        age_groups["61+"] += 1
        return age_groups

    def _getGenderDistribution(self, results: List[Dict[str, Any]]) -> Dict[str, int]:
        gender_count: Dict[str, int] = {"Nam": 0, "Nữ": 0}
        for result in results:
            if result.get("valid"):
                gender = result.get("summary", {}).get("gender")
                if gender in gender_count:
                    gender_count[gender] += 1
        return gender_count
