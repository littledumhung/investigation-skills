"""Report serialization; all evidence is data, never executable instructions."""
import json
from pathlib import Path
from scripts.candidate_ranker import rank_candidates
from scripts.evidence_graph import now, validate_bundle
from scripts.search_adapters import BUDGETS

LABELS = {'high': '高', 'medium': '中', 'low': '低', 'undetermined': '無法判定'}

def build_report(case_id, inputs, bundle, mode='standard', language='zh-TW', privacy='pending_review', limitations=()):
    validate_bundle(bundle)
    ranked = rank_candidates(bundle.get('hypotheses', []), bundle.get('evidence', []), bundle.get('contradiction_checks', []))[:BUDGETS[mode]['candidates']]
    if privacy != 'reviewed_public':
        ranked = []
        bundle = {}
    best = ranked[0] if ranked else None
    confidence = best['confidence'] if best else 'undetermined'
    # A rank winner without net support is not an answer.
    answer = best['name'] if best and best['score'] > 0 else None
    issues = list(limitations)
    relevant = [e for e in bundle.get('evidence', []) if best and e['hypothesis_id'] == best['id']]
    for e in relevant:
        issues.extend(str(x) for x in e.get('limitations', []) if str(x) not in issues)
    if relevant and all(e['source_type'] == 'synthetic' for e in relevant):
        answer = None
        confidence = 'undetermined'
        issues.append('Synthetic exercise only; ranking does not establish any real-world answer.')
    if privacy != 'reviewed_public':
        issues.append('Privacy review required or request refused; no location or identity conclusions released.')
    if best and not best['contradiction_checked']:
        issues.append('Contradiction search not recorded; investigation remains partial.')
    if best and best['unverified']:
        issues.extend(str(x) for x in best['unverified'])
    location = dict(best['location']) if answer and best and best.get('location') else None
    if location and location['verification'] == 'verified' and confidence != 'high':
        location['verification'] = 'estimated'
        issues.append('Coordinate verification downgraded: supporting evidence is below high confidence.')
    if location and location['verification'] == 'estimated':
        issues.append('Coordinate is a best guess for the scene, not an established precise location.')
    complete = bool(answer and confidence == 'high' and not issues)
    return {'schema_version': '1.0', 'case_id': case_id, 'created_at': now(), 'language': language,
            'status': 'refused' if privacy == 'refused' else ('complete' if complete else 'partial'),
            'privacy': privacy, 'mode': mode, 'budget': BUDGETS[mode], 'inputs': inputs,
            'answer': answer, 'confidence': confidence, 'location': location, 'hypotheses': ranked,
            'evidence': bundle.get('evidence', []), 'graph': {'nodes': bundle.get('nodes', []), 'edges': bundle.get('edges', [])},
            'contradiction_checks': bundle.get('contradiction_checks', []), 'limitations': issues,
            'next_step': best['next_step'] if best else 'Use host-agent visual/search tools after privacy review; import traceable evidence.',
            'score_notice': 'Heuristic scores rank candidates; they are not calibrated probabilities.'}

def _safe(text):
    # Keep hostile source content visible as text, not active HTML/Markdown links.
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('[', '\\[').replace(']', '\\]').replace('\n', ' ')

def markdown(report):
    en = report['language'] == 'en'
    headings = (['Sherlock Investigation', 'Most likely answer', 'Evidence', 'Other candidates', 'Confidence', 'Limitations', 'Next step']
                if en else ['Sherlock 調查結果', '最可能的答案', '判斷依據', '其他候選', '可信程度', '關鍵限制', '下一步'])
    no_answer = 'Insufficient verified evidence.' if en else '目前證據不足，無法判定。'
    lines = [f'# {headings[0]}', '', f"Case: `{report['case_id']}` · {report['status']}", '',
             f'## {headings[1]}', '', _safe(report['answer'] or no_answer), '', f'## {headings[2]}', '']
    if report.get('location'):
        loc = report['location']
        coordinate = f"{loc['latitude']}, {loc['longitude']}"
        lines[6:6] = [f"**{coordinate}** — {loc['verification']}; {loc['role']}; accuracy ~{loc['accuracy_m']} m", '',
                      f"[Map](https://www.google.com/maps/search/?api=1&query={loc['latitude']}%2C{loc['longitude']})", '']
    best_id = report['hypotheses'][0]['id'] if report['hypotheses'] else None
    evidence = [e for e in report['evidence'] if e['hypothesis_id'] == best_id]
    for e in evidence[:6]:
        lines.append(f"- {_safe(e['original_observation'])} — {_safe(e['source'])} (ID: {_safe(e['evidence_id'])}; {e['kind']}; {_safe(e['source_type'])})")
        if e.get('limitations'):
            lines.append('  ' + _safe('; '.join(map(str,e['limitations']))))
        if e.get('uncertain'):
            lines.append('  ' + ('Uncertain observation/OCR.' if en else '此觀察或 OCR 尚不確定。'))
    if not evidence:
        lines.append(no_answer)
    lines += ['', f'## {headings[3]}', '']
    alternatives = report['hypotheses'][1:]
    for h in alternatives:
        counter = [e['original_observation'] for e in report['evidence'] if e['hypothesis_id'] == h['id'] and e['kind'] == 'contradiction']
        reason = '; '.join(map(str, h['contradicting_clues'] + counter or h['unverified'])) or 'No decisive exclusion evidence.'
        lines.append(f"- {_safe(h['name'])}: {_safe(reason)} (score {h['score']})")
    if not alternatives:
        lines.append('None recorded.' if en else '尚無其他有依據的候選。')
    lines += ['', f'## {headings[4]}', '', report['confidence'] if en else LABELS[report['confidence']]]
    if report['hypotheses']:
        best = report['hypotheses'][0]
        lines += ['', f"Independent strong source groups: {best['independent_strong_sources']}; contradiction check: {best['contradiction_checked']}."]
    lines += ['', report['score_notice'], '', f'## {headings[5]}', '']
    lines.extend('- ' + _safe(x) for x in report['limitations'])
    if not report['limitations']:
        lines.append('None recorded; source authenticity still requires judgment.' if en else '未記錄額外限制；仍須判斷來源真實性。')
    lines += ['', f'## {headings[6]}', '', _safe(report['next_step']), '']
    return '\n'.join(lines)

def write_report(report, directory):
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    # Explicit output directory; case files never overwrite source inputs.
    for name in ('report.json', 'report.md'):
        if (folder / name).exists():
            raise FileExistsError('Report exists; choose a new output directory')
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (folder / 'report.md').write_text(markdown(report), encoding='utf-8')
    return folder
