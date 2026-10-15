"""Đánh giá ứng viên trên Practice/Public qua harness chính thức.

Chỉ chạy từ bản clone đầy đủ repository. Không chạy Private và không đọc
schedule mã hóa hay khóa pha trực tiếp. Mọi báo cáo do harness tạo ra.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

BASELINE = {
    'practice': {'score': 46.97, 'tpr': 0.9394, 'fpr': 0.0, 'cost_ledger': 180.0},
    'public': {'score': 43.05, 'tpr': 0.8974, 'fpr': 0.0, 'cost_ledger': 240.0},
}


def compare(scores):
    """Chỉ chấp nhận khi Practice tốt hơn, Public không giảm và FPR không tăng."""
    for phase in ('practice', 'public'):
        if phase not in scores:
            raise ValueError('Thiếu kết quả ' + phase)
        row = scores[phase]
        for name in ('score', 'tpr', 'fpr', 'cost_ledger'):
            if type(row.get(name)) not in (int, float):
                raise ValueError('Sai dữ liệu %s.%s' % (phase, name))
    practice = scores['practice']
    public = scores['public']
    return {
        'practice_better': practice['score'] > BASELINE['practice']['score'],
        'public_not_worse': public['score'] >= BASELINE['public']['score'],
        'fpr_not_worse': all(scores[p]['fpr'] <= BASELINE[p]['fpr'] for p in scores),
        'practice_score_delta': round(practice['score'] - BASELINE['practice']['score'], 2),
        'public_score_delta': round(public['score'] - BASELINE['public']['score'], 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default='solution/candidate_runs')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / args.output_dir
    target.mkdir(parents=True, exist_ok=True)
    reports = {}
    for phase in ('practice', 'public'):
        path = target / ('%s_report.json' % phase)
        cmd = [sys.executable, str(root / 'harness' / 'run.py'),
               '--phase', phase, '--defense', str(root / 'solution' / 'defense.py'),
               '--out', str(path)]
        subprocess.run(cmd, cwd=root, check=True, stdout=subprocess.DEVNULL)
        record = json.loads(path.read_text(encoding='utf-8'))
        result = record.get('result', {})
        if result.get('phase') != phase or not isinstance(record.get('signature'), str):
            raise ValueError('Báo cáo pha %s không đúng định dạng' % phase)
        reports[phase] = result
    from evaluate_practice import evaluate
    answers = json.loads((root / 'phases' / 'practice_answer_key.json').read_text(encoding='utf-8'))
    practice_summary = evaluate({'result': reports['practice']}, answers)
    if not all(practice_summary['matches_harness'].values()):
        raise ValueError('Báo cáo Practice không khớp tính toán độc lập')
    result = compare(reports)
    result['practice_confusion'] = {k: practice_summary[k] for k in ('tp','fp','fn','tn')}
    result['measured'] = {phase: {k: reports[phase][k] for k in BASELINE[phase]} for phase in BASELINE}
    result['recommendation'] = ('candidate_pass' if
                                result['practice_better'] and result['public_not_worse']
                                and result['fpr_not_worse'] else 'keep_main')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Không tự sửa repo, không gộp nhánh và tuyệt đối không chạy Private.
    return 0 if result['recommendation'] == 'candidate_pass' else 2


if __name__ == '__main__':
    sys.exit(main())
