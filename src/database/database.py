import sqlite3
from datetime import datetime


class Database:
    def listar_execucoes(self):
        """
        Busca todas as análises já salvas no banco SQLite.
        """

        # Abre conexão com o banco
        conexao = self.conectar()
        cursor = conexao.cursor()

        # Busca os registros mais recentes primeiro
        cursor.execute("""
            SELECT
                data_execucao,
                talhao,
                decisao_final,
                confianca,
                risco_previsto,
                explicacao
            FROM execucoes
            ORDER BY id DESC
        """)

        # Guarda os registros encontrados
        registros = cursor.fetchall()

        # Fecha conexão
        conexao.close()

        return registros








    def __init__(self, db_path="hydros.db"):
        self.db_path = db_path
        self.criar_tabela()

    def conectar(self):
        return sqlite3.connect(self.db_path)

    def criar_tabela(self):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_execucao TEXT,
                talhao TEXT,
                decisao_final TEXT,
                confianca REAL,
                risco_previsto TEXT,
                explicacao TEXT
            )
        """)

        conexao.commit()
        conexao.close()

    def salvar_execucao(self, talhao, decisao_final, confianca, risco_previsto, explicacao):
        conexao = self.conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO execucoes (
                data_execucao,
                talhao,
                decisao_final,
                confianca,
                risco_previsto,
                explicacao
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            talhao,
            decisao_final,
            confianca,
            risco_previsto,
            explicacao
        ))

        conexao.commit()
        conexao.close()