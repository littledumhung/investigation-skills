import unittest
from common import bundle
from scripts.evidence_graph import validate_bundle

class EvidenceTests(unittest.TestCase):
    def test_invalid_coordinates_rejected(self):
        for latitude in (91,float('nan'),True):
            b=bundle()
            b['hypotheses'][0]['location']={'latitude':latitude,'longitude':0,'role':'camera_position','verification':'estimated','accuracy_m':50}
            with self.assertRaises(ValueError):
                validate_bundle(b)

    def test_graph_valid(self):
        self.assertEqual(validate_bundle(bundle())['edges'][0]['relation'],'SUPPORTS')

    def test_dangling_edge_rejected(self):
        b=bundle()
        b['edges'][0]['to']='absent'
        with self.assertRaises(ValueError):
            validate_bundle(b)

    def test_duplicate_evidence_rejected(self):
        b=bundle()
        b['evidence'].append(dict(b['evidence'][0]))
        with self.assertRaises(ValueError):
            validate_bundle(b)

    def test_claim_reference_checked(self):
        b=bundle()
        b['evidence'][0]['supporting_claim_ids']=['nonexistent']
        with self.assertRaises(ValueError):
            validate_bundle(b)
