"""Bounded local intake and stable content identities. Never fetch remote input."""
import hashlib
import ipaddress
import mimetypes
import socket
from pathlib import Path, PureWindowsPath, PurePosixPath
from urllib.parse import urlsplit, urlunsplit

MAX_BYTES = 100 * 1024 * 1024
EXTENSIONS = {'.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.webp': 'image',
              '.tif': 'image', '.tiff': 'image', '.mp4': 'video', '.mov': 'video',
              '.mkv': 'video', '.webm': 'video', '.pdf': 'document', '.txt': 'text',
              '.md': 'text', '.json': 'document'}

def portable_name(value):
    return PureWindowsPath(value).name if '\\' in value else PurePosixPath(value).name

def validate_url(url, resolve=True, resolver=None):
    """Reject all non-public resolved addresses, credentials and non-HTTP protocols.

    Validation alone is NOT a fetching permission: DNS may rebind. No HTTP fetcher
    is bundled. A network provider must pin validated IPs and validate redirects.
    """
    if not isinstance(url, str) or any(ord(c) < 33 for c in url) or '\\' in url:
        raise ValueError('URL contains whitespace, control characters or backslashes')
    p = urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Only credential-free HTTP(S) public URLs are permitted')
    if p.port not in (None, 80, 443):
        raise ValueError('Only ports 80 and 443 are permitted')
    host = p.hostname.rstrip('.').lower()
    if host == 'localhost' or host.endswith(('.localhost', '.local', '.internal', '.home', '.lan')) or '.' not in host and ':' not in host:
        raise ValueError('Internal hostname rejected')
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        addresses = []
        if resolve:
            lookup = resolver or socket.getaddrinfo
            addresses = [ipaddress.ip_address(row[4][0]) for row in lookup(host, p.port or 443, type=socket.SOCK_STREAM)]
            if not addresses:
                raise ValueError('No public DNS answer')
    for addr in addresses:
        mapped = getattr(addr, 'ipv4_mapped', None)
        if not addr.is_global or (mapped and not mapped.is_global):
            raise ValueError('Non-public address rejected')
    return urlunsplit((p.scheme, p.netloc, p.path or '/', p.query, ''))

def analyze_input(path, max_bytes=MAX_BYTES):
    p = Path(path).expanduser().resolve(strict=True)
    if not p.is_file() or p.stat().st_size > max_bytes:
        raise ValueError('Input must be a regular file within the size limit')
    kind = EXTENSIONS.get(p.suffix.lower())
    if not kind:
        raise ValueError('Unsupported file type')
    h = hashlib.sha256()
    count = 0
    with p.open('rb') as stream:
        head = stream.read(32)
        stream.seek(0)
        for chunk in iter(lambda: stream.read(65536), b''):
            count += len(chunk)
            if count > max_bytes:
                raise ValueError('Input grew beyond size limit')
            h.update(chunk)
    if not count:
        raise ValueError('Empty input')
    if kind == 'image':
        known = (head.startswith(b'\xff\xd8\xff') or head.startswith(b'\x89PNG\r\n\x1a\n') or
                 head.startswith((b'II*\x00', b'MM\x00*')) or head[:4] == b'RIFF' and head[8:12] == b'WEBP')
        if not known:
            raise ValueError('Image signature does not match an allowed format')
    if p.suffix.lower() == '.pdf' and not head.startswith(b'%PDF-'):
        raise ValueError('Invalid PDF signature')
    if kind == 'video' and not (head[4:8] == b'ftyp' or head.startswith(b'\x1aE\xdf\xa3')):
        raise ValueError('Unsupported video container signature')
    return {'kind': kind, 'path': str(p), 'name': portable_name(str(p)), 'bytes': count,
            'sha256': h.hexdigest(), 'mime': mimetypes.guess_type(p.name)[0], 'original': True}

def identity(inputs, intent=''):
    pieces = sorted(x.get('sha256', x.get('url', '')) for x in inputs)
    return 'case-' + hashlib.sha256(('\n'.join(pieces) + '\n' + intent).encode()).hexdigest()[:20]
