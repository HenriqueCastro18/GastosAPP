# 💰 Gerenciador de Gastos Pessoais com Kivy

Este é um aplicativo desktop e mobile (Android) simples para gerenciar seus gastos pessoais, construído com o framework Kivy em Python. Ele permite criar múltiplas contas, registrar despesas, visualizar o histórico e manter um controle sobre seus gastos.

## ✨ Funcionalidades

* **Múltiplas Contas**: Crie e gerencie diferentes arquivos de banco de dados para organizar seus gastos (ex: "Conta Pessoal", "Cartão de Crédito", "Viagem").
* **Registro de Gastos**: Adicione novas despesas com valor, data, descrição e número de parcelas.
* **Visualização de Gastos**: Liste todos os gastos de uma conta específica, com opções para filtrar e visualizar detalhes.
* **Controle de Parcelas**: O aplicativo gerencia automaticamente o status das parcelas, mostrando o valor restante.
* **Edição e Exclusão**: Edite ou remova gastos existentes.
* **Agregação de Gastos**: Uma conta especial "GastosTotais.db" é gerada e atualizada automaticamente para somar todos os gastos de todas as suas contas, oferecendo uma visão geral consolidada.
* **Interface Intuitiva**: Desenvolvido com Kivy para uma experiência de usuário fluida e responsiva em diferentes dispositivos.

## 🚀 Como Usar (Desktop)

### Pré-requisitos

Certifique-se de ter Python 3 e `pip` instalados em seu sistema.

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SeuUsuario/NomeDoSeuRepositorio.git](https://github.com/SeuUsuario/NomeDoSeuRepositorio.git)
    cd NomeDoSeuRepositorio
    ```
2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install kivy
    # O sqlite3 já vem com o Python, então não precisa instalar separadamente.
    ```

### Execução

Após a instalação, você pode executar o aplicativo:

```bash
python main.py