# Importações essenciais para o aplicativo Kivy e módulos customizados
import sys
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from models import atualizar_gastos_totais, atualizar_parcelas
from database import criar_tabela
from screens import Gerenciador
from app_state_manager import AppState
from kivy.core.window import Window
from kivy.metrics import dp

# --- Configuração da Janela (Windows) ---
# Define o tamanho fixo da janela e impede o redimensionamento para simular um layout mobile em desktops Windows.
if sys.platform == 'win32':
    Window.size = (dp(380), dp(640))
    Window.resizable = False

# --- Classe Principal do Aplicativo ---
# Herda de App para funcionalidades Kivy e AppState para gerenciamento de estado global.
class main(AppState, App):
    def build(self):
        # Carrega o arquivo KV que define a estrutura da interface do usuário.
        Builder.load_file('main.kv')

        # Agenda a inicialização do banco de dados e atualização de dados após a construção da UI.
        Clock.schedule_once(self.inicializar_app, 0)

        # Agenda a atualização periódica das parcelas a cada 10 segundos.
        Clock.schedule_interval(self.testar_parcelas, 10)

        # Retorna o widget gerenciador de telas como a raiz do aplicativo.
        return Gerenciador()

    # --- Funções de Inicialização e Manutenção ---
    def inicializar_app(self, dt):
        # Obtém o caminho do arquivo do banco de dados ativo.
        db_file = self.active_db_file
        # Cria a tabela no banco de dados, se não existir.
        criar_tabela(db_file)
        # Atualiza o status das parcelas.
        atualizar_parcelas(db_file)
        # Recalcula e atualiza os gastos totais.
        atualizar_gastos_totais()

    def testar_parcelas(self, dt):
        # Chama a função para garantir que as parcelas estejam sempre atualizadas.
        atualizar_parcelas(self.active_db_file)

# --- Execução Principal ---
# Inicia o aplicativo Kivy.
if __name__ == '__main__':
    main().run()