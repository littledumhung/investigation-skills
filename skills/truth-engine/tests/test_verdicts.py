import pytest
from copy import deepcopy
from scripts.verdict_engine import recommend
from scripts.validate import validate

def test_missing_evidence(): assert recommend()=='UNVERIFIED'
def test_outdated(): assert recommend(support=True,refutation=True,outdated=True)=='OUTDATED'
def test_misleading_comparison(): assert recommend(support=True,misleading=True)=='MISLEADING'
def test_correlation_not_causation(): assert recommend(support=False)=='UNVERIFIED'
def test_retraction(report):
    report['sources'][0]['correction_status']='RETRACTED'
    with pytest.raises(ValueError):validate(report)
def test_inaccessible_degrades(report):
    report['sources'][0]['accessible']=False
    with pytest.raises(ValueError):validate(report)
    report['verdicts'][0].update(verdict='UNVERIFIED',strongest_support=[]);validate(report)
def test_missing_support(report):
    report['verdicts'][0]['strongest_support']=[]
    with pytest.raises(ValueError):validate(report)
def test_neutral_structure(report):
    a=validate(deepcopy(report));report['claims'][0]['subject']='Opposite political party';b=validate(report)
    assert a['verdicts']==b['verdicts']
def test_mixed_article(report):
    c=deepcopy(report['claims'][0]);c['claim_id']='C2';report['claims'].append(c)
    v=deepcopy(report['verdicts'][0]);v.update(verdict_id='V2',claim_id='C2',verdict='UNVERIFIED',strongest_support=[]);report['verdicts'].append(v)
    assert [v['verdict'] for v in validate(report)['verdicts']]==['TRUE','UNVERIFIED']

def test_preprint_not_peer_reviewed():
    from scripts.scientific_analyzer import review_status
    r=review_status('PREPRINT','NONE_KNOWN',False)
    assert r['status']=='NOT_CONFIRMED_PEER_REVIEWED'
    assert r['methods_review']=='FULL_REVIEW_NOT_POSSIBLE'
def test_corrected_recheck():
    from scripts.scientific_analyzer import review_status
    assert review_status('JOURNAL','CORRECTED',True)['status']=='RECHECK_CORRECTED_VERSION'
