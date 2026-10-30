import pytest
from copy import deepcopy
from scripts.claim_parser import intake, validate_claims
from scripts.validate import validate

def test_no_fake_decomposition():
    result=intake('A增加40%，但B已超越A，而且B抄襲A。')
    assert result['claims']==[] and result['status']=='AWAITING_AGENT_DECOMPOSITION'
def test_multiple_agent_claims(report):
    c=deepcopy(report['claims'][0]); c.update(claim_id='C2',dependencies=['C1'],claim_type='CAUSAL')
    assert len(validate_claims(report['claims']+[c]))==2
def test_opinion_not_fact(report):
    report['claims'][0]['claim_type']='OPINION'
    with pytest.raises(ValueError): validate(report)
    report['verdicts'][0]['verdict']='NOT_CHECKABLE';validate(report)
def test_dependency_cycle(report):
    report['claims'][0]['dependencies']=['C1']
    with pytest.raises(ValueError): validate_claims(report['claims'])
