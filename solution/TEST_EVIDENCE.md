# Bằng chứng triển khai trong sandbox (2026-10-15)

## Đã kiểm tra

- Nguồn yêu cầu: commit GitHub `29ad49d54455f44506d046b4acc9ce3904cea709`.
- Tệp được sửa hoặc tạo để nộp: chỉ thuộc `solution/` và `submission/`.
- Đã triển khai 5 handler với mapping `checks`, `contracts`, `lineage`, `ai_infra`, `ai_infra`.
- Chạy `python -m py_compile solution/defense.py`: PASS.
- Chạy `python -m unittest discover -s solution/tests -v`: PASS, 30 test.
- Chạy kiểm tra cấu trúc bằng bản sao tự tạo dựa trên `harness/selfcheck.py` đã đọc từ GitHub: 5/5.
- Test trên dữ liệu giả lập xác nhận: cảnh báo lỗi rõ, xử lý giá trị thiếu, điều kiện biên, cache, deterministic output, không xuất stdout và trạng thái giữa lần chạy.

## Chưa xác minh

- Sandbox không tải được các dữ liệu chạy mã hóa và khóa pha từ GitHub. Do đó **chưa chạy** `harness/run.py` trên Practice, Public hoặc Private trong môi trường này.
- Chưa có số liệu TP/FP/FN/TN, TPR/FPR, điểm thực hoặc chi phí thực cho bất kỳ pha nào.
- Bài kiểm thử tại sandbox sử dụng API rút gọn có cùng hợp đồng `Verdict` và đăng ký handler, không thay thế việc chạy harness chính thức.
- `solution/private_report.json` phải do harness thực tạo, không tự sinh thủ công.

## Lệnh chạy trên bản clone chính thức

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe harness\selfcheck.py
.\.venv\Scripts\python.exe -m unittest discover -s solution\tests -v
.\.venv\Scripts\python.exe harness\run.py --phase practice --defense solution/defense.py --out solution/practice_report.json
.\.venv\Scripts\python.exe harness\run.py --phase public --defense solution/defense.py --out solution/public_report.json
```

Chỉ chạy Private khi đã khóa mã và xem xét kết quả Practice/Public; lệnh chính thức ở `docs/SUBMIT.md`.