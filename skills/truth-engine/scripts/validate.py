if __name__ == '__main__' and not __package__:
    import sys
    from pathlib import Path
    sys.path.insert(0,str(Path(__file__).resolve().parents[1])); __package__='scripts'
import json
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit
from jsonschema import Draft202012Validator, ValidationError
from .claim_parser import validate_claims
from .evidence_graph import graph
from .temporal_checker import normalize, temporal_status
from .statistics_engine import calculate
from .contradiction_analyzer import counterevidence_complete

def validate(report):
    schema=json.loads((Path(__file__).resolve().parent/'report.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator(schema).validate(report)
    date.fromisoformat(report['as_of']); normalize(report['checked_at'])
    validate_claims(report['claims']); graph(report)
    claims={x['claim_id']:x for x in report['claims']}
    sources={x['source_id']:x for x in report['sources']}
    evidence={x['evidence_id']:x for x in report['evidence']}
    for source in sources.values():
        if not source['url'] and not source['missing_reason']: raise ValueError('Missing URL requires reason')
        if source['url'] and (urlsplit(source['url']).scheme not in ('http','https') or not urlsplit(source['url']).hostname): raise ValueError('Invalid source URL')
        temporal_status(source,report['as_of']); normalize(source['accessed_at'])
        if source['content_sha256']:
            from .source_deduplicator import content_hash
            if content_hash(source['content']) != source['content_sha256']: raise ValueError('Captured content hash mismatch')
        if set(source['derived_from'])-sources.keys(): raise ValueError('Unknown provenance source')
    for e in evidence.values():
        if e['claim_id'] not in claims or e['source_id'] not in sources: raise ValueError('Dangling evidence reference')
    for q in report['quotes']:
        if q['source_id'] not in sources or not q['text'] or q['text'] not in sources[q['source_id']]['content']: raise ValueError('Quote must exactly occur in captured source content')
    for d in report['datasets']:
        if d['source_id'] not in sources: raise ValueError('Unknown dataset source')
    for c in report['calculations']:
        if set(c['sources'])-sources.keys(): raise ValueError('Unknown calculation source')
        actual=calculate(c['operation'],c['values'],sources=c['sources'],unit=c['unit'],assumptions=c['assumptions'],round_digits=c['round_digits'])
        if any(actual[k]!=c[k] for k in ('result','formula','rounding')): raise ValueError('Calculation cannot be reproduced')
    for c in report['contradictions']:
        if c['claim_id'] not in claims or set(c['evidence_ids'])-evidence.keys(): raise ValueError('Dangling contradiction')
    seen=set()
    for v in report['verdicts']:
        cid=v['claim_id']; decision=v['verdict']
        if cid not in claims or cid in seen: raise ValueError('Verdict must map uniquely to claim')
        seen.add(cid); normalize(v['checked_at'])
        if not counterevidence_complete(v['counterevidence_search']): raise ValueError('Counterevidence search record required')
        supports=v['strongest_support']; counters=v['strongest_counterevidence']
        for ids,relation in ((supports,'SUPPORTS'),(counters,'CONTRADICTS')):
            for eid in ids:
                if eid not in evidence or evidence[eid]['claim_id']!=cid or evidence[eid]['relation']!=relation: raise ValueError('Incorrect verdict evidence link')
        if claims[cid]['claim_type'] in ('OPINION','VALUE','UNVERIFIABLE') and decision!='NOT_CHECKABLE': raise ValueError('Subjective claims are not true/false')
        if decision not in ('UNVERIFIED','NOT_CHECKABLE'):
            if not supports+counters: raise ValueError('Substantive verdict requires evidence')
            if decision in ('TRUE','MOSTLY_TRUE') and not supports: raise ValueError('Support required')
            if decision=='FALSE' and not counters: raise ValueError('Refutation required')
            if decision=='OUTDATED' and not (supports and counters): raise ValueError('Past support and current refutation required')
            for eid in supports+counters:
                src=sources[evidence[eid]['source_id']]
                if not src['accessible'] or not src['content'] or src['correction_status']=='RETRACTED': raise ValueError('Unavailable/retracted evidence cannot substantiate verdict')
                if temporal_status(src,report['as_of'])=='POST_CUTOFF': raise ValueError('Post-cutoff evidence cannot substantiate historical verdict')
    if seen != claims.keys(): raise ValueError('Every claim needs a verdict')
    return report

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('report',nargs='?');a=p.parse_args()
    if a.report:
        try:
            validate(json.loads(Path(a.report).read_text(encoding='utf-8-sig')))
            print('Valid report')
        except ValidationError as exc:
            import sys
            print('Schema violation at /'+'/'.join(str(x) for x in exc.absolute_path)+' (rule: '+str(exc.validator)+')',file=sys.stderr)
            raise SystemExit(2)
        except ValueError as exc:
            import sys
            # Deterministic integrity errors contain fixed explanations, not document bodies.
            print('Integrity check failed: '+str(exc),file=sys.stderr)
            raise SystemExit(2)
    else:
        Draft202012Validator.check_schema(json.loads((Path(__file__).resolve().parent/'report.schema.json').read_text(encoding='utf-8')));print('Report schema valid; pass a report path to validate evidence')
if __name__=='__main__':
    if not __package__:
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[1])); __package__='scripts'
    main()
