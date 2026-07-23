"""Teste de regressão da migração do banco legado do Hydros."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from tempfile import TemporaryDirectory

from src.database.database import Database


def criar_banco_legado(path: Path) -> None:
    conexao = sqlite3.connect(path)
    try:
        conexao.execute(
            """
            CREATE TABLE execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_execucao TEXT,
                talhao TEXT,
                decisao_final TEXT,
                confianca REAL,
                risco_previsto TEXT,
                explicacao TEXT
            )
            """
        )
        conexao.execute(
            """
            INSERT INTO execucoes (
                data_execucao,
                talhao,
                decisao_final,
                confianca,
                risco_previsto,
                explicacao
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "2026-07-23 10:00:00",
                "Talhao_Legado",
                "manter_irrigacao",
                0.80,
                "baixo",
                "Registro criado antes da versão 0.3.0-agentic.",
            ),
        )
        conexao.commit()
    finally:
        conexao.close()


def main() -> None:
    with TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "hydros_legado.db"
        criar_banco_legado(db_path)

        database = Database(str(db_path))
        registros = database.listar_execucoes_detalhadas()

        conexao = sqlite3.connect(db_path)
        try:
            colunas = {
                row[1]
                for row in conexao.execute("PRAGMA table_info(execucoes)")
            }
            indices = {
                row[1]
                for row in conexao.execute("PRAGMA index_list(execucoes)")
            }
        finally:
            conexao.close()

        obrigatorias = {
            "execution_id",
            "modo_execucao",
            "versao_arquitetura",
            "trace_json",
            "status_usuario",
        }

        assert obrigatorias.issubset(colunas), (
            f"Colunas não migradas: {sorted(obrigatorias - colunas)}"
        )
        assert "idx_execucoes_execution_id" in indices
        assert len(registros) == 1
        assert registros[0]["execution_id"]
        assert registros[0]["decisao_original"] == "manter_irrigacao"
        assert registros[0]["unit_id"] == "Talhao_Legado"
        assert registros[0]["status_usuario"] == "nao_avaliada"

        print("\n=== MIGRAÇÃO DO BANCO LEGADO ===")
        print(f"Colunas após migração: {len(colunas)}")
        print(f"Registros preservados: {len(registros)}")
        print(f"Execution ID criado: {registros[0]['execution_id']}")
        print("Índice de rastreabilidade: OK")
        print("MIGRAÇÃO DO BANCO LEGADO: OK")


if __name__ == "__main__":
    main()
