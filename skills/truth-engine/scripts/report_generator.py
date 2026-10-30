from .validate import validate
from .source_deduplicator import independent_groups
from .evidence_graph import graph

def render(report):
    validate(report)
    sources={s['source_id']:s for s in report['sources']}
    ev={e['evidence_id']:e for e in report['evidence']}
    lines=['# Truth Engine 查核報告','','## 總結',report['summary'],'',f"查核基準：{report['as_of']}；查核時間：{report['checked_at']}",'','## 主張拆解']
    for c in report['claims']: lines.append(f"- {c['claim_id']}：{c['normalized_claim']}（{c['claim_type']}；時間：{c['time_scope']}）")
    lines+=['','## 逐項查核結果']
    for v in report['verdicts']:
        lines += ['',f"### {v['claim_id']}：{v['verdict']}",v['evidence_summary']]
        for label,key in [('支持證據','strongest_support'),('反面證據','strongest_counterevidence')]:
            lines.append(f"- {label}：")
            for eid in v[key]:
                e=ev[eid];s=sources[e['source_id']]
                source_label=f"[{s['title']}]({s['url']})" if s['url'] else s['title']+'（無URL：'+str(s['missing_reason'])+'）'
                lines.append(f"  - {e['summary']} — {source_label}；位置：{e['locator'] or '未提供'}")
            if not v[key]: lines.append('  - 未取得；不能解讀為不存在。')
        lines+=['- 來源品質：'+v['source_quality'],'- 限制：'+'；'.join(v['limitations'])]
    lines+=['','## 原始資料']
    for s in report['sources']:
        source_label=f"[{s['title']}]({s['url']})" if s['url'] else s['title']+'（無URL：'+str(s['missing_reason'])+'）'
        lines.append(f"- {s['source_id']} {source_label}；{s['kind']}；發布：{s['published_at'] or '未知'}；更正：{s['correction_status']}")
    lines+=['','## 是否存在誤導']
    for v in report['verdicts']:
        if v['verdict'] in ('MISLEADING','MIXED','OUTDATED'):
            lines.append(f"- {v['claim_id']}：{v['evidence_summary']}")
    lines+=['- 其餘問題參見逐項證據與限制；未另作無證據的推論。','','## 查核可信程度']
    lines += [f"- {v['claim_id']}：{v['confidence_level']}；{v['source_quality']}" for v in report['verdicts']]
    lines+=['','## 目前無法確定的部分']+['- '+s for s in report['limitations']]+['','## 更精確的說法',report['precise_wording']]
    if report['mode'] in ('deep','forensic'):
        lines+=['','## 來源相依群組（相異群組不自動證明獨立）']
        lines += [f'- {sid} → {group}' for sid,group in independent_groups(report['sources']).items()]
        lines+=['','## 時間線']
        for source in report['sources']:
            for key in ('event_at','spoken_at','collected_at','published_at','updated_at','accessed_at','effective_from','effective_until'):
                if source.get(key): lines.append(f"- {source['source_id']} {key}：{source[key]}")
        lines+=['','## 計算紀錄']
        for c in report['calculations']:
            lines.append(f"- {c['calculation_id']}：{c['formula']}；輸入 {c['values']} {c['unit']}；結果 {c['result']}；來源 {c['sources']}；前提 {c['assumptions']}")
        lines+=['','## 搜尋歷程']
        for entry in report['search_log']:
            lines.append(f"- {entry['searched_at']} {entry['provider']}：{entry['query']} — {entry['status']}；{entry['notes']}")
    return '\n'.join(lines)+'\n'
