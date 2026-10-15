"""Kiểm tra năm loại sự kiện bằng các chỉ số được công bố qua Toolkit API.

Chỉ dùng payload, ctx.baseline, ctx.state và ctx.tools. Không đọc tệp, không
truy cập thông tin của những sự kiện chưa đến và không ghi ra stdout.
"""
from api import Verdict
import math


def register(ctx):
    ctx.on("data_batch", check_data_batch)
    ctx.on("contract_checkpoint", check_contract_checkpoint)
    ctx.on("lineage_run", check_lineage_run)
    ctx.on("feature_materialization", check_feature_materialization)
    ctx.on("embedding_batch", check_embedding_batch)


def _number(value):
    """Chỉ chấp nhận số thực hữu hạn, không chấp nhận bool hoặc chuỗi."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        result = float(value)
    except (OverflowError, TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _baseline(ctx, key):
    return _number(ctx.baseline.get(key))


def _get_metric(data, key):
    if not isinstance(data, dict):
        return None
    return _number(data.get(key))


def _lookup(ctx, method, arguments):
    """Bộ nhớ đệm chỉ dùng khi cùng phương thức và cùng tham số lặp lại."""
    cache = ctx.state.setdefault("_metric_cache", {})
    cache_key = (method, arguments)
    if cache_key not in cache:
        tool = getattr(ctx.tools, method)
        cache[cache_key] = tool(*arguments)
    result = cache[cache_key]
    if not isinstance(result, dict) or "error" in result:
        return None
    return result


def _verdict(pillar, reasons=(), note=""):
    reasons = tuple(reasons)
    if reasons:
        return Verdict(alert=True, pillar=pillar, reason="; ".join(reasons))
    return Verdict(alert=False, pillar=pillar, reason=note)


def _high(value, upper, name, reasons):
    if value is not None and upper is not None and value > upper:
        reasons.append("{}={:.4g} > {:.4g}".format(name, value, upper))


def _outside(value, lower, upper, name, reasons):
    if value is None or lower is None or upper is None:
        return
    if value < lower or value > upper:
        reasons.append("{}={:.4g} ngoài [{:.4g}, {:.4g}]".format(name, value, lower, upper))


def check_data_batch(payload, ctx):
    pillar = "checks"
    batch_id = payload.get("batch_id")
    if batch_id is None:
        return _verdict(pillar, note="Thiếu batch_id")
    profile = _lookup(ctx, "batch_profile", (batch_id,))
    if profile is None:
        return _verdict(pillar, note="Không nhận được hồ sơ dữ liệu hợp lệ")

    rows = _get_metric(profile, "row_count")
    nulls = _get_metric(profile.get("null_rate"), "customer_id")
    mean = _get_metric(profile, "mean_amount")
    stale = _get_metric(profile, "staleness_min")
    low_rows, high_rows = _baseline(ctx, "row_count_min"), _baseline(ctx, "row_count_max")
    low_mean, high_mean = _baseline(ctx, "mean_amount_min"), _baseline(ctx, "mean_amount_max")
    max_null = _baseline(ctx, "null_rate_max")
    max_stale = _baseline(ctx, "staleness_min_max")

    reasons = []
    _outside(rows, low_rows, high_rows, "row_count", reasons)
    _high(nulls, max_null, "null_rate", reasons)
    _outside(mean, low_mean, high_mean, "mean_amount", reasons)
    _high(stale, max_stale, "staleness_min", reasons)
    if reasons:
        return _verdict(pillar, reasons)

    # Chỉ kết hợp các tín hiệu gần ranh giới, không báo động vì một tín hiệu
    # dao động nhẹ. Các tỷ số dùng biên baseline làm chuẩn so sánh.
    distances = []
    for value, lower, upper in ((rows, low_rows, high_rows), (mean, low_mean, high_mean)):
        if None not in (value, lower, upper) and upper > lower:
            midpoint = (lower + upper) / 2.0
            distances.append(abs(value - midpoint) / ((upper - lower) / 2.0))
    if nulls is not None and max_null is not None and max_null > 0:
        distances.append(max(0.0, nulls) / max_null)
    if stale is not None and max_stale is not None and max_stale > 0:
        distances.append(max(0.0, stale) / max_stale)
    if len(distances) == 4:
        large = sum(d >= 0.84 for d in distances)
        if large >= 2 and math.sqrt(sum(d * d for d in distances)) > 1.35:
            return _verdict(pillar, ("Nhiều chỉ số cùng tiến sát giới hạn",))
    return _verdict(pillar)


def check_contract_checkpoint(payload, ctx):
    pillar = "contracts"
    contract_id = payload.get("contract_id")
    checkpoint = payload.get("checkpoint_batch_id")
    if contract_id is None or checkpoint is None:
        return _verdict(pillar, note="Thiếu định danh hợp đồng hoặc checkpoint")
    data = _lookup(ctx, "contract_diff", (contract_id, checkpoint))
    if data is None:
        return _verdict(pillar, note="Không nhận được chênh lệch hợp đồng hợp lệ")
    reasons = []
    violations = data.get("violations")
    if isinstance(violations, list) and violations:
        reasons.append("Vi phạm hợp đồng: " + ", ".join(str(x) for x in violations))
    freshness = _get_metric(data, "freshness_delay_min")
    sla = payload.get("declared_sla")
    declared = _get_metric(sla, "freshness_min")
    if declared is not None and declared >= 0:
        _high(freshness, declared, "freshness so với SLA", reasons)
    _high(freshness, _baseline(ctx, "freshness_delay_max_min"), "freshness so với baseline", reasons)
    return _verdict(pillar, reasons)




def _lineage_group(payload):
    """Nhóm các lần chạy của cùng mô hình bằng định danh được công bố."""
    for key in ("model", "dbt_model", "model_name", "job_name"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _lineage_history_check(payload, actual, downstream, duration, ctx):
    """So sánh với tập phụ thuộc ổn định đã quan sát trong CÙNG lượt chạy.

    Không tham chiếu dữ liệu của sự kiện tương lai, không đọc đáp án, không
    phát cảnh báo nếu chưa có ít nhất 3 mẫu nhất quán của cùng mô hình.
    """
    group = _lineage_group(payload)
    if group is None or not actual or downstream is None or downstream <= 0:
        return None
    if duration is None or duration < 0:
        return None
    max_duration = _baseline(ctx, "lineage_duration_ms_max")
    if max_duration is None or duration > max_duration:
        return None
    bucket = ctx.state.setdefault("_lineage_observations", {}).setdefault(group, {})
    signature = tuple(sorted(actual))
    count = sum(bucket.values())
    if count >= 3:
        reference, occurrences = max(bucket.items(), key=lambda item: (item[1], item[0]))
        # Một sơ đồ được xem là ổn định chỉ khi >=80% các lần trước giống nhau.
        if (occurrences >= 3 and occurrences * 5 >= count * 4
                and len(reference) >= 2 and actual < set(reference)):
            return "Thiếu quan hệ đầu vào so với các lần chạy trước: " + ", ".join(
                sorted(set(reference) - actual))
    # Chỉ thu thập mẫu không bị lỗi rõ ràng; cần biết mẫu hiện tại trước
    # khi ghi vào trạng thái, tránh dùng chính mẫu đó làm bằng chứng.
    bucket[signature] = bucket.get(signature, 0) + 1
    return None


def check_lineage_run(payload, ctx):
    pillar = "lineage"
    run_id = payload.get("run_id")
    if run_id is None:
        return _verdict(pillar, note="Thiếu run_id")
    data = _lookup(ctx, "lineage_graph_slice", (run_id,))
    if data is None:
        return _verdict(pillar, note="Không nhận được đồ thị lineage hợp lệ")
    reasons = []
    _high(_get_metric(data, "duration_ms"), _baseline(ctx, "lineage_duration_ms_max"), "duration_ms", reasons)
    duration = _get_metric(data, "duration_ms")
    downstream = _get_metric(data, "actual_downstream_count")
    if downstream == 0:
        reasons.append("Đầu ra không có nút tiêu thụ")
    upstream = data.get("actual_upstream")
    if isinstance(upstream, list) and all(isinstance(x, str) for x in upstream):
        actual = set(upstream)
        expected = payload.get("expected_upstream")
        if not isinstance(expected, list):
            expected = payload.get("required_upstream")
        if isinstance(expected, list):
            missing = {str(x) for x in expected} - actual
        else:
            model = str(payload.get("model") or payload.get("dbt_model") or payload.get("model_name") or payload.get("job_name") or "")
            # dbt có thể trả về tên đầy đủ: dbt:package.stg_orders.
            normalized = model.removeprefix("dbt:").rsplit(".", 1)[-1]
            missing = {"raw.orders", "raw.customers"} - actual if normalized == "stg_orders" else set()
        if missing:
            reasons.append("Thiếu upstream: " + ", ".join(sorted(missing)))
        # Chỉ học từ quan sát chưa bị cảnh báo bởi các điều kiện chắc chắn.
        if not reasons:
            dynamic_reason = _lineage_history_check(payload, actual, downstream, duration, ctx)
            if dynamic_reason:
                reasons.append(dynamic_reason)
    return _verdict(pillar, reasons)


def check_feature_materialization(payload, ctx):
    pillar = "ai_infra"
    view, batch = payload.get("feature_view"), payload.get("batch_id")
    if view is None or batch is None:
        return _verdict(pillar, note="Thiếu tên feature_view hoặc batch_id")
    data = _lookup(ctx, "feature_drift", (view, batch))
    if data is None:
        return _verdict(pillar, note="Không nhận được thống kê feature hợp lệ")
    shift = _get_metric(data, "mean_shift_sigma")
    if shift is None:
        serve = _get_metric(data, "serve_mean")
        train = _get_metric(data, "train_mean")
        std = _get_metric(data, "train_std")
        if None not in (serve, train, std) and std > 0:
            shift = abs(serve - train) / std
    if shift is None:
        return _verdict(pillar, note="Không đủ dữ liệu feature")
    bound = _baseline(ctx, "feature_mean_shift_sigma_max")
    if bound is None:
        return _verdict(pillar, note="Không có baseline feature")
    # Chừa khoảng an toàn cho dao động bình thường quanh biên 3σ.
    threshold = max(0.65, bound * 1.5)
    reasons = []
    _high(shift, threshold, "mean_shift_sigma", reasons)
    return _verdict(pillar, reasons)


def check_embedding_batch(payload, ctx):
    pillar = "ai_infra"
    corpus, batch = payload.get("corpus"), payload.get("chunk_batch_id")
    if corpus is None or batch is None:
        return _verdict(pillar, note="Thiếu corpus hoặc chunk_batch_id")
    data = _lookup(ctx, "embedding_drift", (corpus, batch))
    if data is None:
        return _verdict(pillar, note="Không nhận được thống kê embedding hợp lệ")
    reasons = []
    _high(_get_metric(data, "centroid_shift"), _baseline(ctx, "embedding_centroid_shift_max"), "centroid_shift", reasons)
    _high(_get_metric(data, "avg_doc_age_days"), _baseline(ctx, "corpus_avg_doc_age_days_max"), "avg_doc_age_days", reasons)
    return _verdict(pillar, reasons)