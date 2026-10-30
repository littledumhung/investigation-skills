from pathlib import Path
from .source_deduplicator import content_hash
import hashlib

def inspect(path):
    p=Path(path)
    if p.stat().st_size>25_000_000: raise ValueError('Local media exceeds 25MB')
    result={'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'authenticity':'UNVERIFIED','limitations':['Metadata does not establish authenticity. Reverse image search and video extraction require agent tools.']}
    try:
        from PIL import Image
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            result.update(format=im.format,size=list(im.size),exif={str(k):str(v)[:500] for k,v in im.getexif().items()})
    except ImportError: result['limitations'].append('Install media extra for EXIF inspection')
    except (OSError,ValueError) as e: result['limitations'].append('Not a supported image: '+type(e).__name__)
    return result
