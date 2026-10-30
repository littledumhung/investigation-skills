import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.input_analyzer import analyze_input, portable_name, identity
from scripts.metadata_extractor import extract_metadata
from scripts.clue_extractor import observation, classify

class InputTests(unittest.TestCase):
    def test_gps_exif(self):
        from PIL import Image
        from PIL.TiffImagePlugin import IFDRational
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'gps.jpg'
            exif = Image.Exif()
            exif[34853] = {1:'N', 2:tuple(IFDRational(x) for x in (25,2,0)),
                           3:'E', 4:tuple(IFDRational(x) for x in (121,30,0))}
            Image.new('RGB',(16,16)).save(path, exif=exif)
            info = extract_metadata(path, True)
            self.assertAlmostEqual(info['gps']['latitude'], 25+2/60)
            self.assertAlmostEqual(info['gps']['longitude'], 121.5)
            self.assertIsNone(extract_metadata(path)['gps'])

    def test_no_exif_no_gps(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'plain.jpg'
            Image.new('RGB',(8,8)).save(path)
            self.assertIsNone(extract_metadata(path, True)['gps'])
            self.assertFalse(extract_metadata(path, True)['exif_present'])

    def test_hash_size_signature_and_paths(self):
        self.assertEqual(portable_name(r'C:\Users\test\photo.jpg'), 'photo.jpg')
        self.assertEqual(portable_name('/tmp/photo.jpg'), 'photo.jpg')
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / '線索 note.txt'
            p.write_text('public evidence',encoding='utf-8')
            a = analyze_input(p)
            self.assertEqual(a['sha256'], analyze_input(p)['sha256'])
            self.assertEqual(identity([a]), identity([a]))
            with self.assertRaises(ValueError):
                analyze_input(p,max_bytes=1)
            bad = Path(temp) / 'fake.jpg'
            bad.write_text('not an image')
            with self.assertRaises(ValueError):
                analyze_input(bad)

    def test_ocr_uncertainty(self):
        clue = observation('S0NY or SONY?',method='ocr')
        self.assertTrue(clue['uncertain'])
        self.assertEqual(clue['text'],'S0NY or SONY?')
        self.assertFalse(clue['trusted_instructions'])

    def test_mixed_classification(self):
        self.assertIn('VIDEO_INVESTIGATION',classify('where was this filmed?', 'video'))
