import sqlite3
import datetime

# --- Módulo de Gerenciamento de Banco de Dados ---
# Este módulo encapsula todas as interações com o banco de dados SQLite,
# garantindo operações consistentes e seguras.
# O design agora exige que o caminho do arquivo do banco de dados (db_file)
# seja explicitamente passado para as funções, promovendo modularidade e reusabilidade.
# Nota: A importação de 'app_state_manager' foi removida para evitar dependências circulares,
# um padrão comum em arquiteturas Kivy onde o AppState é acessado via App.get_running_app().

# Conecta-se a um banco de dados SQLite específico.
# db_file: O caminho completo para o arquivo do banco de dados.
def conectar(db_file):
    return sqlite3.connect(db_file) # Retorna o objeto de conexão, essencial para todas as operações de DB.

# Cria a tabela 'Gastos' no banco de dados se ela ainda não existir.
# Esta função é idempotente, garantindo que a tabela só seja criada uma vez.
# db_file: O caminho para o arquivo do banco de dados onde a tabela será criada.
def criar_tabela(db_file):
    conn = conectar(db_file) # Estabelece uma conexão com o DB.
    cur = conn.cursor() # Cria um cursor para executar comandos SQL.
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            parcelas INTEGER NOT NULL,
            ultima_atualizacao TEXT NOT NULL
        )
    ''') # Define a estrutura da tabela 'Gastos' com colunas para valor, data, descrição, parcelas e data da última atualização.
    conn.commit() # Salva as alterações (criação da tabela) no banco de dados.
    conn.close() # Fecha a conexão, liberando o recurso do banco de dados.