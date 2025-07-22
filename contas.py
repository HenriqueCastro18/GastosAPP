import os

# --- Gerenciamento de Arquivos de Contas ---
# Este módulo é responsável por gerenciar os arquivos de banco de dados que representam
# as diferentes contas financeiras do usuário.

# Garanto que o diretório 'contas' exista. Se não existir, ele será criado.
# Isso é fundamental para organizar os arquivos de banco de dados de forma estruturada.
os.makedirs("contas", exist_ok=True)

# Lista todos os arquivos de banco de dados (.db) presentes no diretório 'contas'.
# Permite filtrar o arquivo 'GastosTotais.db', que pode ser um banco de dados de agregação.
def listar_contas(incluir_totais=False):
    # Lista todos os itens (arquivos e diretórios) dentro do diretório 'contas'.
    arquivos = os.listdir("contas")
    
    # Se 'incluir_totais' for False, remove 'GastosTotais.db' da lista.
    if not incluir_totais:
        arquivos = [f for f in arquivos if f != "GastosTotais.db"]
    
    # Retorna apenas os arquivos que terminam com '.db', garantindo que apenas bancos de dados sejam listados.
    return [f for f in arquivos if f.endswith(".db")]

# Cria um novo arquivo de banco de dados para uma nova conta.
# Garante que o nome do arquivo termine com '.db' e evita sobrescrever contas existentes.
def criar_nova_conta(nome_arquivo):
    # Adiciona a extensão '.db' se o usuário não a forneceu.
    if not nome_arquivo.endswith(".db"):
        nome_arquivo += ".db"
    
    # Constrói o caminho completo para o novo arquivo no diretório 'contas'.
    caminho = os.path.join("contas", nome_arquivo)
    
    # Verifica se já existe um arquivo com o mesmo nome para evitar duplicatas.
    if os.path.exists(caminho):
        return False, "Já existe uma conta com esse nome."
    
    # Cria um novo arquivo vazio no caminho especificado.
    # O 'with open(...)' garante que o arquivo seja fechado corretamente.
    with open(caminho, 'w'):
        pass
    
    return True, "Conta criada com sucesso!"