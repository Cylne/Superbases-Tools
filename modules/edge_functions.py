from __future__ import annotations
import os, shutil
from .config import AppConfig
from .utils import run

def deploy_functions(cfg: AppConfig, names: list[str] | None = None) -> None:
    if not shutil.which("supabase"): raise RuntimeError("Supabase CLI is required; run ./install.sh --with-supabase-cli")
    if not cfg.target.project_ref or not cfg.target.access_token: raise ValueError("target.project_ref and target.access_token are required")
    if not cfg.functions_dir.is_dir(): raise FileNotFoundError(cfg.functions_dir)
    selected = names or sorted(p.name for p in cfg.functions_dir.iterdir() if p.is_dir() and p.name != "_shared")
    if not selected: raise ValueError(f"no Edge Functions found in {cfg.functions_dir}")
    env = os.environ.copy(); env["SUPABASE_ACCESS_TOKEN"] = cfg.target.access_token
    for name in selected:
        if not (cfg.functions_dir / name).is_dir(): raise FileNotFoundError(cfg.functions_dir / name)
        run(["supabase", "functions", "deploy", name, "--project-ref", cfg.target.project_ref, "--workdir", str(cfg.functions_dir.parent.parent)], timeout=cfg.command_timeout, redact=[cfg.target.access_token], env=env)
