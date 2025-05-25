# C:\Confia\confia_app\main_app_frame.py
# ... (imports no topo) ...
import customtkinter as ctk
import tkinter 
from tkinter import messagebox
from datetime import datetime, date, timedelta 
import db_manager 
import os

class AddEditCreditDialog(ctk.CTkToplevel):
    def __init__(self, master, refresh_callback, transaction_data=None):
        super().__init__(master)
        self.refresh_callback = refresh_callback
        self.categories_map = {} 
        self.editing_transaction_id = None

        if transaction_data:
            self.editing_transaction_id = transaction_data.get('id')
            self.title("Editar Crédito")
        else:
            self.title("Adicionar Novo Crédito")

        self.geometry("500x400") # Altura pode ser reduzida um pouco
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        dialog_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        dialog_main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        dialog_main_frame.grid_columnconfigure(1, weight=1)

        # Data
        ctk.CTkLabel(dialog_main_frame, text="Data:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        initial_date = transaction_data['data'] if transaction_data else date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, initial_date)

        # Valor
        ctk.CTkLabel(dialog_main_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="Ex: 150.75")
        self.value_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.value_entry.insert(0, f"{transaction_data['valor']:.2f}")

        # Categoria
        ctk.CTkLabel(dialog_main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        # ... (lógica de categoria como estava) ...
        self.category_var = ctk.StringVar()
        credit_categories_data = db_manager.get_categories_by_type('Crédito')
        category_names = []
        initial_category_name = None
        if credit_categories_data:
            for cat_id, nome, cor, fixa in credit_categories_data:
                self.categories_map[nome] = cat_id
                category_names.append(nome)
                if transaction_data and transaction_data.get('categoria_id') == cat_id: # .get para segurança
                    initial_category_name = nome
            if category_names and not initial_category_name:
                 initial_category_name = category_names[0]
            elif not category_names:
                initial_category_name = "Nenhuma categoria"
                category_names.append(initial_category_name)
        else: 
            initial_category_name = "Nenhuma categoria"
            category_names.append(initial_category_name)
        self.category_var.set(initial_category_name if initial_category_name else "Nenhuma categoria")
        self.category_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.category_var, values=category_names if category_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if not credit_categories_data or not category_names or self.category_var.get().startswith("Nenhuma categoria"):
            self.category_menu.configure(state="disabled")

        # Observação
        ctk.CTkLabel(dialog_main_frame, text="Observação:").grid(row=3, column=0, padx=5, pady=10, sticky="nw")
        self.observation_textbox = ctk.CTkTextbox(dialog_main_frame, height=100) # Aumentei um pouco a altura
        self.observation_textbox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.observation_textbox.insert("1.0", transaction_data['descricao'])
        
        # REMOVIDO CAMPO STATUS
        # ctk.CTkLabel(dialog_main_frame, text="Status:").grid(row=4, column=0, padx=5, pady=10, sticky="w")
        # self.status_var ...
        # self.status_menu ...

        # Botões
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(20,20), padx=20, side="bottom", fill="x", anchor="e") # Aumentado pady superior
        
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_action)
        self.save_button.pack(side="left", padx=(0,5))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left")
        
        if not transaction_data:
            self.value_entry.focus()
        else:
            self.observation_textbox.focus()

    def _save_action(self):
        data_str = self.date_entry.get()
        valor_str = self.value_entry.get().replace(",",".")
        categoria_nome = self.category_var.get()
        observacao = self.observation_textbox.get("1.0", ctk.END).strip()
        # REMOVIDO: status_str = self.status_var.get()
        # REMOVIDO: efetivada = 1 if status_str == "Efetivada" else 0

        # ... (validações como estavam) ...
        if not data_str: messagebox.showerror("Erro de Validação", "O campo Data é obrigatório.", parent=self); return
        try: datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro de Validação", "Formato de Data inválido (YYYY-MM-DD).", parent=self); return
        if not valor_str: messagebox.showerror("Erro de Validação", "O campo Valor é obrigatório.", parent=self); return
        try:
            valor = float(valor_str)
            if valor <= 0 and not self.editing_transaction_id: 
                 messagebox.showerror("Erro de Validação", "Valor deve ser positivo.", parent=self); return
        except ValueError: messagebox.showerror("Erro de Validação", "Valor inválido.", parent=self); return
        if categoria_nome.startswith("Nenhuma categoria") or not categoria_nome:
            messagebox.showerror("Erro de Validação", "Selecione uma Categoria válida.", parent=self); return
        categoria_id = self.categories_map.get(categoria_nome)
        if categoria_id is None: messagebox.showerror("Erro Interno", "ID da categoria não encontrado.", parent=self); return


        if self.editing_transaction_id:
            # Chamada para update_transaction sem 'efetivada'
            if db_manager.update_transaction(self.editing_transaction_id, data_str, observacao, valor, categoria_id):
                messagebox.showinfo("Sucesso", "Crédito atualizado com sucesso!", parent=self.master)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Erro no Banco", "Não foi possível atualizar o crédito.", parent=self)
        else: 
            # Chamada para add_transaction sem 'efetivada'
            if db_manager.add_transaction(data_str, observacao, valor, 'Crédito', categoria_id):
                messagebox.showinfo("Sucesso", "Crédito adicionado com sucesso!", parent=self.master)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Erro no Banco", "Não foi possível adicionar o crédito.", parent=self)

# --- CLASSE MainAppFrame (sem outras alterações nesta etapa) ---
# ... (O restante da classe MainAppFrame permanece o mesmo, incluindo __init__, _setup_menu, _create_tabs,
#      _setup_credits_tab, _load_initial_credits_data, _load_and_display_credits,
#      _on_filter_credits_button_click, _on_add_credit_button_click, _on_edit_credit_button_click,
#      _confirm_delete_credit, _setup_debits_tab, e os callbacks de menu) ...
# ...
# O if __name__ == "__main__": no final do arquivo também permanece o mesmo.
# Para ser completo, aqui está o restante da MainAppFrame para você colar o arquivo inteiro.

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self._setup_menu()
        self._create_tabs() 
        self.dialog_add_edit_credit = None 

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

        self.credit_col_config = [
            {"weight": 0, "minsize": 100, "text": "Data", "anchor": "w"},
            {"weight": 0, "minsize": 120, "text": "Valor", "anchor": "e"},
            {"weight": 1, "minsize": 130, "text": "Categoria", "anchor": "w"},
            {"weight": 2, "minsize": 150, "text": "Observação", "anchor": "w"},
            {"weight": 0, "minsize": 80,  "text": "Ações", "anchor": "center"}
        ]
        for i, config in enumerate(self.credit_col_config):
            self.credits_table_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=("gray85", "gray25"), corner_radius=0)
            header_cell_frame.grid(row=0, column=i, sticky="nsew")
            label = ctk.CTkLabel(header_cell_frame, text=config["text"], font=ctk.CTkFont(weight="bold"), anchor=config["anchor"])
            label.pack(padx=5, pady=5, fill="both", expand=True)
        separator = ctk.CTkFrame(self.credits_table_grid_container, height=1, fg_color=("gray70", "gray30"))
        separator.grid(row=1, column=0, columnspan=len(self.credit_col_config), sticky="ew", pady=(0,5))
        self._load_initial_credits_data()

    def _load_initial_credits_data(self):
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
            col_details = [
                (data_val, self.credit_col_config[0]["anchor"]),
                (f"R$ {valor:.2f}", self.credit_col_config[1]["anchor"]),
                (categoria_nome, self.credit_col_config[2]["anchor"]),
                (observacao, self.credit_col_config[3]["anchor"])
            ]
            for col_idx, (text, anchor) in enumerate(col_details):
                cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
                cell_frame.grid(row=current_row, column=col_idx, sticky="nsew")
                wraplen = self.credit_col_config[col_idx]["minsize"] - 10 if col_idx == 3 else 0
                label = ctk.CTkLabel(cell_frame, text=text, anchor=anchor, justify="left", wraplength=wraplen if wraplen > 0 else 0)
                label.pack(padx=5, pady=3, fill="both", expand=True)
            
            actions_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            actions_cell_frame.grid(row=current_row, column=4, sticky="nsew")
            actions_cell_frame.grid_columnconfigure(0, weight=1) 
            actions_cell_frame.grid_columnconfigure(1, weight=1)
            actions_cell_frame.grid_rowconfigure(0, weight=1)   
            edit_button = ctk.CTkButton(
                actions_cell_frame, text="✎", width=28, height=28, fg_color="transparent",
                text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                command=lambda t_id=trans_id: self._on_edit_credit_button_click(t_id)
            )
            edit_button.grid(row=0, column=0, padx=(0,2), pady=2, sticky="e")
            delete_button = ctk.CTkButton(
                actions_cell_frame, text="✕", width=28, height=28, fg_color="transparent",
                text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                command=lambda t_id=trans_id, t_desc=observacao: self._confirm_delete_credit(t_id, t_desc)
            )
            delete_button.grid(row=0, column=1, padx=(2,0), pady=2, sticky="w")
            current_row += 1

    def _on_filter_credits_button_click(self):
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
        if hasattr(self, 'dialog_add_edit_credit') and self.dialog_add_edit_credit is not None and self.dialog_add_edit_credit.winfo_exists():
            self.dialog_add_edit_credit.focus()
            return
        self.dialog_add_edit_credit = AddEditCreditDialog(master=self.controller, 
                                                          refresh_callback=self._on_filter_credits_button_click)

    def _on_edit_credit_button_click(self, transaction_id: int):
        print(f"Editando crédito ID: {transaction_id}")
        transaction_data = db_manager.get_transaction_by_id(transaction_id)
        if transaction_data:
            if hasattr(self, 'dialog_add_edit_credit') and self.dialog_add_edit_credit is not None and self.dialog_add_edit_credit.winfo_exists():
                self.dialog_add_edit_credit.focus()
                return
            self.dialog_add_edit_credit = AddEditCreditDialog(master=self.controller, 
                                                              refresh_callback=self._on_filter_credits_button_click,
                                                              transaction_data=transaction_data)
        else:
            messagebox.showerror("Erro", f"Não foi possível encontrar os dados do crédito ID {transaction_id} para edição.", parent=self.controller)

    def _confirm_delete_credit(self, transaction_id: int, transaction_description: str):
        display_desc = (transaction_description[:30] + '...') if len(transaction_description) > 30 else transaction_description
        confirm = messagebox.askyesno(
            title="Confirmar Exclusão de Crédito",
            message=f"Tem certeza que deseja excluir o crédito:\n'{display_desc}'?",
            parent=self.controller 
        )
        if confirm:
            if db_manager.delete_transaction(transaction_id):
                messagebox.showinfo("Sucesso", "Crédito excluído com sucesso.", parent=self.controller)
                self._on_filter_credits_button_click() 
            else:
                messagebox.showerror("Erro", "Não foi possível excluir o crédito.", parent=self.controller)
        else:
            print(f"Exclusão do crédito '{display_desc}' cancelada.")

    def _setup_debits_tab(self, tab): # Placeholder para a aba de débitos
        label = ctk.CTkLabel(tab, text="Conteúdo de Débitos Aqui. Será implementado em breve!")
        label.pack(pady=20, padx=20)
        
    # Callbacks de Menu (placeholders)
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário' (a ser implementado)")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha' (a ser implementado)")
    def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste' (a ser implementado)")
    def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste' (a ser implementado)")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

class AddEditDebitDialog(ctk.CTkToplevel):
    def __init__(self, master, refresh_callback, transaction_data=None):
        super().__init__(master)
        self.refresh_callback = refresh_callback
        self.categories_map = {} 
        self.editing_transaction_id = None

        if transaction_data:
            self.editing_transaction_id = transaction_data.get('id')
            self.title("Editar Débito")
        else:
            self.title("Adicionar Novo Débito")

        self.geometry("500x400") 
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        dialog_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        dialog_main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        dialog_main_frame.grid_columnconfigure(1, weight=1)

        # Data
        ctk.CTkLabel(dialog_main_frame, text="Data:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        initial_date = transaction_data['data'] if transaction_data else date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, initial_date)

        # Valor
        ctk.CTkLabel(dialog_main_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="Ex: 70.25")
        self.value_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.value_entry.insert(0, f"{transaction_data['valor']:.2f}")

        # Categoria (busca categorias de 'Débito')
        ctk.CTkLabel(dialog_main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.category_var = ctk.StringVar()
        debit_categories_data = db_manager.get_categories_by_type('Débito') # ALTERADO AQUI
        
        category_names = []
        initial_category_name = None
        if debit_categories_data:
            for cat_id, nome, cor, fixa in debit_categories_data:
                self.categories_map[nome] = cat_id
                category_names.append(nome)
                if transaction_data and transaction_data.get('categoria_id') == cat_id:
                    initial_category_name = nome
            
            if category_names and not initial_category_name:
                 initial_category_name = category_names[0]
            elif not category_names:
                initial_category_name = "Nenhuma categoria"
                category_names.append(initial_category_name)
        else:
            initial_category_name = "Nenhuma categoria de débito" # Mensagem específica
            category_names.append(initial_category_name)

        self.category_var.set(initial_category_name if initial_category_name else "Nenhuma categoria")
        self.category_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.category_var, values=category_names if category_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if not debit_categories_data or not category_names or self.category_var.get().startswith("Nenhuma categoria"):
            self.category_menu.configure(state="disabled")

        # Observação
        ctk.CTkLabel(dialog_main_frame, text="Observação:").grid(row=3, column=0, padx=5, pady=10, sticky="nw")
        self.observation_textbox = ctk.CTkTextbox(dialog_main_frame, height=100)
        self.observation_textbox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.observation_textbox.insert("1.0", transaction_data['descricao'])
        
        # Botões
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(20,20), padx=20, side="bottom", fill="x", anchor="e")
        
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_action)
        self.save_button.pack(side="left", padx=(0,5))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left")
        
        if not transaction_data:
            self.value_entry.focus()
        else:
            self.observation_textbox.focus()

    def _save_action(self):
        data_str = self.date_entry.get()
        valor_str = self.value_entry.get().replace(",",".")
        categoria_nome = self.category_var.get()
        observacao = self.observation_textbox.get("1.0", ctk.END).strip()
        # 'efetivada' não é mais gerenciado aqui, usará o default do BD

        if not data_str: messagebox.showerror("Erro de Validação", "O campo Data é obrigatório.", parent=self); return
        try: datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro de Validação", "Formato de Data inválido (YYYY-MM-DD).", parent=self); return
        if not valor_str: messagebox.showerror("Erro de Validação", "O campo Valor é obrigatório.", parent=self); return
        try:
            valor = float(valor_str)
            if valor <= 0 and not self.editing_transaction_id : # Débitos também devem ser positivos (o tipo 'Débito' define a natureza da transação)
                 messagebox.showerror("Erro de Validação", "Valor deve ser positivo.", parent=self); return
        except ValueError: messagebox.showerror("Erro de Validação", "Valor inválido.", parent=self); return
        if categoria_nome.startswith("Nenhuma categoria") or not categoria_nome:
            messagebox.showerror("Erro de Validação", "Selecione uma Categoria válida.", parent=self); return
        categoria_id = self.categories_map.get(categoria_nome)
        if categoria_id is None: messagebox.showerror("Erro Interno", "ID da categoria não encontrado.", parent=self); return

        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id, data_str, observacao, valor, categoria_id): # Passa tipo 'Débito'
                messagebox.showinfo("Sucesso", "Débito atualizado com sucesso!", parent=self.master)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Erro no Banco", "Não foi possível atualizar o débito.", parent=self)
        else: 
            if db_manager.add_transaction(data_str, observacao, valor, 'Débito', categoria_id): # Passa tipo 'Débito'
                messagebox.showinfo("Sucesso", "Débito adicionado com sucesso!", parent=self.master)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Erro no Banco", "Não foi possível adicionar o débito.", parent=self)

# --- CLASSE MainAppFrame (adicionar/modificar métodos para Débitos) ---
class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self._setup_menu()
        self._create_tabs() 
        self.dialog_add_edit_credit = None 
        self.dialog_add_edit_debit = None # Novo atributo para o diálogo de débito

    # ... (_setup_menu como estava) ...
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
        self.tab_debits = self.tab_view.add("Débitos") # Aba de Débitos
        self.tab_cards = self.tab_view.add("Cartões")
        self.tab_calculations = self.tab_view.add("Cálculos")
        self.tab_reports = self.tab_view.add("Relatórios/Insights")

        self._setup_dashboard_tab(self.tab_dashboard)
        self._setup_credits_tab(self.tab_credits) 
        self._setup_debits_tab(self.tab_debits) # Chama o setup para a aba de débitos
        # ... setup para outras abas ...

        self.tab_view.set("Dashboard")

    def _setup_dashboard_tab(self, tab):
        # ... (como estava) ...
        label = ctk.CTkLabel(tab, text="Conteúdo do Dashboard Aqui")
        label.pack(pady=20, padx=20)

    def _setup_credits_tab(self, tab_credits):
        # ... (código da aba de créditos como estava na sua versão funcional mais recente) ...
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
        self.credit_col_config = [
            {"weight": 0, "minsize": 100, "text": "Data", "anchor": "w"},
            {"weight": 0, "minsize": 120, "text": "Valor", "anchor": "e"},
            {"weight": 1, "minsize": 130, "text": "Categoria", "anchor": "w"},
            {"weight": 2, "minsize": 150, "text": "Observação", "anchor": "w"},
            {"weight": 0, "minsize": 80,  "text": "Ações", "anchor": "center"}
        ]
        for i, config in enumerate(self.credit_col_config):
            self.credits_table_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=("gray85", "gray25"), corner_radius=0)
            header_cell_frame.grid(row=0, column=i, sticky="nsew")
            label = ctk.CTkLabel(header_cell_frame, text=config["text"], font=ctk.CTkFont(weight="bold"), anchor=config["anchor"])
            label.pack(padx=5, pady=5, fill="both", expand=True)
        separator = ctk.CTkFrame(self.credits_table_grid_container, height=1, fg_color=("gray70", "gray30"))
        separator.grid(row=1, column=0, columnspan=len(self.credit_col_config), sticky="ew", pady=(0,5))
        self._load_initial_credits_data()

    def _load_initial_credits_data(self):
        # ... (como estava) ...
        today = date.today()
        start_of_month_dt = today.replace(day=1)
        if today.month == 12: end_of_month_dt = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else: end_of_month_dt = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        start_of_month_str = start_of_month_dt.strftime("%Y-%m-%d")
        end_of_month_str = end_of_month_dt.strftime("%Y-%m-%d")
        if hasattr(self, 'credits_start_date_entry'):
            self.credits_start_date_entry.delete(0, ctk.END); self.credits_start_date_entry.insert(0, start_of_month_str)
            self.credits_end_date_entry.delete(0, ctk.END); self.credits_end_date_entry.insert(0, end_of_month_str)
        self._load_and_display_credits(start_of_month_str, end_of_month_str)

    def _load_and_display_credits(self, start_date=None, end_date=None):
        # ... (como estava, incluindo a criação dos botões de editar e excluir) ...
        for i, widget in enumerate(self.credits_table_grid_container.winfo_children()):
            if widget.grid_info().get("row", 0) >= 2 : widget.destroy()
        transactions = db_manager.get_transactions('Crédito', start_date, end_date)
        if not transactions:
            ctk.CTkLabel(self.credits_table_grid_container, text="Nenhum crédito encontrado para o período.").grid(row=2, column=0, columnspan=len(self.credit_col_config), pady=10)
            return
        current_row = 2 
        for trans_id, data_val, valor, categoria_nome, observacao in transactions:
            row_fg_color = ("gray98", "gray22") if current_row % 2 == 0 else ("gray92", "gray18")
            col_details = [(data_val, self.credit_col_config[0]["anchor"]), (f"R$ {valor:.2f}", self.credit_col_config[1]["anchor"]), 
                           (categoria_nome, self.credit_col_config[2]["anchor"]), (observacao, self.credit_col_config[3]["anchor"])]
            for col_idx, (text, anchor) in enumerate(col_details):
                cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
                cell_frame.grid(row=current_row, column=col_idx, sticky="nsew")
                wraplen = self.credit_col_config[col_idx]["minsize"] - 10 if col_idx == 3 else 0
                ctk.CTkLabel(cell_frame, text=text, anchor=anchor, justify="left", wraplength=wraplen if wraplen > 0 else 0).pack(padx=5, pady=3, fill="both", expand=True)
            actions_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            actions_cell_frame.grid(row=current_row, column=4, sticky="nsew")
            actions_cell_frame.grid_columnconfigure(0, weight=1); actions_cell_frame.grid_columnconfigure(1, weight=1); actions_cell_frame.grid_rowconfigure(0, weight=1)   
            ctk.CTkButton(actions_cell_frame, text="✎", width=28, height=28, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda t_id=trans_id: self._on_edit_credit_button_click(t_id)).grid(row=0, column=0, padx=(0,2), pady=2, sticky="e")
            ctk.CTkButton(actions_cell_frame, text="✕", width=28, height=28, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda t_id=trans_id, t_desc=observacao: self._confirm_delete_credit(t_id, t_desc)).grid(row=0, column=1, padx=(2,0), pady=2, sticky="w")
            current_row += 1

    def _on_filter_credits_button_click(self):
        # ... (como estava) ...
        start_date_str = self.credits_start_date_entry.get(); end_date_str = self.credits_end_date_entry.get()
        try: datetime.strptime(start_date_str, "%Y-%m-%d"); datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro de Data", "Formato inválido. Use YYYY-MM-DD.", parent=self.controller); return
        self._load_and_display_credits(start_date_str, end_date_str)

    def _on_add_credit_button_click(self):
        # ... (como estava, usando AddEditCreditDialog) ...
        if hasattr(self, 'dialog_add_edit_credit') and self.dialog_add_edit_credit is not None and self.dialog_add_edit_credit.winfo_exists(): self.dialog_add_edit_credit.focus(); return
        self.dialog_add_edit_credit = AddEditCreditDialog(master=self.controller, refresh_callback=self._on_filter_credits_button_click)
    
    def _on_edit_credit_button_click(self, transaction_id: int):
        # ... (como estava, usando AddEditCreditDialog) ...
        transaction_data = db_manager.get_transaction_by_id(transaction_id)
        if transaction_data:
            if hasattr(self, 'dialog_add_edit_credit') and self.dialog_add_edit_credit is not None and self.dialog_add_edit_credit.winfo_exists(): self.dialog_add_edit_credit.focus(); return
            self.dialog_add_edit_credit = AddEditCreditDialog(master=self.controller, refresh_callback=self._on_filter_credits_button_click, transaction_data=transaction_data)
        else: messagebox.showerror("Erro", f"Dados do crédito ID {transaction_id} não encontrados.", parent=self.controller)

    def _confirm_delete_credit(self, transaction_id: int, transaction_description: str):
        # ... (como estava) ...
        display_desc = (transaction_description[:30] + '...') if len(transaction_description) > 30 else transaction_description
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir crédito:\n'{display_desc}'?", parent=self.controller):
            if db_manager.delete_transaction(transaction_id): messagebox.showinfo("Sucesso", "Crédito excluído.", parent=self.controller); self._on_filter_credits_button_click()
            else: messagebox.showerror("Erro", "Não foi possível excluir o crédito.", parent=self.controller)
        else: print(f"Exclusão do crédito '{display_desc}' cancelada.")

    # --- NOVOS MÉTODOS E LÓGICA PARA A ABA DÉBITOS ---
    def _setup_debits_tab(self, tab_debits):
        """Configura o conteúdo da aba Débitos."""
        debits_main_frame = ctk.CTkFrame(tab_debits, fg_color="transparent")
        debits_main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        filter_add_frame = ctk.CTkFrame(debits_main_frame)
        filter_add_frame.pack(fill="x", pady=(0,10), padx=5)
        
        ctk.CTkLabel(filter_add_frame, text="Data Inicial:").pack(side="left", padx=(5,0), pady=5)
        self.debits_start_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.debits_start_date_entry.pack(side="left", padx=(0,10), pady=5)

        ctk.CTkLabel(filter_add_frame, text="Data Final:").pack(side="left", padx=(5,0), pady=5)
        self.debits_end_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.debits_end_date_entry.pack(side="left", padx=(0,10), pady=5)

        filter_button_debits = ctk.CTkButton(filter_add_frame, text="Filtrar", width=80, command=self._on_filter_debits_button_click)
        filter_button_debits.pack(side="left", padx=5, pady=5)

        add_debit_button = ctk.CTkButton(filter_add_frame, text="Adicionar Débito", command=self._on_add_debit_button_click)
        add_debit_button.pack(side="right", padx=5, pady=5)
        
        self.debits_table_scrollframe = ctk.CTkScrollableFrame(debits_main_frame, label_text="Registros de Débito")
        self.debits_table_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)

        self.debits_table_grid_container = ctk.CTkFrame(self.debits_table_scrollframe, fg_color=("gray95", "gray20"))
        self.debits_table_grid_container.pack(fill="both", expand=True)

        # Reutiliza a config de colunas, mas pode ser específica se necessário
        self.debit_col_config = self.credit_col_config # Mesma estrutura de colunas
        for i, config in enumerate(self.debit_col_config):
            self.debits_table_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_cell_frame = ctk.CTkFrame(self.debits_table_grid_container, fg_color=("gray85", "gray25"), corner_radius=0)
            header_cell_frame.grid(row=0, column=i, sticky="nsew")
            label = ctk.CTkLabel(header_cell_frame, text=config["text"], font=ctk.CTkFont(weight="bold"), anchor=config["anchor"])
            label.pack(padx=5, pady=5, fill="both", expand=True)

        separator = ctk.CTkFrame(self.debits_table_grid_container, height=1, fg_color=("gray70", "gray30"))
        separator.grid(row=1, column=0, columnspan=len(self.debit_col_config), sticky="ew", pady=(0,5))
        
        self._load_initial_debits_data()

    def _load_initial_debits_data(self):
        today = date.today()
        start_of_month_dt = today.replace(day=1)
        if today.month == 12: end_of_month_dt = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else: end_of_month_dt = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        start_of_month_str = start_of_month_dt.strftime("%Y-%m-%d")
        end_of_month_str = end_of_month_dt.strftime("%Y-%m-%d")

        if hasattr(self, 'debits_start_date_entry'):
            self.debits_start_date_entry.delete(0, ctk.END); self.debits_start_date_entry.insert(0, start_of_month_str)
            self.debits_end_date_entry.delete(0, ctk.END); self.debits_end_date_entry.insert(0, end_of_month_str)
        self._load_and_display_debits(start_of_month_str, end_of_month_str)

    def _load_and_display_debits(self, start_date=None, end_date=None):
        for i, widget in enumerate(self.debits_table_grid_container.winfo_children()):
            if widget.grid_info().get("row", 0) >= 2 : widget.destroy()
        transactions = db_manager.get_transactions('Débito', start_date, end_date) # Busca TIPO 'Débito'
        if not transactions:
            ctk.CTkLabel(self.debits_table_grid_container, text="Nenhum débito encontrado para o período.").grid(row=2, column=0, columnspan=len(self.debit_col_config), pady=10)
            return

        current_row = 2 
        for trans_id, data_val, valor, categoria_nome, observacao in transactions:
            row_fg_color = ("gray98", "gray22") if current_row % 2 == 0 else ("gray92", "gray18")
            col_details = [(data_val, self.debit_col_config[0]["anchor"]), (f"R$ {valor:.2f}", self.debit_col_config[1]["anchor"]), 
                           (categoria_nome, self.debit_col_config[2]["anchor"]), (observacao, self.debit_col_config[3]["anchor"])]
            for col_idx, (text, anchor) in enumerate(col_details):
                cell_frame = ctk.CTkFrame(self.debits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
                cell_frame.grid(row=current_row, column=col_idx, sticky="nsew")
                wraplen = self.debit_col_config[col_idx]["minsize"] - 10 if col_idx == 3 else 0
                ctk.CTkLabel(cell_frame, text=text, anchor=anchor, justify="left", wraplength=wraplen if wraplen > 0 else 0).pack(padx=5, pady=3, fill="both", expand=True)
            
            actions_cell_frame = ctk.CTkFrame(self.debits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            actions_cell_frame.grid(row=current_row, column=4, sticky="nsew")
            actions_cell_frame.grid_columnconfigure(0, weight=1); actions_cell_frame.grid_columnconfigure(1, weight=1); actions_cell_frame.grid_rowconfigure(0, weight=1)   
            ctk.CTkButton(actions_cell_frame, text="✎", width=28, height=28, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda t_id=trans_id: self._on_edit_debit_button_click(t_id)).grid(row=0, column=0, padx=(0,2), pady=2, sticky="e")
            ctk.CTkButton(actions_cell_frame, text="✕", width=28, height=28, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), command=lambda t_id=trans_id, t_desc=observacao: self._confirm_delete_debit(t_id, t_desc)).grid(row=0, column=1, padx=(2,0), pady=2, sticky="w")
            current_row += 1

    def _on_filter_debits_button_click(self):
        start_date_str = self.debits_start_date_entry.get(); end_date_str = self.debits_end_date_entry.get()
        try: datetime.strptime(start_date_str, "%Y-%m-%d"); datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro de Data", "Formato inválido. Use YYYY-MM-DD.", parent=self.controller); return
        self._load_and_display_debits(start_date_str, end_date_str)

    def _on_add_debit_button_click(self):
        if hasattr(self, 'dialog_add_edit_debit') and self.dialog_add_edit_debit is not None and self.dialog_add_edit_debit.winfo_exists(): self.dialog_add_edit_debit.focus(); return
        self.dialog_add_edit_debit = AddEditDebitDialog(master=self.controller, refresh_callback=self._on_filter_debits_button_click)
    
    def _on_edit_debit_button_click(self, transaction_id: int):
        transaction_data = db_manager.get_transaction_by_id(transaction_id)
        if transaction_data:
            if hasattr(self, 'dialog_add_edit_debit') and self.dialog_add_edit_debit is not None and self.dialog_add_edit_debit.winfo_exists(): self.dialog_add_edit_debit.focus(); return
            self.dialog_add_edit_debit = AddEditDebitDialog(master=self.controller, refresh_callback=self._on_filter_debits_button_click, transaction_data=transaction_data)
        else: messagebox.showerror("Erro", f"Dados do débito ID {transaction_id} não encontrados.", parent=self.controller)

    def _confirm_delete_debit(self, transaction_id: int, transaction_description: str):
        display_desc = (transaction_description[:30] + '...') if len(transaction_description) > 30 else transaction_description
        if messagebox.askyesno("Confirmar Exclusão", f"Excluir débito:\n'{display_desc}'?", parent=self.controller):
            if db_manager.delete_transaction(transaction_id): messagebox.showinfo("Sucesso", "Débito excluído.", parent=self.controller); self._on_filter_debits_button_click()
            else: messagebox.showerror("Erro", "Não foi possível excluir o débito.", parent=self.controller)
        else: print(f"Exclusão do débito '{display_desc}' cancelada.")
        
    # Placeholder para outras abas
    def _setup_cards_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Cartões Aqui"); label.pack(pady=20, padx=20)
    def _setup_calculations_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Cálculos Aqui"); label.pack(pady=20, padx=20)
    def _setup_reports_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Relatórios/Insights Aqui"); label.pack(pady=20, padx=20)

    # Callbacks de Menu (placeholders)
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário' (a ser implementado)")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha' (a ser implementado)")
    def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste' (a ser implementado)")
    def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste' (a ser implementado)")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

if __name__ == '__main__':
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste MainAppFrame - CRUD Completo")
            self.geometry("1000x700")
            ctk.set_appearance_mode("light")
            if not os.path.exists(db_manager.DATABASE_DIR): os.makedirs(db_manager.DATABASE_DIR)
            if os.path.exists(db_manager.DATABASE_PATH): 
                try: os.remove(db_manager.DATABASE_PATH)
                except Exception as e: print(f"Não foi possível remover {db_manager.DATABASE_PATH} para teste: {e}")
            db_manager.initialize_database()
            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(fill="both", expand=True)
            self.main_frame_instance = MainAppFrame(parent=container, controller=self)
            self.main_frame_instance.pack(fill="both", expand=True)
            # self.main_frame_instance.tab_view.set("Créditos") # Teste Créditos
            self.main_frame_instance.tab_view.set("Débitos") # Teste Débitos
        def _on_app_closing(self): print("MockAppController: Chamado _on_app_closing (Sair)"); self.destroy()
        def show_frame(self, frame_name): print(f"MockAppController: Chamado show_frame para '{frame_name}'")
    mock_app = MockAppController()
    mock_app.mainloop()

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