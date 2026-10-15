# DAY 27 — DATA SIEGE: ĐẶC TẢ THỰC THI VÀ DANH SÁCH VIỆC PHẢI LÀM

**Loại tài liệu:** Hướng dẫn giao việc cho coding agent, có thứ tự, lệnh chạy, kiểm thử và tiêu chí chấp nhận.  
**Ngày lập:** 15/10/2026.  
**Repository:** `https://github.com/Soraishiro/Day27-Track2-VuHieuThien-2A202602867-DataSiege-Student`  
**Nhánh đích:** `main`.  
**Commit đã đối chiếu trước khi lập kế hoạch:** `75f967c09b09b3ec40eb63aaf125e1ae60741d71`.  
**Nguồn có hiệu lực cao hơn tài liệu này:** `RULES.md`, `README.md`, `docs/TOOLKIT_API.md`, `docs/SUBMIT.md` và mã harness đang có trên nhánh đích.

> **ĐÂY LÀ ĐẶC TẢ, KHÔNG PHẢI BIÊN BẢN ĐÃ HOÀN THÀNH.** Các mục bên dưới mặc định ở trạng thái `TODO`. Không tự chuyển thành `PASS` chỉ vì đọc thấy mã hoặc kết quả cũ. Các con số 35/35 và 5/5 là kết quả kiểm thử mô phỏng ở phiên trước; phải chạy lại trong bản clone chính thức. Chưa có kết quả chính thức của Practice, Public hoặc Private tại thời điểm lập tài liệu.

---

## 0. LỆNH DÀNH CHO AGENT — ĐỌC TRƯỚC KHI LÀM

**Mục tiêu duy nhất:** hoàn thiện giải pháp `solution/defense.py`, kiểm thử trong phạm vi được phép, chạy các pha bằng harness gốc, tạo báo cáo hợp lệ và nộp các tệp theo `docs/SUBMIT.md`. Không cố tìm nhãn ẩn của Public hoặc Private.

**Làm đúng thứ tự:** `T00 → T01 → T02 → T03 → T04 → T05 → T06 → T07 → T08 → T09 → T10 → T11 → T12`. Một bước không đạt điều kiện nghiệm thu thì chưa được chuyển bước phụ thuộc. Thực hiện tối đa 5 vòng cải thiện có chủ đích trước khi chốt mã và tối đa 1 lần chạy lại Public để xác minh sửa lỗi kỹ thuật. Private chỉ chạy **một lần có kết quả hợp lệ** sau khi khóa mã.

**Hợp đồng hành vi:**

1. Mỗi khi bắt đầu việc, ghi `DOING` vào `solution/EXECUTION_LOG.md`. Khi xong, ghi `PASS` kèm lệnh và kết quả thật. Khi lỗi, ghi `FAIL`, nguyên nhân và bằng chứng. Khi chưa đủ điều kiện, ghi `BLOCKED` và không giả định đã qua bước đó.
2. Chỉ được tạo/sửa/xóa tệp trong `solution/` và `submission/`. Không sửa `harness/`, `phases/`, `data/`, `docs/`, `README.md`, `RULES.md`, `.gitignore`, `requirements.txt` hoặc tệp ở thư mục gốc. Không sửa chương trình chấm điểm, file khóa hoặc dữ liệu mã hóa.
3. `defense.py` chỉ dùng `payload`, `ctx.baseline`, `ctx.state`, các phương thức công khai của `ctx.tools` và import thuộc danh sách cho phép. Không đọc tệp, mạng, tiến trình ngoài, đồng hồ, seed, đáp án, mã harness trong handler. Không ghi ra stdout. Không cài bảng quyết định theo `seq`, `event_id`, `batch_id` hoặc run cụ thể.
4. Chỉ dùng `phases/practice_answer_key.json` từ chương trình đánh giá bên ngoài `defense.py` để đối chiếu nhãn Practice. Không mở trực tiếp tệp `.key`, `.enc`, không giải mã lịch sự kiện, không suy ngược nhãn ẩn từ harness. Để harness chính thức tự dùng các tệp pha.
5. Không tự tạo, chỉnh sửa, sao chép hoặc tính lại chữ ký `solution/private_report.json`. Chỉ dùng bản do `harness/run.py --phase private` tạo ra. Không dùng bản Private để lựa chọn lại ngưỡng.
6. Nếu thấy mã hiện tại khác giả định của tài liệu này, so sánh `git diff` và tài liệu gốc trước. Không âm thầm ghi đè thay đổi của người khác.
7. Luôn giải thích số liệu thật bằng tiếng Việt tự nhiên, dùng tên API, khóa JSON và tên tệp đúng nguyên dạng. Không dùng văn mẫu phóng đại, không nói “đã tối ưu” khi mới kiểm thử giả lập.
8. Không dùng `git push --force`, `git reset --hard`, `git clean -fd`, `git checkout .` hoặc lệnh xóa lịch sử. Không tự động xóa hoặc sửa các báo cáo cũ khi chưa xác nhận nguồn gốc.

### 0.1. Quy tắc chọn phương án khi nhiều phương án đều đạt kiểm thử

So sánh trên **cùng pha và cùng bộ dữ liệu** theo thứ tự: (1) điểm số cao hơn; (2) nếu cùng điểm đến hai chữ số thập phân, FPR thấp hơn; (3) nếu vẫn bằng, TPR cao hơn; (4) nếu vẫn bằng, chi phí thấp hơn; (5) nếu vẫn bằng, phương án có ít điều kiện đặc thù hơn. Không chọn theo cảm giác. Không so sánh điểm Practice với điểm Public để kết luận phương án nào tốt hơn, vì hai luồng có phân phối khác nhau.

### 0.2. Quy tắc dừng

- `STOP-SAFETY`: phát hiện bất kỳ thao tác vi phạm `RULES.md`, sửa file ngoài phạm vi cho phép, truy cập tệp khóa, giải mã tệp ẩn hoặc dùng bảng tra nhãn theo ID. Hoàn tác phần vi phạm và báo rõ; không chạy Private.
- `STOP-ENV`: không chạy được Python, thiếu tệp đầu vào, clone lỗi hoặc quyền truy cập GitHub không đủ. Lưu lỗi; không giả mạo kết quả.
- `STOP-TEST`: kiểm thử đơn vị, selfcheck hoặc phép tính lại kết quả Practice không đạt. Sửa lỗi kỹ thuật trước khi chạy Public.
- `STOP-PRIVATE`: đã có báo cáo Private hợp lệ. Không tiếp tục dò ngưỡng hoặc chạy thêm lần khác để lấy điểm cao hơn.
- `DONE`: hồ sơ đúng định dạng, đã push, đã xác minh SHA đầu nhánh và các tệp bắt buộc có thật.

### 0.3. Định dạng ghi tiến độ bắt buộc

Dùng đúng mẫu bên dưới cho mỗi mục trong `solution/EXECUTION_LOG.md`:

```text
ID: Txx.yy
Trạng thái: TODO | DOING | PASS | FAIL | BLOCKED
Commit trước thay đổi: <SHA>
Tệp liên quan: <đường dẫn>
Lệnh đã chạy: <lệnh chính xác>
Mã thoát: <số hoặc 'chưa chạy'>
Kết quả quan sát: <giá trị thực; không suy đoán>
Bằng chứng: <tệp báo cáo, đường dẫn log, commit hoặc dòng đầu ra>
Quyết định tiếp theo: <giữ / sửa / hoàn tác / dừng / chuyển bước>
```

Không ghi `PASS` khi `Mã thoát` và bằng chứng không có. Với nhiệm vụ chỉ đọc hoặc rà soát, ghi đường dẫn và đoạn kiểm tra cụ thể; mã thoát có thể ghi `không áp dụng`.

---

## 1. BẢN ĐỒ HỆ THỐNG ĐÃ XÁC MINH

### 1.1. File và tình trạng tại commit tham chiếu

| File | Có ở repo | Vai trò | Trạng thái đầu vào |
|---|---|---|---|
| `solution/defense.py` | Có | 5 handler phát hiện lỗi | Đã triển khai; chưa kiểm thử trên stream chính thức |
| `solution/tests/test_defense.py` | Có | Kiểm thử handler bằng fake toolkit | Có 30 bài kiểm thử mô phỏng ở lượt trước |
| `solution/evaluate_practice.py` | Có | Ghép verdict Practice theo `seq`, tính TP/FP/FN/TN | Đã triển khai, chưa đánh giá bằng report Practice thật |
| `solution/tests/test_practice_evaluator.py` | Có | Kiểm thử bộ đánh giá | Có 5 bài kiểm thử mô phỏng ở lượt trước |
| `solution/TEST_EVIDENCE.md` | Có | Bằng chứng cũ và giới hạn | Nêu rõ 35/35 không thay cho kiểm thử harness |
| `solution/reflection.md` | Có | Báo cáo ≤1 trang | Bản nháp, chưa có kết quả pha thật |
| `submission/manifest.json` | Có | Khai báo vị trí tệp nộp | Đã điền tên; chưa có `private_report.json` |
| `solution/practice_report.json` | Chưa xác nhận | Kết quả Practice | Phải tạo bằng harness chính thức |
| `solution/public_report.json` | Chưa xác nhận | Kết quả Public | Phải tạo bằng harness chính thức |
| `solution/private_report.json` | Chưa xác nhận | Kết quả Private có chữ ký | Chỉ được tạo sau khi khóa mã |

### 1.2. Hợp đồng API không được tự thay đổi

| Event | Handler | Pillar | RPC | Phí mỗi lần |
|---|---|---|---|---:|
| `data_batch` | `check_data_batch` | `checks` | `batch_profile(batch_id)` | 1.0 |
| `contract_checkpoint` | `check_contract_checkpoint` | `contracts` | `contract_diff(contract_id, checkpoint_batch_id)` | 1.5 |
| `lineage_run` | `check_lineage_run` | `lineage` | `lineage_graph_slice(run_id)` | 1.0 |
| `feature_materialization` | `check_feature_materialization` | `ai_infra` | `feature_drift(feature_view, ref)` | 2.0 |
| `embedding_batch` | `check_embedding_batch` | `ai_infra` | `embedding_drift(corpus, ref)` | 2.0 |

Hai RPC miễn phí là `spend_so_far()` và `budget_remaining()`. Chỉ dùng khi chúng cung cấp thông tin cần thiết; “miễn phí” không có nghĩa là phải gọi liên tục.

`Verdict(alert: bool, confidence: float = 1.0, reason: str = "", pillar: str = "")`. Handler nhận `(payload, ctx)`, trả đúng một `Verdict`. `confidence` hiện không tác động đến công thức điểm trong `harness/scoring.py`.

Ngưỡng `ctx.baseline` hiện tại: `row_count_min=435.4732`, `row_count_max=561.2948`, `null_rate_max=0.0109`, `mean_amount_min=72.7645`, `mean_amount_max=90.6053`, `staleness_min_max=8.418`, `freshness_delay_max_min=11.1141`, `lineage_duration_ms_max=5134.9804`, `feature_mean_shift_sigma_max=0.4095`, `embedding_centroid_shift_max=0.0435`, `corpus_avg_doc_age_days_max=49.7955`. **Trong code phải đọc từ `ctx.baseline`, không chép các số này vào handler.**

### 1.3. Điểm số và giới hạn thông tin

```text
Score = 100 × (0.5 × TPR − 0.3 × FPR − 0.2 × min(cost_overage, 1))
TPR = TP / (TP + FN)
FPR = FP / (FP + TN)
cost_overage = max(0, (cost_ledger − budget) / budget)
```

- Practice: **120** sự kiện, ngân sách **220** credit; đáp án đã công bố có **33 lỗi, 87 bình thường**. Báo cáo chứa quyết định theo `seq`.
- Public: **160** sự kiện, ngân sách **220** credit; báo cáo tổng hợp và các mức `high`, `medium`, `low` theo trụ cột; **không** có verdict từng sự kiện.
- Private: **200** sự kiện, ngân sách **320** credit; chỉ trả kết quả tổng hợp cuối cùng và chữ ký.
- Điểm tối đa của công thức là **50.00** khi `TPR=1`, `FPR=0`, không vượt ngân sách. Không suy ra rằng hệ thống mặc định đạt điểm này.
- Mức `high` chỉ chứng minh TPR của trụ cột ≥0.75 theo mã chấm. Không có nghĩa TPR=1.
- Vượt ngân sách **không làm harness dừng**; chỉ giảm điểm. Tuyệt đối không mặc định hết ngân sách thì tắt mọi công cụ.

---

## 2. T00 — ĐỒNG BỘ VÀ KIỂM KÊ (CHẶN MỌI BƯỚC KHÁC NẾU LỖI)

- [ ] **T00.01 — Xác nhận thư mục gốc.** Mở terminal tại repo, chạy `git rev-parse --show-toplevel`. Kết quả phải trỏ đến repo `Day27-Track2-VuHieuThien-2A202602867-DataSiege-Student`. Nếu không, chuyển thư mục đúng; chưa được sửa file.
- [ ] **T00.02 — Kiểm tra thay đổi trước khi làm.** Chạy `git status --short`. Nếu có thay đổi chưa commit, ghi danh sách vào `solution/EXECUTION_LOG.md`. Không ghi đè file đã được người khác sửa. Nếu thay đổi trùng file cần xử lý, tạm dừng phần ghi vào file đó và báo `BLOCKED`.
- [ ] **T00.03 — Đồng bộ an toàn.** Chạy `git fetch origin main`, `git pull --ff-only origin main`; nếu không fast-forward được, dừng. Không rebase tự động hoặc force push.
- [ ] **T00.04 — Ghi SHA.** Chạy `git rev-parse HEAD`. Nếu SHA khác `75f967c09b09b3ec40eb63aaf125e1ae60741d71`, đối chiếu thêm `git log -5 --oneline` và thay đổi trong `solution/`, `submission/` trước khi tiếp tục.
- [ ] **T00.05 — Đọc luật.** Đọc toàn bộ `RULES.md`, `README.md`, `docs/TOOLKIT_API.md`, `docs/FAULT_PILLARS.md`, `docs/SUBMIT.md`. Ghi lại 4 nội dung: thư mục sửa hợp lệ; cách tính điểm; đầu vào/đầu ra từng RPC; tệp phải nộp.
- [ ] **T00.06 — Đọc mã cần thiết ở ngoài sandbox.** Đọc `harness/child_env/api.py`, `harness/child_env/child_driver.py`, `harness/run.py`, `harness/scoring.py`, `harness/toolkit/metering.py`, `harness/selfcheck.py` để xác minh API và định dạng báo cáo. Không sửa các file đó; không import chúng từ `defense.py`.
- [ ] **T00.07 — Kiểm kê đầu vào.** Xác nhận có `solution/defense.py`, `solution/evaluate_practice.py`, `solution/tests/test_defense.py`, `solution/tests/test_practice_evaluator.py`, `solution/reflection.md`, `submission/manifest.json` và `data/baselines.json`.
- [ ] **T00.08 — Kiểm tra tệp pha chỉ bằng sự tồn tại.** Xác nhận các tệp `.key` và `.enc` cần cho Practice/Public/Private tồn tại hay không bằng kiểm tra đường dẫn (`Test-Path` hoặc `test -f`). Không mở, in, băm hoặc đọc nội dung. Nếu Private chưa phát hành hoặc thiếu tệp, đánh dấu chặn bước Private; vẫn được thực hiện các phần trước.
- [ ] **T00.09 — Ghi tình trạng ban đầu.** Ghi SHA, kết quả `git status`, phiên bản Python và các tệp thiếu vào `solution/EXECUTION_LOG.md`.

**GATE T00:** Tất cả file nguồn bắt buộc có và `git status` đã được xử lý. Không có bất kỳ sửa đổi nào ngoài hai thư mục được phép.

## 3. T01 — TẠO MÔI TRƯỜNG CHẠY VÀ XÁC NHẬN BỘ KIỂM THỬ

### Windows PowerShell (chạy từ thư mục gốc)

```powershell
py -3 -m venv .venv
$PY = ".\.venv\Scripts\python.exe"
& $PY -m pip install -r requirements.txt
& $PY --version
& $PY -m py_compile solution/defense.py solution/evaluate_practice.py
& $PY harness/selfcheck.py
& $PY -m unittest discover -s solution/tests -v
```

### Linux/macOS (chạy từ thư mục gốc)

```bash
python3 -m venv .venv
PY=.venv/bin/python
"$PY" -m pip install -r requirements.txt
"$PY" --version
"$PY" -m py_compile solution/defense.py solution/evaluate_practice.py
"$PY" harness/selfcheck.py
"$PY" -m unittest discover -s solution/tests -v
```

- [ ] **T01.01 — Tạo môi trường riêng.** Không cài thư viện vào Python hệ thống nếu có thể dùng `.venv`.
- [ ] **T01.02 — Cài đúng dependency.** Dùng `requirements.txt` nguyên bản, không thêm thư viện ngoài chỉ để thuận tiện.
- [ ] **T01.03 — Kiểm tra biên dịch cú pháp.** Cả `defense.py` và `evaluate_practice.py` phải qua `py_compile`.
- [ ] **T01.04 — Chạy selfcheck gốc.** Kiểm tra đầu ra chứa `5/5 event types have a handler`; `selfcheck` exit code 0 một mình **chưa đủ** vì thiếu handler có thể chỉ cảnh báo.
- [ ] **T01.05 — Chạy toàn bộ unit test.** Yêu cầu **tất cả** kiểm thử hiện tại PASS, không có ERROR/FAIL. Ghi tổng số thật; kỳ vọng đầu vào là 35 bài, nhưng chỉ kết quả mới được coi là bằng chứng.
- [ ] **T01.06 — Khi test lỗi import.** Xác minh chạy từ thư mục gốc, `.venv` đúng và `harness/child_env/api.py` có sẵn. Không sửa harness để chữa lỗi test. Chỉ sửa mã/test trong `solution/`.
- [ ] **T01.07 — Khi test lỗi thuật toán.** Xác định tên test, input, expected/actual. Không sửa kỳ vọng của test chỉ để biến FAIL thành PASS; phải chứng minh kỳ vọng sai theo tài liệu gốc mới được sửa test.

**GATE T01:** Cú pháp PASS; selfcheck đúng 5/5; toàn bộ unit tests PASS. Nếu không, trạng thái là `STOP-TEST`.

## 4. T02 — RÀ SOÁT VÀ KHÓA HỢP ĐỒNG 5 HANDLER

Chỉ bắt đầu sau T01. Trước khi sửa, đọc `solution/defense.py` hiện tại và so sánh với chính tài liệu này; không thay toàn bộ mã bằng khung rỗng.

- [ ] **T02.01 — Kiểm tra `register(ctx)`.** Phải đăng ký đúng 5 loại sự kiện: `data_batch`, `contract_checkpoint`, `lineage_run`, `feature_materialization`, `embedding_batch`. Không trùng hoặc sai tên.
- [ ] **T02.02 — Kiểm tra đầu ra.** Mỗi handler nhận đúng `(payload, ctx)` và trả đối tượng `Verdict`, với `alert` là bool; pillar lần lượt là `checks`, `contracts`, `lineage`, `ai_infra`, `ai_infra`.
- [ ] **T02.03 — Kiểm tra phản hồi lỗi từ tool.** Khi tool trả `{"error": ...}` hoặc dạng dữ liệu thiếu trường, handler không được crash và không tự suy diễn đó là lỗi đường ống dữ liệu. Ghi lý do chẩn đoán phù hợp.
- [ ] **T02.04 — Kiểm tra kiểu dữ liệu.** Đầu vào `None`, chuỗi thay số, `bool`, `NaN`, `inf`, số âm ở trường không được âm, mẫu số bằng 0 đều phải có xử lý rõ. Không lấy `True` bằng 1.0 khi so ngưỡng.
- [ ] **T02.05 — Kiểm tra các import.** Chỉ giữ `from api import Verdict` và module thuộc allowlist ở `harness/child_env/child_driver.py`; không dùng `numpy`, `pandas`, `os`, `subprocess` hoặc module địa phương không cho phép.
- [ ] **T02.06 — Kiểm tra đầu ra chuẩn.** Không `print()` ra stdout; không tự mở tệp hoặc ghi log từ bên trong `defense.py`. Bằng chứng: quét mã và kiểm thử không sinh stdout.
- [ ] **T02.07 — Kiểm tra bộ nhớ đệm.** Nếu sử dụng `ctx.state`, khóa cache phải gồm tên RPC và toàn bộ tham số; cache chỉ chứa dữ liệu đã nhận trong cùng lần chạy. Không được bỏ gọi tool cho event khác chỉ vì có cùng bảng, trừ khi bộ tham số và định danh thực sự trùng.
- [ ] **T02.08 — Kiểm tra tính lặp lại.** Hai context mới, cùng payload và cùng tool response phải cho verdict giống nhau. Không phụ thuộc thời gian thực, trạng thái toàn cục từ lần chạy trước hoặc ngẫu nhiên.

**GATE T02:** Có unit test chứng minh T02.01–T02.08; kết quả 5/5 selfcheck giữ nguyên.

## 5. T03 — RÀ SOÁT CHÍNH XÁC TỪNG NHÓM LỖI

### T03.A — `data_batch` / `checks`

- [ ] **T03.01** Lấy `payload["batch_id"]` và dùng đúng `ctx.tools.batch_profile(batch_id)` cho event hợp lệ. Không gọi profile hai lần cho cùng tham số.
- [ ] **T03.02** Đọc đúng trường: `row_count`, `null_rate.customer_id`, `mean_amount`, `staleness_min`. Trường `null_rate` là dictionary, không phải số đơn.
- [ ] **T03.03** Kiểm tra ngoài khoảng **nghiêm ngặt**: `rows < min` hoặc `rows > max`; `mean < min` hoặc `mean > max`. Bằng đúng ngưỡng không cảnh báo nếu không có tín hiệu bổ sung.
- [ ] **T03.04** Kiểm tra ngưỡng trên: `null_rate > max`, `staleness_min > max`. Một lỗi rõ phải tạo đúng một Verdict cảnh báo, với reason chỉ rõ tên chỉ số và giá trị/ngưỡng.
- [ ] **T03.05** Kiểm tra logic kết hợp 4 chiều hiện có: cách chuẩn hóa phải được giải thích bằng toán và bài test. Không khẳng định khoảng cách hiện có là z-score thực nếu dùng trung điểm và nửa độ rộng 3σ làm thước đo.
- [ ] **T03.06** Tạo tối thiểu 3 trường hợp sạch mà mỗi chỉ số riêng sát ngưỡng; 3 trường hợp lỗi phối hợp; 1 trường hợp đúng biên. Đo FP phát sinh do điều kiện `>= 2 chiều >= 0.84` và `norm2 > 1.35` đang có. Hai số này là giả thuyết, không phải tiêu chuẩn của người ra đề.
- [ ] **T03.07** Nếu thay logic kết hợp, nêu tác động dự kiến (FP hay FN nào được sửa), viết test trước rồi mới đổi code. Nếu không có bằng chứng, giữ bản hiện tại.

### T03.B — `contract_checkpoint` / `contracts`

- [ ] **T03.08** Gọi `contract_diff(payload["contract_id"], payload["checkpoint_batch_id"])` đúng thứ tự. Kiểm tra lỗi response.
- [ ] **T03.09** Nếu `violations` là list không rỗng, cảnh báo. Không cần dự đoán tên vi phạm chưa xuất hiện. Lý do gồm loại vi phạm.
- [ ] **T03.10** So `freshness_delay_min` với SLA chỉ khi `declared_sla.freshness_min` là số hợp lệ, không âm; đồng thời so với `ctx.baseline["freshness_delay_max_min"]`.
- [ ] **T03.11** Kiểm thử 4 trường hợp: chỉ sai schema/type; chỉ vi phạm SLA; cả hai; hoàn toàn sạch. Thêm trường hợp `declared_sla` vắng mặt và freshness đúng bằng ngưỡng.

### T03.C — `lineage_run` / `lineage`

- [ ] **T03.12** Gọi `lineage_graph_slice(run_id)` đúng một lần cho event hợp lệ.
- [ ] **T03.13** Cảnh báo khi `duration_ms > ctx.baseline["lineage_duration_ms_max"]`.
- [ ] **T03.14** Kiểm tra `actual_downstream_count == 0`, nhưng **xem xét bằng chứng metadata** để phân biệt mô hình đầu cuối hợp lệ và đầu ra mồ côi. Không tự cho rằng mọi đầu ra 0 downstream đều lỗi nếu tài liệu/API cho biết có mô hình đầu cuối hợp lệ. Nếu không có cách phân biệt, ghi rủi ro FP và kiểm tra bằng Practice.
- [ ] **T03.15** Khi có `expected_upstream`/`required_upstream` hợp lệ trong payload, so tập nguồn mong đợi với `actual_upstream`. Không suy ra phụ thuộc từ tên job tùy ý. Với mô hình `dbt:stg_orders`, chỉ dùng hai nguồn `raw.orders` và `raw.customers` khi định nghĩa bài lab xác nhận tương ứng.
- [ ] **T03.16** Viết test cho: mất một nguồn, mất cả hai, thứ tự nguồn khác nhau, có nguồn dư hợp lệ, không downstream, runtime cao, mô hình khác `stg_orders` không có expected list, trường thiếu.

### T03.D — `feature_materialization` / `ai_infra`

- [ ] **T03.17** Gọi `feature_drift(feature_view, batch_id)` đúng một lần. Dữ liệu gồm `mean_shift_sigma` đã làm tròn 3 chữ số thập phân.
- [ ] **T03.18** Kiểm tra nếu tự tính lại `abs(serve_mean-train_mean)/train_std`, phải yêu cầu `train_std > 0` và các số hữu hạn. Không tự tạo độ lệch khi mẫu số 0.
- [ ] **T03.19** Mã hiện tại dùng `threshold = max(0.65, baseline*1.5)`. Ghi đây là **ngưỡng ứng viên chưa xác minh bằng pha thật**, không phải baseline bắt buộc. So với ít nhất một ứng viên lấy trực tiếp baseline 0.4095 và một ứng viên bảo thủ thông qua test biên/Practice. Không thử hàng loạt ngưỡng theo phản hồi Public.
- [ ] **T03.20** Test giá trị đúng bằng ngưỡng, thấp hơn một lượng rất nhỏ, cao hơn một lượng rất nhỏ, tool thiếu `mean_shift_sigma`, `train_std=0`, và trường hợp sạch nhưng gần baseline.

### T03.E — `embedding_batch` / `ai_infra`

- [ ] **T03.21** Gọi `embedding_drift(corpus, chunk_batch_id)` đúng một lần cho event hợp lệ.
- [ ] **T03.22** Kiểm tra `centroid_shift > ctx.baseline["embedding_centroid_shift_max"]` (hiện là 0.0435), không tự dùng 0.039/0.040 làm chuẩn chính thức.
- [ ] **T03.23** Kiểm tra `avg_doc_age_days > ctx.baseline["corpus_avg_doc_age_days_max"]` (hiện là 49.7955), không mặc định 41 hoặc 48 ngày.
- [ ] **T03.24** Mỗi chỉ số vượt ngưỡng hoặc cả hai vượt ngưỡng đều phải cảnh báo. Test trạng thái sạch, lỗi mỗi chiều, cả hai, tại ngưỡng, dữ liệu không hợp lệ.

**GATE T03:** Mỗi loại lỗi có ít nhất một test dương, một test âm và một test biên. Có lý do cho ngưỡng thay đổi. Không viết quy tắc gắn với ID của lịch Practice.

## 6. T04 — KIỂM SOÁT CHI PHÍ VÀ TRÁNH GỌI TOOL THỪA

- [ ] **T04.01** Xác nhận mỗi event hợp lệ gọi đúng RPC ứng với loại sự kiện, tối đa 1 lần trong phương án đầy đủ; cache không phát sinh gọi lặp khi cùng khóa.
- [ ] **T04.02** Trong fake toolkit, đếm số lần gọi từng RPC; test 5 event hợp lệ mỗi event một công cụ, không gọi công cụ trái loại.
- [ ] **T04.03** Kiểm tra `spend_so_far()`/`budget_remaining()` không được dùng như lý do duy nhất để im lặng khi ngân sách đã hết. Harness chấp nhận vượt ngân sách và trừ điểm.
- [ ] **T04.04** Không xây bộ lọc metadata bỏ RPC khi metadata chỉ nêu `table`, `job`, `batch_id` mà chưa đủ thông tin xác định bình thường. Nếu có bộ lọc, phải test rằng nó không bỏ sót lỗi rõ; ghi lý do và tác động điểm.
- [ ] **T04.05** Sau Practice/Public, lấy `cost_ledger` thực và so với ngân sách. Không tính chi phí bằng cách nhân tổng event với một số cố định; mỗi RPC có giá khác nhau.
- [ ] **T04.06** Nếu `cost_overage` nằm trong (0,1), mỗi credit vượt ngân sách 220 gây phạt khoảng `20/220 = 0.09091` điểm; với ngân sách 320 là `20/320 = 0.06250` điểm. Một TP bổ sung đáng giá `50 / n_faulty` điểm và một FP bổ sung mất `30 / n_clean` điểm **trên cùng pha**. Không giả định biết `n_faulty`/`n_clean` ở Public/Private.
- [ ] **T04.07** Ưu tiên tính điểm theo công thức thay vì mục tiêu “không được vượt ngân sách”. Không giảm 1–2 credit bằng cách bỏ kiểm tra nếu rủi ro FN lớn hơn lợi ích.

**GATE T04:** Có test số lần gọi và báo cáo giải thích chi phí bằng dữ liệu thực khi có kết quả pha.

---
## 7. T05 — KIỂM THỬ TỰ ĐỘNG TRƯỚC KHI CHẠY LUỒNG THẬT

- [ ] **T05.01 — Kiểm tra số lượng.** Mở `solution/tests/test_defense.py` và `solution/tests/test_practice_evaluator.py`; đếm tên test đang tồn tại, không xóa test khó chỉ để tăng tỷ lệ PASS. Yêu cầu ít nhất 35 bài hiện có còn chạy được.
- [ ] **T05.02 — Kiểm tra tất cả kiểu lỗi.** Đảm bảo từng event có: sạch, lỗi đơn, lỗi kết hợp nếu áp dụng, đúng bằng ngưỡng, sát ngưỡng, thiếu trường, tool trả `error`, sai kiểu. Nếu thiếu, thêm test có tên dễ hiểu.
- [ ] **T05.03 — Kiểm tra cache.** Hai lần gọi cùng RPC và cùng tham số trong một `ctx.state` phải trả kết quả đã lưu và chỉ tăng bộ đếm RPC lần đầu. Đổi một tham số phải gọi mới. Tạo context mới thì không được dùng lại cache cũ.
- [ ] **T05.04 — Kiểm tra `Verdict.reason`.** Khi `alert=True`, lý do phải giải thích điều kiện lỗi; không ghi chung chung “anomaly” hoặc “bad data”. Khi tool lỗi, lý do phải cho biết không có đủ dữ liệu, không tạo kết luận bất thường giả.
- [ ] **T05.05 — Kiểm tra thứ tự và kết quả ổn định.** Gọi cùng chuỗi event lên hai context khởi tạo giống nhau; so sánh danh sách `alert`, `pillar`, `reason`. Phải trùng nhau hoàn toàn.
- [ ] **T05.06 — Kiểm tra công cụ đánh giá Practice.** Tạo báo cáo giả chỉ trong test, gồm TP/FP/FN/TN đã biết, và yêu cầu `evaluate_practice.evaluate()` khớp phép tính thủ công. Thêm test `seq` trùng, `seq` thiếu, nhãn không phải bool, khác số verdict, pha khác Practice, chênh lệch score.
- [ ] **T05.07 — Kiểm tra an toàn tĩnh.** Xem toàn bộ `solution/defense.py`: không có `open`, `exec`, `eval`, `__import__` tùy ý, `subprocess`, `socket`, truy cập `phases/`, bảng ánh xạ ID thành alert, đọc nhãn Practice, hay print stdout. Không tự động xóa mã bằng tìm-thay khi một từ nằm trong comment; kiểm tra thủ công đoạn liên quan.
- [ ] **T05.08 — Chạy lại đầy đủ.** Chạy lệnh cú pháp, selfcheck và unit tests của T01. Không chấp nhận `skipped` mà không nêu rõ lý do. Ghi tổng số PASS/FAIL/SKIP cùng đầu ra lệnh.
- [ ] **T05.09 — Kiểm tra thay đổi.** Chạy `git diff --check`; kiểm tra đường dẫn đã sửa bằng `git status --short`. Không sửa ngoài `solution/`, `submission/`.

**GATE T05:** 0 FAIL, 0 ERROR; selfcheck 5/5; có test cho các nhánh nêu trên. Chỉ khi đạt mới chạy Practice.

## 8. T06 — PRACTICE THẬT, ĐỐI CHIẾU 120 NHÃN VÀ TÍNH ĐIỂM

### 8.1. Chạy harness gốc

Windows PowerShell:

```powershell
$PY = ".\.venv\Scripts\python.exe"
& $PY harness/run.py --phase practice --defense solution/defense.py --out solution/practice_report.json
if ($LASTEXITCODE -ne 0) { throw "Practice failed" }
& $PY solution/evaluate_practice.py --report solution/practice_report.json --answers phases/practice_answer_key.json
if ($LASTEXITCODE -ne 0) { throw "Practice evaluation mismatch" }
```

Linux/macOS:

```bash
PY=.venv/bin/python
"$PY" harness/run.py --phase practice --defense solution/defense.py --out solution/practice_report.json
"$PY" solution/evaluate_practice.py --report solution/practice_report.json --answers phases/practice_answer_key.json
```

- [ ] **T06.01 — Kiểm tra điều kiện trước chạy.** Đã đạt T05. `solution/practice_report.json` nếu đã có phải được lưu hoặc đổi tên an toàn trước khi ghi đè; không để báo cáo cũ bị hiểu nhầm là của mã mới.
- [ ] **T06.02 — Chạy một lượt Practice gốc.** Không sửa tham số mặc định trong `harness/run.py`. Không đặt môi trường hoặc monkey patch để can thiệp điểm.
- [ ] **T06.03 — Kiểm tra mã thoát và tệp JSON.** CLI exit code phải bằng 0, tệp báo cáo phải có `result`, `signature`, `result.phase="practice"` và `result.verdicts`.
- [ ] **T06.04 — Kiểm tra độ dài.** `len(result.verdicts) == 120`; đáp án Practice có 120 nhãn. Không dùng `zip` trần nếu chưa xác nhận đủ số phần tử và đối sánh `seq`.
- [ ] **T06.05 — Ghép đúng theo `seq`.** Mỗi `seq` ở đáp án và verdict là duy nhất, có cùng tập giá trị. Nếu trùng hoặc thiếu, dừng trước khi tính điểm.
- [ ] **T06.06 — Tính ma trận.** Tính TP, FP, FN, TN bằng nhãn `is_faulty` và dự đoán `alert`. Kiểm tra `TP+FP+FN+TN=120`, `TP+FN=33`, `FP+TN=87` đối với bản Practice hiện hành.
- [ ] **T06.07 — Tính tỷ lệ.** Tính `TPR=TP/33` và `FPR=FP/87`. So với `result.tpr`/`result.fpr`, cho phép sai số làm tròn 4 chữ số thập phân.
- [ ] **T06.08 — Tính điểm.** Lấy `result.cost_ledger`, `result.budget=220`, tính `cost_overage`, sau đó `round(100*(0.5*TPR-0.3*FPR-0.2*min(overage,1)),2)`. So với `result.score`, sai lệch cho phép chỉ do làm tròn.
- [ ] **T06.09 — Kiểm tra bằng evaluator.** `solution/evaluate_practice.py` phải trả mã thoát 0 và `matches_harness` đều `true`. Nếu script báo sai, kiểm tra dữ liệu và phép tính, không sửa nhãn để làm khớp.
- [ ] **T06.10 — Ghi số liệu.** Ghi TP, FP, FN, TN, TPR, FPR, cost, overage và score vào `solution/EXECUTION_LOG.md` cùng SHA hoặc SHA-256 của `defense.py` **(chỉ băm mã nguồn của chính bạn, không băm tệp khóa)**.
- [ ] **T06.11 — Kiểm tra lỗi theo trụ cột.** Phân loại FN theo `pillar`/`fault_key` có trong đáp án Practice. Lưu ý: với event bình thường, đáp án hiện có `pillar=null`, vì vậy **không tự gán FP vào một pillar khi không có thông tin tương ứng**.
- [ ] **T06.12 — Kiểm tra tính xác định.** Chạy lại Practice **với đúng cùng mã**; dùng tên đầu ra riêng `solution/practice_repeat_report.json`. Kết quả `verdicts`, score và cost phải trùng. Nếu khác, tìm lỗi trạng thái/ngẫu nhiên trước khi tối ưu.

**ĐIỀU KIỆN NHÁNH:**

- Nếu không chạy được harness: `STOP-ENV` hoặc `STOP-TEST` theo lỗi thực; không tự dựng `practice_report.json`.
- Nếu evaluator không khớp: `STOP-TEST`.
- Nếu có FP/FN: chuyển T07 để phân tích, không sửa ngay 5 nhóm logic cùng lúc.
- Nếu điểm Practice đạt 50 và các bài test sát biên đạt: có thể bỏ vòng cải thiện không cần thiết, chuyển T08.

## 9. T07 — VÒNG LẶP CẢI THIỆN CÓ KIỂM SOÁT

**Chỉ được dùng nhãn Practice đã công bố và test giả lập hợp lệ.** Không mở lịch sự kiện mã hóa. Không tra cứu nhãn Private. Không dựng bảng quyết định theo `seq` của Practice.

### 9.1. Một vòng bắt buộc gồm đúng 9 động tác

- [ ] **T07.01 — Chụp mốc trước sửa.** Lưu commit/SHA của `defense.py` đang dẫn đầu, Practice TP/FP/FN/TN, score và chi phí vào bảng ứng viên. Nếu chưa commit, lưu diff để có thể hoàn tác riêng thay đổi của mình mà không đụng thay đổi người khác.
- [ ] **T07.02 — Chọn đúng một vấn đề.** Ưu tiên: lỗi không trả Verdict/không gọi đúng API → FP do điều kiện sai → FN lỗi rõ → FN tinh vi → giảm chi phí. Chỉ chọn một nhóm nguyên nhân mỗi vòng.
- [ ] **T07.03 — Viết giả thuyết có thể bác bỏ.** Ví dụ: “Quy tắc hợp thành ở `data_batch` đang cảnh báo sai khi hai chỉ số sạch sát biên; nếu tăng yêu cầu đồng thời, FP giảm mà TP không đổi”. Không ghi “tối ưu thêm threshold”.
- [ ] **T07.04 — Viết test trước.** Tạo một test tái hiện lỗi cần sửa và một test chống lỗi ngược lại. Ví dụ, test giảm FP phải đi kèm test không bỏ sót lỗi phối hợp rõ.
- [ ] **T07.05 — Chỉ sửa một nhóm điều kiện.** Không thay hàng loạt ngưỡng hoặc năm handler trong một lượt. Không thay harness/fixture thật.
- [ ] **T07.06 — Kiểm thử.** Chạy `py_compile`, `selfcheck`, `unittest`; mọi test phải PASS. Nếu FAIL, sửa đúng vấn đề hoặc hoàn tác ứng viên.
- [ ] **T07.07 — Chạy Practice.** Tạo báo cáo có tên riêng như `solution/practice_candidate_01.json`; dùng evaluator tính score thực. Không ghi đè bằng chứng của ứng viên tốt nhất.
- [ ] **T07.08 — Quyết định.** So score, FPR, TPR, cost và độ phức tạp theo thứ tự mục 0.1. Nếu không tốt hơn hoặc làm mất test biên, hoàn tác đúng thay đổi vừa làm. Nếu tốt hơn, giữ và cập nhật “best candidate”.
- [ ] **T07.09 — Ghi kết quả.** Mỗi vòng có mã ứng viên, mô tả một thay đổi, lệnh và số liệu, quyết định `KEEP`/`REVERT`, cùng bằng chứng.

### 9.2. Giới hạn và điểm dừng

- Tối đa **5 vòng sửa có chủ đích** sau khi có baseline Practice. Không tạo vòng vô hạn.
- Nếu 2 vòng liên tiếp không cải thiện và không có lỗi kỹ thuật rõ ràng, dừng và giữ ứng viên tốt nhất.
- Khi `FP=0` và `FN=0` ở Practice, không tiếp tục hạ ngưỡng để tìm thêm TP không tồn tại.
- Không biến hằng số 0.65, 0.84, 1.35 thành chân lý; nếu thiếu bằng chứng kiểm thử, giữ mức có thể giải thích hơn.
- Nếu sau 5 vòng Practice còn FP/FN, ghi số liệu thực, giữ phương án tốt nhất. Không khai “đạt tối đa” hoặc bịa một bản report tốt hơn.

### 9.3. Mẫu bảng ứng viên

| Ứng viên | SHA/commit | Thay đổi duy nhất | Unit/selfcheck | TP | FP | FN | TN | TPR | FPR | Cost | Score | Quyết định |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| B0 | điền sau chạy | bản trước hiệu chỉnh | điền |  |  |  |  |  |  |  |  | baseline |
| B1 | điền sau chạy | một giả thuyết | điền |  |  |  |  |  |  |  |  | KEEP/REVERT |

Để tránh nhầm lẫn, chỉ điền số đã thu được qua harness, không điền số ví dụ vào bảng kết quả.

**GATE T07:** Đã có ứng viên tốt nhất, đủ bằng chứng và tối thiểu không còn lỗi giao diện. Bắt buộc lưu phiên bản được chọn trước khi chuyển Public.

## 10. T08 — PUBLIC THẬT, KIỂM TRA TÍNH KHÁI QUÁT

Lệnh Windows:

```powershell
$PY = ".\.venv\Scripts\python.exe"
& $PY harness/run.py --phase public --defense solution/defense.py --out solution/public_report.json
if ($LASTEXITCODE -ne 0) { throw "Public failed" }
```

Lệnh Linux/macOS:

```bash
.venv/bin/python harness/run.py --phase public --defense solution/defense.py --out solution/public_report.json
```

- [ ] **T08.01 — Chụp mã.** Ghi SHA/hash `solution/defense.py`, danh sách unit test PASS và Practice score của đúng bản sắp chạy.
- [ ] **T08.02 — Chạy Public lần 1.** Dùng harness gốc, không chỉnh mã hay pha trong khi chạy.
- [ ] **T08.03 — Xác nhận kết quả.** Báo cáo có `result.phase="public"`, `score`, `tpr`, `fpr`, `cost_ledger`, `budget`, `cost_overage` và `per_pillar_band` nếu đã chấm được theo trụ cột.
- [ ] **T08.04 — Không tìm dữ liệu chi tiết bị ẩn.** Không tìm `verdicts` riêng lẻ, đáp án Public hoặc TP/FP/FN/TN chi tiết; không giải mã `.enc`, không dùng debug để trích xuất nhãn.
- [ ] **T08.05 — Đánh giá số liệu.** Ghi TPR/FPR/cost/score và dải của các trụ cột. Với mỗi dải `high`, chỉ được nói “TPR của trụ cột tối thiểu 0.75”, không nói “toàn bộ lỗi đã phát hiện”.
- [ ] **T08.06 — Phân tích suy giảm.** Nếu FPR Public tăng cao, kiểm tra trước các quy tắc có nguy cơ FP: hợp thành nhiều chiều, `downstream_count=0` trên mô hình đầu cuối, SLA giả định, ngưỡng 0.65 chưa kiểm chứng. Không suy ra event cụ thể nào sai khi báo cáo không cung cấp event.
- [ ] **T08.07 — Quy tắc chạy lại.** Chỉ được chạy Public thêm **tối đa một lần** khi đã tìm được lỗi kỹ thuật hoặc quy tắc tổng quát có bằng chứng từ test/Practice. Thêm test, sửa một thay đổi, chạy lại unit + Practice rồi mới chạy Public lần 2. Không dùng Public như bộ dò tham số.
- [ ] **T08.08 — Chọn phiên bản.** Nếu Public lần 2 tồn tại, so kết quả và chất lượng kiểm thử của hai bản; giữ bản có khả năng khái quát tốt hơn. Không coi cải thiện dải `high` là đủ nếu score/FPR xấu đi.
- [ ] **T08.09 — Ghi giới hạn.** Nếu một trụ cột dưới `high`, ghi điều có thể kết luận và điều không thể xác minh. Không viết ra số FN hay FP theo trụ cột khi chỉ có band.

**GATE T08:** Public chạy thành công và ghi kết quả thật; tất cả bài kiểm thử vẫn đạt. Nếu Public không chạy được do môi trường, dừng, không thay bằng dữ liệu mô phỏng.

## 11. T09 — KHÓA MÃ TRƯỚC PRIVATE

**Đây là cổng chặn không được bỏ qua.** Từ thời điểm khóa mã, không điều chỉnh ngưỡng dựa trên kết quả Private.

- [ ] **T09.01** Chạy lại toàn bộ T01 và T05. Phải có 0 FAIL, 0 ERROR; selfcheck đúng 5/5.
- [ ] **T09.02** Xác nhận đã có Practice report thật, evaluator đối chiếu đúng, Public report thật và kết luận lựa chọn mã.
- [ ] **T09.03** Chạy `git diff --check`, xem `git status --short`, xác nhận mọi thay đổi chỉ nằm trong `solution/` và `submission/`.
- [ ] **T09.04** Rà lại `defense.py`: không đọc file, không in stdout, không truy cập mô-đun harness, không chứa bảng ID, không điều chỉnh theo pha.
- [ ] **T09.05** Kiểm tra `solution/private_report.json`: nếu đã tồn tại, xác định có phải kết quả từ lần chạy trước hay không. **Không chạy lại khi đã có kết quả Private hợp lệ.** Nếu không xác minh được nguồn gốc, đánh dấu `BLOCKED` thay vì ghi đè.
- [ ] **T09.06** Ghi SHA-256 `defense.py`, SHA commit, điểm Practice và Public vào `solution/EXECUTION_LOG.md`. Từ đây xem đó là **phiên bản khóa**.
- [ ] **T09.07** Xác nhận `phases/private.key` và `phases/private_schedule.json.enc` tồn tại bằng kiểm tra đường dẫn, không đọc nội dung.
- [ ] **T09.08** Nếu môi trường chưa đủ hoặc có nghi vấn vi phạm luật, dừng trước Private. Không nộp kết quả mô phỏng thay thế.

**GATE T09:** có bằng chứng kiểm thử thật và chữ ký mã đã khóa; không có sửa đổi không kiểm soát; Private đã sẵn sàng.

## 12. T10 — CHẠY PRIVATE CHÍNH THỨC, KHÔNG TINH CHỈNH SAU KẾT QUẢ

Windows:

```powershell
$PY = ".\.venv\Scripts\python.exe"
& $PY harness/run.py --phase private --defense solution/defense.py --out solution/private_report.json
if ($LASTEXITCODE -ne 0) { throw "Private execution failed" }
```

Linux/macOS:

```bash
.venv/bin/python harness/run.py --phase private --defense solution/defense.py --out solution/private_report.json
```

- [ ] **T10.01 — Kiểm tra trước khi chạy.** T09 phải PASS, `private_report.json` chưa có báo cáo hợp lệ. Nếu có, không ghi đè.
- [ ] **T10.02 — Chạy một lượt.** Không chạm vào mã khi harness đang chạy. Không can thiệp cơ chế cách ly hay chi phí.
- [ ] **T10.03 — Kiểm tra exit code.** Phải bằng 0. Nếu chương trình crash trước khi sinh report, ghi stderr/traceback và xác định là lỗi môi trường hay lỗi `defense.py` bằng bài test. Chỉ chạy lại khi **chưa có kết quả hợp lệ**, và phải ghi rõ lý do; không chạy lại để chọn điểm tốt hơn.
- [ ] **T10.04 — Kiểm tra cấu trúc JSON.** Có `result` object và `signature` là chuỗi không rỗng; `result.phase="private"`, có `score`, `tpr`, `fpr`, `cost_overage` đúng kiểu; tên file đúng `solution/private_report.json`.
- [ ] **T10.05 — Kiểm tra không bị sửa.** Sau khi tạo thành công, không mở để sửa, định dạng lại, cắt trường hay ký lại. Được phép đọc trường công khai để báo cáo tổng hợp và xác nhận tồn tại.
- [ ] **T10.06 — So mã đã khóa.** Tính lại SHA-256 `solution/defense.py` và so với T09. Nếu khác, **không tuyên bố kết quả thuộc bản đã khóa**; dừng và báo vấn đề.
- [ ] **T10.07 — Chốt Private.** Ghi duy nhất `score`, `tpr`, `fpr`, `cost_overage`, trạng thái chữ ký có tồn tại, hash file báo cáo và mã nguồn vào `solution/EXECUTION_LOG.md`. Không tính lại chữ ký bằng cách truy cập khóa.
- [ ] **T10.08 — Không mở vòng điều chỉnh mới.** Kể cả Private score thấp, không chỉnh ngưỡng để chạy lại. Chỉ báo cáo trung thực hạn chế và điều đã học.

**GATE T10:** có `private_report.json` thật, có chữ ký do harness tạo, mã không đổi sau khi khóa.

---
## 13. T11 — HOÀN THIỆN BÁO CÁO TIẾNG VIỆT BẰNG KẾT QUẢ THỰC

Có hai tệp với mục đích khác nhau: `solution/reflection.md` là tài liệu nộp, **không quá 1 trang** theo README; `solution/FINAL_REPORT.md` là tài liệu bổ trợ để người xem hiểu kết quả và bằng chứng, không thay thế reflection hoặc báo cáo có chữ ký.

- [ ] **T11.01 — Cập nhật `solution/reflection.md`.** Thay mọi câu còn ghi “chưa chạy Practice/Public/Private” bằng trạng thái thực tế, **chỉ nếu** pha tương ứng đã chạy thật. Nếu còn pha chưa chạy, giữ đúng sự thật và giải thích lý do.
- [ ] **T11.02 — Reflection trả lời đủ hai câu.** (1) Loại lỗi nào khó phát hiện nhất, vì sao? (2) Nếu làm lại sẽ cân đối độ bao phủ, cảnh báo giả và chi phí thế nào? Cần có ví dụ cụ thể từ giải pháp, không chỉ nhận xét chung.
- [ ] **T11.03 — Giữ reflection gọn.** Mục tiêu khoảng 350–500 từ tiếng Việt (chỉ là hướng dẫn độ dài; rà lại việc hiển thị trên một trang nếu có công cụ phù hợp). Tránh bảng dài và đoạn sao chép nguyên văn tài liệu.
- [ ] **T11.04 — Viết `solution/FINAL_REPORT.md`.** Đề cương đúng thứ tự: Bối cảnh → kiến trúc xử lý → các quyết định theo trụ cột → thử nghiệm → kết quả thật → phân tích sai sót → đánh đổi chi phí → giới hạn → cải tiến tiếp theo → kết luận.
- [ ] **T11.05 — Bảng số liệu Practice.** Chỉ điền số thật từ `evaluate_practice.py`: TP, FP, FN, TN, TPR, FPR, cost, overage và score. Trích tệp báo cáo, SHA mã và ngày chạy.
- [ ] **T11.06 — Bảng số liệu Public.** Chỉ điền điểm/tỷ lệ/chi phí và `per_pillar_band` được công bố. Không tự dựng ma trận nhầm lẫn, tỷ lệ lỗi theo loại hoặc nhãn từng event.
- [ ] **T11.07 — Bảng số liệu Private.** Chỉ điền `score`, `tpr`, `fpr`, `cost_overage` có trong kết quả chính thức. Không nói đã đạt bao nhiêu TP/FP hoặc phân loại lỗi nào nếu Private không xuất những số đó.
- [ ] **T11.08 — Phân tích chi phí.** Giải thích vì sao tối đa một RPC đo lường theo mỗi event là đường cơ sở, lúc nào cache có ích, vì sao vượt ngân sách ít có thể tốt hơn bỏ sót lỗi. Phân biệt tính toán lý thuyết và đo thực tế.
- [ ] **T11.09 — Giới hạn.** Nêu rõ thử nghiệm Practice có nhiều lỗi dễ hơn, Public chỉ có thông tin tổng hợp, Private khó hơn; không khẳng định tính tối ưu trên dữ liệu chưa thấy.
- [ ] **T11.10 — Viết đúng văn phong.** Dùng tiếng Việt chuẩn, câu có chủ ngữ và hành động rõ. Giữ các tên API bằng tiếng Anh vì là định danh trong mã. Khi dùng TPR/FPR lần đầu, giải thích “tỷ lệ phát hiện lỗi” và “tỷ lệ cảnh báo nhầm”. Không dùng những cụm sáo rỗng như “đột phá”, “tối ưu vượt trội”, “hoàn hảo” nếu không có bằng chứng.
- [ ] **T11.11 — Đối chiếu số liệu.** Mọi con số trong báo cáo phải truy ngược được đến một trong ba report do harness tạo hoặc `evaluate_practice.py`. Không lấy số trong mô phỏng để thay số thật.
- [ ] **T11.12 — Tự kiểm tra độc lập.** Đọc lại một lần với vai người chấm: có hiểu phương pháp, cách kiểm thử, số liệu, giới hạn và bài học không? Nếu có câu không kiểm tra được, sửa hoặc bỏ câu.

### Mẫu bố cục reflection (không điền số giả)

```markdown
# Nhìn lại bài lab Data Siege

Tôi gặp khó khăn lớn nhất khi [loại lỗi thực sự khó], vì [nguyên nhân kỹ thuật và ví dụ].
Để xử lý, tôi [quy tắc chung]. Tôi kiểm tra phương án này bằng [loại kiểm thử/bộ dữ liệu].

Trên Practice, giải pháp [số liệu thật nếu đã chạy]. Ở Public, [chỉ ghi kết quả
được công bố]. Kết quả Private là [nếu đã có]. Các kết quả không cho biết [giới
hạn xác định].

Nếu cải thiện tiếp, tôi sẽ [một thay đổi có lý do], đồng thời theo dõi TPR,
FPR và chi phí. Tôi không coi việc giảm chi phí là đủ nếu làm bỏ sót nhiều lỗi.
```

**GATE T11:** Nội dung bám sát bằng chứng, tiếng Việt tự nhiên, reflection trong giới hạn một trang; không bịa kết quả hoặc che giấu thử nghiệm chưa thực hiện.

## 14. T12 — KIỂM TRA HỒ SƠ NỘP, COMMIT, PUSH VÀ XÁC NHẬN SAU PUSH

- [ ] **T12.01 — Kiểm tra tệp bắt buộc.** `solution/defense.py`, `solution/reflection.md`, `solution/private_report.json`, `submission/manifest.json` đều tồn tại và không rỗng.
- [ ] **T12.02 — Kiểm tra manifest.** Nội dung hiện yêu cầu `team_or_student = "VuHieuThien-2A202602867"`; 3 đường dẫn phải đúng với các tệp thật. Dùng bộ phân tích JSON để xác nhận cú pháp hợp lệ; không đổi manifest trỏ tới report giả hoặc report của pha khác.
- [ ] **T12.03 — Kiểm tra Private JSON.** `result.phase` phải là `private`, có `result.score`, `result.tpr`, `result.fpr`, `result.cost_overage`, `signature` không rỗng. Không khẳng định chữ ký đã được xác thực mật mã nếu chỉ kiểm tra sự tồn tại.
- [ ] **T12.04 — Kiểm tra quy định tệp.** `git status --short` và `git diff --name-only` không xuất hiện đường dẫn ngoài `solution/`, `submission/` do agent chỉnh sửa. Không đưa `.venv/`, khóa, ciphertext, thư mục `harness/` hoặc cache không cần thiết vào commit.
- [ ] **T12.05 — Chạy kiểm thử cuối.** Lặp `py_compile`, `harness/selfcheck.py`, toàn bộ `unittest`. Sau khi Private đã tạo, chỉ được sửa tài liệu/báo cáo ngoài `defense.py`; mã khóa không thay đổi.
- [ ] **T12.06 — Xác minh hash `defense.py`.** Phải giống T09 và T10. Nếu khác, dừng: không được gắn kết quả Private với mã không trùng.
- [ ] **T12.07 — Stage file rõ ràng.** Dùng `git add solution/defense.py solution/reflection.md solution/private_report.json submission/manifest.json solution/FINAL_REPORT.md solution/EXECUTION_LOG.md` và các test/script thuộc `solution/` nếu đã được phép giữ trong repo. Không sử dụng `git add .` khi chưa kiểm tra toàn bộ trạng thái.
- [ ] **T12.08 — Kiểm tra stage.** Chạy `git diff --cached --name-only`, `git diff --cached --check`. Nếu xuất hiện tệp cấm hoặc lỗi, bỏ riêng tệp đó khỏi stage bằng lệnh phù hợp; không xóa dữ liệu gốc.
- [ ] **T12.09 — Commit.** Chạy `git commit -m "Complete Data Siege lab with verified reports"` sau khi mọi cổng đã PASS. Không ghi “complete” khi thiếu Private report.
- [ ] **T12.10 — Push.** Chạy `git push origin main` nếu không có commit mới của người khác ở remote. Nếu push bị từ chối do nhánh đi trước, đồng bộ theo cách không phá lịch sử, kiểm tra lại diff và test rồi push lại. Không force push.
- [ ] **T12.11 — Đọc lại từ GitHub.** Chạy `git ls-remote origin refs/heads/main` hoặc dùng GitHub API; so SHA với `git rev-parse HEAD`. Mở lại 4 tệp bắt buộc trên GitHub để chắc chắn đã push đúng.
- [ ] **T12.12 — Kiểm tra trạng thái cuối.** `git status --short` phải rõ ràng; nếu còn file kết quả Practice/Public chưa commit, ghi đó là artifact địa phương, không nhầm thành thiếu hồ sơ bắt buộc.
- [ ] **T12.13 — Tổng kết cho người dùng.** Trả: URL commit, số unit test PASS, 5/5 handler, Practice TP/FP/FN/TN/score, Public score/FPR/cost, Private score/FPR/overage, trạng thái chữ ký, hạn chế còn lại. Mỗi số phải lấy từ bằng chứng thực. Không tự đặt số.

**DONE:** đã có báo cáo Private do harness ký; đủ file nộp; commit và push thật; SHA remote khớp; báo cáo phản ánh đúng kết quả.

---

## 15. BẢNG XỬ LÝ LỖI: GẶP LÀ LÀM GÌ?

| Triệu chứng | Kiểm tra ngay | Hành động cho phép | Điều kiện chạy tiếp |
|---|---|---|---|
| `selfcheck` chỉ hiện 4/5 | `register(ctx)` và tên event | Sửa đăng ký trong `solution/defense.py` | Chạy lại và nhìn thấy `5/5` |
| `ModuleNotFoundError: api` trong unit test | Đang chạy từ repo root? Test có thêm `harness/child_env` vào `sys.path`? | Sửa phần khởi tạo test trong `solution/tests/` | Unit test PASS |
| `ImportError` từ child | `harness/child_env/child_driver.py` có allowlist nào? | Bỏ import trái phép khỏi `solution/defense.py`; dùng API công khai | Practice chạy mà không crash |
| `EOFError` hoặc tiến trình con chết | Có `print()` stdout? Có handler gọi thoát tiến trình? Có log stderr quá nhiều? | Loại bỏ stdout/ngoại lệ trong defense, test từng handler | Selfcheck + unit + Practice PASS |
| `{"error": ...}` từ RPC | Tham số ID sai, chưa dispatch, thiếu trường? | Kiểm tra đúng trường payload và cú pháp RPC; không tự thử ID tương lai | Handler trả Verdict hợp lệ và không tự cảnh báo sai |
| `PermissionError` | Code đã gọi `open()` hoặc truy cập tệp? | Loại thao tác I/O khỏi defense; dùng `ctx.state` | Sandbox không lỗi |
| Practice thiếu `verdicts` | File report của phiên bản harness nào? Có đúng phase practice? | Đọc `harness/run.py` và cập nhật mã đánh giá ngoài defense nếu định dạng thay đổi | Đủ 120 verdict hoặc ghi rõ BLOCKED |
| Practice evaluator sai `seq` | Có report cũ hoặc số event thay đổi? | Tạo lại report đúng phiên bản, kiểm tra tập `seq` | Tập `seq` khớp tuyệt đối |
| Practice score không khớp | Công thức, làm tròn, `cost_ledger` và budget | Sửa evaluator nếu có bằng chứng, không sửa harness | Sai số trong giới hạn làm tròn |
| FP tăng sau chỉnh ngưỡng | Thay đổi có quá nhạy không? | Hoàn tác đúng thay đổi vừa làm; thêm test sạch gần biên | Unit + Practice chứng minh tốt hơn |
| Public FPR cao | Quy tắc tổng quát nào có nguy cơ báo giả? | Một vòng sửa dựa trên test/Practice, tối đa một lần chạy lại Public | Có báo cáo thực và ghi rõ rủi ro |
| Public overage > 0 | `cost_ledger`, `budget`, điểm phạt thực | So với giá trị TPR, không tắt RPC theo phản xạ | Chọn bản có điểm tốt hơn |
| Không có `private.key` hoặc ciphertext | Chỉ kiểm tra tệp tồn tại | Dừng T10, không đọc hoặc tự tạo khóa | Nhà tổ chức phát hành đủ file |
| Private chạy lỗi trước report | Exit code, lỗi môi trường/handler | Sửa lỗi kỹ thuật có bằng chứng; không đổi ngưỡng dựa trên nhãn ẩn | Chạy lại chỉ khi chưa có kết quả hợp lệ |
| Private score thấp nhưng report hợp lệ | Kiểm tra JSON và SHA mã | **Không chạy lại để dò điểm**; ghi nhận hạn chế | Tiến hành viết báo cáo và nộp |
| Push bị từ chối | Remote có commit mới? | Fetch, đối chiếu diff và merge fast-forward nếu được, chạy lại test | Push thường thành công, không force |

## 16. THỨ TỰ CẦN ƯU TIÊN NẾU THIẾU THỜI GIAN

1. **Không bỏ qua:** T00, T01, T02, T05, T06, T08, T09, T10, T11, T12. Đây là các bước bảo đảm chạy thật và nộp hợp lệ.
2. **Rà soát kỹ theo rủi ro:** T03, vì quy tắc cảnh báo giả có thể làm điểm giảm mạnh. Bắt đầu từ logic hợp thành của `data_batch`, logic zero-downstream của `lineage_run`, ngưỡng 0.65 của `feature_materialization`.
3. **Chỉ khi có bằng chứng cần thiết:** vòng cải thiện T07 và bộ lọc giảm chi phí T04. Không trì hoãn Private bằng việc thử ngưỡng không có điểm dừng.
4. **Không bao giờ bỏ:** kiểm tra chữ ký có tồn tại, mã đã khóa không đổi, manifest đúng file và xác nhận SHA GitHub sau push.

## 17. MẪU KẾT QUẢ CUỐI BẮT BUỘC CỦA AGENT

Chỉ điền số đã xác minh; không thay các giá trị `<...>` bằng ước đoán.

```markdown
# Báo cáo hoàn thành Data Siege

- Repository: <URL>
- Nhánh/commit đã push: <main/SHA hoặc BLOCKED>
- Phạm vi sửa: <danh sách file thuộc solution/ và submission/>
- Tuân thủ RULES.md: <PASS/FAIL + kiểm tra đã làm>
- Kiểm thử cú pháp: <PASS/FAIL>
- Kiểm thử đơn vị: <số PASS/FAIL/ERROR/SKIP>
- Selfcheck: <5/5 hoặc trạng thái thực>

## Practice
- Mã được kiểm tra: <hash>
- TP/FP/FN/TN: <...>
- TPR/FPR/chi phí/điểm: <...>
- Đối chiếu với harness: <PASS/FAIL>

## Public
- TPR/FPR/chi phí/điểm: <...>
- Kết quả từng pillar (band): <...>
- Những điều không thể kết luận: <...>

## Private
- Mã đã khóa có khớp: <PASS/FAIL>
- Báo cáo có chữ ký do harness tạo: <Có/Không>
- TPR/FPR/overage/điểm: <...>
- File: solution/private_report.json

## Kết luận
- Đã hoàn thành: <...>
- Chưa hoàn thành: <...>
- Giới hạn và rủi ro: <...>
- Đường dẫn bằng chứng: <...>
```

**Quy tắc cuối:** Agent phải nói thẳng việc chưa làm được. Một bản nộp có kiểm thử thật, có giới hạn được công bố và tuân thủ luật có giá trị hơn một bản báo cáo tự tuyên bố đạt điểm cao mà không có bằng chứng.