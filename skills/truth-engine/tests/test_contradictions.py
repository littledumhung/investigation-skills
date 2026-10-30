from scripts.contradiction_analyzer import changes, counterevidence_complete

def test_revision():
    result=changes([{'claim_id':'C1','verdict':'TRUE'}],[{'claim_id':'C1','verdict':'FALSE','evidence_summary':'new original data'}]);assert result[0]['reason']=='new original data'
def test_required_search(): assert not counterevidence_complete({'queries':[],'status':'NONE_FOUND','notes':'none'})
