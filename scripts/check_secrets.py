#!/usr/bin/env python3
"""
Security CI & Pre-commit Check for Pod-Siksha.
Scans repository files and staged changes for secret patterns, leaked credentials,
and prohibited environment files.
"""

import os
import re
import subprocess
import sys

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SECRET_PATTERNS = [
    (r"postgresql://[^:]+:[^@]+@[^/]+/[^\s\"']+", "Database Connection String with credentials"),
    (r"AIzaSy[A-Za-z0-9\\-_]{33}", "Google API Key"),
    (r"vach_[A-Za-z0-9_]{30,}", "Gnani API Key"),
    (r"npg_[A-Za-z0-9_]{10,}", "Neon PostgreSQL Password"),
    (r"AQ\.[A-Za-z0-9_-]{30,}", "Gemini / Vertex API Token"),
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private Key"),
    (r"(?i)(api_key|secret_key|password)\s*=\s*['\"][A-Za-z0-9_\\-]{16,}['\"]", "Hardcoded API Key / Password Assignment"),
]

IGNORED_PATHS = {
    ".git",
    "docs/screenshots",
    "node_modules",
    ".vercel",
    ".pytest_cache",
    "__pycache__",
    "pod_siksha.db",
    "scripts/check_secrets.py",  # self
}

def is_ignored(path: str) -> bool:
    for ignored in IGNORED_PATHS:
        if path == ignored or path.startswith(ignored + "/") or path.startswith(ignored + "\\"):
            return True
    return False

def check_files():
    # Get list of tracked files from git
    try:
        result = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
        tracked_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except Exception as e:
        print(f"Error running git ls-files: {e}")
        return 1

    violations = []

    for file_path in tracked_files:
        if is_ignored(file_path):
            continue

        if file_path == ".env" or file_path.endswith(".env"):
            violations.append((file_path, 1, "Environment secret file committed to repository"))
            continue

        if not os.path.isfile(file_path):
            continue

        # Skip binary files
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            continue

        for line_no, line in enumerate(lines, start=1):
            for pattern, desc in SECRET_PATTERNS:
                if re.search(pattern, line):
                    # Check if line is placeholder or comment
                    if "your_" in line or "dummy" in line or "placeholder" in line or "example" in line:
                        continue
                    violations.append((file_path, line_no, desc))

    if violations:
        print("❌ SECURITY AUDIT FAILED - Secrets or prohibited files found:")
        for file_path, line_no, desc in violations:
            print(f"  - {file_path}:{line_no} -> {desc}")
        return 1

    print("✅ SECURITY AUDIT PASSED - No secrets found in tracked repository files.")
    return 0

if __name__ == "__main__":
    sys.exit(check_files())
