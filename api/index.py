import os
import sys

# Add project root directory to path so server.py is importable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] == "http":
        headers = dict(scope.get("headers", []))
        
        # In Vercel serverless rewrites, the original requested URL path is passed in x-matched-path
        matched_path = headers.get(b"x-matched-path", b"").decode("utf-8")
        if matched_path:
            path = matched_path
        else:
            path = scope.get("path", "")

        # Strip query string if present in path
        if "?" in path:
            path = path.split("?")[0]

        # Normalize /index.py artifacts
        if path.startswith("/api/index.py"):
            path = "/api" + path[len("/api/index.py"):]
        elif path.startswith("/index.py"):
            path = path[len("/index.py"):]

        # Ensure path starts with /api if it's an API route
        if not path.startswith("/api"):
            path = "/api" + path

        scope["path"] = path
        scope["raw_path"] = path.encode("utf-8")

    await fastapi_app(scope, receive, send)
