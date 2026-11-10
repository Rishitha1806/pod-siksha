import os
import sys

# Add project root directory to path so server.py is importable
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app as fastapi_app

async def app(scope, receive, send):
    if scope["type"] == "http":
        path = scope.get("path", "")

        # Normalize path for Vercel Serverless Function invocations
        # 1. Remove /index.py or /api/index.py artifacts if present
        if path.startswith("/api/index.py"):
            path = "/api" + path[len("/api/index.py"):]
        elif path.startswith("/index.py"):
            path = path[len("/index.py"):]

        # 2. Ensure /api prefix is present since all FastAPI backend endpoints start with /api
        if not path.startswith("/api"):
            path = "/api" + path

        scope["path"] = path

    await fastapi_app(scope, receive, send)
