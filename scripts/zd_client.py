# -*- coding: utf-8 -*-
"""
Cliente Zendesk da POC.
- Autenticacao: basic auth email/token:TOKEN (lida do .env; token NUNCA impresso).
- Toda chamada de escrita (POST/PUT) grava par NN_endpoint_request.json /
  NN_endpoint_response.json em historico/.
"""
import json
import os
import re
import time
from pathlib import Path

import requests

BASE_DIR = Path(os.environ.get("POC_DIR", str(Path(__file__).resolve().parent.parent)))
HIST_DIR = BASE_DIR / "historico"
HIST_DIR.mkdir(exist_ok=True)


def _load_env():
    env = {}
    with open(BASE_DIR / ".env", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


_ENV = _load_env()
# Normaliza: aceita subdominio puro, host completo ou URL.
_sub = _ENV["ZENDESK_SUBDOMAIN"]
_sub = re.sub(r"^https?://", "", _sub).rstrip("/")
_sub = re.sub(r"\.zendesk\.com$", "", _sub)
SUBDOMAIN = _sub
BASE_URL = f"https://{SUBDOMAIN}.zendesk.com"

_session = requests.Session()
_session.auth = (f"{_ENV['ZENDESK_EMAIL']}/token", _ENV["ZENDESK_API_TOKEN"])
_session.headers.update({"Content-Type": "application/json"})


def _next_seq():
    seqs = [
        int(m.group(1))
        for p in HIST_DIR.glob("*_request.json")
        if (m := re.match(r"(\d+)_", p.name))
    ]
    return max(seqs, default=0) + 1


def _slug(path):
    return re.sub(r"[^a-z0-9]+", "_", path.split("?")[0].lower()).strip("_")


def api(method, path, payload=None, retries=3):
    """Chamada a API. GET nao gera historico; POST/PUT geram."""
    url = BASE_URL + path
    for attempt in range(retries):
        r = _session.request(method, url, json=payload)
        if r.status_code == 429:
            time.sleep(int(r.headers.get("Retry-After", "10")) + 1)
            continue
        break
    try:
        body = r.json()
    except ValueError:
        body = {"raw_text": r.text[:2000]}
    if method.upper() in ("POST", "PUT"):
        seq = _next_seq()
        stem = f"{seq:02d}_{method.lower()}_{_slug(path)}"
        (HIST_DIR / f"{stem}_request.json").write_text(
            json.dumps({"method": method, "path": path, "payload": payload},
                       ensure_ascii=False, indent=2), encoding="utf-8")
        (HIST_DIR / f"{stem}_response.json").write_text(
            json.dumps({"status_code": r.status_code, "body": body},
                       ensure_ascii=False, indent=2), encoding="utf-8")
    if r.status_code >= 400:
        raise RuntimeError(f"{method} {path} -> {r.status_code}: "
                           f"{json.dumps(body, ensure_ascii=False)[:800]}")
    return body


def get(path):
    return api("GET", path)


def post(path, payload):
    return api("POST", path, payload)


def put(path, payload):
    return api("PUT", path, payload)
