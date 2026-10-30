import pytest
from jsonschema import ValidationError
from scripts.validate import validate
from scripts.report_generator import render
from scripts.statistics_engine import calculate

def test_roundtrip(report):
    assert validate(report)==report
    assert 'https://example.org/fixture' in render(report)
def test_missing_url_reason(report):
    report['sources'][0]['url']=None
    with pytest.raises(ValueError): validate(report)
def test_no_fabricated_date(report):
    assert validate(report)['sources'][0]['published_at'] is None
    assert '發布：未知' in render(report)
def test_fake_quote(report):
    report['quotes']=[{'quote_id':'Q1','source_id':'S1','text':'invented sentence','locator':None}]
    with pytest.raises(ValueError):validate(report)
def test_bad_json(report):
    del report['claims'][0]['time_scope']
    with pytest.raises(ValidationError):validate(report)
def test_calculation_reproduced(report):
    c=calculate('percent_change',[100,140],sources=['S1'],unit='USD');c['calculation_id']='K1';report['calculations']=[c];validate(report)
    c['result']='50'
    with pytest.raises(ValueError):validate(report)

def test_content_tamper(report):
    report['sources'][0]['content_sha256']='0'*64
    with pytest.raises(ValueError):validate(report)
def test_no_empty_report(report):
    report['claims']=[];report['verdicts']=[];report['evidence']=[];report['relations']=[]
    with pytest.raises(ValidationError):validate(report)

def test_missing_url_marked(report):
    report['sources'][0].update(url=None,missing_reason='user supplied synthetic text')
    text=render(report)
    assert '(None)' not in text and 'user supplied synthetic text' in text

def test_intake_requested_markdown(tmp_path):
    import subprocess, sys
    from pathlib import Path
    cli=Path(__file__).resolve().parents[1]/'scripts/cli.py'
    out=tmp_path/'intake.md'
    proc=subprocess.run([sys.executable,str(cli),'--claim','A increases 40%','--format','markdown','--output',str(out)],capture_output=True)
    assert proc.returncode==0
    assert out.read_text(encoding='utf-8').startswith('# Truth Engine 待處理資料')

def test_graph_preserves_provenance_without_explicit_edges(report):
    from scripts.evidence_graph import graph
    report['relations']=[]
    g=graph(report)
    assert {'from':'E1','to':'S1','type':'REPORTED_BY'} in g['edges']
    assert {'from':'V1','to':'E1','type':'DERIVED_FROM'} in g['edges']
