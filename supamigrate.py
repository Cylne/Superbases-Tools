#!/usr/bin/env python3
"""SupaMigrate command line entrypoint."""
from __future__ import annotations

import argparse
import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from modules.auth import export_auth_report
from modules.backup import create_backup
from modules.checker import system_check
from modules.config import ConfigError, load_config
from modules.edge_functions import deploy_functions
from modules.restore import restore_backup
from modules.retention import apply_retention
from modules.storage import migrate_storage

console = Console()

def banner() -> None:
    console.print(Panel.fit("[bold cyan]SupaMigrate Enterprise[/bold cyan]\nSupabase Backup, Restore & Migration Toolkit\n\n[dim]Developer: t.me/inireii3\nChannel: t.me/cylneee[/dim]"))

def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Production Supabase migration toolkit")
    p.add_argument("--config", default=None, help="Path to config.json")
    sub = p.add_subparsers(dest="command")
    b = sub.add_parser("backup", help="Create a verified database backup")
    b.add_argument("--label", default="manual")
    r = sub.add_parser("restore", help="Restore a backup archive")
    r.add_argument("archive")
    r.add_argument("--clean", action="store_true")
    sub.add_parser("check", help="Check configuration and dependencies")
    sub.add_parser("storage", help="Migrate Storage buckets and objects")
    sub.add_parser("auth-report", help="Export Auth users to an audit report")
    f = sub.add_parser("functions", help="Deploy local Edge Functions")
    f.add_argument("--name", action="append", dest="names")
    sub.add_parser("retention", help="Apply backup retention policy")
    return p

def run_command(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    if args.command == "backup":
        result = create_backup(cfg, label=args.label)
        console.print(f"[green]Backup verified:[/green] {result}")
    elif args.command == "restore":
        restore_backup(cfg, args.archive, clean=args.clean)
        console.print("[green]Restore and verification completed.[/green]")
    elif args.command == "check":
        return 0 if system_check(cfg) else 1
    elif args.command == "storage":
        console.print(f"[green]Storage migration completed:[/green] {migrate_storage(cfg)}")
    elif args.command == "auth-report":
        console.print(f"[green]Auth report written:[/green] {export_auth_report(cfg)}")
    elif args.command == "functions":
        deploy_functions(cfg, args.names)
    elif args.command == "retention":
        console.print(f"[green]Retention complete:[/green] removed {apply_retention(cfg)} archive(s)")
    return 0

def interactive(config_path: str | None) -> int:
    while True:
        banner()
        choice = questionary.select("Choose an operation", choices=["Backup database", "Restore database", "Migrate Storage", "Export Auth report", "Deploy Edge Functions", "Apply retention", "System check", "Exit"]).ask()
        if not choice or choice == "Exit":
            return 0
        argv = ["--config", config_path] if config_path else []
        if choice == "Backup database": argv += ["backup"]
        elif choice == "Restore database":
            archive = questionary.path("Backup archive:", only_files=True).ask()
            if not archive: continue
            clean = questionary.confirm("Clean matching target objects first?", default=False).ask()
            argv += ["restore", archive] + (["--clean"] if clean else [])
        elif choice == "Migrate Storage": argv += ["storage"]
        elif choice == "Export Auth report": argv += ["auth-report"]
        elif choice == "Deploy Edge Functions": argv += ["functions"]
        elif choice == "Apply retention": argv += ["retention"]
        else: argv += ["check"]
        try:
            run_command(parser().parse_args(argv))
        except Exception as exc:
            console.print(f"[bold red]Failed:[/bold red] {exc}")
        questionary.press_any_key_to_continue().ask()

def main() -> int:
    args = parser().parse_args()
    try:
        return run_command(args) if args.command else interactive(args.config)
    except (ConfigError, FileNotFoundError, RuntimeError, ValueError) as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
        return 130

if __name__ == "__main__":
    sys.exit(main())
