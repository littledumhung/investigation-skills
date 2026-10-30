import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import bundle,ROOT
from scripts.input_analyzer import identity
from scripts.report_generator import build_report,write_report,markdown
from scripts.search_adapters import Research,ProviderUnavailable,Budget
from scripts.cli import main

INPUTS=[{'kind':'text','sha256':'fixture'}]

class BrokenProvider:
    name='test-only-broken'
    capabilities={'web_search'}
    def search(self,query,capability,timeout):
        raise TimeoutError('secret=DO_NOT_LOG')

class ReportsTests(unittest.TestCase):
    def test_game_estimate_coordinates(self):
        b=bundle()
        for e in b['evidence']:
            e['source_type']='test_reviewed_document'
        b['hypotheses'][0]['location']={'latitude':25.0,'longitude':121.0,'role':'estimated_photo_position','verification':'estimated','accuracy_m':50000}
        report=build_report(identity(INPUTS),INPUTS,b,privacy='reviewed_public')
        self.assertEqual(report['location']['latitude'],25.0)
        self.assertEqual(report['status'],'partial')
        self.assertIn('25.0, 121.0',markdown(report))

    def test_verified_multi_source_report(self):
        b=bundle()
        for e in b['evidence']:
            e['source_type']='test_verified_public_document'
            e['limitations']=[]
        report=build_report(identity(INPUTS),INPUTS,b,privacy='reviewed_public')
        self.assertEqual(report['confidence'],'high')
        self.assertEqual(report['status'],'complete')
        self.assertEqual(report['answer'],b['hypotheses'][0]['name'])

    def test_synthetic_is_not_real_world_answer(self):
        report=build_report(identity(INPUTS),INPUTS,bundle(),privacy='reviewed_public')
        self.assertIsNone(report['answer'])
        self.assertEqual(report['confidence'],'undetermined')
        self.assertEqual(report['status'],'partial')
        self.assertIn('Synthetic demonstration',report['limitations'])
        self.assertEqual(report['hypotheses'][0]['confidence'],'undetermined')
        self.assertIn('The road is straight',markdown(report))
        self.assertIn('synthetic',markdown(report))

    def test_provider_failure_partial_report(self):
        r=Research([BrokenProvider()])
        self.assertEqual(r.search('public landmark'),[])
        self.assertEqual(len(r.failures),2)
        self.assertNotIn('DO_NOT_LOG',str(r.failures))
        report=build_report(identity(INPUTS),INPUTS,{},limitations=['Provider unavailable'])
        self.assertEqual(report['status'],'partial')
        self.assertIsNone(report['answer'])

    def test_json_schema(self):
        from jsonschema import Draft202012Validator,FormatChecker
        schema=json.loads((ROOT/'assets/report.schema.json').read_text(encoding='utf-8'))
        report=build_report(identity(INPUTS),INPUTS,bundle(),privacy='reviewed_public')
        Draft202012Validator(schema,format_checker=FormatChecker()).validate(report)
        bad=dict(report,confidence='95%')
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(bad)))

    def test_bilingual_reports_no_overwrite(self):
        report=build_report(identity(INPUTS),INPUTS,bundle(),language='en',privacy='reviewed_public')
        self.assertIn('Most likely answer',markdown(report))
        report['language']='zh-TW'
        self.assertIn('最可能的答案',markdown(report))
        with tempfile.TemporaryDirectory() as temp:
            write_report(report,temp)
            with self.assertRaises(FileExistsError):
                write_report(report,temp)

    def test_offline_cli(self):
        with tempfile.TemporaryDirectory() as temp, patch('socket.getaddrinfo',side_effect=OSError('offline')):
            out=Path(temp)/'case'
            self.assertEqual(main(['--text','Identify a public object','--scope','public','--output',str(out)]),0)
            report=json.loads((out/'report.json').read_text(encoding='utf-8'))
            self.assertEqual(report['status'],'partial')

    def test_budget_exhaustion(self):
        b=Budget('quick')
        for _ in range(3):
            b.consume()
        with self.assertRaises(ProviderUnavailable):
            b.consume()

    def test_no_capability_returns_no_claims(self):
        self.assertEqual(Research().search('unknown public clue'),[])
