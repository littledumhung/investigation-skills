import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from scripts.frame_extractor import extract_frames
from scripts.image_tools import average_hash,distance,crop

class VideoTests(unittest.TestCase):
    def test_decoder_timeout_degrades_and_cleans_up(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'clip.mp4'
            source.write_bytes(b'fixture')
            with patch('scripts.frame_extractor.shutil.which',return_value='ffmpeg'), patch('scripts.frame_extractor.subprocess.run',side_effect=subprocess.TimeoutExpired('ffmpeg',1)):
                with self.assertRaises(RuntimeError):
                    with extract_frames(source):
                        self.fail('Decoder should time out')

    @unittest.skipUnless(shutil.which('ffmpeg'),'ffmpeg unavailable: video acceptance NOT verified')
    def test_video_frames_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            video=Path(temp)/'public synthetic.mp4'
            subprocess.run([shutil.which('ffmpeg'),'-nostdin','-loglevel','error','-f','lavfi','-i',
                            'testsrc=size=160x120:rate=10','-t','3','-pix_fmt','yuv420p',str(video)],check=True,timeout=30)
            with extract_frames(video,count=3,interval=0.5) as frames:
                self.assertEqual(len(frames),3)
                frame=Path(frames[0]['path'])
                self.assertTrue(frame.exists())
                self.assertEqual(distance(average_hash(frame),average_hash(frame)),0)
                dest=Path(temp)/'crop.jpg'
                crop(frame,dest,(0,0,10,10))
                self.assertTrue(dest.exists())
            self.assertFalse(frame.exists())

    def test_invalid_frame_limits(self):
        with self.assertRaises(ValueError):
            with extract_frames('unneeded',count=100):
                self.fail('Unreachable')
