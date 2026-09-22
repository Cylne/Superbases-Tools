from __future__ import annotations
import json, tempfile
from pathlib import Path
from .config import AppConfig
from .notify import notify
from .utils import file_lock, run, safe_extract_tar, sha256_file

def restore_backup(cfg: AppConfig, archive: str | Path, clean: bool = False) -> None:
    if not cfg.target.database_url: raise ValueError("target.database_url is required")
    source = Path(archive).expanduser().resolve()
    if not source.is_file(): raise FileNotFoundError(source)
    with file_lock(cfg.backup_dir / ".restore.lock"):
        with tempfile.TemporaryDirectory(prefix="supamigrate-restore-") as tmp:
            safe_extract_tar(source, Path(tmp))
            root = Path(tmp) / "backup"; manifest_path, dump = root / "manifest.json", root / "database.dump"
            if not manifest_path.is_file() or not dump.is_file(): raise ValueError("invalid SupaMigrate archive")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("format_version") != 1: raise ValueError("unsupported backup format")
            if sha256_file(dump) != manifest.get("database_sha256"): raise ValueError("checksum mismatch; restore aborted")
            cmd = ["pg_restore", "--dbname", cfg.target.database_url, "--no-owner", "--no-privileges", "--exit-on-error"]
            if clean: cmd += ["--clean", "--if-exists"]
            cmd.append(str(dump)); run(cmd, timeout=cfg.command_timeout, redact=[cfg.target.database_url])
            run(["psql", cfg.target.database_url, "-v", "ON_ERROR_STOP=1", "-Atc", "SELECT 1"], timeout=60, redact=[cfg.target.database_url])
    notify(cfg, f"✅ SupaMigrate restore completed\n{source.name} → {cfg.target.name}")
