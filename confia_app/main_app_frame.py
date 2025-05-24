# C:\Confia\confia_app\main_app_frame.py
# ... (imports e classe AddCreditDialog como estavam) ...
import customtkinter as ctk
import tkinter 
from tkinter import messagebox
from datetime import datetime, date, timedelta 
import db_manager 
import os # Adicionado para o if __name__ == "__main__"

class AddCreditDialog(ctk.CTkToplevel):
    # ... (código da AddCreditDialog sem alterações nesta etapa) ...
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.refresh_callback = refresh_callback
        self.categories_map = {} 

        self.title("Adicionar Novo Crédito")
        self.geometry("500x400") 
        self.resizable(False, False)
        self.transient(master) 
        self.grab_set() 

        dialog_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        dialog_main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        dialog_main_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dialog_main_frame, text="Data:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d")) 

        ctk.CTkLabel(dialog_main_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="Ex: 150.75")
        self.value_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.category_var = ctk.StringVar()
        credit_categories_data = db_manager.get_categories_by_type('Crédito')
        
        category_names = []
        if credit_categories_data:
            for cat_id, nome, cor, fixa in credit_categories_data:
                self.categories_map[nome] = cat_id 
                category_names.append(nome)
            if category_names: 
                self.category_var.set(category_names[0])
            else: 
                self.category_var.set("Nenhuma categoria")
        else:
            category_names.append("Nenhuma categoria de crédito")
            self.category_var.set(category_names[0])

        self.category_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.category_var, values=category_names if category_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if not credit_categories_data or not category_names or category_names[0].startswith("Nenhuma categoria"):
            self.category_menu.configure(state="disabled")

        ctk.CTkLabel(dialog_main_frame, text="Observação:").grid(row=3, column=0, padx=5, pady=10, sticky="nw")
        self.observation_textbox = ctk.CTkTextbox(dialog_main_frame, height=80)
        self.observation_textbox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10, padx=20, side="bottom", fill="x", anchor="e")
        
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_credit_action)
        self.save_button.pack(side="left", padx=(0,5))

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left")
        
        self.value_entry.focus()

    def _save_credit_action(self):
        data_str = self.date_entry.get()
        valor_str = self.value_entry.get().replace(",", ".")
        categoria_nome = self.category_var.get()
        observacao = self.observation_textbox.get("1.0", ctk.END).strip()
        if not data_str:
            messagebox.showerror("Erro de Validação", "O campo Data é obrigatório.", parent=self)
            return
        try:
            datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro de Validação", "Formato de Data inválido. Use YYYY-MM-DD.", parent=self)
            return
        if not valor_str:
            messagebox.showerror("Erro de Validação", "O campo Valor é obrigatório.", parent=self)
            return
        try:
            valor = float(valor_str)
            if valor <= 0:
                messagebox.showerror("Erro de Validação", "O Valor deve ser um número positivo.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Erro de Validação", "Valor inválido. Insira um número.", parent=self)
            return
        if categoria_nome.startswith("Nenhuma categoria") or not categoria_nome:
            messagebox.showerror("Erro de Validação", "Selecione uma Categoria válida.", parent=self)
            return
        categoria_id = self.categories_map.get(categoria_nome)
        if categoria_id is None:
             messagebox.showerror("Erro Interno", "ID da categoria não encontrado.", parent=self)
             return
        if db_manager.add_transaction(data_str, observacao, valor, 'Crédito', categoria_id): # Adiciona como efetivada por padrão
            messagebox.showinfo("Sucesso", "Crédito adicionado com sucesso!", parent=self.master)
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Erro no Banco", "Não foi possível adicionar o crédito.\nVerifique o console para mais detalhes.", parent=self)

class MainAppFrame(ctk.CTkFrame):
    # ... (__init__, _setup_menu, _create_tabs, _setup_dashboard_tab como estavam) ...
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self._setup_menu()
        self._create_tabs() 
        self.dialog_add_credit = None 

    def _setup_menu(self):
        menubar = tkinter.Menu(self.controller) 
        menu_sistema = tkinter.Menu(menubar, tearoff=0)
        menu_sistema.add_command(label="Criar Novo Usuário", command=self._criar_novo_usuario)
        menu_sistema.add_command(label="Alterar Senha", command=self._alterar_senha)
        menu_sistema.add_command(label="Gerenciar Categorias", command=lambda: self.controller.show_frame("CategoryManagementFrame"))
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
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)
        self.tab_dashboard = self.tab_view.add("Dashboard")
        self.tab_credits = self.tab_view.add("Créditos") 
        self.tab_debits = self.tab_view.add("Débitos")
        self.tab_cards = self.tab_view.add("Cartões")
        self.tab_calculations = self.tab_view.add("Cálculos")
        self.tab_reports = self.tab_view.add("Relatórios/Insights")
        self._setup_dashboard_tab(self.tab_dashboard)
        self._setup_credits_tab(self.tab_credits) 
        self._setup_debits_tab(self.tab_debits)
        self.tab_view.set("Dashboard") 

    def _setup_dashboard_tab(self, tab):
        label = ctk.CTkLabel(tab, text="Conteúdo do Dashboard Aqui")
        label.pack(pady=20, padx=20)

    def _setup_credits_tab(self, tab_credits):
        credits_main_frame = ctk.CTkFrame(tab_credits, fg_color="transparent")
        credits_main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        filter_add_frame = ctk.CTkFrame(credits_main_frame)
        filter_add_frame.pack(fill="x", pady=(0,10), padx=5)
        
        ctk.CTkLabel(filter_add_frame, text="Data Inicial:").pack(side="left", padx=(5,0), pady=5)
        self.credits_start_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.credits_start_date_entry.pack(side="left", padx=(0,10), pady=5)

        ctk.CTkLabel(filter_add_frame, text="Data Final:").pack(side="left", padx=(5,0), pady=5)
        self.credits_end_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.credits_end_date_entry.pack(side="left", padx=(0,10), pady=5)

        filter_button_credits = ctk.CTkButton(filter_add_frame, text="Filtrar", width=80, command=self._on_filter_credits_button_click)
        filter_button_credits.pack(side="left", padx=5, pady=5)

        add_credit_button = ctk.CTkButton(filter_add_frame, text="Adicionar Crédito", command=self._on_add_credit_button_click)
        add_credit_button.pack(side="right", padx=5, pady=5)
        
        self.credits_table_scrollframe = ctk.CTkScrollableFrame(credits_main_frame, label_text="Registros de Crédito")
        self.credits_table_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)

        self.credits_table_grid_container = ctk.CTkFrame(self.credits_table_scrollframe, fg_color=("gray95", "gray20"))
        self.credits_table_grid_container.pack(fill="both", expand=True)

        # --- MODIFICAÇÃO: Adiciona coluna "Ações" e ajusta configs ---
        self.credit_col_config = [
            {"weight": 0, "minsize": 100, "text": "Data", "anchor": "w"},
            {"weight": 0, "minsize": 120, "text": "Valor", "anchor": "e"},
            {"weight": 1, "minsize": 150, "text": "Categoria", "anchor": "w"},
            {"weight": 2, "minsize": 180, "text": "Observação", "anchor": "w"}, # Reduzido minsize um pouco
            {"weight": 0, "minsize": 50,  "text": "Ações", "anchor": "center"} # Nova coluna para Ações
        ]

        for i, config in enumerate(self.credit_col_config):
            self.credits_table_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, 
                                             fg_color=("gray85", "gray25"), corner_radius=0)
            header_cell_frame.grid(row=0, column=i, sticky="nsew")
            label = ctk.CTkLabel(header_cell_frame, text=config["text"], 
                                 font=ctk.CTkFont(weight="bold"), anchor=config["anchor"])
            label.pack(padx=5, pady=5, fill="both", expand=True)

        separator = ctk.CTkFrame(self.credits_table_grid_container, height=1, fg_color=("gray70", "gray30"))
        separator.grid(row=1, column=0, columnspan=len(self.credit_col_config), sticky="ew", pady=(0,5))
        
        self._load_initial_credits_data()

    def _load_initial_credits_data(self):
        # ... (como estava) ...
        today = date.today()
        start_of_month_dt = today.replace(day=1)
        if today.month == 12:
            end_of_month_dt = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month_dt = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        start_of_month_str = start_of_month_dt.strftime("%Y-%m-%d")
        end_of_month_str = end_of_month_dt.strftime("%Y-%m-%d")
        if hasattr(self, 'credits_start_date_entry'):
            self.credits_start_date_entry.delete(0, ctk.END)
            self.credits_start_date_entry.insert(0, start_of_month_str)
            self.credits_end_date_entry.delete(0, ctk.END)
            self.credits_end_date_entry.insert(0, end_of_month_str)
        self._load_and_display_credits(start_of_month_str, end_of_month_str)

    def _load_and_display_credits(self, start_date=None, end_date=None):
        for i, widget in enumerate(self.credits_table_grid_container.winfo_children()):
            if widget.grid_info().get("row", 0) >= 2 : 
                widget.destroy()

        transactions = db_manager.get_transactions('Crédito', start_date, end_date)
        
        if not transactions:
            no_data_label = ctk.CTkLabel(self.credits_table_grid_container, text="Nenhum crédito encontrado para o período.")
            no_data_label.grid(row=2, column=0, columnspan=len(self.credit_col_config), pady=10)
            return

        current_row = 2 
        for trans_id, data_val, valor, categoria_nome, observacao in transactions:
            row_fg_color = ("gray98", "gray22") if current_row % 2 == 0 else ("gray92", "gray18")

            # Coluna 0: Data
            data_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            data_cell_frame.grid(row=current_row, column=0, sticky="nsew")
            data_label = ctk.CTkLabel(data_cell_frame, text=data_val, anchor=self.credit_col_config[0]["anchor"])
            data_label.pack(padx=5, pady=3, fill="both", expand=True)

            # Coluna 1: Valor
            valor_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            valor_cell_frame.grid(row=current_row, column=1, sticky="nsew")
            valor_label = ctk.CTkLabel(valor_cell_frame, text=f"R$ {valor:.2f}", anchor=self.credit_col_config[1]["anchor"])
            valor_label.pack(padx=5, pady=3, fill="both", expand=True)

            # Coluna 2: Categoria
            cat_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            cat_cell_frame.grid(row=current_row, column=2, sticky="nsew")
            categoria_label = ctk.CTkLabel(cat_cell_frame, text=categoria_nome, anchor=self.credit_col_config[2]["anchor"])
            categoria_label.pack(padx=5, pady=3, fill="both", expand=True)

            # Coluna 3: Observação
            obs_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            obs_cell_frame.grid(row=current_row, column=3, sticky="nsew")
            observacao_label = ctk.CTkLabel(obs_cell_frame, text=observacao, 
                                            anchor=self.credit_col_config[3]["anchor"], justify="left",
                                            wraplength=self.credit_col_config[3]["minsize"] - 10)
            observacao_label.pack(padx=5, pady=3, fill="both", expand=True)
            
            # --- MODIFICAÇÃO: Coluna 4: Ações (Botão Excluir) ---
            action_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            action_cell_frame.grid(row=current_row, column=4, sticky="nsew")
            action_cell_frame.grid_columnconfigure(0, weight=1) # Para centralizar o botão
            action_cell_frame.grid_rowconfigure(0, weight=1)    # Para centralizar o botão

            delete_button = ctk.CTkButton(
                action_cell_frame, 
                text="✕", 
                width=28, height=28,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda t_id=trans_id, t_desc=observacao: self._confirm_delete_credit(t_id, t_desc)
            )
            delete_button.grid(row=0, column=0, padx=0, pady=0) # Centralizado no action_cell_frame
            # --- FIM DA MODIFICAÇÃO ---
            
            current_row += 1

    def _on_filter_credits_button_click(self):
        # ... (como estava) ...
        start_date_str = self.credits_start_date_entry.get()
        end_date_str = self.credits_end_date_entry.get()
        try:
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro de Data", "Formato de data inválido. Use YYYY-MM-DD.", parent=self.controller)
            return
        self._load_and_display_credits(start_date_str, end_date_str)

    def _on_add_credit_button_click(self):
        # ... (como estava) ...
        if hasattr(self, 'dialog_add_credit') and self.dialog_add_credit is not None and self.dialog_add_credit.winfo_exists():
            self.dialog_add_credit.focus()
            return
        self.dialog_add_credit = AddCreditDialog(master=self.controller, 
                                                 refresh_callback=self._on_filter_credits_button_click)

    # --- NOVO MÉTODO PARA CONFIRMAR E EXCLUIR CRÉDITO ---
    def _confirm_delete_credit(self, transaction_id: int, transaction_description: str):
        """Pede confirmação e então tenta excluir a transação de crédito."""
        # Pega uma parte da descrição para a mensagem, caso seja muito longa
        display_desc = (transaction_description[:30] + '...') if len(transaction_description) > 30 else transaction_description
        
        confirm = messagebox.askyesno(
            title="Confirmar Exclusão de Crédito",
            message=f"Tem certeza que deseja excluir o crédito:\n'{display_desc}'?",
            parent=self.controller 
        )
        if confirm:
            if db_manager.delete_transaction(transaction_id):
                messagebox.showinfo("Sucesso", "Crédito excluído com sucesso.", parent=self.controller)
                self._on_filter_credits_button_click() # Recarrega a lista com os filtros atuais
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o crédito.", parent=self.controller)
        else:
            print(f"Exclusão do crédito '{display_desc}' cancelada.")

    def _setup_debits_tab(self, tab):
        label = ctk.CTkLabel(tab, text="Conteúdo de Débitos Aqui")
        label.pack(pady=20, padx=20)
        
    # ... (callbacks de menu como estavam) ...
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário' (a ser implementado)")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha' (a ser implementado)")
    def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste' (a ser implementado)")
    def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste' (a ser implementado)")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

# Bloco if __name__ == '__main__': (como estava, com os imports necessários)
if __name__ == '__main__':
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste MainAppFrame - Aba Créditos")
            self.geometry("1000x700")
            ctk.set_appearance_mode("light")
            if not os.path.exists(db_manager.DATABASE_DIR): os.makedirs(db_manager.DATABASE_DIR)
            if os.path.exists(db_manager.DATABASE_PATH): 
                try:
                    os.remove(db_manager.DATABASE_PATH)
                except Exception as e:
                    print(f"Não foi possível remover {db_manager.DATABASE_PATH} para teste: {e}")
            db_manager.initialize_database()
            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(fill="both", expand=True)
            self.main_frame_instance = MainAppFrame(parent=container, controller=self)
            self.main_frame_instance.pack(fill="both", expand=True)
            self.main_frame_instance.tab_view.set("Créditos")
        def _on_app_closing(self): 
            print("MockAppController: Chamado _on_app_closing (Sair)")
            self.destroy()
        def show_frame(self, frame_name):
            print(f"MockAppController: Chamado show_frame para '{frame_name}'")
    mock_app = MockAppController()
    mock_app.mainloop()