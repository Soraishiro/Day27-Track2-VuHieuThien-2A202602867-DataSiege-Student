# Biên bản đối chiếu tình trạng kiểm thử Data Siege

Ngày rà soát: 15/10/2026. Nguồn: mã và nhật ký tại commit `0677babf29225154e3623b604555a692e0da3b8c`. Phần dưới phân biệt kết quả ghi nhận trong nhật ký với những tệp có thể kiểm tra trực tiếp trên GitHub.

## 1. Những việc được nhật ký thực thi ghi nhận

- `harness/selfcheck.py`: 5/5 loại sự kiện có hàm xử lý.
- `python -m unittest discover -s solution/tests -v`: 35/35 bài kiểm thử đạt.
- Practice: điểm 46,97; TPR 0,9394; FPR 0; chi phí 180,0/220 tín dụng.
- Public: điểm 43,05; TPR 0,8974; FPR 0; chi phí 240,0/220 tín dụng; cả bốn trụ cột được xếp mức `high`.
- Private: điểm 26,85; TPR 0,537; FPR 0; không vượt ngân sách.

Những kết quả trên có bản ghi trong `solution/EXECUTION_LOG.md`. Đây là bằng chứng do quá trình thực thi ghi lại, không phải bản xác nhận độc lập rằng mọi lệnh đã được chạy lại trong môi trường rà soát này.

## 2. Những tệp được xác minh trực tiếp trên nhánh main

- `solution/defense.py`: hiện diện, có đủ năm bộ xử lý.
- `solution/private_report.json`: hiện diện, có cấu trúc `result` và `signature`, số liệu khớp bản ghi đã cung cấp. Chữ ký có định dạng 64 ký tự thập lục phân; chưa xác minh mật mã độc lập.
- `submission/manifest.json`: có mã `VuHieuThien-2A202602867` và các đường dẫn đúng.
- `solution/reflection.md`: đã viết thu hoạch cá nhân.
- `solution/tests/`: có các phép thử đơn vị và kiểm tra công cụ đối chiếu Practice.

## 3. Phần còn thiếu so với checklist VLearn

Hai file `solution/practice_report.json` và `solution/public_report.json` **không có trên nhánh main** trong lần rà soát này. Nhật ký cho biết chúng đã được tạo trên máy chạy thử. Nếu cần nộp đủ cả ba báo cáo, phải dùng đúng các tệp do `harness/run.py` tạo ra, kiểm tra cấu trúc/chữ ký và commit chúng; không dựng lại JSON từ bảng điểm.

Theo `RULES.md`, hệ thống chấm chỉ yêu cầu `defense.py`, `reflection.md` và `private_report.json`. Sự khác biệt giữa quy định chấm và checklist cần được phân biệt khi báo cáo tiến độ.

## 4. Bảo toàn kết quả Private

Không sửa `solution/private_report.json` bằng tay. Không thay đổi `solution/defense.py` rồi dùng báo cáo Private cũ như thể chúng thuộc cùng phiên bản. Không dùng dữ liệu ẩn của Private để dò đáp án. Nếu cần xác minh chữ ký, hãy dùng quy trình kiểm tra được cho phép trên môi trường chính thức.

## 5. Phép kiểm tra trước khi nộp

```powershell
.\.venv\Scripts\python.exe harness\selfcheck.py
.\.venv\Scripts\python.exe -m unittest discover -s solution\tests -v
git status --short
git ls-files solution submission
```

Với yêu cầu nộp đủ ba báo cáo, chạy thêm phép kiểm tra tồn tại ba tệp và đối chiếu với bản gốc trên máy thực thi. Không đánh dấu đạt khi một tệp vẫn chưa được đưa lên GitHub.
