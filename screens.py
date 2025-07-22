import datetime
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ListProperty
from kivy.app import App
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
import os

# Importações de módulos locais que contêm a lógica de negócios e utilitários.
from contas import criar_nova_conta, listar_contas # Funções para gerenciar contas de banco de dados
from database import criar_tabela # Função para criar tabelas no banco de dados
from app_state_manager import app_state # Gerenciador de estado global para o DB ativo
from popups import show_message_popup # Função para exibir popups de mensagem
from models import (
    listar_gastos,
    adicionar_gasto,
    atualizar_parcelas,
    remover_gasto,
    buscar_gasto_por_id,
    editar_gasto
) # Funções para manipular os dados de gastos
from kivy_widgets import Botao # Botão customizado para melhor estética


# --- Gerenciador de Telas ---
# Esta classe é o coração da navegação do aplicativo, permitindo a transição entre as diferentes telas (views).
class Gerenciador(ScreenManager):
    pass

# --- ClickableLabel ---
# Uma classe auxiliar que combina um Label com o comportamento de um Button.
class ClickableLabel(ButtonBehavior, Label):
    pass

# --- ConfirmationMixin ---
# Um mixin (classe que adiciona funcionalidades a outras classes por herança múltipla)
# para telas que precisam de uma funcionalidade de confirmação de saída padronizada.
class ConfirmationMixin:
    def confirmacao(self, *args):
        # Layout principal do popup de confirmação.
        box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Container para centralizar os botões "Sim" e "Não".
        botoes_container = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=(0, 0, 0, 0),
            pos_hint={"center_x": 0.5} # Centraliza horizontalmente.
        )

        # O popup em si.
        pop = Popup(
            title='Deseja Mesmo sair?',
            content=box,
            size_hint=(None, None),
            size=(dp(235), dp(180)) # Tamanho fixo para consistência.
        )

        # Botão "Sim" que, ao ser liberado, para a aplicação.
        sim = Botao(
            text='Sim',
            on_release=App.get_running_app().stop, # Chama o método stop() da aplicação para sair.
            size_hint=(None, None),
            width=dp(90),
            height=dp(40),
            cor=(0.1, 0.7, 0.1, 1), # Cor verde para "Sim".
            cor2=(0.05, 0.35, 0.05, 1)
        )
        # Botão "Não" que, ao ser liberado, fecha o popup.
        nao = Botao(
            text='Não',
            on_release=pop.dismiss, # Fecha o popup.
            size_hint=(None, None),
            width=dp(90),
            height=dp(40),
            cor=(0.8, 0.2, 0.2, 1), # Cor vermelha para "Não".
            cor2=(0.4, 0.1, 0.1, 1)
        )

        botoes_container.add_widget(sim)
        botoes_container.add_widget(nao)

        saida = Label()  # Um Label vazio que pode ser usado para uma imagem ou texto adicional.

        box.add_widget(saida)
        box.add_widget(botoes_container)

        pop.open() # Abre o popup.

# --- Tela Principal do Menu ---
# Esta é a tela de "boas-vindas" ou painel principal do aplicativo,
# onde o usuário pode navegar para outras funcionalidades.
class Menu(Screen, ConfirmationMixin):
    # StringProperty para exibir o nome da conta ativa na tela.
    conta_nome = StringProperty("Conta: Nenhuma")

    # Chama a função para criar uma nova conta.
    def criar_conta(self):
        criar_conta()

    # Chama a função para trocar a conta ativa.
    def trocar_conta(self):
        trocar_conta()

    # Evento chamado antes da tela ser exibida.
    def on_pre_enter(self):
        # Atualiza o nome da conta exibido para o usuário.
        nome = app_state.active_db_file.replace(".db", "") # Remove a extensão .db para exibir um nome amigável.
        self.conta_nome = f"Conta: {nome}"

# --- GastoTableRow ---
# Este widget representa uma única linha na tabela de gastos,
# combinando um BoxLayout com comportamento de botão para torná-lo clicável.
class GastoTableRow(ButtonBehavior, BoxLayout):
    gasto_id = NumericProperty(0) # ID do gasto associado a esta linha.
    id_text = StringProperty()
    valor = StringProperty()
    data = StringProperty()
    descricao = StringProperty()
    parcelas = StringProperty()
    background_color = ListProperty([0.2, 0.2, 0.2, 0.8]) # Cor de fundo padrão.

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40) # Altura fixa da linha.

    # Altera a cor de fundo ao pressionar (feedback visual).
    def on_press(self):
        self.background_color = (1, 1, 1, 1)

    # Altera a cor de fundo ao soltar e notifica a tela 'gastos' sobre a seleção.
    def on_release(self):
        self.background_color = (0.2, 0.2, 0.2, 0.8)
        # Acessa a tela 'gastos' através do gerenciador de telas e chama o método select_gasto.
        App.get_running_app().root.get_screen('gastos').select_gasto(self.gasto_id)

# Registra a classe GastoTableRow com o Kivy Factory,
# permitindo que ela seja usada diretamente em arquivos KV.
Factory.register(classname='GastoTableRow', cls=GastoTableRow)

# --- Tela de Listagem de Gastos ---
# Exibe uma lista de todos os gastos registrados, com funcionalidades de seleção, remoção e edição.
class Gastos(Screen, ConfirmationMixin):
    selected_gasto_id = NumericProperty(0) # Armazena o ID do gasto selecionado.
    selected_row = None  # Referência à linha (GastoTableRow) atualmente selecionada.

    def __init__(self, gastos=[], **kwargs):
        super().__init__(**kwargs)

    # Limita o tamanho da descrição para 32 caracteres em um TextInput.
    def limitar_descricao(self, instance, value):
        if len(value) > 32:
            instance.text = value[:32]

    # Evento chamado antes da tela ser exibida.
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar) # Associa a tecla "voltar" (Esc no desktop) para navegação.
        self.load_gastos() # Carrega e exibe a lista de gastos.
        self.selected_gasto_id = 0 # Reseta a seleção.
        self.selected_row = None

    # Carrega os gastos do banco de dados e os exibe na tabela.
    def load_gastos(self):
        self.ids.table_content.clear_widgets() # Limpa o conteúdo anterior da tabela.
        gastos = listar_gastos() # Obtém os gastos do modelo de dados.
        total_gastos = 0.0

        # Função auxiliar para criar Labels formatados para a tabela.
        def criar_label(texto, alinhamento='left', cor=(1,1,1,1), proporcao=0.25, padding=(dp(8), 0, dp(8), 0)):
            # Importação local para evitar importações globais desnecessárias se não for comum criar labels fora daqui.
            from kivy.uix.boxlayout import BoxLayout
            label = Label(
                text=texto,
                color=cor,
                halign=alinhamento,
                valign='middle',
                font_size=dp(12)
            )
            # Garante que o texto se adapte ao tamanho do label.
            label.bind(size=lambda inst, val: setattr(inst, 'text_size', inst.size))
            wrapper = BoxLayout(padding=padding, size_hint_x=proporcao)
            wrapper.add_widget(label)
            return wrapper

        # Itera sobre cada gasto para criar uma linha na tabela.
        for gasto in gastos:
            id_gasto, valor, data, descricao, parcelas = gasto
            # Formata o valor para exibição em moeda brasileira.
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            row = GastoTableRow(gasto_id=id_gasto) # Cria uma nova linha da tabela.

            # Adiciona os Labels formatados à linha.
            row.add_widget(criar_label(valor_formatado, alinhamento='right', cor=(1, 1, 1, 1), proporcao=0.37))
            row.add_widget(criar_label(datetime.datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y"), alinhamento='center', proporcao=0.4))
            row.add_widget(criar_label(descricao, alinhamento='left', proporcao=0.6))
            row.add_widget(criar_label(str(parcelas), alinhamento='left', proporcao=0.2))

            self.ids.table_content.add_widget(row) # Adiciona a linha ao layout da tabela.
            total_gastos += valor # Soma o valor para o total.

        # Atualiza o Label que exibe o total de gastos.
        self.ids.total_gastos_label.text = f"TOTAL: R$ {total_gastos:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # Lida com a seleção de um gasto na tabela.
    def select_gasto(self, gasto_id):
        self.selected_gasto_id = gasto_id

        # Limpa a seleção anterior, restaurando a cor de fundo.
        if self.selected_row:
            self.selected_row.background_color = (0.2, 0.2, 0.2, 0.8)

        # Encontra a nova linha selecionada e muda sua cor de fundo.
        for child in self.ids.table_content.children:
            if isinstance(child, GastoTableRow) and child.gasto_id == gasto_id:
                child.background_color = (0.3, 0.5, 0.3, 1)  # Cor de seleção (verde claro).
                self.selected_row = child
                break

    # Lida com o evento de pressionar a tecla "voltar" (Esc).
    def voltar(self, window, key, *args):
        if key == 27: # 27 é o código da tecla Esc.
            App.get_running_app().root.current = 'menu' # Navega para a tela 'menu'.
            return True # Indica que o evento foi tratado.

    # Evento chamado antes da tela ser deixada.
    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar) # Remove o bind da tecla "voltar".
        # Desseleciona a linha se houver uma selecionada.
        if self.selected_row:
            self.selected_row.background_color = (0.4, 0.2, 0.2, 0.8) # Restaura a cor de fundo (ou outra cor padrão).
            self.selected_row = None

    # Lógica para remover um gasto.
    def remover_gasto_action(self):
        if self.selected_gasto_id == 0:
            show_message_popup("Erro", "Selecione um gasto para remover.", is_error=True)
            return

        # Busca os detalhes do gasto para exibir no popup de confirmação.
        gasto_para_remover = buscar_gasto_por_id(self.selected_gasto_id)
        if not gasto_para_remover:
            show_message_popup("Erro", "Gasto não encontrado.", is_error=True)
            return

        # Desestrutura o gasto para obter a descrição.
        id_gasto, valor, data, descricao, parcelas, ultima_atualizacao = gasto_para_remover

        # Layout e widgets do popup de confirmação de remoção.
        content = BoxLayout(orientation='vertical', padding=dp(18), spacing=dp(10))
        content.add_widget(Label(text=f"Remover o gasto:\n {descricao} ?",
                                 halign='center', valign='middle', text_size=(dp(280), None)))

        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        btn_sim = Botao(text='Sim', size_hint=(None, None), width=dp(90), height=dp(40),
                        cor=(0.1, 0.7, 0.1, 1), cor2=(0.05, 0.35, 0.05, 1))
        btn_nao = Botao(text='Não', size_hint=(None, None), width=dp(90), height=dp(40),
                        cor=(0.8, 0.2, 0.2, 1), cor2=(0.4, 0.1, 0.1, 1))

        button_layout.add_widget(btn_sim)
        button_layout.add_widget(btn_nao)
        content.add_widget(button_layout)

        popup = Popup(title='Confirmar Remoção', content=content, size_hint=(None, None), size=(dp(250), dp(200)))

        # Função chamada ao confirmar a remoção.
        def on_confirm(instance):
            remover_gasto(self.selected_gasto_id)
            show_message_popup("Sucesso", "Gasto removido com sucesso!")
            self.load_gastos() # Recarrega a lista de gastos.
            self.selected_gasto_id = 0 # Reseta a seleção.
            popup.dismiss()

        btn_sim.bind(on_release=on_confirm) # Liga o botão "Sim" à função de confirmação.
        btn_nao.bind(on_release=popup.dismiss) # Liga o botão "Não" para fechar o popup.
        popup.open() # Abre o popup.

    # Lógica para editar um gasto.
    def editar_gasto_action(self):
        if self.selected_gasto_id == 0:
            show_message_popup("Erro", "Selecione um gasto para editar.", is_error=True)
            return

        gasto_para_editar = buscar_gasto_por_id(self.selected_gasto_id)
        if not gasto_para_editar:
            show_message_popup("Erro", "Gasto não encontrado para edição.", is_error=True)
            return

        # Desestrutura o gasto a ser editado.
        id_gasto, valor, data_str, descricao, parcelas, ultima_atualizacao = gasto_para_editar

        # Layout principal do popup de edição.
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(20), dp(20), dp(150)], # Padding ajustado para o layout.
            spacing=dp(10),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height')) # Ajusta a altura do layout ao seu conteúdo.

        # Função auxiliar para criar Labels para os campos de entrada.
        def criar_label(texto):
            return Label(
                text=texto,
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(25),
                halign='left',
                valign='middle',
                text_size=(dp(300), None)
            )

        # Campos de entrada de texto (TextInput) pré-preenchidos com os dados do gasto.
        valor_input = TextInput(
            text=str(valor), input_type='number', multiline=False,
            size_hint_y=None, height=dp(40),
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=(0, 1, 0, 1),
            font_size=dp(20)
        )

        data_formatada = datetime.datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        data_input = TextInput(
            text=data_formatada, multiline=False,
            size_hint_y=None, height=dp(40),
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=(0, 1, 0, 1),
            font_size=dp(20)
        )

        descricao_input = TextInput(
            text=descricao, multiline=False, size_hint_y=None, height=dp(40),
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=(0, 1, 0, 1),
            font_size=dp(20)
        )
        descricao_input.bind(text=self.limitar_descricao) # Liga a função de limitação de caracteres.

        qtd_parcelas_input = TextInput(
            text=str(parcelas), input_type='number', multiline=False,
            size_hint_y=None, height=dp(40),
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1), cursor_color=(0, 1, 0, 1),
            font_size=dp(20)
        )

        # Função auxiliar para criar linhas de input com rótulos.
        def criar_linha_input(rotulo, widget_input):
            linha = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
            linha.add_widget(Label(
                text=rotulo,
                color=(1, 1, 1, 1),
                size_hint_y=None,
                height=dp(15),
                padding=[dp(40), 0, 0, 0],
                halign='left',
                valign='middle',
                text_size=(dp(350), None)
            ))
            linha.add_widget(widget_input)
            linha.height = widget_input.height + dp(25) # Ajusta a altura da linha.
            return linha

        # Adiciona os campos de entrada ao layout do popup.
        content.add_widget(criar_linha_input("VALOR DO GASTO", valor_input))
        content.add_widget(criar_linha_input("DATA", data_input))
        content.add_widget(criar_linha_input("DESCRIÇÃO", descricao_input))
        content.add_widget(criar_linha_input("PARCELAS", qtd_parcelas_input))

        # Layout para os botões "Salvar" e "Cancelar".
        button_layout = BoxLayout(
            orientation='horizontal', size_hint_y=None, height=dp(60),
            padding=[0, 0, dp(10), dp(-120)],
            spacing=dp(20), pos_hint={"center_x": 0.48}
        )

        btn_salvar = Botao(text='Salvar', cor=(0.1, 0.7, 0.1, 1), cor2=(0.05, 0.35, 0.05, 1))
        btn_cancelar = Botao(text='Cancelar', cor=(0.8, 0.2, 0.2, 1), cor2=(0.4, 0.1, 0.1, 1))

        button_layout.add_widget(btn_salvar)
        button_layout.add_widget(btn_cancelar)
        content.add_widget(button_layout)

        popup = Popup(title='Editar Gasto', content=content, size_hint=(None, None), size=(dp(350), dp(600)))

        # Função chamada ao salvar as edições.
        def on_salvar_edicao(instance):
            try:
                novo_valor = float(valor_input.text)
                nova_data_str = data_input.text.strip()
                nova_descricao = descricao_input.text.strip().capitalize()

                try:
                    # Validação do formato da data.
                    nova_data = datetime.datetime.strptime(nova_data_str, "%d/%m/%Y").date().isoformat()
                except ValueError:
                    show_message_popup("Erro de Data", "Formato de data inválido. Use DD/MM/AAAA.", is_error=True)
                    return

                try:
                    novas_parcelas = int(qtd_parcelas_input.text)
                    if novas_parcelas <= 0:
                        show_message_popup("Erro", "Quantidade de parcelas deve ser maior que zero.", is_error=True)
                        return
                except ValueError:
                    show_message_popup("Erro", "Quantidade de parcelas inválida.", is_error=True)
                    return

                # Chama a função de edição no modelo de dados.
                editar_gasto(id_gasto, novo_valor, nova_data, nova_descricao, novas_parcelas)
                show_message_popup("Sucesso", "Gasto atualizado com sucesso!")
                self.load_gastos() # Recarrega a lista.
                self.selected_gasto_id = 0 # Reseta a seleção.
                popup.dismiss()

            except ValueError:
                show_message_popup("Erro", "Verifique os dados inseridos (Valor deve ser um número).", is_error=True)
            except Exception as e:
                show_message_popup("Erro", f"Ocorreu um erro: {e}", is_error=True)

        btn_salvar.bind(on_release=on_salvar_edicao) # Liga o botão "Salvar" à função de salvar.
        btn_cancelar.bind(on_release=popup.dismiss) # Liga o botão "Cancelar" para fechar o popup.
        popup.open() # Abre o popup de edição.

# --- Gasto (Widget de Gasto Individual) ---
# Este widget parece ser um remanescente ou uma classe auxiliar que não é mais usada diretamente
# na forma como a lista de gastos é construída atualmente (GastoTableRow).
# Pode ser removida se não houver um uso direto em main.kv ou outros lugares.
class Gasto(BoxLayout):
    def __init__(self, text='', **kwards):
        super().__init__(**kwards)
        self.ids.label.text = text

# --- Tela de Adição de Novo Gasto ---
# Esta tela fornece um formulário para o usuário adicionar novos registros de despesas.
class AdicionarGastoScreen(Screen):
    # Propriedade booleana que controla a visibilidade do campo de quantidade de parcelas.
    is_parcelado = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Chamado quando a tela é exibida (se torna a tela atual).
    def on_enter(self, *args):
        # Preenche a data com a data atual por padrão e limpa outros campos.
        self.ids.data_input.text = datetime.date.today().strftime("%d/%m/%Y")
        self.ids.valor_input.text = ''
        self.ids.descricao_input.text = ''
        self.ids.qtd_parcelas_spinner.text = '1'

        self.ids.descricao_input.bind(text=self.limitar_descricao) # Liga a função de limitação de caracteres.

    # Alterna a visibilidade do campo de quantidade de parcelas com base no checkbox.
    def toggle_parcelas_input(self, checkbox_instance, value):
        self.is_parcelado = value # Atualiza a propriedade.

    # Valida o formato da data inserida.
    def validar_data(self):
        data_str = self.ids.data_input.text.strip()
        if not data_str:
            show_message_popup("Erro de Data", "A data não pode estar vazia.", is_error=True)
            return False
        try:
            datetime.datetime.strptime(data_str, "%d/%m/%Y")
            return True
        except ValueError:
            show_message_popup("Erro de Data", "Formato de data inválido. Use DD/MM/AAAA.", is_error=True)
            return False

    # Limita o tamanho da descrição.
    def limitar_descricao(self, instance, value):
        if len(value) > 32:
            instance.text = value[:32]

    # Salva os dados do formulário no banco de dados.
    def salvar_gasto(self):
        try:
            valor_total = float(self.ids.valor_input.text)
            data_str = self.ids.data_input.text
            descricao = self.ids.descricao_input.text.strip()[:32].capitalize()

            # Validação e conversão da data.
            try:
                data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date().isoformat()
            except ValueError:
                show_message_popup("Erro de Data", "Formato de data inválido. Use DD/MM/AAAA.", is_error=True)
                return

            parcelas = 1
            if self.is_parcelado: # Se o gasto é parcelado.
                try:
                    # Altere esta linha para pegar o valor do Spinner
                    parcelas = int(self.ids.qtd_parcelas_spinner.text)
                    if parcelas <= 0:
                        show_message_popup("Erro", "Quantidade de parcelas deve ser maior que zero.", is_error=True)
                        return
                except ValueError:
                    show_message_popup("Erro", "Quantidade de parcelas inválida.", is_error=True)
                    return

            valor_parcela = round(valor_total / parcelas, 2) # Calcula o valor de cada parcela.

            adicionar_gasto(valor_parcela, data, descricao, parcelas) # Adiciona o gasto ao DB.
            show_message_popup("Sucesso", "Gasto adicionado!")
            self.manager.current = 'menu' # Volta para o menu principal.

        except ValueError:
            show_message_popup("Erro", "Verifique os dados inseridos (Valor deve ser um número).", is_error=True)
        except Exception as e:
            show_message_popup("Erro", f"Ocorreu um erro: {e}", is_error=True)

    # Cancela a adição do gasto e volta para a tela de menu.
    def cancelar_gasto(self):
        self.manager.current = 'menu'

# --- Função para Criar Nova Conta ---
# Exibe um popup para o usuário inserir o nome de uma nova conta financeira.
def criar_conta():
    layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

    label = Label(
        text="Nova conta:",
        size_hint_y=None,
        height=dp(30),
        color=(1, 1, 1, 1)
    )

    input_nome = TextInput(
        hint_text="Ex: CartãoNubank...",
        multiline=False,
        size_hint_y=None,
        height=dp(50),
        font_size=dp(18),
        background_color=(0.15, 0.15, 0.15, 1),
        foreground_color=(1, 1, 1, 1),
        cursor_color=(0, 1, 0, 1),
        padding=(dp(10), dp(10))
    )

    botoes = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(20))
    btn_criar = Button(
        text="Criar",
        background_normal='',
        background_color=(0.2, 0.6, 0.2, 1),
        font_size=dp(16)
    )
    btn_cancelar = Button(
        text="Cancelar",
        background_normal='',
        background_color=(0.7, 0.2, 0.2, 1),
        font_size=dp(16)
    )

    popup = Popup(
        title="Criar Nova Conta",
        content=layout,
        size_hint=(None, None),
        size=(dp(300), dp(300)),
        auto_dismiss=False # Não fecha o popup ao clicar fora.
    )

    # Função chamada ao criar a conta.
    def criar():
        nome = input_nome.text.strip()
        if not nome:
            show_message_popup("Erro", "O nome da conta não pode estar vazio.", is_error=True)
            return

        sucesso, mensagem = criar_nova_conta(nome) # Tenta criar a nova conta.
        if sucesso:
            db_nome = nome if nome.endswith(".db") else nome + ".db"
            caminho = os.path.join("contas", db_nome)
            criar_tabela(caminho) # Cria a tabela 'Gastos' na nova conta.
            popup.dismiss()
            show_message_popup("Conta Criada", mensagem)
        else:
            show_message_popup("Erro", mensagem, is_error=True)

    btn_criar.bind(on_release=lambda x: criar()) # Liga o botão "Criar" à função de criação.
    btn_cancelar.bind(on_release=popup.dismiss) # Liga o botão "Cancelar" para fechar o popup.

    botoes.add_widget(btn_criar)
    botoes.add_widget(btn_cancelar)

    layout.add_widget(label)
    layout.add_widget(input_nome)
    layout.add_widget(botoes)

    popup.open() # Abre o popup de criação de conta.

# --- Função para Trocar Conta Ativa ---
# Exibe um popup com uma lista de contas disponíveis e permite ao usuário trocar a conta ativa.
def trocar_conta():
    layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))

    label = Label(text="Contas Disponíveis", color=(1,1,1,1), size_hint_y=None, height=dp(30))
    layout.add_widget(label)

    contas_scroll = ScrollView(size_hint=(1, 1)) # Permite rolar a lista de contas.
    contas_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10), padding=dp(5))
    contas_layout.bind(minimum_height=contas_layout.setter('height')) # Ajusta a altura do layout ao conteúdo.

    contas = listar_contas(incluir_totais=True) # Lista todas as contas, incluindo "GastosTotais.db".
    conta_ativa = app_state.active_db_file # Obtém a conta atualmente ativa.

    for conta in contas:
        linha = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))

        # Define a cor do botão da conta: diferente para a conta ativa.
        cor = (0.3, 0.7, 1, 1) if conta == conta_ativa else (0.2, 0.2, 0.2, 1)

        btn_trocar = Button(
            text=conta.replace(".db", ""), # Exibe o nome da conta sem a extensão.
            size_hint_y=None,
            height=dp(48),
            font_size=dp(16),
            padding=(dp(10), dp(10)),
            background_normal='',
            background_color=cor,
            color=(1, 1, 1, 1),
            bold=True if conta == conta_ativa else False # Texto em negrito para a conta ativa.
        )

        # Função chamada ao trocar a conta.
        def trocar_conta(nome=conta):
            if nome == conta_ativa:
                show_message_popup("Aviso", "Essa conta já está ativa.")
                return
            app_state.active_db_file = nome # Define a nova conta ativa.
            from models import atualizar_gastos_totais
            atualizar_gastos_totais() # Atualiza o DB totalizador após a troca.

            # Atualiza o texto da conta ativa na tela de menu diretamente.
            menu_screen = App.get_running_app().root.get_screen('menu')
            menu_screen.conta_nome = f"Conta: {nome.replace('.db', '')}"

            show_message_popup("Conta Trocada", f"Conta ativa agora: {nome}")
            popup.dismiss()

        btn_trocar.bind(on_release=lambda x, nome=conta: trocar_conta(nome))

        btn_excluir = Button(
            text="Excluir",
            size_hint_x=None,
            width=dp(80),
            background_normal='',
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )

        # Função para confirmar a exclusão de uma conta.
        def confirmar_exclusao(nome=conta):
            if nome == conta_ativa:
                show_message_popup("Erro", "Você não pode excluir a conta ativa.", is_error=True)
                return

            caminho = os.path.join("contas", nome)
            if os.path.exists(caminho):
                os.remove(caminho) # Remove o arquivo da conta.
                show_message_popup("Conta Excluída", f"{nome} foi removida.")
            else:
                show_message_popup("Erro", f"Conta {nome} não encontrada.", is_error=True)

            popup.dismiss()
            trocar_conta()  # Reabre o popup para mostrar a lista atualizada.

        btn_excluir.bind(on_release=lambda x, nome=conta: confirmar_exclusao(nome))

        linha.add_widget(btn_trocar)
        # O botão de exclusão só é adicionado se a conta não for a conta ativa.
        if conta != conta_ativa:
            linha.add_widget(btn_excluir)

        contas_layout.add_widget(linha)

    contas_scroll.add_widget(contas_layout)
    layout.add_widget(contas_scroll)

    btn_fechar = Button(
        text="Fechar",
        size_hint=(1, None),
        height=dp(50),
        background_normal='',
        background_color=(0.3, 0.3, 0.3, 1),
        color=(1, 1, 1, 1)
    )
    btn_fechar.bind(on_release=lambda x: popup.dismiss()) # Liga o botão "Fechar" para fechar o popup.

    layout.add_widget(btn_fechar)

    # Declara 'popup' como global para que possa ser acessado e descartado de outras funções.
    global popup
    popup = Popup(
        title="Trocar Conta",
        content=layout,
        size_hint=(None, None),
        size=(dp(300), dp(400)),
        auto_dismiss=False
    )
    popup.open() # Abre o popup de troca de conta.