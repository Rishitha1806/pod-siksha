import os
import sys
from urllib.parse import parse_qs, urlencode

# Add project root directory to path so server.py is importable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] == "http":
        qs = scope.get("query_string", b"").decode("latin-1")
        params = parse_qs(qs, keep_blank_values=True)
        if "__path__" in params:
            subpath = params.pop("__path__")[0]
            if not subpath.startswith("/"):
                subpath = "/" + subpath
            target_path = f"/api{subpath}" if not subpath.startswith("/api") else subpath
            scope["path"] = target_path
            scope["raw_path"] = target_path.encode("latin-1")
            # Reconstruct clean query string without __path__
            new_qs = urlencode(params, doseq=True).encode("latin-1")
            scope["query_string"] = new_qs

    await fastapi_app(scope, receive, send)
