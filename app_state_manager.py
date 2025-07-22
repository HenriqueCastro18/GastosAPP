from kivy.app import App
from kivy.properties import StringProperty


# --- Gerenciamento de Estado Global do Aplicativo (AppState) ---
# Esta classe foi projetada para atuar como um contêiner centralizado para o estado global da aplicação.
# Meu objetivo principal aqui é gerenciar o caminho do arquivo de banco de dados ativo,
# tornando-o facilmente acessível de qualquer parte do aplicativo Kivy.
class AppState(App): # Herda de App para integrar-se ao ciclo de vida do aplicativo Kivy, embora não seja a classe principal do App.
    # active_db_file é uma Kivy StringProperty, o que significa que mudanças nela
    # podem ser observadas (bindadas) por outros widgets, se necessário.
    # Defino "GastosTotais.db" como o arquivo de banco de dados padrão.
    active_db_file = StringProperty("GastosTotais.db")
    # Futuramente, outras propriedades globais poderiam ser adicionadas aqui,
    # como configurações do usuário, estado de login, etc.

# Instância global para acessar o estado do DB em qualquer lugar do código.
# Ao criar uma instância de AppState aqui, permito que outros módulos importem 'app_state'
# e acessem 'app_state.active_db_file' de forma conveniente.
# Isso evita a necessidade de passar o caminho do DB entre as telas e funções.
app_state = AppState()