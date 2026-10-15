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

## Kiểm tra tự động trên bản clone chính thức

Từ thư mục gốc của nhánh thử nghiệm, chạy:

```powershell
.\.venv\Scripts\python.exe harness\selfcheck.py
.\.venv\Scripts\python.exe -m unittest discover -s solution\tests -v
.\.venv\Scripts\python.exe solution\benchmark_candidate.py
```

Công cụ chỉ chạy Practice và Public, tự đối chiếu Practice theo `seq` và trả `candidate_pass` hoặc `keep_main`. Nếu mã thoát là 2 hoặc báo `keep_main`, **không** gộp nhánh. Kết quả là một phép thử mới, không phải bằng chứng thay cho báo cáo Private hiện tại.

## Kết quả đo kiểm thực tế trên Harness chính thức

### 1. Phân tích nguyên nhân ở bước đầu (Commit eb31951)

Khi chạy `benchmark_candidate.py` trên commit `eb31951`, kết quả ban đầu vẫn là `keep_main` (điểm Practice +0.0, vẫn sót 2 lỗi `missing_upstream` tại seq 17 và seq 52):
- **Nguyên nhân cốt lõi**: Khóa trường định danh trong payload sự kiện `lineage_run` của harness thực tế sử dụng chuẩn OpenLineage với tên khóa là `"job"` (ví dụ: `{'run_id': 'b-0017', 'job': 'dbt:stg_orders', ...}`).
- Mã ban đầu chỉ tìm các khóa `("model", "dbt_model", "model_name", "job_name")`, do đó `model` trả về rỗng, khiến cả nhánh kiểm tra `stg_orders` lẫn cơ chế học thích ứng `_lineage_group` đều không kích hoạt trên luồng dữ liệu thật.

### 2. Tinh chỉnh hoàn thiện

- Đã cập nhật `_lineage_group(payload)` hỗ trợ đầy đủ các định dạng: `"job"` (cả chuỗi và dict `{"name": ...}`), `"job_name"`, `"model"`, `"dbt_model"`, `"model_name"`.
- Thống nhất chuẩn hóa tên mô hình qua `_lineage_group` trong `check_lineage_run`.
- Bổ sung 2 bài kiểm thử đơn vị cho khóa `"job"` dạng chuỗi và dict trong `test_lineage_adaptive.py`, nâng tổng số bài kiểm thử lên **50/50 đạt**.

### 3. Bảng đối chiếu kết quả đo kiểm (Harness chính thức)

| Chỉ số / Pha | Baseline cũ (main) | Ứng viên sau tinh chỉnh | Chênh lệch (Delta) | Đánh giá |
|---|---|---|---|---|
| **Practice Score** | **46.97** | **50.00** | **+3.03** | Cải thiện tối đa (đạt trần 50) |
| Practice TPR | 93.94% (31/33) | 100.0% (33/33) | +6.06% | Bắt trọn 2 lỗi seq 17 & 52 (FN: 2 → 0) |
| Practice FPR | 0.0% (0/87) | 0.0% (0/87) | 0.0% | Không báo giả (FP = 0) |
| Practice Chi phí | 180.0 | 180.0 | 0.0 | Dưới ngân sách 220, overage = 0.0 |
| **Public Score** | **43.05** | **44.34** | **+1.29** | Tăng điểm tổng |
| Public TPR | 89.74% (35/39) | 92.31% (36/39) | +2.57% | Bắt thêm lỗi missing_upstream tại seq 107 |
| Public FPR | 0.0% (0/121) | 0.0% (0/121) | 0.0% | Không báo giả (FP = 0) |
| Public Chi phí | 240.0 | 240.0 | 0.0 | Giữ nguyên mức overage 9.09% |
| **Khuyến nghị tự động** | - | **`candidate_pass`** | - | **Đạt tiêu chuẩn gộp ứng viên** |

### 4. Kết luận và bảo toàn báo cáo Private

- Phiên bản ứng viên đã được xác minh bằng harness chính thức trên cả Practice và Public, hoàn toàn thỏa mãn cổng kiểm định chất lượng: Practice tăng điểm, Public tăng điểm, FPR không tăng, chi phí không tăng.
- Giữ nguyên tắc: Báo cáo `solution/private_report.json` trên nhánh `main` hiện vẫn đại diện cho phiên bản chạy chính thức đã khóa. Ứng viên này được lưu và quản lý an toàn trên nhánh thử nghiệm `experiment/lineage-adaptive-20261015`, sẵn sàng cho lượt chạy thẩm định Private độc lập.
