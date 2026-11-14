"""Small HTTP helpers on urllib (no third-party packages)."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = "career-tools/0.1 (personal job and news tracker)"


def fetch(url: str, data: dict | None = None, timeout: int = 15, retries: int = 1, curl_first: bool = False) -> bytes:
    if curl_first and data is None:
        r = subprocess.run(["curl", "-sfL", "-m", str(timeout), url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
    body = json.dumps(data).encode() if data is not None else None
    headers = {"User-Agent": UA, "Accept": "application/json, text/html, application/xml;q=0.9, */*;q=0.8"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (429, 500, 502, 503, 504):
                break  # not worth retrying; fall through to the curl fallback for GETs
        except (urllib.error.URLError, OSError) as e:  # includes socket timeouts
            last = e
        time.sleep(1.5 * (attempt + 1))  # polite backoff
    if body is None:  # some hosts (e.g. FRED) refuse Python clients but answer plain curl
        r = subprocess.run(["curl", "-sfL", "-m", str(timeout), url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
    raise last  # type: ignore[misc]


def get_json(url: str, data: dict | None = None, **kw):
    return json.loads(fetch(url, data, **kw))


CACHE_DIR = Path(os.environ.get("CAREER_TOOLS_CACHE_DIR", Path(__file__).resolve().parents[2] / "private" / "cache" / "http"))


def cached(url: str, hours: float = 6, **kw) -> bytes:
    """fetch() with an on-disk cache, for big files that change slowly (sitemaps, job lists)."""
    path = CACHE_DIR / (hashlib.sha1(url.encode()).hexdigest() + ".bin")
    if path.exists() and time.time() - path.stat().st_mtime < hours * 3600:
        return path.read_bytes()
    data = fetch(url, **kw)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data
