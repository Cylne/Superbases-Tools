from __future__ import annotations
from .config import AppConfig

def apply_retention(cfg: AppConfig) -> int:
    cfg.backup_dir.mkdir(parents=True, exist_ok=True)
    archives = sorted(cfg.backup_dir.glob("supamigrate_*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    for archive in archives[cfg.retention_count:]: archive.unlink()
    return max(0, len(archives) - cfg.retention_count)
