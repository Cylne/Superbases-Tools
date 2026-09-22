import io, json, tarfile
from pathlib import Path
import pytest
from modules.config import load_config
from modules.utils import safe_extract_tar, sha256_file

def test_config_expands_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("SOURCE_DATABASE_URL", "postgresql://source")
    monkeypatch.setenv("TARGET_DATABASE_URL", "postgresql://target")
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text('{"source":{"database_url":"${SOURCE_DATABASE_URL}"},"target":{"database_url":"${TARGET_DATABASE_URL}"},"settings":{"retention_count":3}}')
    cfg = load_config(str(cfg_file))
    assert cfg.source.database_url == "postgresql://source"
    assert cfg.retention_count == 3

def test_config_missing_environment_is_clear(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"source":{"database_url":"${NOT_SET}"},"target":{}}')
    with pytest.raises(RuntimeError, match="NOT_SET"):
        load_config(str(path))

def test_safe_extract_rejects_traversal(tmp_path):
    archive = tmp_path / "bad.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        data = b"bad"; info = tarfile.TarInfo("../../escape.txt"); info.size = len(data); tar.addfile(info, io.BytesIO(data))
    with pytest.raises(ValueError, match="unsafe path"):
        safe_extract_tar(archive, tmp_path / "out")

def test_sha256_is_stable(tmp_path):
    path = tmp_path / "value"; path.write_bytes(b"abc")
    assert sha256_file(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
