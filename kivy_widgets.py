from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.metrics import dp

# --- Botão Customizado (Botao) ---
# Desenvolvi esta classe para criar botões visualmente atraentes e personalizáveis.
# O objetivo é ter um botão com formato arredondado, cores dinâmicas e que reage ao clique.
class Botao(ButtonBehavior, Label):
    # Propriedades Kivy para controlar as cores do botão.
    # 'cor' é a cor primária e 'cor2' é usada para o estado de pressionado.
    cor = ListProperty([0.1, 0.5, 0.7, 1]) # Cor padrão: um tom de azul/ciano
    cor2 = ListProperty([0.1, 0.1, 0.1, 1]) # Cor secundária: cinza escuro

    def __init__(self, **kwargs):
        # Definição de valores padrão para as propriedades de layout do botão.
        # Isso garante um tamanho base consistente para todos os botões, mas ainda permite sobrescrever.
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', dp(60)) # Altura padrão de 60dp
        kwargs.setdefault('size_hint_x', None)
        kwargs.setdefault('width', dp(140)) # Largura padrão de 140dp
        kwargs.setdefault('color', [1, 1, 1, 1]) # Cor do texto padrão: branco

        super(Botao, self).__init__(**kwargs)
        # Agendo a primeira atualização do desenho do botão assim que ele é inicializado.
        # Isso garante que ele apareça corretamente desde o início.
        Clock.schedule_once(self.atualizar, 0)

    # --- Reações a Mudanças de Propriedade e Eventos ---
    # As seguintes funções garantem que o desenho do botão seja atualizado
    # sempre que sua posição, tamanho ou estado de cor mudarem.

    def on_pos(self, *args):
        self.atualizar()

    def on_size(self, *args):
        self.atualizar()

    def on_press(self, *args):
        # Ao pressionar, troco as cores primária e secundária para criar um feedback visual.
        self.cor, self.cor2 = self.cor2, self.cor
        self.atualizar()

    def on_release(self, *args):
        # Ao soltar, as cores voltam ao normal.
        self.cor, self.cor2 = self.cor2, self.cor
        self.atualizar()

    def on_cor(self, *args):
        # Garante que o botão redesenhe se a propriedade 'cor' for alterada diretamente.
        self.atualizar()

    # --- Lógica de Desenho Personalizado ---
    # Este é o cerne do botão, onde as formas gráficas são desenhadas no canvas.
    def atualizar(self, *args):
        # Evito erros de divisão por zero ou desenho inválido se o widget não tiver tamanho.
        if self.canvas and self.canvas.before:
            if self.width <= 0 or self.height <= 0:
                return

            self.canvas.before.clear() # Limpo desenhos anteriores para evitar sobreposição.
            with self.canvas.before:
                Color(rgba=self.cor) # Define a cor de preenchimento para as formas seguintes.

                # NOVO: Desenho um retângulo que preenche toda a área do botão.
                # Esta é uma otimização importante. Antes, apenas as formas arredondadas e o retângulo central eram desenhados.
                # Isso podia deixar pequenos "buracos" nas bordas se o arredondamento não cobrisse 100% da área,
                # permitindo que o fundo do layout subjacente aparecesse.
                # Agora, garanto que toda a área do botão esteja preenchida com a 'cor' definida.
                Rectangle(size=self.size, pos=self.pos)

                # Em seguida, desenho as formas arredondadas e o retângulo central POR CIMA do retângulo anterior.
                # Essa abordagem de desenho em camadas garante um visual limpo e arredondado.

                # Canto esquerdo arredondado (semicírculo)
                Ellipse(size=(self.height, self.height),
                        pos=self.pos)
                # Canto direito arredondado (semicírculo)
                Ellipse(size=(self.height, self.height),
                        pos=(self.x + self.width - self.height, self.y))

                # Retângulo central para conectar os semicírculos e formar o corpo do botão.
                overlap = dp(1) # Pequena sobreposição para garantir uma conexão perfeita entre as formas.
                                # Isso evita pequenas frestas visíveis.

                # Cálculos para a posição e largura do retângulo central, considerando a sobreposição.
                rect_x_overlapped = self.x + (self.height / 2.0) - overlap
                rect_width_overlapped = self.width - self.height + (2 * overlap)

                # Garante que a largura do retângulo não seja negativa em casos de botões muito pequenos.
                if rect_width_overlapped < 0:
                    rect_width_overlapped = 0

                Rectangle(size=(rect_width_overlapped, self.height),
                          pos=(rect_x_overlapped, self.y))

# --- ClickableBoxLayout ---
# Uma classe auxiliar para transformar qualquer BoxLayout em um widget clicável.
# Útil para criar áreas interativas complexas que precisam reagir como botões.
class ClickableBoxLayout(BoxLayout, ButtonBehavior):
    pass

# Registra a classe ClickableBoxLayout com o Kivy Factory.
# Isso permite que ela seja instanciada diretamente a partir de arquivos KV,
# simplificando a construção da interface do usuário.
Factory.register('ClickableBoxLayout', cls=ClickableBoxLayout)