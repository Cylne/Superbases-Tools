from __future__ import annotations
import json, tempfile
from datetime import datetime, timezone
from pathlib import Path
from .config import AppConfig
from .notify import notify
from .retention import apply_retention
from .utils import atomic_tar, file_lock, run, sha256_file

def create_backup(cfg: AppConfig, label: str = "manual") -> Path:
    if not cfg.source.database_url: raise ValueError("source.database_url is required")
    cfg.backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_label = "".join(c for c in label if c.isalnum() or c in "-_")[:32] or "manual"
    final = cfg.backup_dir / f"supamigrate_{stamp}_{safe_label}.tar.gz"
    with file_lock(cfg.backup_dir / ".backup.lock"):
        with tempfile.TemporaryDirectory(prefix="supamigrate-") as tmp:
            root = Path(tmp) / "backup"; root.mkdir()
            dump, log = root / "database.dump", root / "pg_dump.log"
            result = run(["pg_dump", cfg.source.database_url, "--format=custom", "--no-owner", "--no-privileges", "--verbose", "--file", str(dump)], timeout=cfg.command_timeout, redact=[cfg.source.database_url])
            log.write_text(result.stderr, encoding="utf-8")
            manifest = {"format_version": 1, "created_at": datetime.now(timezone.utc).isoformat(), "source_name": cfg.source.name, "label": safe_label, "dump_format": "postgresql-custom", "database_sha256": sha256_file(dump), "database_size": dump.stat().st_size, "tool": "SupaMigrate Enterprise"}
            (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            atomic_tar(root, final)
        if not final.is_file() or final.stat().st_size < 128: raise RuntimeError("backup archive validation failed")
        apply_retention(cfg)
        notify(cfg, f"✅ SupaMigrate backup completed\n{final.name}\n{final.stat().st_size:,} bytes")
        return final
