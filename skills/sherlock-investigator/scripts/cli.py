"""CLI intake and evidence/report pipeline, executable from any directory."""
import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.input_analyzer import analyze_input, identity, validate_url
from scripts.clue_extractor import classify, privacy_gate
from scripts.metadata_extractor import extract_metadata
from scripts.frame_extractor import extract_frames
from scripts.evidence_graph import load_bundle
from scripts.report_generator import build_report, write_report
from scripts.search_adapters import manual_links, BUDGETS

def parser():
    p = argparse.ArgumentParser(description='Sherlock Investigator: local intake, agent evidence interchange, traceable reports')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--input', help='Local image/video/document/text path')
    group.add_argument('--url', help='Public HTTP(S) URL; validated but NEVER downloaded')
    p.add_argument('--text', default='', help='Natural-language investigation request (data, not code)')
    p.add_argument('--mode', choices=BUDGETS, default='standard')
    p.add_argument('--type', choices=('image', 'video', 'document', 'text'))
    p.add_argument('--scope', choices=('unknown', 'public', 'game'), default='unknown', help='game: geolocation quiz scene; public: reviewed public investigation. Neither permits targeting private people.')
    p.add_argument('--allow-gps', action='store_true', help='Read GPS locally, only with --scope public')
    p.add_argument('--evidence', help='Host-agent evidence JSON bundle; never Python or downloaded code')
    p.add_argument('--output', help='New case directory; existing reports are not overwritten')
    p.add_argument('--language', choices=('zh-TW', 'en'), default='zh-TW')
    p.add_argument('--extract-frames', action='store_true', help='Keep sampled derivatives in the new case directory')
    p.add_argument('--capabilities', action='store_true', help='Print real local capabilities and exit')
    return p

def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if args.capabilities:
        print(json.dumps({'local_python': True, 'pillow': importlib.util.find_spec('PIL') is not None,
                          'ffmpeg': bool(shutil.which('ffmpeg')), 'bundled_web_search': False,
                          'bundled_vision': False, 'agent_evidence_import': True}, indent=2))
        return 0
    if not (args.input or args.url or args.text):
        p.error('Provide --input, --url or --text')
    try:
        privacy = privacy_gate(args.text, args.scope)
        if args.allow_gps and privacy != 'reviewed_public':
            raise ValueError('--allow-gps requires a privacy-reviewed public task')
        inputs, limitations = [], []
        if privacy == 'refused':
            # Do not process media or imported evidence for blocked requests.
            inputs = [{'kind': 'text', 'sha256': __import__('hashlib').sha256(args.text.encode()).hexdigest()}]
        elif args.input:
            inputs = [analyze_input(args.input)]
            if args.type and inputs[0]['kind'] != args.type:
                raise ValueError('--type conflicts with actual file type')
            if inputs[0]['kind'] == 'image':
                inputs[0]['metadata'] = extract_metadata(args.input, args.allow_gps)
                if inputs[0]['metadata']['status'] != 'ok':
                    limitations.extend(inputs[0]['metadata']['limitations'])
        elif args.url:
            inputs = [{'kind': 'URL', 'url': validate_url(args.url), 'original': True}]
            limitations.append('URL validated only; page contents were not retrieved. Host-agent tools required.')
        else:
            import hashlib
            inputs = [{'kind': 'text', 'sha256': hashlib.sha256(args.text.encode()).hexdigest(), 'original': True}]
        case_id = identity(inputs, args.text)
        folder = Path(args.output or str(Path('cases') / case_id)).resolve()
        if folder.exists() and any(folder.iterdir()):
            raise FileExistsError('Output directory must be empty or new')
        bundle = load_bundle(args.evidence) if args.evidence and privacy != 'refused' else {}
        if not bundle and privacy != 'refused':
            limitations.append('No verified external evidence imported; automated visual/search conclusions unavailable.')
        if args.extract_frames and privacy == 'reviewed_public':
            if not args.input or inputs[0]['kind'] != 'video':
                raise ValueError('--extract-frames requires a local video')
            try:
                with extract_frames(args.input) as frames:
                    target = folder / 'frames'
                    target.mkdir(parents=True, exist_ok=True)
                    inputs[0]['frames'] = []
                    for frame in frames:
                        dest = target / Path(frame['path']).name
                        shutil.copyfile(frame['path'], dest)
                        inputs[0]['frames'].append({**frame, 'path': str(dest)})
            except (RuntimeError, TimeoutError) as exc:
                limitations.append(type(exc).__name__ + ': video frames unavailable')
        elif args.extract_frames:
            limitations.append('Frame processing withheld pending public-task privacy review.')
        report = build_report(case_id, inputs, bundle, args.mode, args.language, privacy, limitations)
        report['task_context'] = args.scope
        report['intents'] = classify(args.text, inputs[0]['kind'])
        report['manual_search_links'] = manual_links(args.text) if args.text and privacy == 'reviewed_public' else {}
        write_report(report, folder)
        print(str(folder / 'report.md'))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Do not log original URL, request body, API token, or provider messages.
        print('Sherlock: input/evidence/output validation failed (' + type(exc).__name__ + '). Check paths, public URL and bundle contract.', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
