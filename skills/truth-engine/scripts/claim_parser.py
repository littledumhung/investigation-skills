"""Validate agent-authored atomic claims; never simulate semantic decomposition."""
TYPES = ['FACT','NUMERIC','CAUSAL','COMPARATIVE','PREDICTION','OPINION','VALUE','UNVERIFIABLE']
def intake(text):
    if not text.strip():
        raise ValueError('Input is empty')
    return {'original_text': text, 'status': 'AWAITING_AGENT_DECOMPOSITION', 'claims': [],
            'instruction': 'Agent: split atomic claims, preserve quotations and ambiguity, then populate evidence JSON. No verdict has been reached.'}
def validate_claims(claims):
    ids = set()
    for c in claims:
        required = {'claim_id','original_text','normalized_claim','claim_type','subject','predicate','object','time_scope','geographic_scope','required_evidence','checkability','ambiguity','dependencies'}
        if required - c.keys():
            raise ValueError('Missing claim fields: '+str(sorted(required-c.keys())))
        if c['claim_id'] in ids or c['claim_type'] not in TYPES:
            raise ValueError('Duplicate claim ID or invalid type')
        ids.add(c['claim_id'])
    for c in claims:
        if set(c['dependencies']) - ids or c['claim_id'] in c['dependencies']:
            raise ValueError('Unknown or self dependency')
    visiting, done = set(), set()
    by_id = {c['claim_id']: c for c in claims}
    def visit(i):
        if i in visiting: raise ValueError('Cyclic claim dependencies')
        if i in done: return
        visiting.add(i)
        for j in by_id[i]['dependencies']: visit(j)
        visiting.remove(i); done.add(i)
    for i in ids: visit(i)
    return claims
