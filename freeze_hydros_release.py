"""Cria uma cópia congelada e reproduzível da versão atual do Hydros."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.config.hydros_terms import VERSAO_ARQUITETURA

ROOT = Path(__file__).resolve().parent
RELEASES = ROOT / "releases"
VALIDATION_REPORT = (
    ROOT / "results" / "validation" / "hydros_validation_report.json"
)

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".venv-1",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "releases",
}

EXCLUDED_FILES = {
    "hydros.db",
    ".DS_Store",
}

INCLUDED_ROOTS = [
    "src",
    "ontology",
    "data",
    "results/dssat_comparison",
]

INCLUDED_FILES = [
    "app.py",
    "README.md",
    "STATUS_HYDROS.md",
    "DOCUMENTACAO_CODIGO_HYDROS.md",
    "REPRODUCIBILITY.md",
    "CHANGELOG.md",
    "requirements.txt",
    "run_dssat_comparison.py",
    "diagnostico_resultados.py",
    "gerar_resultados_artigo.py",
    "run_hydros_validation.py",
    "freeze_hydros_release.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def allowed(path: Path) -> bool:
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.name in EXCLUDED_FILES:
        return False
    if path.suffix in {".pyc", ".pyo"}:
        return False
    return True


def collect_files() -> list[Path]:
    files: set[Path] = set()

    for relative in INCLUDED_ROOTS:
        root = ROOT / relative
        if root.exists():
            for path in root.rglob("*"):
                if path.is_file() and allowed(path.relative_to(ROOT)):
                    files.add(path)

    for pattern in ("test_*.py",):
        for path in ROOT.glob(pattern):
            if path.is_file():
                files.add(path)

    for relative in INCLUDED_FILES:
        path = ROOT / relative
        if path.exists() and path.is_file():
            files.add(path)

    if VALIDATION_REPORT.exists():
        files.add(VALIDATION_REPORT)
        md_report = VALIDATION_REPORT.with_suffix(".md")
        if md_report.exists():
            files.add(md_report)

    return sorted(files, key=lambda item: str(item.relative_to(ROOT)))


def main() -> None:
    if not VALIDATION_REPORT.exists():
        raise RuntimeError(
            "Execute python run_hydros_validation.py antes do congelamento."
        )

    validation = json.loads(
        VALIDATION_REPORT.read_text(encoding="utf-8")
    )
    if validation.get("overall_status") != "ok":
        raise RuntimeError(
            "O relatório de validação não está aprovado. "
            "Corrija as falhas antes de criar a versão."
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_version = VERSAO_ARQUITETURA.replace(".", "_").replace("-", "_")
    release_name = f"hydros_{safe_version}_{timestamp}"
    RELEASES.mkdir(parents=True, exist_ok=True)

    staging = RELEASES / release_name
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    manifest_files = []
    for source in collect_files():
        relative = source.relative_to(ROOT)
        target = staging / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        manifest_files.append(
            {
                "path": str(relative).replace("\\", "/"),
                "size_bytes": source.stat().st_size,
                "sha256": sha256(source),
            }
        )

    manifest = {
        "release_name": release_name,
        "architecture_version": VERSAO_ARQUITETURA,
        "created_at_utc": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ),
        "validation_report": str(
            VALIDATION_REPORT.relative_to(ROOT)
        ).replace("\\", "/"),
        "file_count": len(manifest_files),
        "files": manifest_files,
        "scientific_scope": (
            "Protótipo funcional e rastreável para avaliação experimental "
            "preliminar; não constitui sistema agronomicamente validado."
        ),
    }

    manifest_path = staging / "RELEASE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    archive_path = RELEASES / f"{release_name}.zip"
    if archive_path.exists():
        archive_path.unlink()

    with zipfile.ZipFile(
        archive_path, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for path in sorted(staging.rglob("*")):
            if path.is_file():
                archive.write(
                    path,
                    Path(release_name) / path.relative_to(staging),
                )

    archive_hash = sha256(archive_path)
    checksum_path = archive_path.with_suffix(".sha256")
    checksum_path.write_text(
        f"{archive_hash}  {archive_path.name}\n",
        encoding="utf-8",
    )

    shutil.rmtree(staging)

    print("\n=== VERSÃO CONGELADA DO HYDROS ===")
    print(f"Versão: {VERSAO_ARQUITETURA}")
    print(f"Arquivos incluídos: {len(manifest_files)}")
    print(f"ZIP: {archive_path}")
    print(f"SHA-256: {archive_hash}")
    print("CONGELAMENTO DA VERSÃO: OK")


if __name__ == "__main__":
    main()
