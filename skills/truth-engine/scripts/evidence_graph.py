RELATIONS={'SUPPORTS','CONTRADICTS','QUOTES','DERIVED_FROM','CALCULATED_FROM','REPORTED_BY','UPDATES','CORRECTS'}
def graph(report):
    groups={'claims':'claim_id','sources':'source_id','evidence':'evidence_id','quotes':'quote_id','datasets':'dataset_id','calculations':'calculation_id','contradictions':'contradiction_id','verdicts':'verdict_id'}
    nodes=[{'id':x[key],'type':kind} for kind,key in groups.items() for x in report.get(kind,[])]
    ids=[x['id'] for x in nodes]
    if len(ids)!=len(set(ids)): raise ValueError('Graph IDs must be globally unique')
    for edge in report.get('relations',[]):
        if edge['type'] not in RELATIONS or edge['from'] not in ids or edge['to'] not in ids: raise ValueError('Invalid graph edge')
    edges=list(report.get('relations',[]))
    def add(a,b,kind):
        if a not in ids or b not in ids: raise ValueError('Unknown graph reference')
        edge={'from':a,'to':b,'type':kind}
        if edge not in edges: edges.append(edge)
    for e in report.get('evidence',[]):
        add(e['evidence_id'],e['source_id'],'REPORTED_BY')
        if e['relation'] in ('SUPPORTS','CONTRADICTS'): add(e['evidence_id'],e['claim_id'],e['relation'])
    for source in report.get('sources',[]):
        for ref in source.get('derived_from',[]): add(source['source_id'],ref,'DERIVED_FROM')
    for q in report.get('quotes',[]): add(q['quote_id'],q['source_id'],'QUOTES')
    for d in report.get('datasets',[]): add(d['dataset_id'],d['source_id'],'DERIVED_FROM')
    for c in report.get('calculations',[]):
        for ref in c['sources']: add(c['calculation_id'],ref,'CALCULATED_FROM')
    for v in report.get('verdicts',[]):
        add(v['verdict_id'],v['claim_id'],'DERIVED_FROM')
        for ref in v['strongest_support']+v['strongest_counterevidence']: add(v['verdict_id'],ref,'DERIVED_FROM')
    for c in report.get('contradictions',[]):
        add(c['contradiction_id'],c['claim_id'],'DERIVED_FROM')
        for ref in c['evidence_ids']: add(c['contradiction_id'],ref,'DERIVED_FROM')
    return {'nodes':nodes,'edges':edges}
