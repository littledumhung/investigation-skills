from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import hashlib
TRACKING={'fbclid','gclid'}
def canonical_url(url):
    p=urlsplit(url)
    q=[(k,v) for k,v in parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith('utm_') and k.lower() not in TRACKING]
    return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path or '/',urlencode(sorted(q)),''))
def independent_groups(sources):
    parent={s['source_id']:s['source_id'] for s in sources}
    def root(x):
        while parent[x]!=x: x=parent[x]
        return x
    def union(a,b):
        a,b=root(a),root(b)
        if a!=b: parent[b]=a
    seen={}
    for s in sources:
        sid=s['source_id']
        keys=[('url',canonical_url(s['url']))] if s.get('url') else []
        if s.get('content_sha256'): keys.append(('hash',s['content_sha256']))
        if s.get('independence_group'): keys.append(('declared',s['independence_group']))
        for k in keys:
            if k in seen: union(sid,seen[k])
            else: seen[k]=sid
        for ref in s.get('derived_from',[]):
            if ref in parent: union(sid,ref)
    return {sid:root(sid) for sid in parent}
def content_hash(text): return hashlib.sha256(text.encode('utf-8')).hexdigest()
