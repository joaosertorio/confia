# C:\Confia\confia_app\main_app_frame.py
# Módulo responsável pelo frame (tela) principal da aplicação Confia,
# contendo o menu e as abas.

import customtkinter as ctk
import tkinter
from tkinter import messagebox  # Para mensagens de erro/sucesso
from datetime import datetime, date, timedelta
import db_manager  # Acesso às funções do BD
import os # Usado no bloco de teste __main__

# --- DIÁLOGOS (AddEditCreditDialog, AddEditDebitDialog, AddEditCardDialog) ---
# (Mantenha as definições das classes AddEditCreditDialog, AddEditDebitDialog, 
# e AddEditCardDialog aqui como foram fornecidas e validadas anteriormente)

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
        initial_date = transaction_data['data'] if transaction_data else date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, initial_date) 

        ctk.CTkLabel(dialog_main_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="Ex: 150.75")
        self.value_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.value_entry.insert(0, f"{transaction_data['valor']:.2f}")

        ctk.CTkLabel(dialog_main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.category_var = ctk.StringVar()
        credit_categories_data = db_manager.get_categories_by_type('Crédito')
        
        category_names = []
        initial_category_name = None
        if credit_categories_data:
            for cat_id, nome, cor, fixa in credit_categories_data:
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
            initial_category_name = "Nenhuma categoria"
            category_names.append(initial_category_name)
        self.category_var.set(initial_category_name if initial_category_name else "Nenhuma categoria")
        self.category_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.category_var, values=category_names if category_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if not credit_categories_data or not category_names or self.category_var.get().startswith("Nenhuma categoria"):
            self.category_menu.configure(state="disabled")

        ctk.CTkLabel(dialog_main_frame, text="Observação:").grid(row=3, column=0, padx=5, pady=10, sticky="nw")
        self.observation_textbox = ctk.CTkTextbox(dialog_main_frame, height=100)
        self.observation_textbox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.observation_textbox.insert("1.0", transaction_data['descricao'])
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(20,20), padx=20, side="bottom", fill="x", anchor="e")
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_action)
        self.save_button.pack(side="left", padx=(0,5))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left")
        if not transaction_data: self.value_entry.focus()
        else: self.observation_textbox.focus()

    def _save_action(self):
        data_str = self.date_entry.get(); valor_str = self.value_entry.get().replace(",",".")
        categoria_nome = self.category_var.get(); observacao = self.observation_textbox.get("1.0", ctk.END).strip()
        if not data_str: messagebox.showerror("Erro", "Data é obrigatória.", parent=self); return
        try: datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro", "Formato de Data inválido (YYYY-MM-DD).", parent=self); return
        if not valor_str: messagebox.showerror("Erro", "Valor é obrigatório.", parent=self); return
        try:
            valor = float(valor_str)
            if valor <= 0 and not self.editing_transaction_id : messagebox.showerror("Erro", "Valor deve ser positivo.", parent=self); return
        except ValueError: messagebox.showerror("Erro", "Valor inválido.", parent=self); return
        if categoria_nome.startswith("Nenhuma categoria"): messagebox.showerror("Erro", "Selecione uma Categoria.", parent=self); return
        categoria_id = self.categories_map.get(categoria_nome)
        if categoria_id is None: messagebox.showerror("Erro", "ID da categoria não encontrado.", parent=self); return
        
        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id, data_str, observacao, valor, categoria_id): # 'efetivada' removido
                messagebox.showinfo("Sucesso", "Crédito atualizado!", parent=self.master); self.refresh_callback(); self.destroy()
            else: messagebox.showerror("Erro", "Não foi possível atualizar o crédito.", parent=self)
        else: 
            if db_manager.add_transaction(data_str, observacao, valor, 'Crédito', categoria_id): # 'efetivada' removido
                messagebox.showinfo("Sucesso", "Crédito adicionado!", parent=self.master); self.refresh_callback(); self.destroy()
            else: messagebox.showerror("Erro", "Não foi possível adicionar o crédito.", parent=self)

class AddEditDebitDialog(ctk.CTkToplevel): #Mesma estrutura do AddEditCreditDialog, mas para Débitos
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

        ctk.CTkLabel(dialog_main_frame, text="Data:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="YYYY-MM-DD")
        self.date_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        initial_date = transaction_data['data'] if transaction_data else date.today().strftime("%Y-%m-%d")
        self.date_entry.insert(0, initial_date) 

        ctk.CTkLabel(dialog_main_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="Ex: 70.25")
        self.value_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.value_entry.insert(0, f"{transaction_data['valor']:.2f}")

        ctk.CTkLabel(dialog_main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.category_var = ctk.StringVar()
        debit_categories_data = db_manager.get_categories_by_type('Débito') # BUSCA CATEGORIAS DE DÉBITO
        
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
            initial_category_name = "Nenhuma categoria"
            category_names.append(initial_category_name)
        self.category_var.set(initial_category_name if initial_category_name else "Nenhuma categoria")
        self.category_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.category_var, values=category_names if category_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if not debit_categories_data or not category_names or self.category_var.get().startswith("Nenhuma categoria"):
            self.category_menu.configure(state="disabled")

        ctk.CTkLabel(dialog_main_frame, text="Observação:").grid(row=3, column=0, padx=5, pady=10, sticky="nw")
        self.observation_textbox = ctk.CTkTextbox(dialog_main_frame, height=100)
        self.observation_textbox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data:
            self.observation_textbox.insert("1.0", transaction_data['descricao'])
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(20,20), padx=20, side="bottom", fill="x", anchor="e")
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_action)
        self.save_button.pack(side="left", padx=(0,5))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left")
        if not transaction_data: self.value_entry.focus()
        else: self.observation_textbox.focus()

    def _save_action(self):
        data_str = self.date_entry.get(); valor_str = self.value_entry.get().replace(",",".")
        categoria_nome = self.category_var.get(); observacao = self.observation_textbox.get("1.0", ctk.END).strip()
        if not data_str: messagebox.showerror("Erro", "Data é obrigatória.", parent=self); return
        try: datetime.strptime(data_str, "%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro", "Formato de Data inválido (YYYY-MM-DD).", parent=self); return
        if not valor_str: messagebox.showerror("Erro", "Valor é obrigatório.", parent=self); return
        try:
            valor = float(valor_str)
            if valor <= 0 and not self.editing_transaction_id: messagebox.showerror("Erro", "Valor deve ser positivo.", parent=self); return
        except ValueError: messagebox.showerror("Erro", "Valor inválido.", parent=self); return
        if categoria_nome.startswith("Nenhuma categoria"): messagebox.showerror("Erro", "Selecione uma Categoria.", parent=self); return
        categoria_id = self.categories_map.get(categoria_nome)
        if categoria_id is None: messagebox.showerror("Erro", "ID da categoria não encontrado.", parent=self); return
        
        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id, data_str, observacao, valor, categoria_id): # Passa TIPO 'Débito'
                messagebox.showinfo("Sucesso", "Débito atualizado!", parent=self.master); self.refresh_callback(); self.destroy()
            else: messagebox.showerror("Erro", "Não foi possível atualizar o débito.", parent=self)
        else: 
            if db_manager.add_transaction(data_str, observacao, valor, 'Débito', categoria_id): # Passa TIPO 'Débito'
                messagebox.showinfo("Sucesso", "Débito adicionado!", parent=self.master); self.refresh_callback(); self.destroy()
            else: messagebox.showerror("Erro", "Não foi possível adicionar o débito.", parent=self)

class AddEditCardDialog(ctk.CTkToplevel):
    def __init__(self, master, controller, refresh_callback, card_data=None):
        super().__init__(master)
        self.controller = controller 
        self.refresh_callback = refresh_callback
        self.editing_card_id = None

        # Paleta de cores para cartões
        self.card_color_map = {
            "Azul Clássico": "#3B8ED0", "Verde Esmeralda": "#2ECC71", "Vermelho Rubi": "#E74C3C",
            "Amarelo Solar": "#F1C40F", "Laranja Vibrante": "#E67E22", "Roxo Profundo": "#8E44AD",
            "Cinza Grafite": "#34495E", "Prata": "#BDC3C7", "Turquesa": "#1ABC9C"
        }
        self.card_color_names = list(self.card_color_map.keys())

        # Lista de bandeiras
        self.card_flags = ["Mastercard", "Visa", "American Express", "Elo", "Hipercard", "Outros"]

        if card_data:
            self.editing_card_id = card_data.get('id')
            self.title("Editar Cartão")
        else:
            self.title("Adicionar Novo Cartão")

        self.geometry("500x400") # Ajuste conforme necessário para os novos campos
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        dialog_main_frame = ctk.CTkFrame(self, fg_color="transparent")
        dialog_main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        dialog_main_frame.grid_columnconfigure(1, weight=1) # Coluna de entrada expande
        dialog_main_frame.grid_columnconfigure(2, weight=0) # Coluna para preview de cor

        # Nome do Cartão
        ctk.CTkLabel(dialog_main_frame, text="Nome do Cartão:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(dialog_main_frame, width=300) # Largura maior
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky="ew") # Colspan
        if card_data: self.name_entry.insert(0, card_data.get('nome', ''))

        # Bandeira (OptionMenu)
        ctk.CTkLabel(dialog_main_frame, text="Bandeira:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.flag_var = ctk.StringVar(value=self.card_flags[0]) # Padrão
        if card_data and card_data.get('bandeira') in self.card_flags:
            self.flag_var.set(card_data.get('bandeira'))
        self.flag_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.flag_var, values=self.card_flags, width=300)
        self.flag_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=10, sticky="ew")

        # Cor do Cartão (OptionMenu + Preview)
        ctk.CTkLabel(dialog_main_frame, text="Cor do Cartão:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        default_color_name = self.card_color_names[0]
        if card_data and card_data.get('cor'):
            # Tenta encontrar o nome da cor a partir do HEX salvo
            hex_to_name = {v: k for k, v in self.card_color_map.items()}
            default_color_name = hex_to_name.get(card_data.get('cor'), self.card_color_names[0])

        self.card_color_var = ctk.StringVar(value=default_color_name)
        self.card_color_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.card_color_var, 
                                                 values=self.card_color_names, command=self._update_card_color_preview,
                                                 width=230) # Largura ajustada
        self.card_color_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        self.card_color_preview_box = ctk.CTkFrame(dialog_main_frame, width=30, height=30, border_width=1)
        self.card_color_preview_box.grid(row=2, column=2, padx=(5,10), pady=10, sticky="w")
        self._update_card_color_preview() # Cor inicial do preview

        # Futuros campos (Limite, etc.) podem vir aqui na row=3, column=0 e 1...

        # Botões
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(30,20), padx=20, side="bottom", fill="x", anchor="e")
        
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_action)
        self.save_button.pack(side="left", padx=(0,5))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="left")
        
        self.name_entry.focus()

    def _update_card_color_preview(self, selected_color_name_event=None):
        selected_name = self.card_color_var.get()
        hex_color = self.card_color_map.get(selected_name, "#FFFFFF") # Branco se não encontrar
        self.card_color_preview_box.configure(fg_color=hex_color)

    def _save_action(self):
        nome = self.name_entry.get().strip()
        bandeira = self.flag_var.get()
        selected_color_name = self.card_color_var.get()
        cor_hex = self.card_color_map.get(selected_color_name, '#808080') # Cinza padrão se algo der errado

        if not nome:
            messagebox.showerror("Erro de Validação", "O Nome do Cartão é obrigatório.", parent=self)
            return
        if bandeira == "Outros" and not messagebox.askyesno("Confirmação", "Bandeira 'Outros' selecionada. Continuar?", parent=self):
            return # Permite ao usuário reconsiderar "Outros"

        # Campos opcionais que não estão na UI ainda, mas estão no DB: banco, limite, dia_fechamento, dia_vencimento
        # Se fossem adicionados à UI, seriam coletados aqui.
        # Por enquanto, passaremos None ou os valores existentes se estiver editando e não os mudamos.
        banco = None 
        limite = None
        dia_fechamento = None
        dia_vencimento = None

        if self.editing_card_id: # Modo Edição
            # Se estiver editando, busca os valores atuais de campos não presentes no form para não sobrescrevê-los com None
            # a menos que esses campos também sejam editáveis no form.
            # Por ora, como o form só edita nome, bandeira e cor, vamos buscar o resto para manter.
            current_card_data = db_manager.get_card_by_id(self.editing_card_id)
            if current_card_data:
                banco = current_card_data.get('banco') # Mantém banco existente
                limite = current_card_data.get('limite')
                dia_fechamento = current_card_data.get('dia_fechamento')
                dia_vencimento = current_card_data.get('dia_vencimento')

            if db_manager.update_card(self.editing_card_id, nome, bandeira, cor_hex, limite, dia_fechamento, dia_vencimento, banco):
                messagebox.showinfo("Sucesso", f"Cartão '{nome}' atualizado com sucesso!", parent=self.master)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Erro no Banco", "Não foi possível atualizar o cartão.", parent=self)
        else: # Modo Adicionar
            new_card_id = db_manager.add_card(nome, bandeira, cor_hex, limite, dia_fechamento, dia_vencimento, banco)
            if new_card_id:
                messagebox.showinfo("Sucesso", f"Cartão '{nome}' adicionado com sucesso!", parent=self.master)
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("Erro no Banco", "Não foi possível adicionar o cartão.\nVerifique se já existe um cartão com este nome.", parent=self)


class MainAppFrame(ctk.CTkFrame):
    # ... (__init__, _setup_menu, _create_tabs, _on_tab_change, _setup_dashboard_tab, 
    #      métodos de Créditos e Débitos como estavam) ...
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self.dialog_add_edit_credit = None 
        self.dialog_add_edit_debit = None
        self.dialog_add_edit_card = None 
        self.selected_card_id = None 
        self.last_selected_card_row_frame = None 
        self.current_invoice_year = date.today().year 
        self._setup_menu()
        self._create_tabs() 

    def _setup_menu(self):
        # ... (código do menu como estava) ...
        menubar = tkinter.Menu(self.controller); menu_sistema = tkinter.Menu(menubar, tearoff=0)
        menu_sistema.add_command(label="Criar Novo Usuário", command=self._criar_novo_usuario)
        menu_sistema.add_command(label="Alterar Senha", command=self._alterar_senha)
        menu_sistema.add_command(label="Gerenciar Categorias", command=lambda: self.controller.show_frame("CategoryManagementFrame"))
        menu_sistema.add_separator(); menu_sistema.add_command(label="Sair", command=self.controller._on_app_closing)
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
        # ... (como estava) ...
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.configure(command=self._on_tab_change)
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
        self._setup_cards_tab(self.tab_cards) 
        self._setup_calculations_tab(self.tab_calculations)
        self._setup_reports_tab(self.tab_reports)
        self.tab_view.set("Dashboard") 

    def _on_tab_change(self):
        # ... (como estava) ...
        selected_tab_name = self.tab_view.get()
        if selected_tab_name == "Créditos" and hasattr(self, '_load_initial_credits_data'): self._load_initial_credits_data()
        elif selected_tab_name == "Débitos" and hasattr(self, '_load_initial_debits_data'): self._load_initial_debits_data()
        elif selected_tab_name == "Cartões" and hasattr(self, '_load_and_display_cards'): 
            self._load_and_display_cards()
            if self.selected_card_id is None and hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                 self.invoice_details_block_frame.grid_remove()
    
    def _setup_dashboard_tab(self, tab):
        # ... (como estava) ...
        ctk.CTkLabel(tab, text="Conteúdo do Dashboard Aqui").pack(pady=20, padx=20)
    
    def _setup_credits_tab(self, tab_credits):
        # ... (código completo da aba de créditos como estava) ...
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
        ctk.CTkButton(filter_add_frame, text="Filtrar", width=80, command=self._on_filter_credits_button_click).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(filter_add_frame, text="Adicionar Crédito", command=self._on_add_credit_button_click).pack(side="right", padx=5, pady=5)
        self.credits_table_scrollframe = ctk.CTkScrollableFrame(credits_main_frame, label_text="Registros de Crédito")
        self.credits_table_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.credits_table_grid_container = ctk.CTkFrame(self.credits_table_scrollframe, fg_color=("gray95", "gray20"))
        self.credits_table_grid_container.pack(fill="both", expand=True)
        self.credit_col_config = [
            {"weight": 0, "minsize": 100, "text": "Data", "anchor": "w"}, {"weight": 0, "minsize": 120, "text": "Valor", "anchor": "e"},
            {"weight": 1, "minsize": 130, "text": "Categoria", "anchor": "w"}, {"weight": 2, "minsize": 150, "text": "Observação", "anchor": "w"},
            {"weight": 0, "minsize": 80,  "text": "Ações", "anchor": "center"}]
        for i, config in enumerate(self.credit_col_config):
            self.credits_table_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=("gray85", "gray25"), corner_radius=0)
            header_cell_frame.grid(row=0, column=i, sticky="nsew")
            ctk.CTkLabel(header_cell_frame, text=config["text"], font=ctk.CTkFont(weight="bold"), anchor=config["anchor"]).pack(padx=5, pady=5, fill="both", expand=True)
        ctk.CTkFrame(self.credits_table_grid_container, height=1, fg_color=("gray70", "gray30")).grid(row=1, column=0, columnspan=len(self.credit_col_config), sticky="ew", pady=(0,5))

    def _load_initial_credits_data(self):
        # ... (como estava) ...
        today = date.today(); start_of_month_dt = today.replace(day=1)
        if today.month == 12: end_of_month_dt = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else: end_of_month_dt = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        start_str, end_str = start_of_month_dt.strftime("%Y-%m-%d"), end_of_month_dt.strftime("%Y-%m-%d")
        if hasattr(self, 'credits_start_date_entry'):
            self.credits_start_date_entry.delete(0, ctk.END); self.credits_start_date_entry.insert(0, start_str)
            self.credits_end_date_entry.delete(0, ctk.END); self.credits_end_date_entry.insert(0, end_str)
        self._load_and_display_credits(start_str, end_str)

    def _load_and_display_credits(self, start_date=None, end_date=None):
        # ... (como estava) ...
        for i, widget in enumerate(self.credits_table_grid_container.winfo_children()):
            if widget.grid_info().get("row", 0) >= 2 : widget.destroy()
        transactions = db_manager.get_transactions('Crédito', start_date, end_date)
        if not transactions: ctk.CTkLabel(self.credits_table_grid_container, text="Nenhum crédito encontrado.").grid(row=2, column=0, columnspan=len(self.credit_col_config), pady=10); return
        current_row = 2 
        for trans_id, data_val, valor, cat_nome, obs in transactions:
            fg = ("gray98", "gray22") if current_row % 2 == 0 else ("gray92", "gray18")
            details = [(data_val,0), (f"R$ {valor:.2f}",1), (cat_nome,2), (obs,3)]
            for col, (txt,c_idx) in enumerate(details):
                cf = ctk.CTkFrame(self.credits_table_grid_container, fg_color=fg, corner_radius=0); cf.grid(row=current_row,column=col,sticky="nsew")
                wl = self.credit_col_config[c_idx]["minsize"]-10 if c_idx==3 else 0
                ctk.CTkLabel(cf,text=txt,anchor=self.credit_col_config[c_idx]["anchor"],wraplength=wl if wl>0 else 0,justify="left").pack(padx=5,pady=3,fill="both",expand=True)
            acf = ctk.CTkFrame(self.credits_table_grid_container,fg_color=fg,corner_radius=0); acf.grid(row=current_row,column=4,sticky="nsew")
            acf.grid_columnconfigure(0,weight=1); acf.grid_columnconfigure(1,weight=1); acf.grid_rowconfigure(0,weight=1)
            ctk.CTkButton(acf,text="✎",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=trans_id:self._on_edit_credit_button_click(i)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(acf,text="✕",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=trans_id,d=obs:self._confirm_delete_credit(i,d)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            current_row+=1

    def _on_filter_credits_button_click(self):
        # ... (como estava) ...
        s,e = self.credits_start_date_entry.get(), self.credits_end_date_entry.get()
        try: datetime.strptime(s,"%Y-%m-%d"); datetime.strptime(e,"%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro","Formato de Data inválido.",parent=self.controller); return
        self._load_and_display_credits(s,e)
        
    def _on_add_credit_button_click(self):
        # ... (como estava) ...
        if hasattr(self,'dialog_add_edit_credit') and self.dialog_add_edit_credit and self.dialog_add_edit_credit.winfo_exists(): self.dialog_add_edit_credit.focus(); return
        self.dialog_add_edit_credit = AddEditCreditDialog(self.controller, self._on_filter_credits_button_click)

    def _on_edit_credit_button_click(self, transaction_id: int):
        # ... (como estava) ...
        data = db_manager.get_transaction_by_id(transaction_id)
        if data:
            if hasattr(self,'dialog_add_edit_credit') and self.dialog_add_edit_credit and self.dialog_add_edit_credit.winfo_exists(): self.dialog_add_edit_credit.focus(); return
            self.dialog_add_edit_credit = AddEditCreditDialog(self.controller, self._on_filter_credits_button_click, data)
        else: messagebox.showerror("Erro",f"Crédito ID {transaction_id} não encontrado.",parent=self.controller)

    def _confirm_delete_credit(self, transaction_id: int, transaction_description: str):
        # ... (como estava) ...
        desc=(transaction_description[:30]+'...') if len(transaction_description)>30 else transaction_description
        if messagebox.askyesno("Confirmar",f"Excluir crédito:\n'{desc}'?",parent=self.controller):
            if db_manager.delete_transaction(transaction_id): messagebox.showinfo("Sucesso","Crédito excluído.",parent=self.controller); self._on_filter_credits_button_click()
            else: messagebox.showerror("Erro","Não foi possível excluir.",parent=self.controller)

    def _setup_debits_tab(self, tab_debits):
        # ... (código completo da aba de débitos como estava) ...
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
        ctk.CTkButton(filter_add_frame, text="Filtrar", width=80, command=self._on_filter_debits_button_click).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(filter_add_frame, text="Adicionar Débito", command=self._on_add_debit_button_click).pack(side="right", padx=5, pady=5)
        self.debits_table_scrollframe = ctk.CTkScrollableFrame(debits_main_frame, label_text="Registros de Débito")
        self.debits_table_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.debits_table_grid_container = ctk.CTkFrame(self.debits_table_scrollframe, fg_color=("gray95", "gray20"))
        self.debits_table_grid_container.pack(fill="both", expand=True)
        self.debit_col_config = self.credit_col_config 
        for i, config in enumerate(self.debit_col_config):
            self.debits_table_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_cell_frame = ctk.CTkFrame(self.debits_table_grid_container, fg_color=("gray85", "gray25"), corner_radius=0)
            header_cell_frame.grid(row=0, column=i, sticky="nsew")
            ctk.CTkLabel(header_cell_frame, text=config["text"], font=ctk.CTkFont(weight="bold"), anchor=config["anchor"]).pack(padx=5, pady=5, fill="both", expand=True)
        ctk.CTkFrame(self.debits_table_grid_container, height=1, fg_color=("gray70", "gray30")).grid(row=1, column=0, columnspan=len(self.debit_col_config), sticky="ew", pady=(0,5))

    def _load_initial_debits_data(self):
        # ... (como estava) ...
        today = date.today(); start_of_month_dt = today.replace(day=1)
        if today.month == 12: end_of_month_dt = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else: end_of_month_dt = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        start_str, end_str = start_of_month_dt.strftime("%Y-%m-%d"), end_of_month_dt.strftime("%Y-%m-%d")
        if hasattr(self, 'debits_start_date_entry'):
            self.debits_start_date_entry.delete(0, ctk.END); self.debits_start_date_entry.insert(0, start_str)
            self.debits_end_date_entry.delete(0, ctk.END); self.debits_end_date_entry.insert(0, end_str)
        self._load_and_display_debits(start_str, end_str)

    def _load_and_display_debits(self, start_date=None, end_date=None):
        # ... (como estava) ...
        for i, widget in enumerate(self.debits_table_grid_container.winfo_children()):
            if widget.grid_info().get("row", 0) >= 2 : widget.destroy()
        transactions = db_manager.get_transactions('Débito', start_date, end_date)
        if not transactions: ctk.CTkLabel(self.debits_table_grid_container, text="Nenhum débito encontrado.").grid(row=2, column=0, columnspan=len(self.debit_col_config), pady=10); return
        current_row = 2
        for trans_id,data_val,valor,cat_nome,obs in transactions:
            fg = ("gray98","gray22") if current_row%2==0 else ("gray92","gray18")
            details = [(data_val,0), (f"R$ {valor:.2f}",1), (cat_nome,2), (obs,3)]
            for col,(txt,c_idx) in enumerate(details):
                cf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=fg,corner_radius=0); cf.grid(row=current_row,column=col,sticky="nsew")
                wl=self.debit_col_config[c_idx]["minsize"]-10 if c_idx==3 else 0
                ctk.CTkLabel(cf,text=txt,anchor=self.debit_col_config[c_idx]["anchor"],wraplength=wl if wl>0 else 0,justify="left").pack(padx=5,pady=3,fill="both",expand=True)
            acf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=fg,corner_radius=0); acf.grid(row=current_row,column=4,sticky="nsew")
            acf.grid_columnconfigure(0,weight=1); acf.grid_columnconfigure(1,weight=1); acf.grid_rowconfigure(0,weight=1)
            ctk.CTkButton(acf,text="✎",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=trans_id:self._on_edit_debit_button_click(i)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(acf,text="✕",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=trans_id,d=obs:self._confirm_delete_debit(i,d)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            current_row+=1

    def _on_filter_debits_button_click(self):
        # ... (como estava) ...
        s,e = self.debits_start_date_entry.get(), self.debits_end_date_entry.get()
        try: datetime.strptime(s,"%Y-%m-%d"); datetime.strptime(e,"%Y-%m-%d")
        except ValueError: messagebox.showerror("Erro","Formato de Data inválido.",parent=self.controller); return
        self._load_and_display_debits(s,e)

    def _on_add_debit_button_click(self):
        # ... (como estava) ...
        if hasattr(self,'dialog_add_edit_debit') and self.dialog_add_edit_debit and self.dialog_add_edit_debit.winfo_exists(): self.dialog_add_edit_debit.focus(); return
        self.dialog_add_edit_debit = AddEditDebitDialog(self.controller, self._on_filter_debits_button_click)
    
    def _on_edit_debit_button_click(self, transaction_id: int):
        # ... (como estava) ...
        data = db_manager.get_transaction_by_id(transaction_id)
        if data:
            if hasattr(self,'dialog_add_edit_debit') and self.dialog_add_edit_debit and self.dialog_add_edit_debit.winfo_exists(): self.dialog_add_edit_debit.focus(); return
            self.dialog_add_edit_debit = AddEditDebitDialog(self.controller, self._on_filter_debits_button_click, data)
        else: messagebox.showerror("Erro",f"Débito ID {transaction_id} não encontrado.",parent=self.controller)

    def _confirm_delete_debit(self, transaction_id: int, transaction_description: str):
        # ... (como estava) ...
        desc=(transaction_description[:30]+'...') if len(transaction_description)>30 else transaction_description
        if messagebox.askyesno("Confirmar",f"Excluir débito:\n'{desc}'?",parent=self.controller):
            s,m = db_manager.delete_transaction(transaction_id) 
            if s: messagebox.showinfo("Sucesso","Débito excluído.",parent=self.controller); self._on_filter_debits_button_click()
            else: messagebox.showerror("Erro","Não foi possível excluir.",parent=self.controller)

    # --- ABA CARTÕES ---
    def _setup_cards_tab(self, tab_cards):
        cards_main_frame = ctk.CTkFrame(tab_cards, fg_color="transparent")
        cards_main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        action_buttons_frame = ctk.CTkFrame(cards_main_frame)
        action_buttons_frame.pack(fill="x", pady=(0, 10), padx=5, anchor="nw")
        self.add_card_button = ctk.CTkButton(action_buttons_frame, text="Adicionar Cartão", command=self._on_add_card_button_click)
        self.add_card_button.pack(side="left", padx=5, pady=5)
        self.edit_card_button = ctk.CTkButton(action_buttons_frame, text="Editar Cartão", command=self._on_edit_card_button_click, state="disabled")
        self.edit_card_button.pack(side="left", padx=5, pady=5)
        self.remove_card_button = ctk.CTkButton(action_buttons_frame, text="Remover Cartão", command=self._on_remove_card_button_click, state="disabled")
        self.remove_card_button.pack(side="left", padx=5, pady=5)

        cards_content_frame = ctk.CTkFrame(cards_main_frame, fg_color="transparent")
        cards_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        cards_content_frame.grid_columnconfigure(0, weight=1) 
        cards_content_frame.grid_columnconfigure(1, weight=2) 
        cards_content_frame.grid_rowconfigure(0, weight=1)    

        cards_list_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17"))
        cards_list_block_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5), pady=5)
        ctk.CTkLabel(cards_list_block_frame, text="Meus Cartões", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=10, anchor="nw")
        self.cards_list_scrollframe = ctk.CTkScrollableFrame(cards_list_block_frame, label_text="", fg_color="transparent")
        self.cards_list_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.cards_list_grid_container = ctk.CTkFrame(self.cards_list_scrollframe, fg_color="transparent")
        self.cards_list_grid_container.pack(fill="x", expand=True) 
        self.card_list_col_config = [
            {"weight": 1, "minsize": 100, "text": "Nome", "anchor": "w"},
            {"weight": 1, "minsize": 80,  "text": "Bandeira", "anchor": "w"} # Removido Banco
            # Adicionaremos Ações aqui para os cartões também? Ou a seleção já é a ação?
        ]
        for i, config in enumerate(self.card_list_col_config):
            self.cards_list_grid_container.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])
            header_label = ctk.CTkLabel(self.cards_list_grid_container, text=config["text"], 
                                        font=ctk.CTkFont(weight="bold"), anchor=config["anchor"],
                                        fg_color=("gray80", "gray25"), padx=5, pady=3)
            header_label.grid(row=0, column=i, padx=(0,1 if i < len(self.card_list_col_config)-1 else 0), pady=(0,1), sticky="ew")
        
        # Bloco da Direita: Detalhes e Faturas
        self.invoice_details_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17"))
        self.invoice_details_block_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=5)
        
        # Container para as abas de ano
        self.year_tab_view_container = ctk.CTkFrame(self.invoice_details_block_frame, fg_color="transparent", height=60) # Altura para as abas
        self.year_tab_view_container.pack(pady=(10,0), padx=10, fill="x", anchor="n")
        self.year_tab_view_container.pack_propagate(False) # Impede que o TabView encolha o container
        self.year_tab_view = None 

        self.invoice_details_scrollframe = ctk.CTkScrollableFrame(self.invoice_details_block_frame, label_text="Faturas Mensais", fg_color="transparent")
        self.invoice_details_scrollframe.pack(fill="both", expand=True, padx=5, pady=10)
        self.invoice_details_grid_container = ctk.CTkFrame(self.invoice_details_scrollframe, fg_color="transparent")
        self.invoice_details_grid_container.pack(fill="both", expand=True)

        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        for i, month_name in enumerate(months): 
            self.invoice_details_grid_container.grid_columnconfigure(i, weight=1, minsize=60)
            month_header_frame = ctk.CTkFrame(self.invoice_details_grid_container, fg_color=("gray80", "gray25"), corner_radius=0)
            month_header_frame.grid(row=0, column=i, padx=(0,1 if i < len(months)-1 else 0), pady=(0,1), sticky="nsew")
            ctk.CTkLabel(month_header_frame, text=month_name, font=ctk.CTkFont(weight="bold")).pack(padx=2, pady=5, fill="both", expand=True)
        
        self.invoice_details_block_frame.grid_remove() # Oculta o painel direito inicialmente

    def _on_add_card_button_click(self):
        if hasattr(self, 'dialog_add_edit_card') and self.dialog_add_edit_card and self.dialog_add_edit_card.winfo_exists():
            self.dialog_add_edit_card.focus(); return
        self.dialog_add_edit_card = AddEditCardDialog(master=self.controller, controller=self.controller, 
                                                      refresh_callback=self._load_and_display_cards, card_data=None)

    def _on_edit_card_button_click(self):
        if self.selected_card_id is None: messagebox.showwarning("Atenção", "Selecione um cartão para editar.", parent=self.controller); return
        card_data = db_manager.get_card_by_id(self.selected_card_id)
        if card_data:
            if hasattr(self, 'dialog_add_edit_card') and self.dialog_add_edit_card and self.dialog_add_edit_card.winfo_exists():
                self.dialog_add_edit_card.focus(); return
            self.dialog_add_edit_card = AddEditCardDialog(master=self.controller, controller=self.controller,
                                                          refresh_callback=self._load_and_display_cards, card_data=card_data)
        else: messagebox.showerror("Erro", "Não foi possível carregar os dados do cartão.", parent=self.controller)

    def _on_remove_card_button_click(self):
        if self.selected_card_id is None: messagebox.showwarning("Atenção", "Selecione um cartão para remover.", parent=self.controller); return
        card_data = db_manager.get_card_by_id(self.selected_card_id)
        if not card_data: messagebox.showerror("Erro", "Cartão não encontrado.", parent=self.controller); return
        
        # A mensagem de confirmação foi atualizada para ser mais clara sobre o impacto em transações
        confirm_msg = (f"Tem certeza que deseja excluir o cartão '{card_data['nome']}'?\n"
                       "Todas as faturas associadas serão excluídas (ON DELETE CASCADE).\n"
                       "Transações existentes vinculadas a este cartão terão o 'cartao_id' definido como NULO.\n"
                       "Esta ação não pode ser desfeita.")
        confirm = messagebox.askyesno("Confirmar Exclusão", confirm_msg, parent=self.controller)
        if confirm:
            success, message = db_manager.delete_card(self.selected_card_id)
            if success:
                messagebox.showinfo("Sucesso", message, parent=self.controller)
                self.selected_card_id = None
                self.edit_card_button.configure(state="disabled")
                self.remove_card_button.configure(state="disabled")
                self._load_and_display_cards() # Atualiza a lista
                self._clear_invoice_details_panel() # Limpa e oculta painel direito
            else:
                messagebox.showerror("Erro ao Excluir", message, parent=self.controller)

    def _load_and_display_cards(self):
        for widget in self.cards_list_grid_container.winfo_children():
            if widget.grid_info().get("row",0)>0: widget.destroy()
        
        cards = db_manager.get_all_cards() # Retorna lista de dicts com id, nome, bandeira, cor
        if not cards:
            ctk.CTkLabel(self.cards_list_grid_container,text="Nenhum cartão cadastrado.").grid(row=1,column=0,columnspan=len(self.card_list_col_config),pady=10)
            self.edit_card_button.configure(state="disabled"); self.remove_card_button.configure(state="disabled")
            self._clear_invoice_details_panel(); self.selected_card_id = None
            return

        current_row=1
        first_card_in_list_data = cards[0] if cards else None # Pega o dict do primeiro cartão
        newly_selected_row_frame_ref = None

        for card_data in cards: # card_data é um dicionário
            card_color = card_data.get('cor', ("gray90", "gray25")) # Cor de fundo da linha
            # Para "leve transparência", usamos cores mais claras ou a cor do tema
            # Se a cor do cartão for muito escura, o texto pode precisar ser claro
            # Usaremos a cor do cartão como fundo da linha.
            card_row_frame=ctk.CTkFrame(self.cards_list_grid_container, corner_radius=3, fg_color=card_color)
            card_row_frame.grid(row=current_row,column=0,columnspan=len(self.card_list_col_config),sticky="ew",pady=(0,2),ipady=1) # ipady para altura interna
            
            for i, config in enumerate(self.card_list_col_config): 
                card_row_frame.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])

            details_to_display = [card_data.get('nome','-'), card_data.get('bandeira','-')] # Removido Banco
            
            for col_idx, text_to_display in enumerate(details_to_display):
                anchor_val = self.card_list_col_config[col_idx]["anchor"]
                # Determina a cor do texto baseada na luminosidade da cor de fundo do cartão
                # (Implementação simples: se a cor for escura, texto branco, senão texto padrão)
                # Isso é complexo de fazer perfeitamente sem uma biblioteca de cores.
                # Por enquanto, usamos a cor de texto padrão do tema.
                # O usuário deve escolher cores de cartão que funcionem com o texto padrão.
                text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"]

                item_label = ctk.CTkButton(card_row_frame, text=text_to_display, anchor=anchor_val,
                                           fg_color="transparent", text_color=text_color, hover=False,
                                           command=lambda c_id=card_data['id'], r_frame=card_row_frame: self._on_card_selected(c_id, r_frame))
                item_label.grid(row=0, column=col_idx, padx=5, pady=0, sticky="ew")
            
            if self.selected_card_id == card_data['id']: newly_selected_row_frame_ref = card_row_frame
            current_row+=1
        
        if not self.selected_card_id and first_card_in_list_data:
            first_row_widget = next((c for c in self.cards_list_grid_container.winfo_children() if isinstance(c,ctk.CTkFrame) and c.grid_info().get("row")==1),None)
            if first_row_widget: self._on_card_selected(first_card_in_list_data['id'], first_row_widget)
        elif newly_selected_row_frame_ref: # Se um cartão já estava selecionado, re-aplica o destaque
             self._on_card_selected(self.selected_card_id, newly_selected_row_frame_ref) # Chama para re-destacar e carregar faturas
        elif not cards : # Se a lista ficou vazia após uma exclusão
            self.edit_card_button.configure(state="disabled");self.remove_card_button.configure(state="disabled")
            self._clear_invoice_details_panel();self.selected_card_id=None


    def _on_card_selected(self, card_id, selected_widget_row_frame):
        # Limpa a cor de fundo da linha anteriormente selecionada
        if self.last_selected_card_row_frame and self.last_selected_card_row_frame.winfo_exists():
            # Pega a cor original do cartão para restaurar
            # Isso requer que a cor original seja armazenada ou que o zebrado seja reimplementado
            # Por simplicidade, vamos definir uma cor "não selecionada" que seja a cor do cartão
            if self.selected_card_id: # Se havia uma seleção anterior
                previous_card_data = db_manager.get_card_by_id(self.selected_card_id) # Busca dados do cartão anterior
                if previous_card_data:
                     self.last_selected_card_row_frame.configure(fg_color=previous_card_data.get('cor', ("gray90","gray25")))
        
        self.selected_card_id = card_id
        self.edit_card_button.configure(state="normal")
        self.remove_card_button.configure(state="normal")

        if selected_widget_row_frame and selected_widget_row_frame.winfo_exists():
             selected_widget_row_frame.configure(fg_color=("#3B8ED0", "#1F6AA5")) # Cor de destaque para a linha selecionada
             self.last_selected_card_row_frame = selected_widget_row_frame
        
        if hasattr(self, 'invoice_details_block_frame'):
            self.invoice_details_block_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=5)

        self.current_invoice_year = date.today().year 
        self._setup_year_tabs() 

    def _setup_year_tabs(self):
        if not hasattr(self, 'year_tab_view_container'): return 
        if hasattr(self, 'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists():
            self.year_tab_view.destroy()
        if not self.selected_card_id: self._clear_invoice_details_panel(); return

        self.year_tab_view = ctk.CTkTabview(self.year_tab_view_container, command=self._on_year_tab_change, height=50, border_width=1, segmented_button_selected_color=("#A9D5F5", "#1F6AA5"))
        self.year_tab_view.pack(fill="x", expand=False, pady=(0,5))
        year_now = self.current_invoice_year
        years_to_display = [str(year_now - 1), str(year_now), str(year_now + 1)]
        for year_str in years_to_display: self.year_tab_view.add(year_str)
        self.year_tab_view.set(str(year_now)) 
        self._load_and_display_invoice_details(self.selected_card_id, year_now)

    def _on_year_tab_change(self):
        if not self.selected_card_id or not hasattr(self, 'year_tab_view') or not self.year_tab_view.winfo_exists(): return 
        try:
            selected_year_str = self.year_tab_view.get() 
            if selected_year_str:
                self.current_invoice_year = int(selected_year_str)
                self._load_and_display_invoice_details(self.selected_card_id, self.current_invoice_year)
        except ValueError: print(f"Erro: Aba de ano inválida '{selected_year_str}'")
        except Exception as e: print(f"Erro em _on_year_tab_change: {e}")

    def _clear_invoice_details_panel(self): 
        if hasattr(self, 'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists():
            self.year_tab_view.destroy(); self.year_tab_view = None
        if hasattr(self, 'invoice_details_grid_container'):
            for widget in self.invoice_details_grid_container.winfo_children():
                if widget.grid_info().get("row", 0) > 0: widget.destroy()
            ctk.CTkLabel(self.invoice_details_grid_container, text="Selecione um cartão e um ano para ver as faturas.").grid(row=1, column=0, columnspan=12, pady=20)
        if hasattr(self, 'invoice_details_block_frame') and self.selected_card_id is None:
            self.invoice_details_block_frame.grid_remove()

    def _load_and_display_invoice_details(self, card_id, year):
        if not hasattr(self, 'invoice_details_grid_container'): return
        for widget in self.invoice_details_grid_container.winfo_children():
            if widget.grid_info().get("row", 0) > 0: widget.destroy()
        
        faturas = db_manager.get_faturas(card_id, year) 
        selected_card_info = db_manager.get_card_by_id(card_id)
        card_bg_color = selected_card_info.get('cor', ("gray95", "gray20")) if selected_card_info else ("gray95", "gray20")

        if not faturas or all(value == 0.0 for value in faturas.values()):
            ctk.CTkLabel(self.invoice_details_grid_container, text=f"Nenhuma fatura encontrada para {year}.").grid(row=1, column=0, columnspan=12, pady=10)
            return

        current_data_row = 1 
        months = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        for i, month_name in enumerate(months):
            month_number = i + 1
            valor_fatura = faturas.get(month_number, 0.0)
            # Usar a cor do cartão para o fundo da célula da fatura, mas mais claro/sutil
            # Esta é uma aproximação. Uma função para clarear hex seria melhor.
            # Por enquanto, vamos usar um cinza claro para as células de fatura para contraste com o texto.
            cell_bg_color = ("#E5E5E5", "#2E2E2E") # Cinza bem claro / Cinza escuro sutil
            
            invoice_value_cell_frame = ctk.CTkFrame(self.invoice_details_grid_container, 
                                                    fg_color=cell_bg_color, corner_radius=3) # Usando cor mais neutra para células
            invoice_value_cell_frame.grid(row=current_data_row, column=i, padx=1, pady=1, sticky="nsew")
            
            fatura_value_text = f"R$ {valor_fatura:.2f}"
            # Aqui é onde a edição "livre" precisará ser implementada.
            # Por enquanto, um label. Futuramente, pode ser um CTkEntry ou um botão que o revela.
            fatura_value_label = ctk.CTkLabel(invoice_value_cell_frame, text=fatura_value_text, anchor="e")
            fatura_value_label.pack(padx=5, pady=5, fill="both", expand=True)
            # Exemplo de como adicionar um botão de edição por célula:
            # edit_invoice_button = ctk.CTkButton(invoice_value_cell_frame, text="✎", width=20, height=20,
            # command=lambda c_id=card_id, y=year, m=month_number, v=valor_fatura: self._edit_single_invoice(c_id,y,m,v))
            # edit_invoice_button.pack(side="right", padx=2)
            
    # Placeholders para outras abas e callbacks de menu
    def _setup_calculations_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Cálculos Aqui"); label.pack(pady=20, padx=20)
    def _setup_reports_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Relatórios/Insights Aqui"); label.pack(pady=20, padx=20)
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário'")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha'")
    def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste'")
    def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste'")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

if __name__ == '__main__':
    # ... (bloco if __name__ == '__main__' como estava) ...
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste MainAppFrame - Aba Cartões")
            self.geometry("1200x700")
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
            self.main_frame_instance.tab_view.set("Cartões") 
        def _on_app_closing(self): print("MockAppController: Chamado _on_app_closing (Sair)"); self.destroy()
        def show_frame(self, frame_name): print(f"MockAppController: Chamado show_frame para '{frame_name}'")
    mock_app = MockAppController()
    mock_app.mainloop()

class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        
        self.dialog_add_edit_credit = None 
        self.dialog_add_edit_debit = None
        self.dialog_add_edit_card = None 
        self.selected_card_id = None 
        self.last_selected_card_row_frame = None 
        # Cor de fundo padrão para linhas não selecionadas na lista de cartões (tupla para light/dark)
        self.card_row_default_fg_color = ("gray92", "gray18") 
        self.card_row_selected_fg_color = ("#A9D5F5", "#1F6AA5") # Azul para destaque

        self.current_invoice_year = date.today().year 

        self._setup_menu()
        self._create_tabs() 

    # ... (_setup_menu, _create_tabs, _on_tab_change, _setup_dashboard_tab,
    #      métodos de Créditos e Débitos como estavam) ...
    def _setup_menu(self):
        # ... (código do menu como estava) ...
        menubar = tkinter.Menu(self.controller); menu_sistema = tkinter.Menu(menubar, tearoff=0)
        menu_sistema.add_command(label="Criar Novo Usuário", command=self._criar_novo_usuario)
        menu_sistema.add_command(label="Alterar Senha", command=self._alterar_senha)
        menu_sistema.add_command(label="Gerenciar Categorias", command=lambda: self.controller.show_frame("CategoryManagementFrame"))
        menu_sistema.add_separator(); menu_sistema.add_command(label="Sair", command=self.controller._on_app_closing)
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
        # ... (como estava) ...
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.configure(command=self._on_tab_change)
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
        self._setup_cards_tab(self.tab_cards) 
        self._setup_calculations_tab(self.tab_calculations)
        self._setup_reports_tab(self.tab_reports)
        self.tab_view.set("Dashboard") 

    def _on_tab_change(self):
        # ... (como estava) ...
        selected_tab_name = self.tab_view.get()
        if selected_tab_name == "Créditos" and hasattr(self, '_load_initial_credits_data'): self._load_initial_credits_data()
        elif selected_tab_name == "Débitos" and hasattr(self, '_load_initial_debits_data'): self._load_initial_debits_data()
        elif selected_tab_name == "Cartões" and hasattr(self, '_load_and_display_cards'): 
            self._load_and_display_cards()
            if self.selected_card_id is None and hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                 self.invoice_details_block_frame.grid_remove()
    
    def _setup_dashboard_tab(self, tab):
        # ... (como estava) ...
        ctk.CTkLabel(tab, text="Conteúdo do Dashboard Aqui").pack(pady=20, padx=20)
    
    def _setup_credits_tab(self, tab_credits):
        # ... (código completo da aba de créditos como estava) ...
        credits_main_frame = ctk.CTkFrame(tab_credits, fg_color="transparent"); credits_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        filter_add_frame = ctk.CTkFrame(credits_main_frame); filter_add_frame.pack(fill="x", pady=(0,10), padx=5)
        ctk.CTkLabel(filter_add_frame, text="Data Inicial:").pack(side="left", padx=(5,0), pady=5)
        self.credits_start_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120); self.credits_start_date_entry.pack(side="left", padx=(0,10), pady=5)
        ctk.CTkLabel(filter_add_frame, text="Data Final:").pack(side="left", padx=(5,0), pady=5)
        self.credits_end_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120); self.credits_end_date_entry.pack(side="left", padx=(0,10), pady=5)
        ctk.CTkButton(filter_add_frame, text="Filtrar", width=80, command=self._on_filter_credits_button_click).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(filter_add_frame, text="Adicionar Crédito", command=self._on_add_credit_button_click).pack(side="right", padx=5, pady=5)
        self.credits_table_scrollframe = ctk.CTkScrollableFrame(credits_main_frame, label_text="Registros de Crédito"); self.credits_table_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.credits_table_grid_container = ctk.CTkFrame(self.credits_table_scrollframe, fg_color=("gray95", "gray20")); self.credits_table_grid_container.pack(fill="both", expand=True)
        self.credit_col_config = [{"weight":0,"minsize":100,"text":"Data","anchor":"w"},{"weight":0,"minsize":120,"text":"Valor","anchor":"e"},{"weight":1,"minsize":130,"text":"Categoria","anchor":"w"},{"weight":2,"minsize":150,"text":"Observação","anchor":"w"},{"weight":0,"minsize":80,"text":"Ações","anchor":"center"}]
        for i,cfg in enumerate(self.credit_col_config):
            self.credits_table_grid_container.grid_columnconfigure(i,weight=cfg["weight"],minsize=cfg["minsize"])
            hcf=ctk.CTkFrame(self.credits_table_grid_container,fg_color=("gray85","gray25"),corner_radius=0);hcf.grid(row=0,column=i,sticky="nsew")
            ctk.CTkLabel(hcf,text=cfg["text"],font=ctk.CTkFont(weight="bold"),anchor=cfg["anchor"]).pack(padx=5,pady=5,fill="both",expand=True)
        ctk.CTkFrame(self.credits_table_grid_container,height=1,fg_color=("gray70","gray30")).grid(row=1,column=0,columnspan=len(self.credit_col_config),sticky="ew",pady=(0,5))

    def _load_initial_credits_data(self):
        # ... (como estava) ...
        today=date.today();som=today.replace(day=1)
        if som.month==12:eom=som.replace(year=som.year+1,month=1,day=1)-timedelta(days=1)
        else:eom=som.replace(month=som.month+1,day=1)-timedelta(days=1)
        s,e=som.strftime("%Y-%m-%d"),eom.strftime("%Y-%m-%d")
        if hasattr(self,'credits_start_date_entry'):
            self.credits_start_date_entry.delete(0,ctk.END);self.credits_start_date_entry.insert(0,s)
            self.credits_end_date_entry.delete(0,ctk.END);self.credits_end_date_entry.insert(0,e)
        self._load_and_display_credits(s,e)

    def _load_and_display_credits(self,start_date=None,end_date=None):
        # ... (como estava) ...
        for w in self.credits_table_grid_container.winfo_children():
            if w.grid_info().get("row",0)>=2:w.destroy()
        tx=db_manager.get_transactions('Crédito',start_date,end_date)
        if not tx:ctk.CTkLabel(self.credits_table_grid_container,text="Nenhum crédito encontrado.").grid(row=2,column=0,columnspan=len(self.credit_col_config),pady=10);return
        r=2
        for t_id,d,v,cat,o in tx:
            fg=("gray98","gray22") if r%2==0 else ("gray92","gray18")
            details=[(d,0),(f"R$ {v:.2f}",1),(cat,2),(o,3)]
            for col,(txt,c_idx) in enumerate(details):
                cf=ctk.CTkFrame(self.credits_table_grid_container,fg_color=fg,corner_radius=0);cf.grid(row=r,column=col,sticky="nsew")
                wl=self.credit_col_config[c_idx]["minsize"]-10 if c_idx==3 else 0
                ctk.CTkLabel(cf,text=txt,anchor=self.credit_col_config[c_idx]["anchor"],wraplength=wl if wl>0 else 0,justify="left").pack(padx=5,pady=3,fill="both",expand=True)
            acf=ctk.CTkFrame(self.credits_table_grid_container,fg_color=fg,corner_radius=0);acf.grid(row=r,column=4,sticky="nsew")
            acf.grid_columnconfigure(0,weight=1);acf.grid_columnconfigure(1,weight=1);acf.grid_rowconfigure(0,weight=1)
            ctk.CTkButton(acf,text="✎",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=t_id:self._on_edit_credit_button_click(i)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(acf,text="✕",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=t_id,d_txt=o:self._confirm_delete_credit(i,d_txt)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            r+=1

    def _on_filter_credits_button_click(self):
        # ... (como estava) ...
        s,e=self.credits_start_date_entry.get(),self.credits_end_date_entry.get()
        try:datetime.strptime(s,"%Y-%m-%d");datetime.strptime(e,"%Y-%m-%d")
        except ValueError:messagebox.showerror("Erro","Data inválida.",parent=self.controller);return
        self._load_and_display_credits(s,e)
    def _on_add_credit_button_click(self):
        # ... (como estava) ...
        if hasattr(self,'dialog_add_edit_credit') and self.dialog_add_edit_credit and self.dialog_add_edit_credit.winfo_exists():self.dialog_add_edit_credit.focus();return
        self.dialog_add_edit_credit=AddEditCreditDialog(self.controller,self._on_filter_credits_button_click,None)
    def _on_edit_credit_button_click(self,transaction_id):
        # ... (como estava) ...
        data=db_manager.get_transaction_by_id(transaction_id)
        if data:
            if hasattr(self,'dialog_add_edit_credit') and self.dialog_add_edit_credit and self.dialog_add_edit_credit.winfo_exists():self.dialog_add_edit_credit.focus();return
            self.dialog_add_edit_credit=AddEditCreditDialog(self.controller,self._on_filter_credits_button_click,data)
        else:messagebox.showerror("Erro",f"ID {transaction_id} não encontrado.",parent=self.controller)
    def _confirm_delete_credit(self,transaction_id,desc):
        # ... (como estava) ...
        d=(desc[:30]+'...') if len(desc)>30 else desc
        if messagebox.askyesno("Confirmar",f"Excluir crédito:\n'{d}'?",parent=self.controller):
            if db_manager.delete_transaction(transaction_id):messagebox.showinfo("Sucesso","Crédito excluído.",parent=self.controller);self._on_filter_credits_button_click()
            else:messagebox.showerror("Erro","Não foi possível excluir.",parent=self.controller)

    def _setup_debits_tab(self, tab_debits):
        # ... (código completo da aba de débitos como estava) ...
        debits_main_frame = ctk.CTkFrame(tab_debits, fg_color="transparent"); debits_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        filter_add_frame = ctk.CTkFrame(debits_main_frame); filter_add_frame.pack(fill="x", pady=(0,10), padx=5)
        ctk.CTkLabel(filter_add_frame, text="Data Inicial:").pack(side="left", padx=(5,0), pady=5)
        self.debits_start_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120); self.debits_start_date_entry.pack(side="left", padx=(0,10), pady=5)
        ctk.CTkLabel(filter_add_frame, text="Data Final:").pack(side="left", padx=(5,0), pady=5)
        self.debits_end_date_entry = ctk.CTkEntry(filter_add_frame, placeholder_text="YYYY-MM-DD", width=120); self.debits_end_date_entry.pack(side="left", padx=(0,10), pady=5)
        ctk.CTkButton(filter_add_frame, text="Filtrar", width=80, command=self._on_filter_debits_button_click).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(filter_add_frame, text="Adicionar Débito", command=self._on_add_debit_button_click).pack(side="right", padx=5, pady=5)
        self.debits_table_scrollframe = ctk.CTkScrollableFrame(debits_main_frame, label_text="Registros de Débito"); self.debits_table_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.debits_table_grid_container = ctk.CTkFrame(self.debits_table_scrollframe, fg_color=("gray95", "gray20")); self.debits_table_grid_container.pack(fill="both", expand=True)
        self.debit_col_config = self.credit_col_config 
        for i,cfg in enumerate(self.debit_col_config):
            self.debits_table_grid_container.grid_columnconfigure(i,weight=cfg["weight"],minsize=cfg["minsize"])
            hcf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=("gray85","gray25"),corner_radius=0);hcf.grid(row=0,column=i,sticky="nsew")
            ctk.CTkLabel(hcf,text=cfg["text"],font=ctk.CTkFont(weight="bold"),anchor=cfg["anchor"]).pack(padx=5,pady=5,fill="both",expand=True)
        ctk.CTkFrame(self.debits_table_grid_container,height=1,fg_color=("gray70","gray30")).grid(row=1,column=0,columnspan=len(self.debit_col_config),sticky="ew",pady=(0,5))

    def _load_initial_debits_data(self):
        # ... (como estava) ...
        today=date.today();som=today.replace(day=1)
        if som.month==12:eom=som.replace(year=som.year+1,month=1,day=1)-timedelta(days=1)
        else:eom=som.replace(month=som.month+1,day=1)-timedelta(days=1)
        s,e=som.strftime("%Y-%m-%d"),eom.strftime("%Y-%m-%d")
        if hasattr(self,'debits_start_date_entry'):
            self.debits_start_date_entry.delete(0,ctk.END);self.debits_start_date_entry.insert(0,s)
            self.debits_end_date_entry.delete(0,ctk.END);self.debits_end_date_entry.insert(0,e)
        self._load_and_display_debits(s,e)

    def _load_and_display_debits(self,start_date=None,end_date=None):
        # ... (como estava) ...
        for w in self.debits_table_grid_container.winfo_children():
            if w.grid_info().get("row",0)>=2:w.destroy()
        tx=db_manager.get_transactions('Débito',start_date,end_date)
        if not tx:ctk.CTkLabel(self.debits_table_grid_container,text="Nenhum débito.").grid(row=2,column=0,columnspan=len(self.debit_col_config),pady=10);return
        r=2
        for t_id,d_val,v,cat,o in tx:
            fg=("g98","g22") if r%2==0 else ("g92","g18")
            details=[(d_val,0),(f"R$ {v:.2f}",1),(cat,2),(o,3)]
            for col,(txt,c_idx) in enumerate(details):
                cf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=fg,corner_radius=0);cf.grid(row=r,column=col,sticky="nsew")
                wl=self.debit_col_config[c_idx]["minsize"]-10 if c_idx==3 else 0
                ctk.CTkLabel(cf,text=txt,anchor=self.debit_col_config[c_idx]["anchor"],wraplength=wl if wl>0 else 0,justify="left").pack(padx=5,pady=3,fill="both",expand=True)
            acf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=fg,corner_radius=0);acf.grid(row=r,column=4,sticky="nsew")
            acf.grid_columnconfigure(0,weight=1);acf.grid_columnconfigure(1,weight=1);acf.grid_rowconfigure(0,weight=1)
            ctk.CTkButton(acf,text="✎",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=t_id:self._on_edit_debit_button_click(i)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(acf,text="✕",width=28,height=28,fg_color="transparent",text_color=("g10","g90"),hover_color=("g70","g30"),command=lambda i=t_id,d_txt=o:self._confirm_delete_debit(i,d_txt)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            r+=1

    def _on_filter_debits_button_click(self):
        # ... (como estava) ...
        s,e=self.debits_start_date_entry.get(),self.debits_end_date_entry.get()
        try:datetime.strptime(s,"%Y-%m-%d");datetime.strptime(e,"%Y-%m-%d")
        except ValueError:messagebox.showerror("Erro","Data inválida.",parent=self.controller);return
        self._load_and_display_debits(s,e)
    def _on_add_debit_button_click(self):
        # ... (como estava) ...
        if hasattr(self,'dialog_add_edit_debit') and self.dialog_add_edit_debit and self.dialog_add_edit_debit.winfo_exists():self.dialog_add_edit_debit.focus();return
        self.dialog_add_edit_debit=AddEditDebitDialog(self.controller,self._on_filter_debits_button_click)
    def _on_edit_debit_button_click(self,transaction_id):
        # ... (como estava) ...
        data=db_manager.get_transaction_by_id(transaction_id)
        if data:
            if hasattr(self,'dialog_add_edit_debit') and self.dialog_add_edit_debit and self.dialog_add_edit_debit.winfo_exists():self.dialog_add_edit_debit.focus();return
            self.dialog_add_edit_debit=AddEditDebitDialog(self.controller,self._on_filter_debits_button_click,data)
        else:messagebox.showerror("Erro",f"ID {transaction_id} não encontrado.",parent=self.controller)
    def _confirm_delete_debit(self,transaction_id,desc):
        # ... (como estava) ...
        d=(desc[:30]+'...') if len(desc)>30 else desc
        if messagebox.askyesno("Confirmar",f"Excluir débito:\n'{d}'?",parent=self.controller):
            s,m=db_manager.delete_transaction(transaction_id)
            if s:messagebox.showinfo("Sucesso","Débito excluído.",parent=self.controller);self._on_filter_debits_button_click()
            else:messagebox.showerror("Erro","Não foi possível excluir.",parent=self.controller)

    # --- ABA CARTÕES ---
    def _setup_cards_tab(self, tab_cards):
        # ... (como estava no Passo 47, com a correção da visibilidade do painel direito) ...
        cards_main_frame = ctk.CTkFrame(tab_cards, fg_color="transparent"); cards_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        action_buttons_frame = ctk.CTkFrame(cards_main_frame); action_buttons_frame.pack(fill="x", pady=(0, 10), padx=5, anchor="nw")
        self.add_card_button = ctk.CTkButton(action_buttons_frame, text="Adicionar Cartão", command=self._on_add_card_button_click); self.add_card_button.pack(side="left", padx=5, pady=5)
        self.edit_card_button = ctk.CTkButton(action_buttons_frame, text="Editar Cartão", command=self._on_edit_card_button_click, state="disabled"); self.edit_card_button.pack(side="left", padx=5, pady=5)
        self.remove_card_button = ctk.CTkButton(action_buttons_frame, text="Remover Cartão", command=self._on_remove_card_button_click, state="disabled"); self.remove_card_button.pack(side="left", padx=5, pady=5)
        cards_content_frame = ctk.CTkFrame(cards_main_frame, fg_color="transparent"); cards_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        cards_content_frame.grid_columnconfigure(0, weight=1); cards_content_frame.grid_columnconfigure(1, weight=2); cards_content_frame.grid_rowconfigure(0, weight=1)    
        cards_list_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17")); cards_list_block_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5), pady=5)
        ctk.CTkLabel(cards_list_block_frame, text="Meus Cartões", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10, padx=10, anchor="nw")
        self.cards_list_scrollframe = ctk.CTkScrollableFrame(cards_list_block_frame, label_text="", fg_color="transparent"); self.cards_list_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.cards_list_grid_container = ctk.CTkFrame(self.cards_list_scrollframe, fg_color="transparent"); self.cards_list_grid_container.pack(fill="x", expand=True)
        self.card_list_col_config = [{"weight":1,"minsize":100,"text":"Nome","anchor":"w"},{"weight":1,"minsize":80,"text":"Bandeira","anchor":"w"}] # Removido Banco
        for i,cfg in enumerate(self.card_list_col_config):
            self.cards_list_grid_container.grid_columnconfigure(i,weight=cfg["weight"],minsize=cfg["minsize"])
            h_lbl=ctk.CTkLabel(self.cards_list_grid_container,text=cfg["text"],font=ctk.CTkFont(weight="bold"),anchor=cfg["anchor"],fg_color=("gray80","gray25"),padx=5,pady=3)
            h_lbl.grid(row=0,column=i,padx=(0,1 if i<len(self.card_list_col_config)-1 else 0),pady=(0,1),sticky="ew")
        
        self.invoice_details_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17")) # Cor de fundo padrão para o bloco
        self.invoice_details_block_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=5)
        self.invoice_details_block_frame.grid_remove() # Começa oculto
        
        self.year_tab_view_container = ctk.CTkFrame(self.invoice_details_block_frame, fg_color="transparent", height=60); self.year_tab_view_container.pack(pady=(10,5), padx=10, fill="x", anchor="n"); self.year_tab_view_container.pack_propagate(False); self.year_tab_view = None 
        self.invoice_details_scrollframe = ctk.CTkScrollableFrame(self.invoice_details_block_frame, label_text="Faturas Mensais", fg_color="transparent"); self.invoice_details_scrollframe.pack(fill="both", expand=True, padx=5, pady=10)
        self.invoice_details_grid_container = ctk.CTkFrame(self.invoice_details_scrollframe, fg_color="transparent"); self.invoice_details_grid_container.pack(fill="both", expand=True)
        months = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        for i,m_name in enumerate(months):
            self.invoice_details_grid_container.grid_columnconfigure(i,weight=1,minsize=60)
            mhf=ctk.CTkFrame(self.invoice_details_grid_container,fg_color=("gray80","gray25"),corner_radius=0);mhf.grid(row=0,column=i,padx=(0,1 if i<len(months)-1 else 0),pady=(0,1),sticky="nsew")
            ctk.CTkLabel(mhf,text=m_name,font=ctk.CTkFont(weight="bold")).pack(padx=2,pady=5,fill="both",expand=True)
        self._clear_invoice_details_panel() 

    def _on_add_card_button_click(self):
        # ... (como estava) ...
        if hasattr(self,'dialog_add_edit_card') and self.dialog_add_edit_card and self.dialog_add_edit_card.winfo_exists():self.dialog_add_edit_card.focus();return
        self.dialog_add_edit_card=AddEditCardDialog(self.controller,self.controller,self._load_and_display_cards,None)
    
    def _on_edit_card_button_click(self):
        # ... (como estava) ...
        if self.selected_card_id is None:messagebox.showwarning("Atenção","Selecione um cartão.",parent=self.controller);return
        card_data=db_manager.get_card_by_id(self.selected_card_id)
        if card_data:
            if hasattr(self,'dialog_add_edit_card') and self.dialog_add_edit_card and self.dialog_add_edit_card.winfo_exists():self.dialog_add_edit_card.focus();return
            self.dialog_add_edit_card=AddEditCardDialog(self.controller,self.controller,self._load_and_display_cards,card_data)
        else:messagebox.showerror("Erro","Não foi possível carregar.",parent=self.controller)

    def _on_remove_card_button_click(self):
        # ... (como estava) ...
        if self.selected_card_id is None:messagebox.showwarning("Atenção","Selecione um cartão.",parent=self.controller);return
        card_data=db_manager.get_card_by_id(self.selected_card_id)
        if not card_data:messagebox.showerror("Erro","Cartão não encontrado.",parent=self.controller);return
        msg=f"Excluir cartão '{card_data['nome']}'?";
        if messagebox.askyesno("Confirmar",msg,parent=self.controller):
            s,m=db_manager.delete_card(self.selected_card_id)
            if s:messagebox.showinfo("Sucesso",m,parent=self.controller);self.selected_card_id=None;self._load_and_display_cards()
            else:messagebox.showerror("Erro",m,parent=self.controller)

    def _load_and_display_cards(self):
        for w in self.cards_list_grid_container.winfo_children():
            if w.grid_info().get("row",0)>0:w.destroy()
        
        current_selection_id_before_reload = self.selected_card_id
        cards = db_manager.get_all_cards()

        if not cards:
            ctk.CTkLabel(self.cards_list_grid_container,text="Nenhum cartão cadastrado.").grid(row=1,column=0,columnspan=len(self.card_list_col_config),pady=10)
            self.edit_card_button.configure(state="disabled"); self.remove_card_button.configure(state="disabled")
            self._clear_invoice_details_panel(); self.selected_card_id = None
            if hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                self.invoice_details_block_frame.grid_remove() # Oculta se não há cartões
            return

        current_row=1
        first_card_in_list_data = cards[0] if cards else None
        card_to_reselect_frame_ref = None

        for card_data in cards: # card_data é um dicionário {id, nome, bandeira, cor}
            # --- COR DA LINHA DO CARTÃO VOLTA A SER PADRÃO/ZEBRADO ---
            row_fg_color = self.card_row_default_fg_color # Cor padrão definida no __init__
            if current_row % 2 == 0: # Efeito zebrado simples
                 row_fg_color = ("gray98", "gray22") 
            
            card_row_frame=ctk.CTkFrame(self.cards_list_grid_container,corner_radius=3, fg_color=row_fg_color)
            card_row_frame.original_bg_color = row_fg_color # Armazena a cor padrão da linha
            card_row_frame.grid(row=current_row,column=0,columnspan=len(self.card_list_col_config),sticky="ew",pady=(0,1),ipady=2)
            
            for i, config in enumerate(self.card_list_col_config): 
                card_row_frame.grid_columnconfigure(i, weight=config["weight"], minsize=config["minsize"])

            details_to_display = [card_data.get('nome','-'), card_data.get('bandeira','-')]
            text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"] # Cor de texto padrão do tema
            
            for col_idx, text_val in enumerate(details_to_display):
                anchor_val = self.card_list_col_config[col_idx]["anchor"]
                item_label = ctk.CTkButton(card_row_frame, text=text_val, anchor=anchor_val,
                                           fg_color="transparent", text_color=text_color, hover=False,
                                           command=lambda c_id=card_data['id'], r_frame=card_row_frame: self._on_card_selected(c_id, r_frame))
                item_label.grid(row=0, column=col_idx, padx=5, pady=0, sticky="ew")
            
            if current_selection_id_before_reload == card_data['id']: 
                card_to_reselect_frame_ref = card_row_frame
            current_row+=1
        
        if card_to_reselect_frame_ref: # Se um cartão já estava selecionado, re-aplica o destaque
            self._on_card_selected(current_selection_id_before_reload, card_to_reselect_frame_ref)
        elif first_card_in_list_data: # Senão, seleciona o primeiro da lista se houver
            first_row_widget = next((c for c in self.cards_list_grid_container.winfo_children() if isinstance(c,ctk.CTkFrame) and c.grid_info().get("row")==1),None)
            if first_row_widget: self._on_card_selected(first_card_in_list_data['id'], first_row_widget)
        else: # Se a lista ficou vazia (nenhum cartão)
             self.edit_card_button.configure(state="disabled");self.remove_card_button.configure(state="disabled")
             self._clear_invoice_details_panel();self.selected_card_id=None
             if hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                self.invoice_details_block_frame.grid_remove()


    def _on_card_selected(self, card_id, selected_widget_row_frame):
        # Restaura a cor original da linha anteriormente selecionada
        if self.last_selected_card_row_frame and self.last_selected_card_row_frame.winfo_exists():
            if hasattr(self.last_selected_card_row_frame, 'original_bg_color'):
                self.last_selected_card_row_frame.configure(fg_color=self.last_selected_card_row_frame.original_bg_color)
            else: # Fallback para cor padrão se 'original_bg_color' não foi setado (improvável)
                self.last_selected_card_row_frame.configure(fg_color=self.card_row_default_fg_color)
        
        self.selected_card_id = card_id
        self.edit_card_button.configure(state="normal")
        self.remove_card_button.configure(state="normal")

        # Aplica cor de destaque à nova linha selecionada
        if selected_widget_row_frame and selected_widget_row_frame.winfo_exists():
            # Armazena a cor original ANTES de aplicar o destaque, se ainda não tiver.
            # Isso já é feito em _load_and_display_cards ao criar o frame.
            selected_widget_row_frame.configure(fg_color=self.card_row_selected_fg_color) 
            self.last_selected_card_row_frame = selected_widget_row_frame
        
        # Mostra e configura o painel de detalhes da fatura
        if hasattr(self, 'invoice_details_block_frame'):
            self.invoice_details_block_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=5)
            # O painel de faturas usa sua própria cor de fundo padrão (não a cor do cartão)
            self.invoice_details_block_frame.configure(fg_color=("gray90","gray17")) 


        self.current_invoice_year = date.today().year 
        self._setup_year_tabs() 

    def _setup_year_tabs(self):
        # ... (como estava) ...
        if not hasattr(self, 'year_tab_view_container'): return 
        if hasattr(self, 'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists(): self.year_tab_view.destroy()
        if not self.selected_card_id: self._clear_invoice_details_panel(); return
        self.year_tab_view = ctk.CTkTabview(self.year_tab_view_container,command=self._on_year_tab_change,height=50,border_width=1,segmented_button_selected_color=self.card_row_selected_fg_color) # Usa cor de destaque
        self.year_tab_view.pack(fill="x",expand=False,pady=(0,5))
        y_now=self.current_invoice_year; years_disp=[str(y_now-1),str(y_now),str(y_now+1)]
        for y_str in years_disp: self.year_tab_view.add(y_str)
        self.year_tab_view.set(str(y_now))
        self._on_year_tab_change() # Chama para carregar faturas do ano selecionado

    def _on_year_tab_change(self):
        # ... (como estava) ...
        if not self.selected_card_id or not hasattr(self,'year_tab_view') or not self.year_tab_view.winfo_exists():return
        try:
            sel_y_str=self.year_tab_view.get()
            if sel_y_str:self.current_invoice_year=int(sel_y_str);self._load_and_display_invoice_details(self.selected_card_id,self.current_invoice_year)
        except ValueError:print(f"Erro: Aba ano '{sel_y_str}'")
        except Exception as e:print(f"Erro _on_year_tab_change: {e}")

    def _clear_invoice_details_panel(self): 
        # ... (como estava, mas o invoice_details_block_frame já tem cor padrão) ...
        if hasattr(self,'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists():self.year_tab_view.destroy();self.year_tab_view=None
        if hasattr(self,'invoice_details_grid_container'):
            for w in self.invoice_details_grid_container.winfo_children():
                if w.grid_info().get("row",0)>0:w.destroy() # Mantém cabeçalho dos meses
            ctk.CTkLabel(self.invoice_details_grid_container,text="Selecione um cartão e um ano.").grid(row=1,column=0,columnspan=12,pady=20)
        if hasattr(self,'invoice_details_block_frame') and self.selected_card_id is None and self.invoice_details_block_frame.winfo_ismapped():
            self.invoice_details_block_frame.grid_remove()

    def _load_and_display_invoice_details(self,card_id,year):
        # ... (como estava, usando uma cor de célula neutra para faturas) ...
        if not hasattr(self,'invoice_details_grid_container'):return
        for w in self.invoice_details_grid_container.winfo_children():
            if w.grid_info().get("row",0)>0:w.destroy()
        faturas=db_manager.get_faturas(card_id,year)
        if not faturas or all(v==0.0 for v in faturas.values()):
            ctk.CTkLabel(self.invoice_details_grid_container,text=f"Nenhuma fatura para {year}.").grid(row=1,column=0,columnspan=12,pady=10);return
        r=1;months=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        for i,m_name in enumerate(months):
            m_num=i+1;val=faturas.get(m_num,0.0)
            cell_fg_color=("#FFFFFF","#333333") 
            cell_frame=ctk.CTkFrame(self.invoice_details_grid_container,fg_color=cell_fg_color,corner_radius=3)
            cell_frame.grid(row=r,column=i,padx=1,pady=1,sticky="nsew")
            ctk.CTkLabel(cell_frame,text=f"R$ {val:.2f}",anchor="e").pack(padx=5,pady=5,fill="both",expand=True)
            
    # Placeholders para outras abas e callbacks de menu
    def _setup_calculations_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Cálculos Aqui"); label.pack(pady=20, padx=20)
    def _setup_reports_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Relatórios/Insights Aqui"); label.pack(pady=20, padx=20)
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário'")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha'")
    def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste'")
    def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste'")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

if __name__ == '__main__':
    # ... (bloco if __name__ == '__main__' como estava) ...
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__(); self.title("Teste MainAppFrame - Aba Cartões"); self.geometry("1200x700"); ctk.set_appearance_mode("light")
            if not os.path.exists(db_manager.DATABASE_DIR): os.makedirs(db_manager.DATABASE_DIR)
            if os.path.exists(db_manager.DATABASE_PATH): 
                try: os.remove(db_manager.DATABASE_PATH)
                except Exception as e: print(f"Erro ao remover DB: {e}")
            db_manager.initialize_database()
            container=ctk.CTkFrame(self,fg_color="transparent"); container.pack(fill="both",expand=True)
            self.main_frame_instance = MainAppFrame(parent=container, controller=self); self.main_frame_instance.pack(fill="both",expand=True)
            self.main_frame_instance.tab_view.set("Cartões") 
        def _on_app_closing(self): self.destroy()
        def show_frame(self, name): print(f"Mock: show {name}")
    MockAppController().mainloop()

if __name__ == '__main__':
    # ... (bloco if __name__ == '__main__' como estava) ...
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste MainAppFrame - Aba Cartões")
            self.geometry("1200x700")
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
            self.main_frame_instance.tab_view.set("Cartões") 
        def _on_app_closing(self): print("MockAppController: Chamado _on_app_closing (Sair)"); self.destroy()
        def show_frame(self, frame_name): print(f"MockAppController: Chamado show_frame para '{frame_name}'")
    mock_app = MockAppController()
    mock_app.mainloop()