#!/usr/bin/env python3
"""Create a fresh, verifiable TASK-012 handover snapshot without credentials/cache."""

import argparse
import datetime
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tarfile


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def snapshot_source(repo, target):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(repo), *args])
    state = dict(head=git("rev-parse", "HEAD").decode().strip(),
                 branch=git("branch", "--show-current").decode().strip(),
                 status=git("status", "--porcelain=v1").decode())
    names = sorted(set(git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0")) - {b""})
    hashes = {}
    with tarfile.open(target, "w:gz", compresslevel=6) as archive:
        for encoded in names:
            relative = encoded.decode()
            source = repo / relative
            if not source.exists() and not source.is_symlink():
                continue  # A tracked deletion is recorded in Git status.
            if source.is_symlink():
                raise RuntimeError(f"Review source symlink before packaging: {source}")
            if not source.is_file():
                continue
            if source.name == ".env" or source.suffix in (".key", ".pem"):
                raise RuntimeError(f"Review possible credential before packaging: {source}")
            hashes[relative] = digest(source)
            archive.add(source, arcname=repo.name + "/" + relative, recursive=False)
    changed = [name for name, value in hashes.items() if not (repo/name).is_file() or digest(repo/name) != value]
    if changed:
        raise RuntimeError("Source changed while packaging: " + repr(changed))
    # Verify every archived file against the source snapshot rather than trusting
    # gzip completion or a tar listing alone.
    with tarfile.open(target, "r:gz") as archive:
        for member in archive.getmembers():
            if member.isfile():
                relative = member.name[len(repo.name)+1:]
                if hashlib.sha256(archive.extractfile(member).read()).hexdigest() != hashes[relative]:
                    raise RuntimeError("Source archive hash mismatch: " + member.name)
    return dict(**state, files=len(hashes), source_sha256=hashes, archive_sha256=digest(target))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--deliverables", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    q, out = args.run_dir.resolve(), args.out.resolve()
    if out.exists():
        raise RuntimeError("Use a new backup path; never overwrite a previous snapshot")
    runtime = json.loads((q/"runtime.json").read_text())
    audit = json.loads((q/"analysis-final.json").read_text())
    if audit["status"] != "PASS" or audit["accepted_runs"] != 15:
        raise RuntimeError("All15 audited runs required before final handover backup")
    for name in ("cold-start.json", "cleanup.json"):
        if json.loads((q/name).read_text())["status"] != "PASS":
            raise RuntimeError("Complete and verify " + name + " before final backup")
    if json.loads((q/"demo-status.json").read_text())["status"] != "QA_PASSED":
        raise RuntimeError("Video must pass playback/visual QA before final backup")
    out.mkdir(parents=True)
    (out/"source").mkdir()
    firmware = Path(runtime["root"])
    sources = {}
    for name in ("firmware", "backend", "dashboard"):
        repo = firmware.parent / name
        sources[name] = snapshot_source(repo, out/"source"/(name+".tar.gz"))
    (out/"source-state.json").write_text(json.dumps(sources, indent=2, ensure_ascii=False) + "\n")
    backup = out/"qa-final.db"
    original = sqlite3.connect(f"file:{runtime['database']}?mode=ro", uri=True)
    destination = sqlite3.connect(backup)
    original.backup(destination)
    original.close()
    check = [row[0] for row in destination.execute("PRAGMA quick_check")]
    counts = {table: destination.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] for table in ("telemetry", "commands", "alerts", "experiments", "ingest_errors")}
    pending = destination.execute("SELECT COUNT(*) FROM commands WHERE status='PENDING'").fetchone()[0]
    opened = destination.execute("SELECT COUNT(*) FROM experiments WHERE ended_at IS NULL").fetchone()[0]
    destination.close()
    if check != ["ok"] or pending or opened:
        raise RuntimeError(f"Database not ready for handover: {check}, pending={pending}, open={opened}")
    (out/"database.json").write_text(json.dumps(dict(quick_check=check, counts=counts, pending_commands=pending, open_experiments=opened, sha256=digest(backup)), indent=2)+"\n")
    shutil.copytree(q/"attempts", out/"attempts", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copytree(args.deliverables, out/"deliverables")
    shutil.copytree(q/"screenshots", out/"screenshots")
    for pattern in ("word-preview*", "slide-preview*", "video-demo-*", "video-raw", "video-review", "office-smoke"):
        for folder in sorted(q.glob(pattern)):
            if folder.is_dir():
                shutil.copytree(folder, out/folder.name)
    runtime_out = out/"qa-runtime"
    runtime_out.mkdir()
    for name in ("mosquitto", "task012-mosquitto-2.1.2.tar.gz", "task012-cjson.tar.gz"):
        shutil.copy2(q/"runtime"/name, runtime_out/name)
    shutil.copytree(q/"runtime/lib", runtime_out/"lib")
    office = runtime_out/"office-manifests"
    office.mkdir()
    for name in ("package.json", "package-lock.json", "requirements-frozen.txt", "setup-result.json", "wps-qt.json"):
        if (q/"runtime/office"/name).exists():
            shutil.copy2(q/"runtime/office"/name, office/name)
    raw = out/"raw"; raw.mkdir()
    for source in sorted(q.glob("*events.jsonl")):
        with source.open("rb") as incoming, gzip.open(raw/(source.name+".gz"), "wb", compresslevel=6) as target:
            shutil.copyfileobj(incoming, target)
        with gzip.open(raw/(source.name+".gz"), "rb") as compressed:
            value = hashlib.sha256()
            for chunk in iter(lambda: compressed.read(1024*1024), b""):
                value.update(chunk)
            if value.hexdigest() != digest(source):
                raise RuntimeError("Raw log changed during backup: " + source.name)
    for name in ("runtime.json", "analysis-final.json", "campaign-completed.json", "campaign-summary.json", "demo-status.json", "owned-processes.json", "mosquitto.conf", "main.log", "cold-start.json", "cleanup.json"):
        if (q/name).is_file():
            shutil.copy2(q/name, out/name)
    for node in ("node_01", "node_02", "node_03"):
        folder = out/"simulations"/node
        folder.mkdir(parents=True)
        for name in ("diagram.json", "wokwi.toml", "build/firmware.bin", "build/firmware.elf"):
            source = q/node/name
            if not source.is_file():
                raise RuntimeError("Missing simulator artifact: " + str(source))
            target = folder/name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    shutil.copy2(firmware/"docs/demo-runbook.md", out/"RUNBOOK.md")
    (out/"README.md").write_text("# TASK-012 backup\n\nSource archives preserve HEAD plus working-tree changes; no commit was created. QA runtime paths are as-run references, not portable startup commands. Restore to a new directory and use RUNBOOK.md. Wokwi license/credentials and dependency caches are excluded. DOCX/PPTX are editable; user exports PDF in WPS.\n", encoding="utf-8")
    files = {str(p.relative_to(out)): dict(bytes=p.stat().st_size, sha256=digest(p)) for p in sorted(out.rglob("*")) if p.is_file()}
    manifest = dict(created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(), files=files)
    (out/"manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+"\n")
    archive_path = out.with_suffix(".tar.gz")
    if archive_path.exists():
        raise RuntimeError("Archive already exists")
    with tarfile.open(archive_path, "w:gz", compresslevel=6) as archive:
        archive.add(out, arcname=out.name)
    checked = 0
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or member.name == out.name+"/manifest.json":
                continue
            name = member.name[len(out.name)+1:]
            if name not in files or hashlib.sha256(archive.extractfile(member).read()).hexdigest() != files[name]["sha256"]:
                raise RuntimeError("Backup archive mismatch: " + member.name)
            checked += 1
    result = dict(status="PASS", archive=str(archive_path), sha256=digest(archive_path), bytes=archive_path.stat().st_size, verified_files=checked, database_quick_check=check)
    (out.parent/(out.name+"-verification.json")).write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
