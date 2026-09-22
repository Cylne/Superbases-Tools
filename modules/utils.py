from __future__ import annotations
import contextlib, fcntl, hashlib, os, subprocess, tarfile
from pathlib import Path
from typing import Iterator, Sequence

def run(command: Sequence[str], timeout: int = 3600, redact: list[str] | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    try: return subprocess.run(list(command), check=True, text=True, capture_output=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc: raise RuntimeError(f"command timed out after {timeout}s") from exc
    except subprocess.CalledProcessError as exc:
        message = (exc.stderr or exc.stdout or "unknown command error").strip()
        for secret in redact or []:
            if secret: message = message.replace(secret, "[REDACTED]")
        raise RuntimeError(message[-2000:]) from exc

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""): digest.update(chunk)
    return digest.hexdigest()

def atomic_tar(source_dir: Path, destination: Path) -> None:
    temp = destination.with_suffix(destination.suffix + ".partial")
    try:
        with tarfile.open(temp, "w:gz") as archive: archive.add(source_dir, arcname=source_dir.name, recursive=True)
        os.replace(temp, destination)
    finally: temp.unlink(missing_ok=True)

def safe_extract_tar(archive_path: Path, destination: Path) -> None:
    destination = destination.resolve()
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            target = (destination / member.name).resolve()
            if destination != target and destination not in target.parents: raise ValueError("unsafe path in backup archive")
            if member.issym() or member.islnk(): raise ValueError("links are not allowed in backup archives")
        archive.extractall(destination, filter="data")

@contextlib.contextmanager
def file_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as lock:
        try: fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise RuntimeError(f"another operation is already running ({path.name})") from exc
        yield
