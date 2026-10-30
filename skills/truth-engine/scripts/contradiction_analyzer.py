def changes(previous,current):
    old={v['claim_id']:v for v in previous}
    return [{'claim_id':v['claim_id'],'previous':old[v['claim_id']]['verdict'],'current':v['verdict'],'reason':v['evidence_summary']} for v in current if v['claim_id'] in old and old[v['claim_id']]['verdict']!=v['verdict']]
def counterevidence_complete(record):
    return bool(record.get('queries')) and record.get('status') in ('FOUND','NONE_FOUND','BLOCKED') and bool(record.get('notes'))
