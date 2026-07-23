"""Validação integral e reproduzível do protótipo Hydros."""

from __future__ import annotations

import hashlib
import importlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "results" / "validation"
COMPARISON_DIR = ROOT / "results" / "dssat_comparison"

FUNCTIONAL_TESTS = [
    "test_hydros_model_flow.py",
    "test_hydros_modes.py",
    "test_hydros_algorithms.py",
    "test_hydros_scenarios.py",
    "test_dssat_adapter.py",
    "test_hydros_traceability.py",
    "test_hydros_evidence_quality.py",
    "test_hydros_action_scores.py",
    "test_hydros_ontology.py",
    "test_hydros_aps_safety.py",
    "test_hydros_aps_governance.py",
    "test_hydros_persistence.py",
    "test_hydros_interface.py",
    "test_hydros_release_readiness.py",
]

PIPELINE = [
    ("run_dssat_comparison.py", 900),
    ("diagnostico_resultados.py", 180),
    ("test_hydros_article_outputs.py", 240),
]

REQUIRED_ARTIFACTS = [
    "comparacao_detalhada.csv",
    "metricas_resumo.csv",
    "matriz_confusao_historico.csv",
    "matriz_confusao_instantaneo.csv",
    "diagnostico/distribuicao_classes.csv",
    "diagnostico/metricas_multiclasse.csv",
    "diagnostico/metricas_binarias.csv",
    "diagnostico/comparacao_modos.csv",
    "artigo/table_main_metrics.csv",
    "artigo/table_divergent_cases.csv",
    "artigo/table_reference_positive_events.csv",
    "artigo/table_actions_without_reference_support.csv",
    "artigo/figure_metrics_comparison.png",
    "artigo/figure_binary_confusion_matrix_historico.png",
    "artigo/figure_binary_confusion_matrix_instantaneo.png",
    "artigo/figure_reference_event_detection.png",
    "artigo/figure_governance_indicators.png",
    "artigo/experimental_results_summary.md",
]

HASH_TARGETS = [
    "src/config/hydros_terms.py",
    "src/core/contracts.py",
    "src/services/hydros_engine.py",
    "src/agents/aiec_agent.py",
    "src/agents/arg_agent.py",
    "src/agents/aps_agent.py",
    "src/agents/amdh_agent.py",
    "src/ontology/hydros_onto.py",
    "ontology/hydros_onto.ttl",
    "src/integrations/dssat_adapter.py",
    "data/hydros_soja_dssat_real_v2.csv",
]


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_version(name: str) -> str | None:
    try:
        module = importlib.import_module(name)
    except Exception:
        return None
    return str(getattr(module, "__version__", "não informado"))


def run_script(filename: str, timeout: int) -> dict[str, Any]:
    path = ROOT / filename
    started = time.perf_counter()

    if not path.exists():
        return {
            "script": filename,
            "status": "ausente",
            "returncode": None,
            "elapsed_seconds": 0.0,
            "stdout": "",
            "stderr": f"Arquivo não encontrado: {path}",
        }

    try:
        process = subprocess.run(
            [sys.executable, str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {
            "script": filename,
            "status": "ok" if process.returncode == 0 else "falhou",
            "returncode": process.returncode,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "script": filename,
            "status": "timeout",
            "returncode": None,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "stdout": exc.stdout if isinstance(exc.stdout, str) else "",
            "stderr": f"Tempo limite excedido: {timeout}s.",
        }


def read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    frame = pd.read_csv(path)
    return json.loads(frame.to_json(orient="records", force_ascii=False))


def scientific_summary() -> dict[str, Any]:
    detailed_path = COMPARISON_DIR / "comparacao_detalhada.csv"
    detailed = (
        pd.read_csv(detailed_path)
        if detailed_path.exists()
        else pd.DataFrame()
    )

    divergences = 0
    if "mesma_decisao_hydros" in detailed.columns:
        divergences = int(
            (~detailed["mesma_decisao_hydros"].astype(bool)).sum()
        )

    return {
        "n_observations": int(len(detailed)),
        "n_dssat_runs": (
            int(detailed["cenario_id"].nunique())
            if "cenario_id" in detailed.columns
            else 0
        ),
        "n_mode_divergences": divergences,
        "metrics_summary": read_csv(
            COMPARISON_DIR / "metricas_resumo.csv"
        ),
        "multiclass_metrics": read_csv(
            COMPARISON_DIR / "diagnostico" / "metricas_multiclasse.csv"
        ),
        "intensification_metrics": read_csv(
            COMPARISON_DIR / "diagnostico" / "metricas_binarias.csv"
        ),
        "limitations": [
            "DSSAT utilizado como benchmark de simulação.",
            "Somente duas execuções DSSAT no conjunto atual.",
            "Forte desbalanceamento entre classes.",
            "APS legado parcialmente fora do domínio nos cenários DSSAT.",
            "Ausência de avaliação em malha fechada.",
            "Resultados interpretados como prova de conceito.",
        ],
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Relatório de validação integral do Hydros",
        "",
        f"- Data UTC: `{report['generated_at_utc']}`",
        f"- Resultado: **{report['overall_status'].upper()}**",
        f"- Python: `{report['environment']['python']}`",
        f"- Plataforma: `{report['environment']['platform']}`",
        "",
        "## Testes funcionais",
        "",
        "| Script | Status | Tempo (s) |",
        "|---|---:|---:|",
    ]

    for result in report["functional_tests"]:
        lines.append(
            f"| `{result['script']}` | {result['status']} | "
            f"{result['elapsed_seconds']:.3f} |"
        )

    lines += [
        "",
        "## Pipeline experimental",
        "",
        "| Script | Status | Tempo (s) |",
        "|---|---:|---:|",
    ]
    for result in report["pipeline"]:
        lines.append(
            f"| `{result['script']}` | {result['status']} | "
            f"{result['elapsed_seconds']:.3f} |"
        )

    summary = report["scientific_summary"]
    lines += [
        "",
        "## Síntese",
        "",
        f"- Observações: **{summary['n_observations']}**",
        f"- Execuções DSSAT: **{summary['n_dssat_runs']}**",
        f"- Divergências entre modos: **{summary['n_mode_divergences']}**",
        "",
        "## Limitações",
        "",
    ]
    lines.extend(f"- {item}" for item in summary["limitations"])

    lines += ["", "## Artefatos", ""]
    for item in report["artifacts"]:
        lines.append(
            f"- `{item['path']}`: {item['status']} "
            f"({item['size_bytes']} bytes)"
        )

    lines += ["", "## SHA-256", ""]
    for item in report["hashes"]:
        lines.append(f"- `{item['path']}`: `{item['sha256']}`")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n=== VALIDAÇÃO INTEGRAL DO HYDROS ===")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Projeto: {ROOT}")

    functional_results: list[dict[str, Any]] = []
    for index, script in enumerate(FUNCTIONAL_TESTS, start=1):
        print(
            f"[TESTE {index:02d}/{len(FUNCTIONAL_TESTS):02d}] "
            f"{script} ... ",
            end="",
            flush=True,
        )
        result = run_script(script, 180)
        functional_results.append(result)
        print(result["status"].upper())
        if result["status"] != "ok":
            print(result["stderr"] or result["stdout"][-2500:])

    functional_ok = all(
        result["status"] == "ok" for result in functional_results
    )

    pipeline_results: list[dict[str, Any]] = []
    if functional_ok:
        for script, timeout in PIPELINE:
            print(f"[PIPELINE] {script} ... ", end="", flush=True)
            result = run_script(script, timeout)
            pipeline_results.append(result)
            print(result["status"].upper())
            if result["status"] != "ok":
                print(result["stderr"] or result["stdout"][-3500:])
                break
    else:
        pipeline_results = [
            {
                "script": script,
                "status": "não executado",
                "returncode": None,
                "elapsed_seconds": 0.0,
                "stdout": "",
                "stderr": "Há testes funcionais com falha.",
            }
            for script, _ in PIPELINE
        ]

    artifacts: list[dict[str, Any]] = []
    for relative in REQUIRED_ARTIFACTS:
        path = COMPARISON_DIR / relative
        artifacts.append(
            {
                "path": str(path.relative_to(ROOT)),
                "status": "ok" if path.exists() and path.stat().st_size > 0
                else "ausente",
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
        )

    hashes = []
    for relative in HASH_TARGETS:
        path = ROOT / relative
        if path.exists():
            hashes.append({"path": relative, "sha256": sha256(path)})

    pipeline_ok = (
        len(pipeline_results) == len(PIPELINE)
        and all(item["status"] == "ok" for item in pipeline_results)
    )
    artifacts_ok = all(item["status"] == "ok" for item in artifacts)
    overall_ok = functional_ok and pipeline_ok and artifacts_ok

    report = {
        "schema_version": "1.0",
        "generated_at_utc": now_utc(),
        "overall_status": "ok" if overall_ok else "falhou",
        "environment": {
            "python": sys.version.replace("\n", " "),
            "executable": sys.executable,
            "platform": platform.platform(),
            "packages": {
                "numpy": package_version("numpy"),
                "pandas": package_version("pandas"),
                "pyarrow": package_version("pyarrow"),
                "scikit-learn": package_version("sklearn"),
                "streamlit": package_version("streamlit"),
                "rdflib": package_version("rdflib"),
            },
        },
        "functional_tests": functional_results,
        "pipeline": pipeline_results,
        "artifacts": artifacts,
        "hashes": hashes,
        "scientific_summary": scientific_summary(),
    }

    json_path = OUTPUT_DIR / "hydros_validation_report.json"
    markdown_path = OUTPUT_DIR / "hydros_validation_report.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(
        markdown_report(report),
        encoding="utf-8",
    )

    passed = sum(
        item["status"] == "ok" for item in functional_results
    )
    print("\n=== RESUMO DA VALIDAÇÃO ===")
    print(f"Testes aprovados: {passed}/{len(FUNCTIONAL_TESTS)}")
    print(f"Pipeline experimental: {'OK' if pipeline_ok else 'FALHOU'}")
    print(f"Artefatos: {'OK' if artifacts_ok else 'INCOMPLETOS'}")
    print(f"Relatório JSON: {json_path}")
    print(f"Relatório Markdown: {markdown_path}")
    print(f"VALIDAÇÃO INTEGRAL: {'OK' if overall_ok else 'FALHOU'}")

    if not overall_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
