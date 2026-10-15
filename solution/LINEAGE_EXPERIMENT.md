# Nhánh thử nghiệm – cải thiện quan hệ đầu vào

## Mục đích

Hai trường hợp bỏ sót trong Practice theo nhật ký gốc đều thuộc `lineage/missing_upstream`. Nhánh này **không dùng** dữ liệu ẩn Private hay kết quả Private để chọn ngưỡng.

Thay đổi: (1) nhận diện tên mô hình dbt có tiền tố gói/dự án; (2) sử dụng lịch sử **chỉ của các sự kiện đã đến** trong `ctx.state` để phát hiện khi quan hệ đầu vào của cùng mô hình bị mất. Cảnh báo dựa vào lịch sử chỉ khi có ít nhất 3 lần quan sát cùng tập quan hệ, chiếm ít nhất 80% tổng số lần quan sát trước đó của mô hình và tập quan hệ hiện tại là tập con thực sự của tập ổn định.

## Bằng chứng hiện có

- Trong sandbox cục bộ, 43/43 bài kiểm thử đơn vị đạt; 8 bài mới tập trung vào logic thích ứng.
- Phần thử nghiệm dùng giao diện giả lập khớp `Verdict` và `SiegeContext`, **chưa chạy** trên harness chính thức.
- Chưa chứng minh TPR/FPR/điểm Practice hoặc Public được cải thiện.

## Các bước bắt buộc trước khi đưa lên main

1. Chạy `python harness/selfcheck.py` và `python -m unittest discover -s solution/tests -v` trong repository chính thức.
2. Chạy Practice bằng harness, sau đó `python solution/evaluate_practice.py`. So sánh điểm, TP, FP, FN với bản cũ: TP=31, FP=0, FN=2, TN=87, cost=180. Phải lưu bảng so sánh có nguồn.
3. Nếu Practice không cải thiện, hoặc xuất hiện FP mới mà điểm giảm, **không gộp**.
4. Nếu Practice cải thiện, kiểm tra Public bằng harness và so với điểm 43.05. Chỉ xem là ứng viên khi điểm tổng tăng và giới hạn chi phí vẫn chấp nhận được.
5. Không dùng nhãn, dữ liệu ẩn hoặc việc chạy lại Private để dò đáp án. Không thay `defense.py` trên main khi `private_report.json` hiện tại còn đại diện cho phiên bản cũ.

Không kết luận phiên bản mới tốt hơn trước khi có kết quả thực tế.
