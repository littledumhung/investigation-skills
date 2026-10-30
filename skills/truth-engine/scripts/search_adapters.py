"""Bounded public HTTPS fetches with DNS-pinned connections and no redirect following."""
import http.client, socket, ssl, ipaddress, json, os
from urllib.parse import urlsplit, urlencode
from dataclasses import dataclass
from typing import Protocol
MAX_BYTES = 2_000_000
class FetchError(ValueError):
    """Untrusted network content could not be safely retrieved."""
def public_endpoint(url):
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.port not in (None,443):
        raise FetchError('Only public HTTPS URLs on port 443 without credentials are supported')
    addresses = socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise FetchError('Non-public address rejected')
    return p, addresses[0][4][0]
class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self,host,address):
        super().__init__(host,timeout=12,context=ssl.create_default_context()); self.address=address
    def connect(self):
        raw=socket.create_connection((self.address,443),self.timeout)
        self.sock=self._context.wrap_socket(raw,server_hostname=self.host)
def fetch(url):
    p,address=public_endpoint(url)
    conn=PinnedHTTPS(p.hostname,address)
    try:
        conn.request('GET',(p.path or '/')+('?' + p.query if p.query else ''),headers={'User-Agent':'TruthEngine/0.1 (+evidence research)','Accept':'application/json,text/html,text/plain'})
        response=conn.getresponse()
        if response.status != 200: raise FetchError('HTTP response '+str(response.status)+'; redirects not followed')
        content_type=response.getheader('Content-Type','').split(';')[0]
        if content_type not in ('application/json','text/html','text/plain','application/xml','text/xml'):
            raise FetchError('Unsupported remote media type; use dedicated bounded extraction tools')
        if response.getheader('Content-Encoding','identity') != 'identity': raise FetchError('Encoded payload rejected')
        data=response.read(MAX_BYTES+1)
        if len(data)>MAX_BYTES: raise FetchError('Response too large')
        return data.decode('utf-8',errors='replace')
    except (OSError, http.client.HTTPException) as e:
        raise FetchError('Network request failed: '+type(e).__name__) from e
    finally: conn.close()
class SearchProvider(Protocol):
    def search(self,query: str,limit: int=5) -> list[dict]: ...
class CrossrefAdapter:
    def search(self,query,limit=5):
        data=json.loads(fetch('https://api.crossref.org/works?'+urlencode({'query':query,'rows':min(max(limit,1),20)})))
        return [{'url':x.get('URL'),'title':(x.get('title') or [''])[0],'doi':x.get('DOI'),'metadata_only':True,'raw_metadata':x} for x in data['message']['items']]
class GoogleFactCheckAdapter:
    def search(self,query,limit=5):
        key=os.environ.get('GOOGLE_FACT_CHECK_API_KEY')
        if not key: raise FetchError('GOOGLE_FACT_CHECK_API_KEY is not configured')
        data=json.loads(fetch('https://factchecktools.googleapis.com/v1alpha1/claims:search?'+urlencode({'query':query,'pageSize':min(max(limit,1),20),'key':key})))
        return data.get('claims',[])
@dataclass
class Budget:
    searches: int
    sources: int
    calls: int
    def spend(self,kind):
        if self.calls <= 0 or getattr(self,kind) <= 0: raise FetchError('Research budget exhausted')
        self.calls-=1; setattr(self,kind,getattr(self,kind)-1)
MODES={'quick':(3,5,12),'deep':(12,20,45),'forensic':(25,40,90)}
