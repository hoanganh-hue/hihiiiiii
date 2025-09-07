
import unittest
from .cccd_config import CCCDConfig
from .cccd_generator_service import CCCDGeneratorService
from .cccd_analyzer_service import CCCDAnalyzerService

class TestCCCDRefactor(unittest.TestCase):
    """
    Kiểm thử các nâng cấp và tái cấu trúc cho module CCCD.
    Bao gồm unit test cho config và integration test cho luồng tạo và phân tích.
    """

    def setUp(self):
        """Khởi tạo các service cần thiết cho mỗi bài test."""
        self.config = CCCDConfig()
        self.generator = CCCDGeneratorService()
        self.analyzer = CCCDAnalyzerService()

    def test_gender_century_codes_completeness(self):
        """
        [Unit Test] Đảm bảo getGenderCenturyCodes() có đủ 10 mã từ 0-9.
        """
        codes = self.config.getGenderCenturyCodes()
        self.assertEqual(len(codes), 10)
        for i in range(10):
            self.assertIn(i, codes)

    def test_gender_century_codes_logic(self):
        """
        [Unit Test] Kiểm tra logic Nam=Chẵn, Nữ=Lẻ trong config.
        """
        codes = self.config.getGenderCenturyCodes()
        for code, info in codes.items():
            if code % 2 == 0:
                self.assertEqual(info['gender'], "Nam", f"Mã {code} phải là Nam")
            else:
                self.assertEqual(info['gender'], "Nữ", f"Mã {code} phải là Nữ")

    def test_full_flow_generator_to_analyzer(self):
        """
        [Integration Test] Kiểm tra luồng từ tạo CCCD đến phân tích.
        Sử dụng một năm sinh trong tương lai (thế kỷ 22) để xác thực logic động.
        """
        # --- Tham số đầu vào ---
        test_province_code = "049"  # Quảng Nam
        test_gender = "Nữ"
        test_birth_year = 2150

        # --- Giai đoạn 1: Tạo CCCD ---
        generated_data_list = self.generator.generateCccdList(
            provinceCodes=[test_province_code],
            gender=test_gender,
            birthYearRange=[test_birth_year, test_birth_year],
            quantity=1
        )
        self.assertEqual(len(generated_data_list), 1)
        generated_data = generated_data_list[0]
        generated_cccd = generated_data['cccd_number']

        # --- Giai đoạn 2: Phân tích CCCD vừa tạo ---
        analysis_result = self.analyzer.analyzeCccdStructure(generated_cccd)

        # --- Giai đoạn 3: Xác thực kết quả ---
        self.assertTrue(analysis_result['valid'], "CCCD được tạo ra phải hợp lệ")

        # Lấy thông tin đã phân tích
        structure = analysis_result['structure']
        summary = analysis_result['summary']

        # 3.1: Xác thực thông tin tỉnh
        self.assertEqual(structure['province']['code'], test_province_code)
        self.assertEqual(structure['province']['name'], "Quảng Nam")
        self.assertEqual(summary['provinceName'], "Quảng Nam")

        # 3.2: Xác thực thông tin giới tính và thế kỷ
        # Thế kỷ 22 (2100-2199), Nữ -> mã phải là 5
        self.assertEqual(structure['genderCentury']['code'], 5)
        self.assertEqual(structure['genderCentury']['gender'], test_gender)
        self.assertEqual(structure['genderCentury']['century'], 22)
        self.assertEqual(summary['gender'], test_gender)

        # 3.3: Xác thực thông tin ngày sinh
        self.assertEqual(structure['birthDate']['fullYear'], test_birth_year)
        self.assertEqual(summary['birthDate'], f"{generated_data['birth_day']:02d}/{generated_data['birth_month']:02d}/{test_birth_year}")

        print("\n--- Integration Test Passed ---")
        print(f"Generated CCCD: {generated_cccd}")
        print(f"Analyzed Summary: {summary['description']}")
        print("-----------------------------")

if __name__ == '__main__':
    unittest.main()
