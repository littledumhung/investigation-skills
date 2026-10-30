import pytest
from scripts.statistics_engine import calculate, compare_context

def test_percent():
    c=calculate('percent_change',[100,50],sources=['S1'],unit='USD');assert c['result']=='-50.0000'
def test_cagr(): assert calculate('cagr',[100,121,2],sources=['S1'],unit='USD')['result']=='10.0000'
def test_period_mismatch(): assert compare_context({'period_length':'quarter'},{'period_length':'year'})['period_length']=='MISMATCH'
def test_risks():
    assert calculate('risk_ratio',[.02,.01],sources=['S1'],unit='probability')['result']=='2.0000'
    assert calculate('risk_difference',[.02,.01],sources=['S1'],unit='probability')['result']=='0.0100'
@pytest.mark.parametrize('values',[[0,1],[-2,1],['NaN',2]])
def test_bad_baselines(values):
    with pytest.raises(ValueError): calculate('percent_change',values,sources=['S1'],unit='USD')
