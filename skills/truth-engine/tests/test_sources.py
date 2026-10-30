from copy import deepcopy
from scripts.source_deduplicator import independent_groups, canonical_url
from scripts.source_tracer import trace
from scripts.search_adapters import CrossrefAdapter

def test_reposts_not_independent(report):
    s=deepcopy(report['sources'][0]);s.update(source_id='S2',kind='REPOST',url='https://example.net/repost',derived_from=['S1'])
    groups=independent_groups(report['sources']+[s]);assert groups['S1']==groups['S2']
    assert trace('S2',report['sources']+[s])[0]['stop']=='PRIMARY'
def test_tracking():
    assert canonical_url('https://EXAMPLE.org/x?utm_source=a&x=1#z')=='https://example.org/x?x=1'
def test_unresolved_origin(report):
    report['sources'][0]['kind']='SECONDARY';assert trace('S1',report['sources'])[0]['stop']=='UNRESOLVED_ORIGIN'
def test_mock_crossref(monkeypatch):
    monkeypatch.setattr('scripts.search_adapters.fetch',lambda u:'{"message":{"items":[{"URL":"https://doi.org/10.test/mock","title":["Synthetic"],"DOI":"10.test/mock"}]}}')
    result=CrossrefAdapter().search('synthetic');assert result[0]['metadata_only'] is True
