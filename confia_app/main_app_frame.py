# C:\Confia\confia_app\main_app_frame.py
# Módulo responsável pelo frame (tela) principal da aplicação Confia

import customtkinter as ctk
import tkinter

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        print("DEBUG: MainAppFrame.__init__ - Iniciando...")
        super().__init__(parent, **kwargs)
    
        self.controller = controller
    
        self.configure(fg_color="transparent") 
        self._setup_menu()
        self._create_tabs()
        print("DEBUG: MainAppFrame.__init__ - Concluído.")

    # ... (restante dos métodos _setup_menu, _create_tabs, e callbacks de menu) ...
    def _setup_menu(self):
        """Cria e configura o menu superior na janela raiz (App)."""
        menubar = tkinter.Menu(self.controller) 
        menu_sistema = tkinter.Menu(menubar, tearoff=0)
        menu_sistema.add_command(label="Criar Novo Usuário", command=self._criar_novo_usuario)
        menu_sistema.add_command(label="Alterar Senha", command=self._alterar_senha)
        menu_sistema.add_separator()
        menu_sistema.add_command(label="Sair", command=self.controller._on_app_closing) 
        menubar.add_cascade(label="Sistema", menu=menu_sistema)
        menu_ferramentas = tkinter.Menu(menubar, tearoff=0)
        menu_ferramentas.add_command(label="Gerar Dados de Teste", command=self._gerar_dados_teste)
        menu_ferramentas.add_command(label="Apagar Dados de Teste", command=self._apagar_dados_teste)
        menubar.add_cascade(label="Ferramentas", menu=menu_ferramentas)
        menu_ajuda = tkinter.Menu(menubar, tearoff=0)
        menu_ajuda.add_command(label="Sobre Confia", command=self._sobre_confia)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        self.controller.config(menu=menubar)

    def _create_tabs(self):
        """Cria e configura o CTkTabview com as abas da aplicação."""
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)
        self.tab_dashboard = self.tab_view.add("Dashboard")
        dashboard_label = ctk.CTkLabel(self.tab_dashboard, text="Conteúdo do Dashboard Aqui")
        dashboard_label.pack(pady=20, padx=20)
        self.tab_creditos = self.tab_view.add("Créditos")
        creditos_label = ctk.CTkLabel(self.tab_creditos, text="Conteúdo de Créditos Aqui")
        creditos_label.pack(pady=20, padx=20)
        self.tab_debitos = self.tab_view.add("Débitos")
        debitos_label = ctk.CTkLabel(self.tab_debitos, text="Conteúdo de Débitos Aqui")
        debitos_label.pack(pady=20, padx=20)
        self.tab_cartoes = self.tab_view.add("Cartões")
        cartoes_label = ctk.CTkLabel(self.tab_cartoes, text="Conteúdo de Cartões Aqui")
        cartoes_label.pack(pady=20, padx=20)
        self.tab_calculos = self.tab_view.add("Cálculos")
        calculos_label = ctk.CTkLabel(self.tab_calculos, text="Conteúdo de Cálculos Aqui")
        calculos_label.pack(pady=20, padx=20)
        self.tab_relatorios = self.tab_view.add("Relatórios/Insights")
        relatorios_label = ctk.CTkLabel(self.tab_relatorios, text="Conteúdo de Relatórios/Insights Aqui")
        relatorios_label.pack(pady=20, padx=20)
        self.tab_view.set("Dashboard")

    def _criar_novo_usuario(self):
        print("MainAppFrame: Ação 'Criar Novo Usuário'")
    def _alterar_senha(self):
        print("MainAppFrame: Ação 'Alterar Senha'")
    def _gerar_dados_teste(self):
        print("MainAppFrame: Ação 'Gerar Dados de Teste'")
    def _apagar_dados_teste(self):
        print("MainAppFrame: Ação 'Apagar Dados de Teste'")
    def _sobre_confia(self):
        print("MainAppFrame: Ação 'Sobre Confia'")
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, 
                      title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0 (Refatorado)\nDesenvolvido com Python e CustomTkinter")

if __name__ == '__main__':
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste MainAppFrame")
            self.geometry("1000x700")
            container = ctk.CTkFrame(self)
            container.pack(fill="both", expand=True)
            self.main_app_frame = MainAppFrame(parent=container, controller=self)
            self.main_app_frame.pack(fill="both", expand=True)
        def _on_app_closing(self):
            print("MockAppController: Fechando aplicação de teste.")
            self.destroy()
    mock_app = MockAppController()
    mock_app.mainloop()