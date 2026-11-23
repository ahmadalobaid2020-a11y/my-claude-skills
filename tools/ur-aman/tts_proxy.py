"""Run the Papermorph tts.py behind an HTTPS proxy with its own CA (cloud sandboxes).
usage: uv run --with edge-tts tools/ur-aman/tts_proxy.py SKILL/scripts/tts.py <narration.json> <audio dir>
Reads HTTPS_PROXY and, when present, /root/.ccr/ca-bundle.crt (or $SSL_CERT_FILE)."""
import os, sys, runpy, functools
ca = os.environ.get('SSL_CERT_FILE') or '/root/.ccr/ca-bundle.crt'
if os.path.exists(ca):
    import certifi
    certifi.where = lambda: ca
import edge_tts
proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
if proxy:
    _C = edge_tts.Communicate
    class Communicate(_C):
        def __init__(self, *a, **k):
            k.setdefault('proxy', proxy)
            super().__init__(*a, **k)
    edge_tts.Communicate = Communicate
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
