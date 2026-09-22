from __future__ import annotations
import shutil
from rich.console import Console
from .config import AppConfig
from .utils import run
console = Console()

def system_check(cfg: AppConfig) -> bool:
    ok = True
    for binary in ("psql", "pg_dump", "pg_restore"):
        if shutil.which(binary): console.print(f"[green]✓[/green] {run([binary, '--version'], timeout=15).stdout.strip()}")
        else: console.print(f"[red]✗[/red] {binary} not found"); ok = False
    for label, endpoint in (("source", cfg.source), ("target", cfg.target)):
        if not endpoint.database_url: console.print(f"[yellow]![/yellow] {label} database URL is not configured"); continue
        try:
            run(["psql", endpoint.database_url, "-v", "ON_ERROR_STOP=1", "-Atc", "SELECT 1"], timeout=30, redact=[endpoint.database_url]); console.print(f"[green]✓[/green] {label} database connection")
        except RuntimeError as exc: console.print(f"[red]✗[/red] {label} database connection: {exc}"); ok = False
    try:
        cfg.backup_dir.mkdir(parents=True, exist_ok=True); probe = cfg.backup_dir / ".write-test"; probe.touch(); probe.unlink(); console.print(f"[green]✓[/green] writable backup directory: {cfg.backup_dir}")
    except OSError as exc: console.print(f"[red]✗[/red] backup directory: {exc}"); ok = False
    return ok
