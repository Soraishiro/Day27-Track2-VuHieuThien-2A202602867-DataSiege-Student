"""Đối chiếu báo cáo Practice với đáp án đã công bố.

Dùng bên ngoài sandbox của defense.py. Không mở hoặc xử lý dữ liệu pha khác.
"""
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def evaluate(report, answers):
    """Trả thống kê, từ chối dữ liệu thiếu hoặc sai thứ tự định danh."""
    if not isinstance(report, dict) or not isinstance(answers, list):
        raise ValueError("Sai định dạng báo cáo hoặc đáp án")
    result = report.get('result')
    if not isinstance(result, dict) or result.get('phase') != 'practice':
        raise ValueError("Chỉ được kiểm tra báo cáo Practice")
    verdicts = result.get('verdicts')
    if not isinstance(verdicts, list) or len(verdicts) != len(answers):
        raise ValueError("Số quyết định không khớp số đáp án")
    a_by_seq = {row.get('seq'): row for row in answers if isinstance(row, dict)}
    v_by_seq = {row.get('seq'): row for row in verdicts if isinstance(row, dict)}
    if len(a_by_seq) != len(answers) or len(v_by_seq) != len(verdicts):
        raise ValueError("seq bị trùng hoặc có phần tử sai định dạng")
    if set(a_by_seq) != set(v_by_seq) or any(type(k) is not int for k in a_by_seq):
        raise ValueError("Các seq không trùng nhau")
    for row in answers:
        if type(row.get('is_faulty')) is not bool:
            raise ValueError("is_faulty phải là bool")
    for row in verdicts:
        if type(row.get('alert')) is not bool:
            raise ValueError("alert phải là bool")

    counts = Counter()
    by_pillar = defaultdict(lambda: Counter())
    by_type = defaultdict(lambda: Counter())
    for seq in sorted(a_by_seq):
        truth = a_by_seq[seq]
        predicted = v_by_seq[seq]['alert']
        actual = truth['is_faulty']
        key = 'tp' if actual and predicted else ('fn' if actual else ('fp' if predicted else 'tn'))
        counts[key] += 1
        # Với event sạch, practice_answer_key không ghi pillar; không suy diễn.
        if actual:
            by_pillar[str(truth.get('pillar'))][key] += 1
            by_type[str(truth.get('fault_key'))][key] += 1
    n_fault = counts['tp'] + counts['fn']
    n_clean = counts['tn'] + counts['fp']
    tpr = counts['tp'] / n_fault if n_fault else 0
    fpr = counts['fp'] / n_clean if n_clean else 0
    spent = result.get('cost_ledger')
    budget = result.get('budget')
    if type(spent) not in (int, float) or type(budget) not in (int, float) or budget <= 0:
        raise ValueError("Chi phí/ngân sách báo cáo không hợp lệ")
    overage = max(0.0, (spent - budget) / budget)
    score = round(100 * (0.5 * tpr - 0.3 * fpr - 0.2 * min(overage, 1.0)), 2)
    checks = {}
    for key, measured, tolerance in (('tpr',tpr,0.00011), ('fpr',fpr,0.00011),
                                      ('cost_overage',overage,0.00011),('score',score,0.02)):
        value = result.get(key)
        checks[key] = type(value) in (int,float) and abs(value-measured) <= tolerance
    return {
        'n':len(answers),'tp':counts['tp'],'fp':counts['fp'],'fn':counts['fn'],'tn':counts['tn'],
        'tpr':round(tpr,4),'fpr':round(fpr,4),'cost':spent,'budget':budget,
        'cost_overage':round(overage,4),'score_recomputed':score,
        'matches_harness':checks,
        'faults_by_pillar':{k:dict(v) for k,v in sorted(by_pillar.items())},
        'faults_by_type':{k:dict(v) for k,v in sorted(by_type.items())}
    }


def main():
    p = argparse.ArgumentParser(description='Phân tích báo cáo Practice')
    p.add_argument('--report',default='solution/practice_report.json')
    p.add_argument('--answers',default='phases/practice_answer_key.json')
    args=p.parse_args()
    report=json.loads(Path(args.report).read_text(encoding='utf-8'))
    answers=json.loads(Path(args.answers).read_text(encoding='utf-8'))
    summary=evaluate(report,answers)
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    if not all(summary['matches_harness'].values()):
        p.exit(2,'CẢNH BÁO: Kết quả tính lại không khớp báo cáo của harness\n')


if __name__ == '__main__':
    main()