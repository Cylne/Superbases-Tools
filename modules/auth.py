from __future__ import annotations
import json, os
from datetime import datetime, timezone
from pathlib import Path
import requests
from .config import AppConfig

def export_auth_report(cfg: AppConfig) -> Path:
    endpoint = cfg.source
    if not endpoint.project_url or not endpoint.service_role_key: raise ValueError("source.project_url and source.service_role_key are required")
    headers = {"Authorization": f"Bearer {endpoint.service_role_key}", "apikey": endpoint.service_role_key}
    users, page = [], 1
    while True:
        response = requests.get(f"{endpoint.project_url.rstrip('/')}/auth/v1/admin/users", headers=headers, params={"page": page, "per_page": 1000}, timeout=60); response.raise_for_status()
        payload = response.json(); batch = payload.get("users", payload if isinstance(payload, list) else [])
        users.extend(batch)
        if len(batch) < 1000: break
        page += 1
    cfg.backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); path = cfg.backup_dir / f"auth_report_{stamp}.json"
    path.write_text(json.dumps({"created_at": datetime.now(timezone.utc).isoformat(), "source": endpoint.name, "count": len(users), "users": users}, indent=2), encoding="utf-8")
    os.chmod(path, 0o600)
    return path
