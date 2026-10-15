# Báo cáo kết quả bài lab Data Siege

## 1. Mục tiêu và phạm vi

Bài lab yêu cầu xây dựng bộ phát hiện lỗi cho một luồng dữ liệu gồm năm loại sự kiện: `data_batch`, `contract_checkpoint`, `lineage_run`, `feature_materialization` và `embedding_batch`. Mỗi sự kiện phải được xử lý trong `solution/defense.py` bằng giao diện được công bố. Điểm số phụ thuộc vào tỷ lệ phát hiện đúng (TPR), tỷ lệ cảnh báo nhầm (FPR) và mức vượt ngân sách công cụ:

```text
Score = 100 × (0.5 × TPR − 0.3 × FPR − 0.2 × min(cost_overage, 1))
```

## 2. Thiết kế giải pháp

Mỗi loại sự kiện có một hàm kiểm tra riêng. Hàm nhận dữ liệu sự kiện và ngữ cảnh, gọi công cụ đo tương ứng rồi trả về `Verdict`. Các kết quả truy vấn được lưu trong `ctx.state` theo tên công cụ và tham số; nếu cùng truy vấn xuất hiện lại trong một lượt chạy, chương trình có thể dùng kết quả đã lưu.

- **Kiểm tra dữ liệu (`checks`)**: đối chiếu số hàng, tỷ lệ thiếu mã khách hàng, giá trị giao dịch trung bình và độ trễ với các giới hạn lịch sử. Nếu từng chỉ số chưa vượt ngưỡng, chương trình xét thêm trường hợp nhiều chỉ số cùng tiến sát giới hạn.
- **Hợp đồng dữ liệu (`contracts`)**: phát hiện vi phạm lược đồ, kiểu dữ liệu hoặc thời hạn cập nhật đã cam kết.
- **Dòng phụ thuộc (`lineage`)**: kiểm tra thời gian chạy, đầu ra không có đơn vị tiêu thụ và các quan hệ đầu vào bắt buộc khi có đủ thông tin tham chiếu.
- **Hạ tầng AI (`ai_infra`)**: kiểm tra mức dịch chuyển đặc trưng giữa huấn luyện và phục vụ; đồng thời kiểm tra độ dịch chuyển vector và tuổi trung bình của tài liệu.

Ngưỡng phát hiện kết hợp và ngưỡng dịch chuyển đặc trưng là lựa chọn thiết kế. Không có bằng chứng rằng chúng tối ưu cho mọi phân phối dữ liệu.

## 3. Kết quả kiểm thử

| Chỉ số | Practice | Public | Private |
|---|---:|---:|---:|
| Điểm | 46,97 | 43,05 | 26,85 |
| TPR | 93,94% | 89,74% | 53,70% |
| FPR | 0% | 0% | 0% |
| Chi phí công cụ | 180 tín dụng | 240 tín dụng | Không công bố trong báo cáo Private |
| Mức vượt ngân sách | 0% | 9,09% | 0% |

Selfcheck đăng ký đủ **5/5** hàm xử lý. Bộ kiểm thử đơn vị có **35/35** bài đạt. Theo nhật ký thực thi, các báo cáo trên được tạo bằng chương trình đi kèm repository. Bản `solution/private_report.json` có trên GitHub, chứa điểm 26,85 và chữ ký ở dạng chuỗi 64 ký tự thập lục phân. Bài rà soát này chưa xác minh độc lập giá trị HMAC bằng khóa gốc. Hai báo cáo Practice/Public được ghi nhận trong nhật ký nhưng chưa được đưa lên nhánh `main` tại thời điểm rà soát.

## 4. Phân tích kết quả và giới hạn

Practice và Public có tỷ lệ cảnh báo nhầm bằng 0, nhưng Public vượt ngân sách 20 tín dụng, tương ứng mức vượt 9,09% và bị trừ khoảng 1,82 điểm. Phương án gọi công cụ cho các sự kiện vẫn đem lại kết quả cao hơn việc bỏ qua kiểm tra chỉ để tránh mức phạt nhỏ này.

Tỷ lệ phát hiện của Private thấp hơn Public **36,04 điểm phần trăm**, trong khi FPR vẫn bằng 0. Kết quả cho thấy các điều kiện phát hiện chưa khái quát tốt sang pha có nhiều lỗi tinh vi hơn. Vì báo cáo Private không cung cấp lỗi theo từng trụ cột, không đủ bằng chứng để quy nguyên nhân chính cho lỗi thiếu quan hệ đầu vào hay bất kỳ loại lỗi cụ thể nào. Kiểm tra mã nguồn chỉ cho phép nêu các khả năng cần nghiên cứu, không thay thế phân tích nhãn thật.

Một giới hạn khác là giải pháp chủ yếu dùng các ngưỡng tĩnh. `ctx.state` hiện hỗ trợ lưu kết quả công cụ, chưa có cơ chế ước lượng xu hướng hoặc thay đổi phân phối theo thời gian. Việc thêm cơ chế đó cần được đánh giá trên dữ liệu được phép sử dụng, với cả TPR, FPR và chi phí.

## 5. Kết luận và hồ sơ

Giải pháp đã triển khai đủ năm bộ xử lý, hoàn thành các kiểm thử được ghi trong nhật ký và tạo báo cáo Private. Kết quả đạt yêu cầu về cấu trúc và không phát sinh cảnh báo nhầm trong ba lượt đo đã báo cáo; tuy nhiên, khả năng phát hiện lỗi tinh vi vẫn còn hạn chế. Các cải tiến tiếp theo phải được đánh giá trên tập được phép dùng để hiệu chuẩn, không khai thác dữ liệu ẩn Private.

Theo `RULES.md`, ba tệp chính được chấm là `solution/defense.py`, `solution/reflection.md` và `solution/private_report.json`. Nếu kiểm tra theo checklist VLearn có yêu cầu cả ba báo cáo, cần bổ sung `solution/practice_report.json` và `solution/public_report.json` từ các lượt chạy gốc trước khi xác nhận đủ hồ sơ.
