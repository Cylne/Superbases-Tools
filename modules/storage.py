from __future__ import annotations
import mimetypes
from collections import deque
from urllib.parse import quote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import AppConfig, Endpoint

def _session(endpoint: Endpoint) -> requests.Session:
    if not endpoint.project_url or not endpoint.service_role_key: raise ValueError(f"{endpoint.name}: project_url and service_role_key are required")
    session = requests.Session(); session.headers.update({"Authorization": f"Bearer {endpoint.service_role_key}", "apikey": endpoint.service_role_key})
    session.mount("https://", HTTPAdapter(max_retries=Retry(total=4, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=None)))
    return session

def _url(endpoint: Endpoint, path: str) -> str: return f"{endpoint.project_url.rstrip('/')}/storage/v1/{path.lstrip('/')}"

def _objects(session: requests.Session, endpoint: Endpoint, bucket: str, page_size: int):
    prefixes, seen = deque([""]), set()
    while prefixes:
        prefix = prefixes.popleft()
        if prefix in seen: continue
        seen.add(prefix); offset = 0
        while True:
            response = session.post(_url(endpoint, f"object/list/{quote(bucket, safe='')}"), json={"prefix": prefix, "limit": page_size, "offset": offset, "sortBy": {"column": "name", "order": "asc"}}, timeout=60); response.raise_for_status(); rows = response.json()
            for row in rows:
                name = row.get("name", ""); full = f"{prefix}/{name}".strip("/")
                if row.get("id") is None: prefixes.append(full)
                elif full: yield full, row
            if len(rows) < page_size: break
            offset += page_size

def migrate_storage(cfg: AppConfig) -> dict[str, int]:
    src, dst = _session(cfg.source), _session(cfg.target); stats = {"buckets": 0, "objects": 0, "failed": 0}
    response = src.get(_url(cfg.source, "bucket"), timeout=60); response.raise_for_status()
    for bucket in response.json():
        bucket_id = str(bucket["id"])
        create = dst.post(_url(cfg.target, "bucket"), json={"id": bucket_id, "name": bucket.get("name", bucket_id), "public": bool(bucket.get("public", False)), "file_size_limit": bucket.get("file_size_limit"), "allowed_mime_types": bucket.get("allowed_mime_types")}, timeout=60)
        if create.status_code not in (200, 201, 409): create.raise_for_status()
        stats["buckets"] += 1
        for object_name, metadata in _objects(src, cfg.source, bucket_id, cfg.storage_page_size):
            encoded = "/".join(quote(part, safe="") for part in object_name.split("/")); bid = quote(bucket_id, safe="")
            try:
                download = src.get(_url(cfg.source, f"object/authenticated/{bid}/{encoded}"), timeout=300, stream=True); download.raise_for_status()
                content_type = download.headers.get("content-type") or metadata.get("metadata", {}).get("mimetype") or mimetypes.guess_type(object_name)[0] or "application/octet-stream"
                upload = dst.post(_url(cfg.target, f"object/{bid}/{encoded}"), data=download.raw, headers={"content-type": content_type, "x-upsert": "true"}, timeout=300); upload.raise_for_status(); stats["objects"] += 1
            except requests.RequestException: stats["failed"] += 1
    if stats["failed"]: raise RuntimeError(f"storage migration finished with {stats['failed']} failed object(s); successful: {stats['objects']}")
    return stats
