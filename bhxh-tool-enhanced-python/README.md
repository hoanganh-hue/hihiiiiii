# Enhanced BHXH Tool v2.0.0 - Python Version

> 🚀 Công cụ tra cứu thông tin BHXH cải tiến với bảo mật, hiệu suất và xử lý lỗi nâng cao

## 📋 Tổng Quan

Enhanced BHXH Tool là phiên bản cải tiến của công cụ tra cứu thông tin Bảo hiểm Xã hội tự động. Công cụ sử dụng API của baohiemxahoi.gov.vn kết hợp với dịch vụ giải CAPTCHA 2captcha để tra cứu thông tin BHXH từ số CCCD/CMND.

### 🎯 Các Cải Tiến Chính

| **Tính Năng** | **Phiên Bản Cũ** | **Phiên Bản Mới** |
|---------------|-------------------|-------------------|
| **Security** | API key trong file text | Environment variables + validation |
| **Performance** | Write Excel per record | Batch writing + memory optimization |
| **Data Collection** | Basic fields only | Complete BHXH data + multiple extraction |
| **Output Format** | Dấu nháy thừa | Clean formatting + standardized dates |
| **Error Handling** | Basic try-catch | Retry + exponential backoff + categorization |
| **Logging** | Console logs | Comprehensive logging với structured logging |
| **Caching** | No caching | Multi-level caching system |
| **Configuration** | Hard-coded values | Environment-based configuration |

## 🔧 Cài Đặt

### 1. Clone và Cài Đặt Dependencies

```bash
cd bhxh-tool-enhanced-python
pip install -r requirements.txt
```

### 2. Cấu Hình Environment Variables

```bash
# Copy template và chỉnh sửa
cp .env.template .env
nano .env
```

**Cấu hình bắt buộc trong `.env`:**

```env
# 2captcha Configuration (BẮT BUỘC)
CAPTCHA_API_KEY=your_2captcha_api_key_here

# Processing Configuration
MAX_CONCURRENT_PROCESSING=5
RETRY_MAX_ATTEMPTS=3
BATCH_WRITE_SIZE=10

# Excel Files
EXCEL_INPUT_FILE=data-input.xlsx
EXCEL_OUTPUT_FILE=data-output.xlsx

# Logging
LOG_LEVEL=info
NODE_ENV=production
```

### 3. Chuẩn Bị Dữ Liệu

**File Excel đầu vào (`data-input.xlsx`)** phải có các cột:

| **Cột** | **Tên** | **Bắt Buộc** | **Định Dạng** |
|---------|----------|---------------|---------------|
| A | Số Điện Thoại | ❌ | Text |
| B | Số CCCD | ✅ | 9-12 chữ số |
| C | Họ và Tên | ✅ | Tiếng Việt có dấu |
| D | Địa Chỉ | ❌ | Text đầy đủ |

**Ví dụ dữ liệu:**

```
Số Điện Thoại | Số CCCD      | Họ và Tên        | Địa Chỉ
0901234567    | 001161041024 | Nguyễn Thị Hồng  | Thôn Cổ Điển, Xã Hải Bối, Huyện Đông Anh, Hà Nội
0907654321    | 024173000048 | Trần Văn Bình    | Phường 1, Quận Tân Bình, TP. Hồ Chí Minh
```

## 🚀 Sử Dụng

### 1. Kiểm Tra Cấu Hình

```bash
# Kiểm tra environment variables
python -c "from config.validate_env import validate_env; validate_env()"

# Chạy diagnostic tests
python main.py --test
```

### 2. Chạy Công Cụ

```bash
# Chạy production
python main.py

# Hoặc chạy trực tiếp, có thể override đường dẫn input/output
python main.py --input ../../data-bhxh-21-6.xlsx --output ./data-output.xlsx

# Chạy với giới hạn số lượng record
python main.py --limit 10
```

### 3. Theo Dõi Progress

Công cụ sẽ hiển thị progress real-time:

```
🚀 Processing Started
📊 Processing 100 records from sheet 'Sheet1'
✅ Validation completed: 98 valid, 2 invalid records
🔄 Processing 98 valid records with 5 concurrent threads
📊 Progress: 25/98 (25%) - ETA: 145s
✅ Record 25 processed successfully - BHXH found
📊 Progress: 50/98 (51%) - ETA: 89s
...
🎉 Processing completed successfully
```

## 📊 Dữ Liệu Đầu Ra

### File Excel Output

File `data-output.xlsx` sẽ chứa các cột:

| **Cột** | **Mô Tả** | **Ví Dụ** |
|----------|------------|-----------|
| Số Điện Thoại | Từ input | `0901234567` |
| Số CCCD | Từ input | `001161041024` |
| Họ và Tên | Từ input | `Nguyễn Thị Hồng` |
| Địa Chỉ | Từ input | `Thôn Cổ Điển, Xã Hải Bối...` |
| Ngày Tháng Năm Sinh | Từ BHXH | `14/05/1974` |
| Mã BHXH | Từ BHXH | `0161041024` |
| Giới Tính | Từ BHXH | `Nữ` |
| Trạng Thái BHXH | Từ BHXH | `Đang tham gia BHXH` |
| Số Kết Quả | Số record tìm thấy | `1` |
| Thời Gian Xử Lý | Duration | `84000ms` |
| Trạng Thái Xử Lý | Success/Failed | `Thành công` |

### Log Files

Log được ghi vào `logs/bhxh-tool.log` với format:

```
[2025-09-05 12:34:56] INFO: 🚀 Processing Started {"totalRecords": 100}
[2025-09-05 12:35:41] INFO: ✓ Record 1 processed successfully {"recordIndex": 0, "cccd": "001***024", "status": "success"}
[2025-09-05 12:36:25] WARN: ⚠ Record 2 failed: CAPTCHA_ERROR {"recordIndex": 1, "cccd": "024***048", "status": "CAPTCHA_ERROR"}
```

## ⚙️ Cấu Hình Nâng Cao

### Environment Variables Đầy Đủ

```env
# 2captcha Configuration
CAPTCHA_API_KEY=your_api_key_here
CAPTCHA_WEBSITE_KEY=6Lcey5QUAAAAADcB0m7xYLj8W8HHi8ur4JQrTCUY
CAPTCHA_WEBSITE_URL=https://baohiemxahoi.gov.vn

# BHXH API Configuration  
BHXH_API_URL=https://baohiemxahoi.gov.vn/UserControls/BHXH/BaoHiemYTe/HienThiHoGiaDinh/pListKoOTP.aspx

# Processing Configuration
MAX_CONCURRENT_PROCESSING=5      # 1-50 threads
RETRY_MAX_ATTEMPTS=3             # Số lần retry
RETRY_BASE_DELAY=2000            # Base delay (ms)
REQUEST_TIMEOUT=30000            # HTTP timeout (ms)

# Excel Configuration
EXCEL_INPUT_FILE=data-input.xlsx
EXCEL_OUTPUT_FILE=data-output.xlsx
BATCH_WRITE_SIZE=10              # Records per batch

# Logging Configuration
LOG_LEVEL=info                   # error, warn, info, debug
LOG_FILE=logs/bhxh-tool.log

# Environment Configuration
NODE_ENV=production              # development, production, test
DEBUG_MODE=false

# Cache Configuration  
CACHE_ENABLED=true
CACHE_TTL=300000                 # 5 minutes in ms
```

### Performance Tuning

| **Tham Số** | **Khuyến Nghị** | **Giải Thích** |
|--------------|-----------------|----------------|
| `MAX_CONCURRENT_PROCESSING` | 3-5 | Quá cao có thể bị rate limit |
| `BATCH_WRITE_SIZE` | 10-20 | Balance giữa memory và I/O |
| `RETRY_MAX_ATTEMPTS` | 3 | Đủ cho network issues |
| `CACHE_TTL` | 300000 (5min) | Cache province mappings |

## 🛠️ Troubleshooting

### Lỗi Thường Gặp

#### 1. CAPTCHA Errors

```bash
❌ CAPTCHA solving failed: Invalid 2captcha API key
```

**Giải pháp:**
- Kiểm tra `CAPTCHA_API_KEY` trong `.env`
- Verify balance tại https://2captcha.com
- Test với: `python -c "import os; print(os.getenv('CAPTCHA_API_KEY'))"`

#### 2. Province Mapping Errors

```bash
❌ Record 5 failed: Không tìm thấy mã tỉnh từ địa chỉ
```

**Giải pháp:**
- Kiểm tra file `tinh-thanh.json` tồn tại
- Đảm bảo địa chỉ chứa tên tỉnh/thành rõ ràng
- Thêm tỉnh vào địa chỉ: `"Huyện ABC, Tỉnh XYZ"`

#### 3. Excel Format Errors

```bash
❌ Input Excel format invalid: Thiếu các cột bắt buộc: Số CCCD, Họ và Tên
```

**Giải pháp:**
- Đảm bảo Excel có header row
- Tên cột phải chính xác: `Số CCCD`, `Họ và Tên`
- Không có dòng trống ở đầu file

#### 4. Network/API Errors

```bash
❌ BHXH query failed: BHXH API timeout
```

**Giải pháp:**
- Kiểm tra kết nối internet
- Tăng `REQUEST_TIMEOUT` trong `.env`
- Giảm `MAX_CONCURRENT_PROCESSING`

### Diagnostic Commands

```bash
# Test configuration
python -c "from config.validate_env import validate_env; validate_env()"

# Test all components
python main.py --test

# Check 2captcha balance
python -c "
import asyncio
from services.captcha_service import get_captcha_service
async def check_balance():
    service = get_captcha_service()
    balance = await service.get_balance()
    print(f'Balance: ${balance}')
asyncio.run(check_balance())
"

# Test province mapping
python -c "
from services.province_service import get_province_service
service = get_province_service()
result = service.test_mapping()
print(f'Success rate: {result[\"success_rate\"]}%')
"
```

## 📈 Monitoring & Statistics

### Real-time Progress

Trong quá trình chạy, công cụ hiển thị:

```
📊 Progress: 45/100 (45%)
✅ Successful: 38 (84%)
❌ Failed: 7 (16%)
⏱️ Avg Time/Record: 82000ms
🎯 ETA: 75 minutes
```

### Final Summary

Khi hoàn thành:

```
🎉 ENHANCED BHXH TOOL - PROCESSING SUMMARY
================================================================================
📊 Records Processed: 100/100
✅ Successful: 87 (87%)
❌ Failed: 13 (13%)
⏱️ Total Duration: 2h 15m 32s
📈 Avg Time/Record: 81000ms

🚨 Error Breakdown:
   CAPTCHA_ERROR: 8
   API_ERROR: 3
   PROVINCE_ERROR: 2

🔐 CAPTCHA Stats:
   Success Rate: 92%
   Avg Solve Time: 75000ms

🌐 BHXH API Stats:
   Success Rate: 89%
   Avg Response Time: 5000ms

📁 Output File: data-output.xlsx
📋 Log File: logs/bhxh-tool.log
================================================================================
```

## 🔒 Security Features

### 1. Environment Variables
- API keys không được hard-code
- Sensitive data được sanitize trong logs
- Input validation & sanitization

### 2. Data Protection
- CCCD numbers bị mask trong logs: `001***024`
- Error messages được sanitize
- Personal data không được cache lâu dài

### 3. Rate Limiting Protection
- Concurrent processing limits
- Exponential backoff retry
- Request timeout configuration

## 🚀 Performance Optimizations

### 1. Batch Processing
- Excel writes theo batch thay vì per-record
- Memory-efficient data processing
- Concurrent processing với asyncio

### 2. Intelligent Caching
- Province mappings được cache
- BHXH results cache (short-term)
- CAPTCHA solutions cache (very short-term)

### 3. Optimized Province Mapping
- Pre-built index cho faster lookups
- Multiple matching strategies
- Fuzzy matching fallback

## 📦 Project Structure

```
bhxh-tool-enhanced-python/
├── config/
│   ├── __init__.py              # Module initialization
│   ├── config.py                # Main configuration
│   └── validate_env.py          # Environment validation
├── utils/
│   ├── __init__.py              # Module initialization
│   ├── logger.py                # Structured logging
│   ├── validator.py             # Input validation
│   ├── retry.py                 # Retry utilities
│   └── cache.py                 # Caching system
├── services/
│   ├── __init__.py              # Module initialization
│   ├── excel_service.py         # Excel processing
│   ├── province_service.py      # Province mapping
│   ├── captcha_service.py       # 2captcha integration
│   └── bhxh_service.py          # BHXH API calls
├── logs/                        # Log files
├── data-input.xlsx              # Input data
├── data-output.xlsx             # Output results
├── tinh-thanh.json             # Province data
├── .env                         # Environment config
├── .env.template               # Environment template
├── requirements.txt             # Dependencies
├── main.py                     # Main application
└── README.md                   # This file
```

## 🤝 Contributing

### Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio black flake8 mypy

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

### Code Style

- Python 3.8+
- PEP 8 compliance
- Type hints
- Comprehensive error handling
- Detailed logging
- Input validation
- Security best practices

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

Nếu gặp vấn đề:

1. ✅ Kiểm tra `.env` configuration
2. ✅ Chạy `python main.py --test` để diagnose
3. ✅ Xem logs trong `logs/bhxh-tool.log`
4. ✅ Kiểm tra 2captcha balance
5. ✅ Verify input Excel format

---

**Enhanced BHXH Tool v2.0.0** - Phát triển để an toàn, hiệu quả và đáng tin cậy hơn! 🚀