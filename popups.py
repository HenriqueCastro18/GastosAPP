from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.metrics import dp # Importa dp para garantir consistência de tamanho em diferentes densidades de tela.

# --- Função para Exibir Popups de Mensagem Genéricos ---
# Esta função é um utilitário central para fornecer feedback rápido ao usuário.
# Ela permite exibir mensagens de sucesso ou erro de forma padronizada e visualmente distinta.
def show_message_popup(title, message, is_error=False):
    # Cria o layout do conteúdo do popup, organizando os widgets verticalmente com espaçamento e preenchimento.
    content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

    # Adiciona o widget de texto (Label) para exibir a mensagem.
    # A cor do texto muda para vermelho se for uma mensagem de erro, garantindo feedback visual imediato.
    # text_size é crucial para quebrar o texto longo em múltiplas linhas, evitando que ele transborde.
    content.add_widget(Label(text=message, halign='center', valign='middle',
                             color=(1,1,1,1) if not is_error else (1,0,0,1),
                             text_size=(dp(300), None))) # Garante que o texto se quebre em 300dp de largura

    # Cria o botão "OK" para fechar o popup.
    # Defino um tamanho fixo para o botão e centralizo-o horizontalmente.
    close_button = Button(text='OK', size_hint=(None, None), size=(dp(100), dp(40)), pos_hint={'center_x': 0.5})
    close_button.background_normal = '' # Remove o fundo padrão do Kivy para permitir estilização com background_color.

    # Define a cor de fundo do botão: azul para mensagens normais/sucesso, vermelho para erros.
    # Isso reforça o feedback visual sobre o tipo de mensagem.
    close_button.background_color = (0.2, 0.6, 0.86, 1) if not is_error else (0.8, 0.2, 0.2, 1)
    content.add_widget(close_button)

    # Cria a instância do Popup.
    # Defino um tamanho fixo para o popup, que foi ajustado para acomodar bem o texto e o botão.
    popup = Popup(title=title, content=content, size_hint=(None, None), size=(dp(380), dp(280)))

    # Associa o evento de clique do botão "OK" à ação de fechar o popup.
    close_button.bind(on_release=popup.dismiss)
    
    # Abre o popup, tornando-o visível na tela.
    popup.open()