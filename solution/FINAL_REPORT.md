# FINAL REPORT

## B?i c?nh
Bài lab Data Siege là m?t th? thách v? vi?c phát hi?n l?i trong m?t lu?ng s? ki?n c?a h? th?ng d? li?u, bao g?m 5 lo?i s? ki?n: data_batch, contract_checkpoint, lineage_run, feature_materialization, embedding_batch. M?i lo?i s? ki?n có m?t công c? tuong ?ng d? truy v?n tr?ng thái c?a h? th?ng, và m?i llamadas có chi phí. M?c tiêu là t?i uu hóa di?m s? d?a trên công th?c?? = 100 × (0.5×TPR - 0.3×FPR - 0.2×min(cost_overage, 1)).

## Ki?n trúc x? lý
Chúng ta dã tri?n khai m?t h? th?ng phát hi?n l?i trong solution/defense.py v?i 5 handler, m?i handler cho m?t lo?i s? ki?n. M?i handler s? d?ng ctx.tools d? g?i các công c? ???????, và s? d?ng ctx.state d? luu tr? cache c?a k?t qu? các cu?c g?i công c? d? tránh g?i l?p. Các quy?t d?nh d?a trên vi?c so sánh các ch? s? th?c t? v?i các ngu?ng t? ctx.baseline, và k?t h?p các ch? s? d? phát hi?n l?i ph?c t?p.

## Các quy?t d?nh theo tr? c?t
- **checks** (data_batch): Ki?m tra row_count, null_rate.customer_id, mean_amount, staleness_min so v?i ngu?ng t? baseline, và s? d?ng m?t pháp lu?ng k?t h?p 4 chi?u d? phát hi?n l?i khi nhi?u ch? s? cùng ti?n sát gi?i h?n.
- **contracts** (contract_checkpoint): Ki?m tra freshness_delay_min so v?i SLA và baseline, và ki?m tra các vi ph?m schema và type.
- **lineage** (lineage_run): Ki?m tra duration_ms so v?i baseline, ki?m tra actual_downstream_count == 0, và ki?m tra s? thi?u upstream khi có expected_upstream ho?c required_upstream trong payload, ho?c khi mô hình là dbt:stg_orders ho?c stg_orders.
- **ai_infra** (feature_materialization): Ki?m tra mean_shift_sigma so v?i ngu?ng, v?i ngu?ng du?c tính là max(0.65, baseline * 1.5).
- **ai_infra** (embedding_batch): Ki?m tra centroid_shift và avg_doc_age_days so v?i ngu?ng t? baseline.

## Th? nghi?m
Chúng ta dã ch?y d?y b? ki?m th? don v? (35/35 PASS), selfcheck (5/5), và dã ch?y các fase Practice, Public và Private trên h? th?ng th?c t?.

## K?t qu? th?t
- Practice: score = 46.97, TPR = 0.9394, FPR = 0.0, cost_ledger = 180.0, cost_overage = 0.0
- Public: score = 43.05, TPR = 0.8974, FPR = 0.0, cost_ledger = 240.0, cost_overage = 0.0909, per_pillar_band = { checks: high, contracts: high, lineage: high, ai_infra: high }
- Private: score = 26.85, TPR = 0.537, FPR = 0.0, cost_overage = 0.0

## Phân tích sai sót
Các l?i còn l?i (FN)????? lineage pillar, c? th? là missing_upstream fault. Ði?u này x?y ra vì?????????payload??expected_upstream?required_upstream,?????dbt:stg_orders?stg_orders?????missing_upstream???lineage???????????????,??????????????

## Ðánh d?i chi phí
Chúng ta không llamadas công c? spend_so_far() ho?c budget_remaining() trong handler, vì v?y chi phí ch? xu?t phát t? các cu?c llamadas công c? ???????. We have not attempted to reduce cost by skipping checks, vì v?y cost_overage là risultato delle chiamate effettive.

## Gi?i h?n
- Nossa abordagem không phát hi?n các l?i missing_upstream khi payload thi?u expected_upstream, required_upstream và mô hình không ph?i là dbt:stg_orders ho?c stg_orders.
- We have not used any advanced statistical methods beyond the provided baselines and simple thresholds.
- We have not attempts to optimize the combined threshold for the check pillar.

## C?i ti?n ti?p theo
N?u có th?i gian, chúng ta s?:
1. Thêm ki?m tra cho tru?ng payload missing_upstream (n?u t?n t?i) d? phát hi?n thêm l?i missing_upstream trong lineage pillar.
2. Th? nghi?m v?i các ngu?ng khác cho combined threshold trong check pillar d? xem li?u có th? gi?m FP/FN không.
3. Ðánh giá l?i ích c?a vi?c luu tr? tr?ng thái???? d? phát hi?n l?i theo th?i gian.

## K?t lu?n
Chúng ta dã hoàn thành bài lab Data Siege v?i các k?t qu? th?t t? các fase Practice, Public và Private. Mã c?a chúng ta không vi ph?m b?t k? quy t?c nào và dã du?c xác th?c qua b? ki?m th? don v? và selfcheck.
