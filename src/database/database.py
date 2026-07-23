"""Persistência rastreável das execuções do Hydros.

O módulo mantém compatibilidade com o banco legado e adiciona:

- identificador único da execução;
- modo Histórico ou Instantâneo;
- decisão, confiança, completude e conflito;
- estado operacional da irrigação;
- metadados e domínio do APS;
- registro integral da rastreabilidade em JSON;
- avaliação humana: aceitar, modificar ou rejeitar.
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import json
import sqlite3
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple
from uuid import uuid4


USER_STATUSES = {"nao_avaliada", "aceita", "modificada", "rejeitada"}
HYDROS_ACTIONS = {
    "iniciar_irrigacao",
    "manter_irrigacao",
    "aumentar_irrigacao",
    "reduzir_irrigacao",
    "finalizar_irrigacao",
}


class Database:
    """Camada SQLite usada pela interface e pelos experimentos do Hydros."""

    def __init__(self, db_path: str = "hydros.db") -> None:
        self.db_path = str(db_path)
        # Ordem obrigatória para compatibilidade com bancos legados:
        # 1) garante a existência da tabela;
        # 2) adiciona as colunas ausentes;
        # 3) cria índices que dependem das novas colunas.
        self.criar_tabela()
        self.migrar_schema()
        self.criar_indices()

    @contextmanager
    def conectar(self) -> Iterator[sqlite3.Connection]:
        """Abre uma conexão transacional e garante o fechamento do arquivo.

        O gerenciador de contexto nativo de ``sqlite3.Connection`` realiza
        commit ou rollback, mas não fecha a conexão. Em Windows, isso pode
        manter o arquivo SQLite bloqueado após os testes e impedir a remoção
        de diretórios temporários. Este gerenciador fecha a conexão de forma
        determinística em todos os caminhos de execução.
        """

        conexao = sqlite3.connect(self.db_path)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        try:
            yield conexao
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    def criar_tabela(self) -> None:
        """Cria a tabela já no formato atual quando o banco é novo."""

        with self.conectar() as conexao:
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS execucoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id TEXT UNIQUE,
                    data_execucao TEXT NOT NULL,
                    analysis_timestamp TEXT,
                    talhao TEXT,
                    unit_id TEXT,
                    modo_execucao TEXT,
                    versao_arquitetura TEXT,
                    decisao_original TEXT,
                    decisao_final TEXT,
                    confianca REAL,
                    completude REAL,
                    indice_conflito REAL,
                    condicao_interna TEXT,
                    condicao_semantica TEXT,
                    revisao_humana INTEGER DEFAULT 0,
                    motivos_revisao_json TEXT,
                    avisos_governanca_json TEXT,
                    irrigacao_ativa INTEGER,
                    estado_irrigacao TEXT,
                    origem_estado_irrigacao TEXT,
                    confianca_estado_irrigacao REAL,
                    risco_previsto TEXT,
                    algoritmo_aps TEXT,
                    versao_modelo_aps TEXT,
                    status_dominio_aps TEXT,
                    compatibilidade_dominio_aps REAL,
                    explicacao TEXT,
                    trace_json TEXT,
                    status_usuario TEXT DEFAULT 'nao_avaliada',
                    acao_modificada_usuario TEXT,
                    justificativa_usuario TEXT,
                    data_avaliacao_usuario TEXT
                )
                """
            )

    def migrar_schema(self) -> None:
        """Acrescenta colunas ao banco legado sem apagar os registros existentes."""

        expected_columns: Dict[str, str] = {
            "execution_id": "TEXT",
            "analysis_timestamp": "TEXT",
            "unit_id": "TEXT",
            "modo_execucao": "TEXT",
            "versao_arquitetura": "TEXT",
            "decisao_original": "TEXT",
            "completude": "REAL",
            "indice_conflito": "REAL",
            "condicao_interna": "TEXT",
            "condicao_semantica": "TEXT",
            "revisao_humana": "INTEGER DEFAULT 0",
            "motivos_revisao_json": "TEXT",
            "avisos_governanca_json": "TEXT",
            "irrigacao_ativa": "INTEGER",
            "estado_irrigacao": "TEXT",
            "origem_estado_irrigacao": "TEXT",
            "confianca_estado_irrigacao": "REAL",
            "algoritmo_aps": "TEXT",
            "versao_modelo_aps": "TEXT",
            "status_dominio_aps": "TEXT",
            "compatibilidade_dominio_aps": "REAL",
            "trace_json": "TEXT",
            "status_usuario": "TEXT DEFAULT 'nao_avaliada'",
            "acao_modificada_usuario": "TEXT",
            "justificativa_usuario": "TEXT",
            "data_avaliacao_usuario": "TEXT",
        }

        with self.conectar() as conexao:
            existing = {
                str(row["name"])
                for row in conexao.execute("PRAGMA table_info(execucoes)")
            }

            for column, sql_type in expected_columns.items():
                if column not in existing:
                    conexao.execute(
                        f"ALTER TABLE execucoes ADD COLUMN {column} {sql_type}"
                    )

            # Registros antigos recebem um identificador rastreável, sem
            # alterar a decisão que já estava armazenada.
            old_rows = conexao.execute(
                """
                SELECT id
                FROM execucoes
                WHERE execution_id IS NULL OR TRIM(execution_id) = ''
                """
            ).fetchall()
            for row in old_rows:
                conexao.execute(
                    "UPDATE execucoes SET execution_id = ? WHERE id = ?",
                    (str(uuid4()), int(row["id"])),
                )

            conexao.execute(
                """
                UPDATE execucoes
                SET status_usuario = 'nao_avaliada'
                WHERE status_usuario IS NULL OR TRIM(status_usuario) = ''
                """
            )
            conexao.execute(
                """
                UPDATE execucoes
                SET decisao_original = decisao_final
                WHERE decisao_original IS NULL
                """
            )
            conexao.execute(
                """
                UPDATE execucoes
                SET unit_id = talhao
                WHERE unit_id IS NULL
                """
            )


    def criar_indices(self) -> None:
        """Cria índices somente após a migração das colunas legadas.

        Em bancos criados por versões anteriores do Hydros, a tabela
        ``execucoes`` não possuía ``execution_id``. Criar o índice antes de
        executar ``migrar_schema`` causava ``sqlite3.OperationalError`` na
        inicialização da interface.
        """

        with self.conectar() as conexao:
            conexao.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_execucoes_execution_id
                ON execucoes(execution_id)
                """
            )
            conexao.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execucoes_talhao_data
                ON execucoes(talhao, data_execucao)
                """
            )

    def salvar_registro_execucao(self, registro: Mapping[str, Any]) -> str:
        """Persiste o registro integral produzido pelo HydrosEngine."""

        if not isinstance(registro, Mapping):
            raise TypeError("O registro da execução deve ser um mapeamento.")

        decision = self._mapping(registro.get("decision"))
        predictive = self._mapping(registro.get("predictive_result"))
        consistency = self._mapping(registro.get("consistency"))
        current_context = self._mapping(registro.get("current_context"))
        irrigation = self._mapping(
            decision.get("irrigation_state")
            if isinstance(decision.get("irrigation_state"), Mapping)
            else consistency.get("irrigation_state")
        )

        execution_id = str(registro.get("execution_id") or uuid4())
        executed_at = str(
            registro.get("executed_at")
            or datetime.now().isoformat(timespec="seconds")
        )
        unit_id = str(
            registro.get("unit_id")
            or current_context.get("talhao")
            or "unidade_nao_informada"
        )
        action = str(
            decision.get("action")
            or decision.get("decisao_final")
            or "nao_informada"
        )

        trace_payload = self._json_roundtrip(dict(registro))

        values = {
            "execution_id": execution_id,
            "data_execucao": executed_at,
            "analysis_timestamp": registro.get("analysis_timestamp"),
            "talhao": unit_id,
            "unit_id": unit_id,
            "modo_execucao": registro.get("mode"),
            "versao_arquitetura": registro.get("architecture_version"),
            "decisao_original": action,
            "decisao_final": action,
            "confianca": self._float_or_none(decision.get("confidence")),
            "completude": self._float_or_none(decision.get("completeness")),
            "indice_conflito": self._float_or_none(
                decision.get("conflict_index")
            ),
            "condicao_interna": decision.get("internal_condition"),
            "condicao_semantica": decision.get("semantic_condition"),
            "revisao_humana": int(
                bool(decision.get("human_review_required", False))
            ),
            "motivos_revisao_json": self._dumps(
                decision.get("human_review_reasons", [])
            ),
            "avisos_governanca_json": self._dumps(
                decision.get("governance_warnings", [])
            ),
            "irrigacao_ativa": self._bool_or_none(
                decision.get("irrigation_active")
            ),
            "estado_irrigacao": decision.get("irrigation_state"),
            "origem_estado_irrigacao": decision.get(
                "irrigation_state_source"
            ),
            "confianca_estado_irrigacao": self._float_or_none(
                decision.get("irrigation_state_confidence")
            ),
            "risco_previsto": predictive.get("predicted_condition"),
            "algoritmo_aps": predictive.get("algorithm"),
            "versao_modelo_aps": predictive.get("model_version"),
            "status_dominio_aps": predictive.get("domain_status"),
            "compatibilidade_dominio_aps": self._float_or_none(
                predictive.get("domain_compatibility")
            ),
            "explicacao": decision.get("rationale"),
            "trace_json": self._dumps(trace_payload),
            "status_usuario": str(
                decision.get("user_status") or "nao_avaliada"
            ),
            "acao_modificada_usuario": decision.get(
                "user_modified_action"
            ),
            "justificativa_usuario": decision.get("user_justification"),
            "data_avaliacao_usuario": None,
        }

        columns = list(values.keys())
        placeholders = ", ".join("?" for _ in columns)
        assignments = ", ".join(
            f"{column} = excluded.{column}"
            for column in columns
            if column not in {"execution_id", "data_execucao"}
        )

        with self.conectar() as conexao:
            conexao.execute(
                f"""
                INSERT INTO execucoes ({', '.join(columns)})
                VALUES ({placeholders})
                ON CONFLICT(execution_id) DO UPDATE SET {assignments}
                """,
                tuple(values[column] for column in columns),
            )

        return execution_id

    def salvar_execucao(
        self,
        talhao: str,
        decisao_final: str,
        confianca: float,
        risco_previsto: str,
        explicacao: str,
    ) -> str:
        """Compatibilidade com a interface antiga.

        Novas integrações devem preferir ``salvar_registro_execucao``.
        """

        execution_id = str(uuid4())
        now = datetime.now().isoformat(timespec="seconds")
        with self.conectar() as conexao:
            conexao.execute(
                """
                INSERT INTO execucoes (
                    execution_id,
                    data_execucao,
                    talhao,
                    unit_id,
                    decisao_original,
                    decisao_final,
                    confianca,
                    risco_previsto,
                    explicacao,
                    status_usuario
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'nao_avaliada')
                """,
                (
                    execution_id,
                    now,
                    str(talhao),
                    str(talhao),
                    str(decisao_final),
                    str(decisao_final),
                    float(confianca),
                    str(risco_previsto),
                    str(explicacao),
                ),
            )
        return execution_id

    def registrar_avaliacao_usuario(
        self,
        execution_id: str,
        status: str,
        acao_modificada: Optional[str] = None,
        justificativa: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Registra a decisão humana sem alterar automaticamente o Hydros."""

        normalized_status = self._normalize_user_status(status)
        normalized_action = (
            str(acao_modificada).strip().lower()
            if acao_modificada is not None
            else None
        )

        if normalized_status == "modificada":
            if normalized_action not in HYDROS_ACTIONS:
                raise ValueError(
                    "Uma avaliação modificada exige uma ação válida do Hydros."
                )
        elif normalized_action is not None:
            raise ValueError(
                "A ação modificada deve ser informada somente quando o "
                "status for 'modificada'."
            )

        justification_text = (
            str(justificativa).strip() if justificativa is not None else None
        )
        evaluated_at = datetime.now().isoformat(timespec="seconds")

        with self.conectar() as conexao:
            row = conexao.execute(
                """
                SELECT trace_json, decisao_original
                FROM execucoes
                WHERE execution_id = ?
                """,
                (str(execution_id),),
            ).fetchone()

            if row is None:
                raise KeyError(
                    f"Execução não encontrada: {execution_id}"
                )

            final_action = (
                normalized_action
                if normalized_status == "modificada"
                else str(row["decisao_original"] or "nao_informada")
            )

            trace_payload = self._loads(row["trace_json"], default={})
            if isinstance(trace_payload, dict) and trace_payload:
                decision = trace_payload.setdefault("decision", {})
                decision["user_status"] = normalized_status
                decision["user_modified_action"] = normalized_action
                decision["user_justification"] = justification_text
                trace_payload.setdefault("metadata", {})[
                    "user_evaluated_at"
                ] = evaluated_at

            conexao.execute(
                """
                UPDATE execucoes
                SET status_usuario = ?,
                    acao_modificada_usuario = ?,
                    justificativa_usuario = ?,
                    data_avaliacao_usuario = ?,
                    decisao_final = ?,
                    trace_json = ?
                WHERE execution_id = ?
                """,
                (
                    normalized_status,
                    normalized_action,
                    justification_text,
                    evaluated_at,
                    final_action,
                    self._dumps(trace_payload) if trace_payload else row["trace_json"],
                    str(execution_id),
                ),
            )

        return self.buscar_execucao(str(execution_id))

    def buscar_execucao(self, execution_id: str) -> Dict[str, Any]:
        with self.conectar() as conexao:
            row = conexao.execute(
                "SELECT * FROM execucoes WHERE execution_id = ?",
                (str(execution_id),),
            ).fetchone()

        if row is None:
            raise KeyError(f"Execução não encontrada: {execution_id}")

        return self._row_to_dict(row)

    def listar_execucoes_detalhadas(
        self,
        limite: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM execucoes ORDER BY id DESC"
        parameters: Sequence[Any] = ()
        if limite is not None:
            if int(limite) <= 0:
                return []
            query += " LIMIT ?"
            parameters = (int(limite),)

        with self.conectar() as conexao:
            rows = conexao.execute(query, parameters).fetchall()

        return [self._row_to_dict(row) for row in rows]

    def listar_execucoes(self) -> List[Tuple[Any, ...]]:
        """Retorna o formato legado usado pela interface anterior."""

        with self.conectar() as conexao:
            rows = conexao.execute(
                """
                SELECT
                    data_execucao,
                    talhao,
                    decisao_final,
                    confianca,
                    risco_previsto,
                    explicacao
                FROM execucoes
                ORDER BY id DESC
                """
            ).fetchall()

        return [tuple(row) for row in rows]

    def quantidade_execucoes(self) -> int:
        with self.conectar() as conexao:
            row = conexao.execute(
                "SELECT COUNT(*) AS total FROM execucoes"
            ).fetchone()
        return int(row["total"])

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        payload = dict(row)
        payload["revisao_humana"] = bool(payload.get("revisao_humana"))
        payload["irrigacao_ativa"] = self._database_bool(
            payload.get("irrigacao_ativa")
        )
        payload["motivos_revisao"] = self._loads(
            payload.pop("motivos_revisao_json", None),
            default=[],
        )
        payload["avisos_governanca"] = self._loads(
            payload.pop("avisos_governanca_json", None),
            default=[],
        )
        payload["registro_execucao"] = self._loads(
            payload.pop("trace_json", None),
            default={},
        )
        return payload

    @staticmethod
    def _mapping(value: Any) -> Mapping[str, Any]:
        return value if isinstance(value, Mapping) else {}

    @staticmethod
    def _float_or_none(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bool_or_none(value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(bool(value))

    @staticmethod
    def _database_bool(value: Any) -> Optional[bool]:
        if value is None:
            return None
        return bool(value)

    @staticmethod
    def _dumps(value: Any) -> str:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            default=str,
            separators=(",", ":"),
        )

    @classmethod
    def _json_roundtrip(cls, value: Any) -> Any:
        return json.loads(cls._dumps(value))

    @staticmethod
    def _loads(value: Any, default: Any) -> Any:
        if value is None or value == "":
            return default
        try:
            return json.loads(str(value))
        except (TypeError, ValueError, json.JSONDecodeError):
            return default

    @staticmethod
    def _normalize_user_status(value: str) -> str:
        text = str(value or "").strip().lower()
        aliases = {
            "aceitar": "aceita",
            "aceito": "aceita",
            "aceitada": "aceita",
            "aceita": "aceita",
            "modificar": "modificada",
            "modificado": "modificada",
            "modificada": "modificada",
            "rejeitar": "rejeitada",
            "rejeitado": "rejeitada",
            "rejeitada": "rejeitada",
            "nao_avaliada": "nao_avaliada",
            "não_avaliada": "nao_avaliada",
        }
        normalized = aliases.get(text, text)
        if normalized not in USER_STATUSES:
            valid = ", ".join(sorted(USER_STATUSES))
            raise ValueError(
                f"Status de avaliação inválido: {value}. Use: {valid}."
            )
        return normalized
