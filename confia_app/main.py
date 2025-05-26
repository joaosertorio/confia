# C:\Confia\confia_app\main_app_frame.py
import customtkinter as ctk
import tkinter
from tkinter import messagebox
from datetime import datetime, date, timedelta
import db_manager 
import os

# --- CLASSES DE DIÁLOGO ---
# (AddEditCreditDialog, AddEditDebitDialog, AddEditCardDialog, UpsertInvoiceDialog)
# Cole aqui as definições completas destas classes como estavam na sua última versão funcional (Passo 64).
# UpsertInvoiceDialog será usada tanto para adicionar quanto para editar faturas.

class AddEditCreditDialog(ctk.CTkToplevel): # Como no Passo 64
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
        self.resizable(False, False); self.transient(master); self.grab_set()
        dialog_main_frame = ctk.CTkFrame(self, fg_color="transparent"); dialog_main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        dialog_main_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(dialog_main_frame, text="Data:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.date_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="YYYY-MM-DD"); self.date_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.date_entry.insert(0, transaction_data['data'] if transaction_data else date.today().strftime("%Y-%m-%d"))
        ctk.CTkLabel(dialog_main_frame, text="Valor (R$):").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(dialog_main_frame, placeholder_text="Ex: 150.75"); self.value_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data: self.value_entry.insert(0, f"{transaction_data['valor']:.2f}")
        ctk.CTkLabel(dialog_main_frame, text="Categoria:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.category_var = ctk.StringVar(); credit_categories_data = db_manager.get_categories_by_type('Crédito')
        category_names = []; initial_category_name = None
        if credit_categories_data:
            for cat_id_loop, nome, cor, fixa in credit_categories_data: 
                self.categories_map[nome] = cat_id_loop; category_names.append(nome)
            if transaction_data: 
                for nome_map, id_map in self.categories_map.items():
                    if id_map == transaction_data.get('categoria_id'): initial_category_name = nome_map; break
            if category_names and not initial_category_name and not transaction_data: initial_category_name = category_names[0]
            elif not category_names: initial_category_name = "Nenhuma categoria"; category_names.append(initial_category_name)
        else: initial_category_name = "Nenhuma categoria"; category_names.append(initial_category_name)
        self.category_var.set(initial_category_name if initial_category_name else "Nenhuma categoria") 
        self.category_menu = ctk.CTkOptionMenu(dialog_main_frame, variable=self.category_var, values=category_names if category_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if not credit_categories_data or not category_names or self.category_var.get().startswith("Nenhuma categoria"): self.category_menu.configure(state="disabled")
        ctk.CTkLabel(dialog_main_frame, text="Observação:").grid(row=3, column=0, padx=5, pady=10, sticky="nw")
        self.observation_textbox = ctk.CTkTextbox(dialog_main_frame, height=100); self.observation_textbox.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if transaction_data: self.observation_textbox.insert("1.0", transaction_data['descricao'])
        button_frame = ctk.CTkFrame(self, fg_color="transparent"); button_frame.pack(pady=(20,20), padx=20, side="bottom", fill="x", anchor="e")
        ctk.CTkButton(button_frame, text="Salvar", command=self._save_action).pack(side="left", padx=(0,5))
        ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray").pack(side="left")
        if not transaction_data: self.value_entry.focus()
        else: self.observation_textbox.focus()

    def _save_action(self):
        data_str=self.date_entry.get(); valor_str=self.value_entry.get().replace(",",""); cat_nome=self.category_var.get(); obs=self.observation_textbox.get("1.0",ctk.END).strip()
        if not data_str: messagebox.showerror("Erro","Data é obrigatória.",parent=self);return
        try:datetime.strptime(data_str,"%Y-%m-%d")
        except ValueError:messagebox.showerror("Erro","Formato Data inválido.",parent=self);return
        if not valor_str:messagebox.showerror("Erro","Valor é obrigatório.",parent=self);return
        try:
            v=float(valor_str)
            if v<=0 and not self.editing_transaction_id:messagebox.showerror("Erro","Valor deve ser positivo.",parent=self);return
        except ValueError:messagebox.showerror("Erro","Valor inválido.",parent=self);return
        if cat_nome.startswith("Nenhuma categoria"):messagebox.showerror("Erro","Selecione Categoria.",parent=self);return
        cat_id=self.categories_map.get(cat_nome)
        if cat_id is None:messagebox.showerror("Erro","ID categoria não encontrado para: "+cat_nome,parent=self);return
        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id,data_str,obs,v,cat_id): 
                messagebox.showinfo("Sucesso","Crédito atualizado!",parent=self.master);self.refresh_callback();self.destroy()
            else:messagebox.showerror("Erro","Não foi possível atualizar o crédito.",parent=self)
        else:
            if db_manager.add_transaction(data_str,obs,v,'Crédito',cat_id): 
                messagebox.showinfo("Sucesso","Crédito adicionado!",parent=self.master);self.refresh_callback();self.destroy()
            else:messagebox.showerror("Erro","Não foi possível adicionar o crédito.",parent=self)

class AddEditDebitDialog(ctk.CTkToplevel): # Como no Passo 64
    def __init__(self, master, refresh_callback, transaction_data=None):
        super().__init__(master); self.refresh_callback=refresh_callback; self.categories_map={}; self.editing_transaction_id=None
        if transaction_data: self.editing_transaction_id=transaction_data.get('id'); self.title("Editar Débito")
        else: self.title("Adicionar Novo Débito")
        self.geometry("500x400"); self.resizable(False,False); self.transient(master); self.grab_set()
        df=ctk.CTkFrame(self,fg_color="transparent"); df.pack(pady=20,padx=20,fill="both",expand=True); df.grid_columnconfigure(1,weight=1)
        ctk.CTkLabel(df,text="Data:").grid(row=0,column=0,padx=5,pady=10,sticky="w")
        self.date_entry=ctk.CTkEntry(df,placeholder_text="YYYY-MM-DD"); self.date_entry.grid(row=0,column=1,padx=5,pady=10,sticky="ew")
        self.date_entry.insert(0,transaction_data['data'] if transaction_data else date.today().strftime("%Y-%m-%d"))
        ctk.CTkLabel(df,text="Valor (R$):").grid(row=1,column=0,padx=5,pady=10,sticky="w")
        self.value_entry=ctk.CTkEntry(df,placeholder_text="Ex: 70.25"); self.value_entry.grid(row=1,column=1,padx=5,pady=10,sticky="ew")
        if transaction_data:self.value_entry.insert(0,f"{transaction_data['valor']:.2f}")
        ctk.CTkLabel(df,text="Categoria:").grid(row=2,column=0,padx=5,pady=10,sticky="w")
        self.category_var=ctk.StringVar(); debit_cats=db_manager.get_categories_by_type('Débito')
        cat_names=[];i_cat_name=None
        if debit_cats:
            for _id_loop,nome,_,_ in debit_cats:
                self.categories_map[nome]=_id_loop; cat_names.append(nome)
            if transaction_data: 
                for nome_map, id_map in self.categories_map.items():
                    if id_map == transaction_data.get('categoria_id'): i_cat_name = nome_map; break
            if cat_names and not i_cat_name and not transaction_data: i_cat_name=cat_names[0]
            elif not cat_names:i_cat_name="Nenhuma categoria";cat_names.append(i_cat_name)
        else:i_cat_name="Nenhuma categoria";cat_names.append(i_cat_name)
        self.category_var.set(i_cat_name if i_cat_name else "Nenhuma categoria")
        self.category_menu=ctk.CTkOptionMenu(df,variable=self.category_var,values=cat_names if cat_names else ["Nenhuma categoria"])
        self.category_menu.grid(row=2,column=1,padx=5,pady=10,sticky="ew")
        if not debit_cats or not cat_names or self.category_var.get().startswith("Nenhuma"):self.category_menu.configure(state="disabled")
        ctk.CTkLabel(df,text="Observação:").grid(row=3,column=0,padx=5,pady=10,sticky="nw")
        self.obs_textbox=ctk.CTkTextbox(df,height=100);self.obs_textbox.grid(row=3,column=1,padx=5,pady=10,sticky="ew")
        if transaction_data:self.obs_textbox.insert("1.0",transaction_data['descricao'])
        bf=ctk.CTkFrame(self,fg_color="transparent");bf.pack(pady=(20,20),padx=20,side="bottom",fill="x",anchor="e")
        ctk.CTkButton(bf,text="Salvar",command=self._save_action).pack(side="left",padx=(0,5))
        ctk.CTkButton(bf,text="Cancelar",command=self.destroy,fg_color="gray").pack(side="left")
        if not transaction_data:self.value_entry.focus()
        else:self.obs_textbox.focus()
    def _save_action(self):
        d=self.date_entry.get();v_str=self.value_entry.get().replace(",",".");cn=self.category_var.get();o=self.obs_textbox.get("1.0",ctk.END).strip()
        if not d:messagebox.showerror("Erro","Data é obrigatória.",parent=self);return
        try:datetime.strptime(d,"%Y-%m-%d")
        except ValueError:messagebox.showerror("Erro","Formato Data inválido.",parent=self);return
        if not v_str:messagebox.showerror("Erro","Valor é obrigatório.",parent=self);return
        try:
            v=float(v_str)
            if v<=0 and not self.editing_transaction_id:messagebox.showerror("Erro","Valor deve ser positivo.",parent=self);return
        except ValueError:messagebox.showerror("Erro","Valor inválido.",parent=self);return
        if cn.startswith("Nenhuma"):messagebox.showerror("Erro","Selecione Categoria.",parent=self);return
        c_id=self.categories_map.get(cn)
        if c_id is None:messagebox.showerror("Erro","ID categoria não encontrado para: "+cn,parent=self);return
        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id,d,o,v,c_id):
                messagebox.showinfo("Sucesso","Débito atualizado!",parent=self.master);self.refresh_callback();self.destroy()
            else:messagebox.showerror("Erro","Não foi possível atualizar o débito.",parent=self)
        else:
            if db_manager.add_transaction(d,o,v,'Débito',c_id):
                messagebox.showinfo("Sucesso","Débito adicionado!",parent=self.master);self.refresh_callback();self.destroy()
            else:messagebox.showerror("Erro","Não foi possível adicionar o débito.",parent=self)

class AddEditCardDialog(ctk.CTkToplevel): # Como no Passo 60
    def __init__(self, master, controller, refresh_callback, card_data=None):
        super().__init__(master);self.controller=controller;self.refresh_callback=refresh_callback;self.editing_card_id=None
        self.card_color_map={"Azul Clássico":"#3B8ED0","Verde Esmeralda":"#2ECC71","Vermelho Rubi":"#E74C3C","Amarelo Solar":"#F1C40F","Laranja Vibrante":"#E67E22","Roxo Profundo":"#8E44AD","Cinza Grafite":"#34495E","Prata":"#BDC3C7","Turquesa":"#1ABC9C", "Preto":"#000000", "Branco":"#FFFFFF"}
        self.card_color_names=list(self.card_color_map.keys())
        self.card_flags=["Mastercard","Visa","American Express","Elo","Hipercard","Outros"]
        if card_data:self.editing_card_id=card_data.get('id');self.title("Editar Cartão")
        else:self.title("Adicionar Novo Cartão")
        self.geometry("500x300");self.resizable(False,False);self.transient(master);self.grab_set()
        df=ctk.CTkFrame(self,fg_color="transparent");df.pack(pady=20,padx=20,fill="both",expand=True);df.grid_columnconfigure(1,weight=1);df.grid_columnconfigure(2,weight=0)
        ctk.CTkLabel(df,text="Nome:").grid(row=0,column=0,padx=5,pady=10,sticky="w")
        self.name_entry=ctk.CTkEntry(df,width=300);self.name_entry.grid(row=0,column=1,columnspan=2,padx=5,pady=10,sticky="ew")
        if card_data:self.name_entry.insert(0,card_data.get('nome',''))
        ctk.CTkLabel(df,text="Bandeira:").grid(row=1,column=0,padx=5,pady=10,sticky="w")
        self.flag_var=ctk.StringVar(value=self.card_flags[0])
        if card_data and card_data.get('bandeira') in self.card_flags:self.flag_var.set(card_data.get('bandeira'))
        self.flag_menu=ctk.CTkOptionMenu(df,variable=self.flag_var,values=self.card_flags,width=300);self.flag_menu.grid(row=1,column=1,columnspan=2,padx=5,pady=10,sticky="ew")
        ctk.CTkLabel(df,text="Cor:").grid(row=2,column=0,padx=5,pady=10,sticky="w")
        def_color_name=self.card_color_names[0]
        if card_data and card_data.get('cor'):hex_to_name={v:k for k,v in self.card_color_map.items()};def_color_name=hex_to_name.get(card_data.get('cor'),self.card_color_names[0])
        self.card_color_var=ctk.StringVar(value=def_color_name)
        self.card_color_menu=ctk.CTkOptionMenu(df,variable=self.card_color_var,values=self.card_color_names,command=self._update_card_color_preview,width=230);self.card_color_menu.grid(row=2,column=1,padx=5,pady=10,sticky="ew")
        self.card_color_preview_box=ctk.CTkFrame(df,width=30,height=30,border_width=1);self.card_color_preview_box.grid(row=2,column=2,padx=(5,10),pady=10,sticky="w")
        self._update_card_color_preview()
        bf=ctk.CTkFrame(self,fg_color="transparent");bf.pack(pady=(30,20),padx=20,side="bottom",fill="x",anchor="e")
        ctk.CTkButton(bf,text="Salvar",command=self._save_action).pack(side="left",padx=(0,5))
        ctk.CTkButton(bf,text="Cancelar",command=self.destroy,fg_color="gray").pack(side="left")
        self.name_entry.focus()
    def _update_card_color_preview(self,event=None):hex_color=self.card_color_map.get(self.card_color_var.get(),"#FFF");self.card_color_preview_box.configure(fg_color=hex_color)
    def _save_action(self):
        nome=self.name_entry.get().strip();bandeira=self.flag_var.get();cor_hex=self.card_color_map.get(self.card_color_var.get(),'#808080')
        if not nome:messagebox.showerror("Erro","Nome do Cartão é obrigatório.",parent=self);return
        banco=None;limite=None;dia_f=None;dia_v=None 
        success_flag = False
        if self.editing_card_id:
            curr=db_manager.get_card_by_id(self.editing_card_id)
            if curr:banco=curr.get('banco');limite=curr.get('limite');dia_f=curr.get('dia_fechamento');dia_v=curr.get('dia_vencimento')
            if db_manager.update_card(self.editing_card_id,nome,bandeira=bandeira,cor=cor_hex,limite=limite,dia_fechamento=dia_f,dia_vencimento=dia_v,banco=banco): # Adicionado bandeira e cor
                messagebox.showinfo("Sucesso",f"Cartão '{nome}' atualizado!",parent=self.master); success_flag=True
            else:messagebox.showerror("Erro","Não foi possível atualizar o cartão.",parent=self)
        else:
            new_id = db_manager.add_card(nome=nome,bandeira=bandeira,cor=cor_hex,limite=limite,dia_fechamento=dia_f,dia_vencimento=dia_v,banco=banco) # Adicionado bandeira e cor
            if new_id:
                messagebox.showinfo("Sucesso",f"Cartão '{nome}' adicionado!",parent=self.master); success_flag=True
            else:messagebox.showerror("Erro","Não foi possível adicionar o cartão.",parent=self)
        if success_flag: self.refresh_callback(); self.destroy()

class UpsertInvoiceDialog(ctk.CTkToplevel): # Como no Passo 64
    def __init__(self, master, controller, refresh_callback, card_id, year, month=None, current_value=0.0, edit_mode=False):
        super().__init__(master)
        self.controller = controller; self.refresh_callback = refresh_callback
        self.card_id_to_affect = card_id; self.year_to_affect = year
        self.month_to_affect = month; self.current_value = current_value
        self.edit_mode = edit_mode 
        self.cards_map = {}; self.month_names_map = {"Janeiro":1, "Fevereiro":2, "Março":3, "Abril":4, "Maio":5, "Junho":6, "Julho":7, "Agosto":8, "Setembro":9, "Outubro":10, "Novembro":11, "Dezembro":12}
        self.month_numbers_map = {v: k for k, v in self.month_names_map.items()}
        card_info = db_manager.get_card_by_id(self.card_id_to_affect)
        card_name_for_title = card_info.get('nome', f"ID {self.card_id_to_affect}") if card_info else f"ID {self.card_id_to_affect}"
        if self.edit_mode and self.month_to_affect:
            month_name_str = self.month_numbers_map.get(self.month_to_affect, f"Mês {self.month_to_affect}")
            self.title(f"Editar Fatura: {card_name_for_title} - {month_name_str}/{self.year_to_affect}")
        else: self.title(f"Adicionar Fatura: {card_name_for_title}")
        self.geometry("450x350"); self.resizable(False, False); self.transient(master); self.grab_set()
        form_frame = ctk.CTkFrame(self, fg_color="transparent"); form_frame.pack(pady=20, padx=20, fill="both", expand=True)
        form_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(form_frame, text="Cartão:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        ctk.CTkLabel(form_frame, text=card_name_for_title).grid(row=0, column=1, padx=5, pady=10, sticky="ew") # Cartão não editável aqui
        ctk.CTkLabel(form_frame, text="Ano:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.year_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY"); self.year_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.year_entry.insert(0, str(self.year_to_affect))
        self.year_entry.configure(state="disabled" if self.edit_mode else "normal") # Ano desabilitado na edição
        ctk.CTkLabel(form_frame, text="Mês:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.month_var = ctk.StringVar()
        month_display_names = list(self.month_names_map.keys())
        default_month_name = self.month_numbers_map.get(self.month_to_affect) if self.edit_mode and self.month_to_affect else month_display_names[date.today().month -1]
        self.month_var.set(default_month_name)
        self.month_menu = ctk.CTkOptionMenu(form_frame, variable=self.month_var, values=month_display_names)
        self.month_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if self.edit_mode: self.month_menu.configure(state="disabled") # Mês desabilitado na edição
        ctk.CTkLabel(form_frame, text="Valor (R$):").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: 250.00"); self.value_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if self.edit_mode: self.value_entry.insert(0, f"{self.current_value:.2f}")
        bf=ctk.CTkFrame(self,fg_color="transparent");bf.pack(pady=(20,20),padx=20,side="bottom",fill="x",anchor="e")
        ctk.CTkButton(bf,text="Salvar",command=self._save_action).pack(side="left",padx=(0,5))
        ctk.CTkButton(bf,text="Cancelar",command=self.destroy,fg_color="gray").pack(side="left")
        self.value_entry.focus()
        if self.edit_mode: self.value_entry.select_range(0,ctk.END)

    def _save_action(self):
        card_id_final = self.card_id_to_affect # Cartão é fixo no contexto deste diálogo
        year_str = self.year_entry.get()
        month_nome_selecionado = self.month_var.get()
        val_str = self.value_entry.get().replace(",",".")
        try: year_final = int(year_str)
        except ValueError: messagebox.showerror("Erro", "Ano inválido.", parent=self); return
        month_final = self.month_names_map.get(month_nome_selecionado)
        if month_final is None : messagebox.showerror("Erro", "Mês inválido.", parent=self); return
        if not val_str: messagebox.showerror("Erro", "Valor é obrigatório.", parent=self); return
        try: val_final = float(val_str)
        except ValueError: messagebox.showerror("Erro", "Valor da fatura inválido.", parent=self); return

        if db_manager.upsert_fatura(card_id_final,year_final,month_final,val_final):
            messagebox.showinfo("Sucesso","Fatura salva!",parent=self.master)
            self.refresh_callback(card_id_final,year_final) 
            self.destroy()
        else: messagebox.showerror("Erro","Não foi possível salvar fatura.",parent=self)

# --- CLASSE MAINAPPFRAME ---
class MainAppFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs): # Assegura que todos os atributos de instância sejam inicializados
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self.dialog_add_edit_credit = None; self.dialog_add_edit_debit = None
        self.dialog_add_edit_card = None; self.dialog_upsert_invoice = None 
        self.selected_card_id = None; self.last_selected_card_row_frame = None 
        self.card_row_default_fg_color = ("gray92", "gray20") # Ajustado para melhor contraste no tema dark
        self.card_row_selected_fg_color = ("#3B8ED0", "#1F6AA5") 
        self.year_tab_selected_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.year_tab_selected_hover_color = ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        self.year_tab_unselected_color = ("gray75", "gray28") 
        self.year_tab_unselected_hover_color = ("gray70", "gray35")
        self.current_invoice_year = date.today().year 
        self.selected_invoice_details = None # Para {card_id, year, month, value, cell_widget}
        self.last_selected_invoice_cell_frame = None # Para destacar célula da fatura
        self.invoice_cell_selected_fg_color = ("#DDEEFF", "#2A3B4D") # Cor de destaque para célula de fatura
        self.invoice_cell_default_fg_color = ("#FFFFFF", "#333333") # Cor padrão para células de fatura

        self._setup_menu()
        self._create_tabs() 

    # ... (_setup_menu, _create_tabs, _on_tab_change, _setup_dashboard_tab,
    #      métodos de Créditos e Débitos permanecem como na sua última versão funcional estável) ...
    def _setup_menu(self):
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
        selected_tab_name = self.tab_view.get()
        if selected_tab_name == "Créditos" and hasattr(self, '_load_initial_credits_data'): self._load_initial_credits_data()
        elif selected_tab_name == "Débitos" and hasattr(self, '_load_initial_debits_data'): self._load_initial_debits_data()
        elif selected_tab_name == "Cartões" and hasattr(self, '_load_and_display_cards'): 
            self._load_and_display_cards()
            if self.selected_card_id is None and hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                 self.invoice_details_block_frame.grid_remove()
            self.selected_invoice_details = None # Limpa seleção de fatura ao mudar de aba
            if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="disabled")
            if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="disabled")
    
    def _setup_dashboard_tab(self, tab):
        ctk.CTkLabel(tab, text="Conteúdo do Dashboard Aqui").pack(pady=20, padx=20)
    
    def _setup_credits_tab(self, tab_credits):
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
        today=date.today();som=today.replace(day=1)
        if som.month==12:eom=som.replace(year=som.year+1,month=1,day=1)-timedelta(days=1)
        else:eom=som.replace(month=som.month+1,day=1)-timedelta(days=1)
        s,e=som.strftime("%Y-%m-%d"),eom.strftime("%Y-%m-%d")
        if hasattr(self,'credits_start_date_entry'):
            self.credits_start_date_entry.delete(0,ctk.END);self.credits_start_date_entry.insert(0,s)
            self.credits_end_date_entry.delete(0,ctk.END);self.credits_end_date_entry.insert(0,e)
        self._load_and_display_credits(s,e)

    def _load_and_display_credits(self,start_date=None,end_date=None):
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
            ctk.CTkButton(acf,text="✎",width=28,height=28,fg_color="transparent",text_color=("gray10","gray90"),hover_color=("gray70","gray30"),command=lambda i=t_id:self._on_edit_credit_button_click(i)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(acf,text="✕",width=28,height=28,fg_color="transparent",text_color=("gray10","gray90"),hover_color=("gray70","gray30"),command=lambda i=t_id,d_txt=o:self._confirm_delete_credit(i,d_txt)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            r+=1

    def _on_filter_credits_button_click(self):
        s,e=self.credits_start_date_entry.get(),self.credits_end_date_entry.get()
        try:datetime.strptime(s,"%Y-%m-%d");datetime.strptime(e,"%Y-%m-%d")
        except ValueError:messagebox.showerror("Erro","Data inválida.",parent=self.controller);return
        self._load_and_display_credits(s,e)
    def _on_add_credit_button_click(self):
        if hasattr(self,'dialog_add_edit_credit') and self.dialog_add_edit_credit and self.dialog_add_edit_credit.winfo_exists():self.dialog_add_edit_credit.focus();return
        self.dialog_add_edit_credit=AddEditCreditDialog(self.controller,self._on_filter_credits_button_click,None)
    def _on_edit_credit_button_click(self,transaction_id):
        data=db_manager.get_transaction_by_id(transaction_id)
        if data:
            if hasattr(self,'dialog_add_edit_credit') and self.dialog_add_edit_credit and self.dialog_add_edit_credit.winfo_exists():self.dialog_add_edit_credit.focus();return
            self.dialog_add_edit_credit=AddEditCreditDialog(self.controller,self._on_filter_credits_button_click,data)
        else:messagebox.showerror("Erro",f"ID {transaction_id} não encontrado.",parent=self.controller)
    def _confirm_delete_credit(self,transaction_id,desc):
        d=(desc[:30]+'...') if len(desc)>30 else desc
        if messagebox.askyesno("Confirmar",f"Excluir crédito:\n'{d}'?",parent=self.controller):
            if db_manager.delete_transaction(transaction_id):messagebox.showinfo("Sucesso","Crédito excluído.",parent=self.controller);self._on_filter_credits_button_click()
            else:messagebox.showerror("Erro","Não foi possível excluir.",parent=self.controller)

    def _setup_debits_tab(self, tab_debits):
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
        today=date.today();som=today.replace(day=1)
        if som.month==12:eom=som.replace(year=som.year+1,month=1,day=1)-timedelta(days=1)
        else:eom=som.replace(month=som.month+1,day=1)-timedelta(days=1)
        s,e=som.strftime("%Y-%m-%d"),eom.strftime("%Y-%m-%d")
        if hasattr(self,'debits_start_date_entry'):
            self.debits_start_date_entry.delete(0,ctk.END);self.debits_start_date_entry.insert(0,s)
            self.debits_end_date_entry.delete(0,ctk.END);self.debits_end_date_entry.insert(0,e)
        self._load_and_display_debits(s,e)

    def _load_and_display_debits(self,start_date=None,end_date=None):
        for w in self.debits_table_grid_container.winfo_children():
            if w.grid_info().get("row",0)>=2:w.destroy()
        tx=db_manager.get_transactions('Débito',start_date,end_date)
        if not tx:ctk.CTkLabel(self.debits_table_grid_container,text="Nenhum débito.").grid(row=2,column=0,columnspan=len(self.debit_col_config),pady=10);return
        r=2
        for t_id,d_val,v,cat,o in tx:
            fg=("gray98","gray22") if r%2==0 else ("gray92","gray18")
            details=[(d_val,0),(f"R$ {v:.2f}",1),(cat,2),(o,3)]
            for col,(txt,c_idx) in enumerate(details):
                cf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=fg,corner_radius=0);cf.grid(row=r,column=col,sticky="nsew")
                wl=self.debit_col_config[c_idx]["minsize"]-10 if c_idx==3 else 0
                ctk.CTkLabel(cf,text=txt,anchor=self.debit_col_config[c_idx]["anchor"],wraplength=wl if wl>0 else 0,justify="left").pack(padx=5,pady=3,fill="both",expand=True)
            acf=ctk.CTkFrame(self.debits_table_grid_container,fg_color=fg,corner_radius=0);acf.grid(row=r,column=4,sticky="nsew")
            acf.grid_columnconfigure(0,weight=1);acf.grid_columnconfigure(1,weight=1);acf.grid_rowconfigure(0,weight=1)
            ctk.CTkButton(acf,text="✎",width=28,height=28,fg_color="transparent",text_color=("gray10","gray90"),hover_color=("gray70","gray30"),command=lambda i=t_id:self._on_edit_debit_button_click(i)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(acf,text="✕",width=28,height=28,fg_color="transparent",text_color=("gray10","gray90"),hover_color=("gray70","gray30"),command=lambda i=t_id,d_txt=o:self._confirm_delete_debit(i,d_txt)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            r+=1

    def _on_filter_debits_button_click(self):
        s,e=self.debits_start_date_entry.get(),self.debits_end_date_entry.get()
        try:datetime.strptime(s,"%Y-%m-%d");datetime.strptime(e,"%Y-%m-%d")
        except ValueError:messagebox.showerror("Erro","Data inválida.",parent=self.controller);return
        self._load_and_display_debits(s,e)
    def _on_add_debit_button_click(self):
        if hasattr(self,'dialog_add_edit_debit') and self.dialog_add_edit_debit and self.dialog_add_edit_debit.winfo_exists():self.dialog_add_edit_debit.focus();return
        self.dialog_add_edit_debit=AddEditDebitDialog(self.controller,self._on_filter_debits_button_click,None)
    def _on_edit_debit_button_click(self,transaction_id):
        data=db_manager.get_transaction_by_id(transaction_id)
        if data:
            if hasattr(self,'dialog_add_edit_debit') and self.dialog_add_edit_debit and self.dialog_add_edit_debit.winfo_exists():self.dialog_add_edit_debit.focus();return
            self.dialog_add_edit_debit=AddEditDebitDialog(self.controller,self._on_filter_debits_button_click,data)
        else:messagebox.showerror("Erro",f"ID {transaction_id} não encontrado.",parent=self.controller)
    def _confirm_delete_debit(self,transaction_id,desc):
        d=(desc[:30]+'...') if len(desc)>30 else desc
        if messagebox.askyesno("Confirmar",f"Excluir débito:\n'{d}'?",parent=self.controller):
            s,m=db_manager.delete_transaction(transaction_id)
            if s:messagebox.showinfo("Sucesso","Débito excluído.",parent=self.controller);self._on_filter_debits_button_click()
            else:messagebox.showerror("Erro","Não foi possível excluir.",parent=self.controller)

    # --- ABA CARTÕES ---
    def _setup_cards_tab(self, tab_cards):
        cards_main_frame = ctk.CTkFrame(tab_cards, fg_color="transparent"); cards_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        card_action_buttons_frame = ctk.CTkFrame(cards_main_frame); card_action_buttons_frame.pack(fill="x", pady=(0, 10), padx=5, anchor="nw")
        self.add_card_button = ctk.CTkButton(card_action_buttons_frame, text="Adicionar Cartão", command=self._on_add_card_button_click); self.add_card_button.pack(side="left", padx=5, pady=5)
        self.edit_card_button = ctk.CTkButton(card_action_buttons_frame, text="Editar Cartão", command=self._on_edit_card_button_click, state="disabled"); self.edit_card_button.pack(side="left", padx=5, pady=5)
        self.remove_card_button = ctk.CTkButton(card_action_buttons_frame, text="Remover Cartão", command=self._on_remove_card_button_click, state="disabled"); self.remove_card_button.pack(side="left", padx=5, pady=5)
        cards_content_frame = ctk.CTkFrame(cards_main_frame, fg_color="transparent"); cards_content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        cards_content_frame.grid_columnconfigure(0, weight=1); cards_content_frame.grid_columnconfigure(1, weight=2); cards_content_frame.grid_rowconfigure(0, weight=1)    
        cards_list_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17")); cards_list_block_frame.grid(row=0, column=0, sticky="nsew", padx=(0,5), pady=0)
        ctk.CTkLabel(cards_list_block_frame, text="Meus Cartões", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10,5), padx=10, anchor="nw")
        self.cards_list_scrollframe = ctk.CTkScrollableFrame(cards_list_block_frame, label_text="", fg_color="transparent"); self.cards_list_scrollframe.pack(fill="both", expand=True, padx=5, pady=5)
        self.cards_list_grid_container = ctk.CTkFrame(self.cards_list_scrollframe, fg_color="transparent"); self.cards_list_grid_container.pack(fill="x", expand=True)
        
        # CORRIGIDO: self.card_list_col_config com 'minsize'
        self.card_list_col_config = [
            {"weight":1, "minsize": 120, "text":"Nome", "anchor":"w"},
            {"weight":1, "minsize": 100, "text":"Bandeira", "anchor":"w"}
        ]
        for i,cfg in enumerate(self.card_list_col_config):
            self.cards_list_grid_container.grid_columnconfigure(i,weight=cfg["weight"],minsize=cfg["minsize"])
            h_lbl=ctk.CTkLabel(self.cards_list_grid_container,text=cfg["text"],font=ctk.CTkFont(weight="bold"),anchor=cfg["anchor"],fg_color=("gray80","gray25"),padx=5,pady=3)
            h_lbl.grid(row=0,column=i,padx=(0,1 if i<len(self.card_list_col_config)-1 else 0),pady=(0,1),sticky="ew")
        
        self.invoice_details_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17"))
        self.invoice_details_block_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=0)
        self.invoice_details_block_frame.grid_remove() 
        
        # Frame para os botões de Ação da Fatura
        invoice_action_buttons_frame = ctk.CTkFrame(self.invoice_details_block_frame, fg_color="transparent")
        invoice_action_buttons_frame.pack(pady=(10,0), padx=10, fill="x", anchor="nw")
        self.add_invoice_button = ctk.CTkButton(invoice_action_buttons_frame, text="Adicionar Fatura", command=self._on_add_invoice_button_click)
        self.add_invoice_button.pack(side="left", padx=(0,5), pady=5)
        self.edit_invoice_button = ctk.CTkButton(invoice_action_buttons_frame, text="Editar Fatura", state="disabled", command=self._on_edit_invoice_button_click)
        self.edit_invoice_button.pack(side="left", padx=5, pady=5)
        self.remove_invoice_button = ctk.CTkButton(invoice_action_buttons_frame, text="Remover Fatura", state="disabled", command=self._on_remove_invoice_button_click)
        self.remove_invoice_button.pack(side="left", padx=5, pady=5)

        self.year_tab_view_container = ctk.CTkFrame(self.invoice_details_block_frame, fg_color="transparent", height=50) 
        self.year_tab_view_container.pack(pady=(5,0), padx=10, fill="x", anchor="n")
        self.year_tab_view_container.pack_propagate(False)
        self.year_tab_view = None 

        self.invoice_details_scrollframe = ctk.CTkScrollableFrame(self.invoice_details_block_frame, label_text="", fg_color="transparent")
        self.invoice_details_scrollframe.pack(fill="both", expand=True, padx=5, pady=(0,10))
        self.invoice_details_grid_container = ctk.CTkFrame(self.invoice_details_scrollframe, fg_color="transparent")
        self.invoice_details_grid_container.pack(fill="both", expand=True)

        months = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        for i,m_name in enumerate(months):
            self.invoice_details_grid_container.grid_columnconfigure(i, weight=1, minsize=70) 
            month_header_frame = ctk.CTkFrame(self.invoice_details_grid_container, fg_color=("gray80", "gray25"), corner_radius=0)
            month_header_frame.grid(row=0, column=i, padx=(0,1 if i < len(months)-1 else 0), pady=(0,1), sticky="nsew")
            ctk.CTkLabel(month_header_frame, text=m_name, font=ctk.CTkFont(weight="bold")).pack(padx=2, pady=5, fill="both", expand=True)
        
        self._clear_invoice_details_panel() 

    def _on_add_card_button_click(self):
        if hasattr(self,'dialog_add_edit_card') and self.dialog_add_edit_card and self.dialog_add_edit_card.winfo_exists():self.dialog_add_edit_card.focus();return
        self.dialog_add_edit_card=AddEditCardDialog(self.controller,self.controller,self._load_and_display_cards,None)
    
    def _on_edit_card_button_click(self):
        if self.selected_card_id is None:messagebox.showwarning("Atenção","Selecione um cartão.",parent=self.controller);return
        card_data=db_manager.get_card_by_id(self.selected_card_id)
        if card_data:
            if hasattr(self,'dialog_add_edit_card') and self.dialog_add_edit_card and self.dialog_add_edit_card.winfo_exists():self.dialog_add_edit_card.focus();return
            self.dialog_add_edit_card=AddEditCardDialog(self.controller,self.controller,self._load_and_display_cards,card_data)
        else:messagebox.showerror("Erro","Não foi possível carregar.",parent=self.controller)

    def _on_remove_card_button_click(self):
        if self.selected_card_id is None:messagebox.showwarning("Atenção","Selecione um cartão.",parent=self.controller);return
        card_data=db_manager.get_card_by_id(self.selected_card_id)
        if not card_data:messagebox.showerror("Erro","Cartão não encontrado.",parent=self.controller);return
        msg=f"Excluir cartão '{card_data['nome']}'?";
        if messagebox.askyesno("Confirmar",msg,parent=self.controller):
            s,m=db_manager.delete_card(self.selected_card_id)
            if s:messagebox.showinfo("Sucesso",m,parent=self.controller);self.selected_card_id=None;self._load_and_display_cards()
            else:messagebox.showerror("Erro",m,parent=self.controller)

    def _load_and_display_cards(self): # CORRIGIDO: Uso de minsize
        for w in self.cards_list_grid_container.winfo_children():
            if w.grid_info().get("row",0)>0:w.destroy()
        current_selection_id_before_reload = self.selected_card_id
        cards=db_manager.get_all_cards()
        if not cards:
            ctk.CTkLabel(self.cards_list_grid_container,text="Nenhum cartão.").grid(row=1,column=0,columnspan=len(self.card_list_col_config),pady=10)
            self.edit_card_button.configure(state="disabled");self.remove_card_button.configure(state="disabled")
            self._clear_invoice_details_panel();self.selected_card_id=None
            if hasattr(self,'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped(): self.invoice_details_block_frame.grid_remove()
            return
        r=1;first_id=cards[0]['id'] if cards else None; card_to_reselect_frame=None
        for card in cards:
            row_fg = self.card_row_default_fg_color if r%2!=0 else ("gray98","gray22")
            rf=ctk.CTkFrame(self.cards_list_grid_container,corner_radius=3,fg_color=row_fg); rf.original_bg_color = row_fg
            rf.grid(row=r,column=0,columnspan=len(self.card_list_col_config),sticky="ew",pady=(0,1),ipady=2)
            # Configura colunas DENTRO de cada frame de linha (rf)
            for i,cfg in enumerate(self.card_list_col_config):
                rf.grid_columnconfigure(i,weight=cfg["weight"],minsize=cfg["minsize"]) 
            
            details_map={"Nome":card.get('nome','-'),"Bandeira":card.get('bandeira','-')}
            for c_idx,key in enumerate(["Nome","Bandeira"]):
                item_btn=ctk.CTkButton(rf,text=details_map[key],anchor=self.card_list_col_config[c_idx]["anchor"],fg_color="transparent",text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"],hover=False,command=lambda _id=card['id'],_rf=rf:self._on_card_selected(_id,_rf))
                item_btn.grid(row=0,column=c_idx,padx=5,pady=0,sticky="ew")
            if current_selection_id_before_reload == card['id']: card_to_reselect_frame=rf
            r+=1
        if card_to_reselect_frame: self._on_card_selected(current_selection_id_before_reload,card_to_reselect_frame)
        elif first_id:
            first_rf=next((c for c in self.cards_list_grid_container.winfo_children() if isinstance(c,ctk.CTkFrame) and c.grid_info().get("row")==1),None)
            if first_rf:self._on_card_selected(first_id,first_rf)
        elif not cards : self.edit_card_button.configure(state="disabled");self.remove_card_button.configure(state="disabled");self._clear_invoice_details_panel();self.selected_card_id=None; self.invoice_details_block_frame.grid_remove()

    def _on_card_selected(self,card_id,selected_rf): # ... (sem alterações)
        if self.last_selected_card_row_frame and self.last_selected_card_row_frame.winfo_exists():
            if hasattr(self.last_selected_card_row_frame,'original_bg_color'): self.last_selected_card_row_frame.configure(fg_color=self.last_selected_card_row_frame.original_bg_color)
            else: self.last_selected_card_row_frame.configure(fg_color=self.card_row_default_fg_color) 
        self.selected_card_id=card_id;self.edit_card_button.configure(state="normal");self.remove_card_button.configure(state="normal")
        if selected_rf and selected_rf.winfo_exists():
            if not hasattr(selected_rf,'original_bg_color'): selected_rf.original_bg_color = selected_rf.cget("fg_color")
            selected_rf.configure(fg_color=self.card_row_selected_fg_color);self.last_selected_card_row_frame=selected_rf
        self.current_invoice_year = date.today().year 
        if hasattr(self,'invoice_details_block_frame'):self.invoice_details_block_frame.grid(row=0,column=1,sticky="nsew",padx=(5,0),pady=5)
        self._setup_year_tabs()

    def _setup_year_tabs(self): # ... (sem alterações)
        if not hasattr(self, 'year_tab_view_container'): return 
        if hasattr(self, 'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists():
            self.year_tab_view.destroy()
        if not self.selected_card_id: self._clear_invoice_details_panel(); return
        self.year_tab_view = ctk.CTkTabview(self.year_tab_view_container,command=self._on_year_tab_change,height=45, border_width=1,
            segmented_button_selected_color = self.year_tab_selected_color, 
            segmented_button_selected_hover_color = self.year_tab_selected_hover_color,
            segmented_button_unselected_color = self.year_tab_unselected_color,
            segmented_button_unselected_hover_color = self.year_tab_unselected_hover_color,
            fg_color = "transparent")
        self.year_tab_view.pack(fill="x",expand=False,pady=(0,5))
        y_now=self.current_invoice_year; years_disp=[str(y_now-1),str(y_now),str(y_now+1)]
        for y_str in years_disp: self.year_tab_view.add(y_str)
        self.year_tab_view.set(str(y_now))
        self._on_year_tab_change() 

    def _on_year_tab_change(self): # ... (sem alterações)
        if not self.selected_card_id or not hasattr(self,'year_tab_view') or not self.year_tab_view.winfo_exists():return
        try:
            sel_y_str=self.year_tab_view.get()
            if sel_y_str:self.current_invoice_year=int(sel_y_str);self._load_and_display_invoice_details(self.selected_card_id,self.current_invoice_year)
        except ValueError:print(f"Erro: Aba ano '{sel_y_str}'")
        except Exception as e:print(f"Erro _on_year_tab_change: {e}")

    def _clear_invoice_details_panel(self): # ... (sem alterações)
        # Limpa seleção de fatura e desabilita botões
        self.selected_invoice_details = None
        if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="disabled")
        if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="disabled")
        if hasattr(self, 'last_selected_invoice_cell_frame') and self.last_selected_invoice_cell_frame and self.last_selected_invoice_cell_frame.winfo_exists():
            self.last_selected_invoice_cell_frame.configure(border_width=0) # Remove destaque da célula
            self.last_selected_invoice_cell_frame = None

        if hasattr(self,'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists():self.year_tab_view.destroy();self.year_tab_view=None
        if hasattr(self,'invoice_details_grid_container'):
            for w in self.invoice_details_grid_container.winfo_children():
                if w.grid_info().get("row",0)>0:w.destroy() 
            ctk.CTkLabel(self.invoice_details_grid_container,text="Selecione um cartão e um ano.").grid(row=1,column=0,columnspan=12,pady=20)
        if hasattr(self,'invoice_details_block_frame') and self.selected_card_id is None and self.invoice_details_block_frame.winfo_ismapped():
            self.invoice_details_block_frame.grid_remove()

    def _load_and_display_invoice_details(self,card_id,year): # Implementa seleção de célula de fatura
        if not hasattr(self,'invoice_details_grid_container'):return
        for w in self.invoice_details_grid_container.winfo_children():
            if w.grid_info().get("row", 0) > 0: w.destroy()
        
        self.selected_invoice_details = None # Reseta seleção de fatura ao recarregar
        if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="disabled")
        if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="disabled")
        if hasattr(self, 'last_selected_invoice_cell_frame') and self.last_selected_invoice_cell_frame and self.last_selected_invoice_cell_frame.winfo_exists():
            self.last_selected_invoice_cell_frame.configure(border_width=0)
            self.last_selected_invoice_cell_frame = None

        faturas=db_manager.get_faturas(card_id,year)
        if not faturas or all(v==0.0 for v in faturas.values()):
            ctk.CTkLabel(self.invoice_details_grid_container,text=f"Nenhuma fatura para {year}.").grid(row=1,column=0,columnspan=12,pady=10)
            return

        current_data_row = 1 
        for i in range(12): 
            month_number = i + 1
            valor_fatura = faturas.get(month_number,0.0)
            
            cell_fg_color = ("#FFFFFF", "#333333") 
            invoice_value_cell_frame = ctk.CTkFrame(self.invoice_details_grid_container, fg_color=cell_fg_color, corner_radius=3, cursor="hand2") # Cursor para indicar clicável
            invoice_value_cell_frame.grid(row=current_data_row, column=i, padx=1, pady=1, sticky="nsew")
            invoice_value_cell_frame.original_border_color = invoice_value_cell_frame.cget("border_color") # Salva cor da borda
            invoice_value_cell_frame.original_border_width = invoice_value_cell_frame.cget("border_width")

            # Bind para seleção da célula
            # Passamos o widget da célula para poder destacá-lo
            invoice_value_cell_frame.bind("<Button-1>", 
                lambda event, c_id=card_id, y=year, m=month_number, val=valor_fatura, cell=invoice_value_cell_frame: 
                self._on_invoice_cell_selected(c_id, y, m, val, cell))

            fatura_value_label = ctk.CTkLabel(invoice_value_cell_frame, text=f"R$ {valor_fatura:.2f}", anchor="e")
            fatura_value_label.pack(padx=5, pady=5, fill="both", expand=True)
            # Propaga o clique do label para o frame pai (célula)
            fatura_value_label.bind("<Button-1>", 
                lambda event, c_id=card_id, y=year, m=month_number, val=valor_fatura, cell=invoice_value_cell_frame: 
                self._on_invoice_cell_selected(c_id, y, m, val, cell))
            
    def _on_invoice_cell_selected(self, card_id, year, month, current_value, cell_widget):
        """Chamado quando uma célula de fatura é clicada."""
        # Remove destaque da célula anterior
        if self.last_selected_invoice_cell_frame and self.last_selected_invoice_cell_frame.winfo_exists():
            self.last_selected_invoice_cell_frame.configure(
                border_width=self.last_selected_invoice_cell_frame.original_border_width,
                border_color=self.last_selected_invoice_cell_frame.original_border_color
            )

        # Armazena detalhes e destaca nova célula
        self.selected_invoice_details = {'card_id': card_id, 'year': year, 'month': month, 'value': current_value}
        
        if cell_widget and cell_widget.winfo_exists():
            cell_widget.configure(border_width=2, border_color=self.card_row_selected_fg_color[0]) # Usa a cor de destaque azul
            self.last_selected_invoice_cell_frame = cell_widget
        
        print(f"Fatura selecionada: Cartão {card_id}, Ano {year}, Mês {month}, Valor {current_value}")
        
        # Habilita botões de editar/remover fatura
        if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="normal")
        if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="normal")


    def _on_add_invoice_button_click(self):
        if not self.selected_card_id:
            messagebox.showwarning("Atenção", "Selecione um cartão da lista primeiro.", parent=self.controller); return
        if hasattr(self, 'dialog_upsert_invoice') and self.dialog_upsert_invoice and self.dialog_upsert_invoice.winfo_exists():
            self.dialog_upsert_invoice.focus(); return
        refresh_func = lambda c_id=self.selected_card_id, y=self.current_invoice_year: self._load_and_display_invoice_details(c_id, y)
        self.dialog_upsert_invoice = UpsertInvoiceDialog(
            master=self.controller, controller=self.controller, 
            refresh_callback=refresh_func,
            card_id=self.selected_card_id, year=self.current_invoice_year,
            edit_mode=False
        )
    
    def _on_edit_invoice_button_click(self):
        if not self.selected_invoice_details:
            messagebox.showwarning("Atenção", "Selecione uma fatura na tabela para editar.", parent=self.controller)
            return
        
        if hasattr(self, 'dialog_upsert_invoice') and self.dialog_upsert_invoice is not None and self.dialog_upsert_invoice.winfo_exists():
            self.dialog_upsert_invoice.focus()
            return

        # Pega os detalhes da fatura selecionada
        data = self.selected_invoice_details
        refresh_func = lambda c_id=data['card_id'], y=data['year']: self._load_and_display_invoice_details(c_id, y)

        self.dialog_upsert_invoice = UpsertInvoiceDialog(
            master=self.controller,
            controller=self.controller,
            refresh_callback=refresh_func,
            card_id=data['card_id'],
            year=data['year'],
            month=data['month'],
            current_value=data['value'],
            edit_mode=True # Abre em modo de edição
        )

    def _on_remove_invoice_button_click(self):
        if not self.selected_invoice_details:
            messagebox.showwarning("Atenção", "Selecione uma fatura na tabela para remover.", parent=self.controller)
            return

        data = self.selected_invoice_details
        month_names=["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        month_name_str = month_names[data['month']-1] if 0 < data['month'] <= 12 else f"Mês {data['month']}"

        confirm = messagebox.askyesno(
            "Confirmar Remoção de Fatura",
            f"Tem certeza que deseja remover a fatura de {month_name_str}/{data['year']} (valor R$ {data['value']:.2f})?\n"
            "Isso definirá o valor da fatura para 0.00.",
            parent=self.controller
        )
        if confirm:
            if db_manager.upsert_fatura(data['card_id'], data['year'], data['month'], 0.0): # Define valor como 0 para "remover"
                messagebox.showinfo("Sucesso", "Fatura removida com sucesso (valor definido para 0).", parent=self.controller)
                self._load_and_display_invoice_details(data['card_id'], data['year']) # Atualiza a tabela
                # Desabilita botões e limpa seleção de fatura
                self.selected_invoice_details = None
                if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="disabled")
                if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="disabled")
                if self.last_selected_invoice_cell_frame and self.last_selected_invoice_cell_frame.winfo_exists():
                    self.last_selected_invoice_cell_frame.configure(border_width=0)
            else:
                messagebox.showerror("Erro", "Não foi possível remover a fatura.", parent=self.controller)
            
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
            db_path = db_manager.DATABASE_PATH
            if os.path.exists(db_path): 
                try: os.remove(db_path)
                except PermissionError: print(f"AVISO: Não foi possível remover {db_path}. Pode estar em uso.")
                except Exception as e: print(f"Erro ao remover DB: {e}")
            db_manager.initialize_database()
            card_test_id = db_manager.add_card(nome="Cartão Teste UI", bandeira="Mastercard", cor="#FF6347", banco="NUBANK")
            if card_test_id:
                db_manager.upsert_fatura(card_test_id, date.today().year, 1, 100.50) 
                db_manager.upsert_fatura(card_test_id, date.today().year, 2, 75.20)  
                db_manager.upsert_fatura(card_test_id, date.today().year - 1, 3, 120.00) 
            container=ctk.CTkFrame(self,fg_color="transparent"); container.pack(fill="both",expand=True)
            self.main_frame_instance = MainAppFrame(parent=container, controller=self); self.main_frame_instance.pack(fill="both",expand=True)
            self.main_frame_instance.tab_view.set("Cartões") 
        def _on_app_closing(self): self.destroy()
        def show_frame(self, name): print(f"Mock: show {name}")
    MockAppController().mainloop()