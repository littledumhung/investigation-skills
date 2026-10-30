import copy
import unittest
from common import bundle
from scripts.candidate_ranker import rank_candidates

class ScoringTests(unittest.TestCase):
    def test_similar_place_contradiction(self):
        b = bundle()
        ranks = rank_candidates(b['hypotheses'],b['evidence'],b['contradiction_checks'])
        self.assertEqual(ranks[0]['id'],'H1')
        self.assertLess(ranks[1]['score'],0)
        self.assertTrue(ranks[1]['has_contradiction'])

    def test_reposts_not_independent(self):
        b = bundle()
        first = b['evidence'][0]
        first['source_type']='test_reviewed_document'
        evidence = [{**first,'evidence_id':f'E{i}','source':f'https://mirror{i}.example/article'} for i in range(10)]
        rank = rank_candidates(b['hypotheses'][:1],evidence,b['contradiction_checks'])[0]
        self.assertEqual(rank['score'],5)
        self.assertEqual(rank['independent_strong_sources'],1)
        self.assertEqual(rank['confidence'],'low')

    def test_unknown_lineage_not_strong(self):
        b = bundle()
        ev = b['evidence'][:2]
        for e in ev:
            e.pop('independence_group')
            e['source_type']='test_reviewed_document'
        rank = rank_candidates(b['hypotheses'][:1],ev,b['contradiction_checks'])[0]
        self.assertEqual(rank['independent_strong_sources'],0)
        self.assertEqual(rank['confidence'],'low')

    def test_high_needs_checks_and_no_unknowns(self):
        b = bundle()
        for e in b['evidence']:
            e['source_type']='test_reviewed_document'
        self.assertEqual(rank_candidates(b['hypotheses'],b['evidence'],b['contradiction_checks'])[0]['confidence'],'high')
        self.assertNotEqual(rank_candidates(b['hypotheses'],b['evidence'])[0]['confidence'],'high')
        b['hypotheses'][0]['unverified'] = ['date unknown']
        self.assertNotEqual(rank_candidates(b['hypotheses'],b['evidence'],b['contradiction_checks'])[0]['confidence'],'high')

    def test_uncertain_ocr_cannot_be_direct_confirmation(self):
        b=bundle()
        b['evidence'][0]['uncertain']=True
        rank=rank_candidates(b['hypotheses'],b['evidence'],b['contradiction_checks'])[0]
        self.assertNotEqual(rank['confidence'],'high')
        self.assertEqual(rank['score'],4)
