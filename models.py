import datetime
from database import conectar # Importa a função de conexão com o banco de dados
from popups import show_message_popup # Importa a função para exibir popups de mensagem
from app_state_manager import app_state # Importa o objeto de estado global para acessar o DB ativo
import os

# --- Funções de Operações com Gastos ---
# Este módulo contém a lógica de negócios para adicionar, atualizar, listar,
# buscar, remover e editar registros de gastos no banco de dados.
# Ele atua como uma camada intermediária entre a UI e o banco de dados.

# Adiciona um novo registro de gasto ao banco de dados ativo.
def adicionar_gasto(valor, data, descricao, parcelas, db_file=None):
    # Usa o arquivo de DB ativo do app_state se nenhum db_file for fornecido.
    if db_file is None:
        db_file = app_state.active_db_file
    # Conecta-se ao banco de dados específico.
    conn = conectar(os.path.join("contas", db_file))
    cur = conn.cursor()
    # Insere um novo registro na tabela 'Gastos'.
    cur.execute(
        "INSERT INTO Gastos (valor, data, descricao, parcelas, ultima_atualizacao) VALUES (?, ?, ?, ?, ?)",
        (valor, data, descricao, parcelas, data)
    )
    conn.commit() # Confirma a transação.
    conn.close() # Fecha a conexão.

# Atualiza o número de parcelas de gastos existentes e remove os finalizados.
# Esta função simula o progresso de pagamentos mensais.
def atualizar_parcelas(db_file=None):
    # Usa o arquivo de DB ativo do app_state se nenhum db_file for fornecido.
    if db_file is None:
        db_file = app_state.active_db_file
    # Conecta-se ao banco de dados.
    conn = conectar(os.path.join("contas", db_file))
    cur = conn.cursor()
    # Seleciona todos os gastos para verificação de parcelas.
    cur.execute("SELECT id, descricao, parcelas, ultima_atualizacao FROM Gastos")
    gastos = cur.fetchall()
    excluidos = [] # Lista para armazenar gastos excluídos para notificação.

    for id_gasto, descricao, parcelas, ultima in gastos:
        ultima_dt = datetime.datetime.fromisoformat(ultima)
        hoje = datetime.datetime.now()
        dias_passados = (hoje - ultima_dt).days

        if dias_passados >= 30: # Verifica se passou um mês ou mais desde a última atualização.
            novas_parcelas = parcelas - (dias_passados // 30)
            if novas_parcelas <= 0: # Se as parcelas acabaram, exclui o gasto.
                cur.execute("DELETE FROM Gastos WHERE id = ?", (id_gasto,))
                excluidos.append(f"ID {id_gasto} - {descricao}")
            else: # Caso contrário, atualiza as parcelas e a data da última atualização.
                nova_data = ultima_dt + datetime.timedelta(days=30 * (dias_passados // 30))
                cur.execute(
                    "UPDATE Gastos SET parcelas = ?, ultima_atualizacao = ? WHERE id = ?",
                    (novas_parcelas, nova_data.isoformat(), id_gasto)
                )

    conn.commit() # Confirma as alterações (deleções/atualizações).
    conn.close() # Fecha a conexão.

    if excluidos: # Se houve gastos excluídos, exibe um popup de notificação.
        show_message_popup("Gastos Excluídos", "Os seguintes gastos foram excluídos automaticamente:\n" + "\n".join(excluidos))

# Lista todos os gastos registrados no banco de dados ativo.
def listar_gastos(db_file=None):
    # Usa o arquivo de DB ativo do app_state se nenhum db_file for fornecido.
    if db_file is None:
        db_file = app_state.active_db_file
    # Conecta-se ao banco de dados.
    conn = conectar(os.path.join("contas", db_file))
    cur = conn.cursor()
    # Seleciona todos os dados da tabela 'Gastos'.
    cur.execute("SELECT id, valor, data, descricao, parcelas FROM Gastos")
    dados = cur.fetchall() # Obtém todos os resultados.
    conn.close() # Fecha a conexão.
    return dados # Retorna a lista de gastos.

# Busca um gasto específico pelo seu ID no banco de dados ativo.
def buscar_gasto_por_id(id_gasto, db_file=None):
    # Usa o arquivo de DB ativo do app_state se nenhum db_file for fornecido.
    if db_file is None:
        db_file = app_state.active_db_file
    # Conecta-se ao banco de dados.
    conn = conectar(os.path.join("contas", db_file))
    cur = conn.cursor()
    # Executa a busca pelo ID.
    cur.execute("SELECT id, valor, data, descricao, parcelas, ultima_atualizacao FROM Gastos WHERE id = ?", (id_gasto,))
    gasto = cur.fetchone() # Retorna apenas um resultado, pois ID é único.
    conn.close() # Fecha a conexão.
    return gasto # Retorna o gasto encontrado ou None.

# Remove um gasto específico pelo seu ID do banco de dados ativo.
def remover_gasto(id_gasto, db_file=None):
    # Usa o arquivo de DB ativo do app_state se nenhum db_file for fornecido.
    if db_file is None:
        db_file = app_state.active_db_file
    # Conecta-se ao banco de dados.
    conn = conectar(os.path.join("contas", db_file))
    cur = conn.cursor()
    # Executa a exclusão pelo ID.
    cur.execute("DELETE FROM Gastos WHERE id = ?", (id_gasto,))
    conn.commit() # Confirma a transação.
    conn.close() # Fecha a conexão.

# Atualiza os dados de um gasto existente no banco de dados ativo.
def editar_gasto(id_gasto, valor, data, descricao, parcelas, db_file=None):
    # Usa o arquivo de DB ativo do app_state se nenhum db_file for fornecido.
    if db_file is None:
        db_file = app_state.active_db_file
    # Conecta-se ao banco de dados.
    conn = conectar(os.path.join("contas", db_file))
    cur = conn.cursor()
    # Atualiza os campos do gasto com base no ID.
    cur.execute("""
        UPDATE Gastos SET valor = ?, data = ?, descricao = ?, parcelas = ?, ultima_atualizacao = ?
        WHERE id = ?
    """, (valor, data, descricao, parcelas, datetime.datetime.now().isoformat(), id_gasto))
    conn.commit() # Confirma a transação.
    conn.close() # Fecha a conexão.

# Agrega todos os gastos de contas individuais em um único banco de dados "GastosTotais.db".
# Isso é útil para uma visão consolidada de todas as despesas.
def atualizar_gastos_totais():
    # Importações locais para evitar dependências circulares, se 'database' e 'os' fossem importados em outras partes de forma complexa.
    from database import criar_tabela, conectar
    import os

    destino = os.path.join("contas", "GastosTotais.db")
    criar_tabela(destino) # Garante que a tabela no DB totalizador exista.
    conn_destino = conectar(destino)
    cur_destino = conn_destino.cursor()
    cur_destino.execute("DELETE FROM Gastos")  # Limpa todos os registros existentes antes de re-popular.
    conn_destino.commit()

    # Lista todos os arquivos .db no diretório 'contas', excluindo o próprio "GastosTotais.db".
    arquivos = [f for f in os.listdir("contas") if f.endswith(".db") and f != destino]

    for arquivo in arquivos:
        conn = conectar(os.path.join("contas", arquivo))
        cur = conn.cursor()
        try:
            # Seleciona os gastos de cada conta individual.
            cur.execute("SELECT valor, data, descricao, parcelas, ultima_atualizacao FROM Gastos")
            gastos = cur.fetchall()
            for gasto in gastos:
                # Insere os gastos na tabela totalizadora.
                cur_destino.execute(
                    "INSERT INTO Gastos (valor, data, descricao, parcelas, ultima_atualizacao) VALUES (?, ?, ?, ?, ?)",
                    gasto
                )
        except:
            pass  # Ignora arquivos de banco de dados que possam estar corrompidos ou mal formatados.
        conn.close() # Fecha a conexão com o DB da conta individual.

    conn_destino.commit() # Confirma todas as inserções no DB totalizador.
    conn_destino.close() # Fecha a conexão com o DB totalizador.