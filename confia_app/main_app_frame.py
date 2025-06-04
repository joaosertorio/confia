# C:\Confia\confia_app\main_app_frame.py
import customtkinter as ctk
import tkinter
from tkinter import messagebox
from tkinter import font as tkFont 
from datetime import datetime, date, timedelta
import db_manager 
import os
import calendar # Adicionado para o filtro do dashboard
from category_management_frame import CategoryManagementFrame 


# Imports para Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt 
import matplotlib.patheffects as path_effects

# --- CLASSES DE DIÁLOGO ---

class AddEditCreditDialog(ctk.CTkToplevel): # Como no Passo 86
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
        success = False
        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id,data_str,obs,v,cat_id): success = True
            else:messagebox.showerror("Erro","Não foi possível atualizar o crédito.",parent=self)
        else:
            if db_manager.add_transaction(data_str,obs,v,'Crédito',cat_id): success = True
            else:messagebox.showerror("Erro","Não foi possível adicionar o crédito.",parent=self)
        if success: messagebox.showinfo("Sucesso","Crédito salvo!",parent=self.master);self.refresh_callback();self.destroy()

class AddEditDebitDialog(ctk.CTkToplevel): # Como no Passo 86
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
        success = False
        if self.editing_transaction_id:
            if db_manager.update_transaction(self.editing_transaction_id,d,o,v,c_id): success = True
            else:messagebox.showerror("Erro","Não foi possível atualizar o débito.",parent=self)
        else:
            if db_manager.add_transaction(d,o,v,'Débito',c_id): success = True
            else:messagebox.showerror("Erro","Não foi possível adicionar o débito.",parent=self)
        if success: messagebox.showinfo("Sucesso","Débito salvo!",parent=self.master);self.refresh_callback();self.destroy()

class AddEditCardDialog(ctk.CTkToplevel): # Como no Passo 86
    def __init__(self, master, controller, refresh_callback, card_data=None):
        local_kwargs = {k: v for k, v in {} if k != 'controller'} # Simulação se kwargs viesse da chamada
        super().__init__(master, **local_kwargs) # Passa master
        self.controller=controller;self.refresh_callback=refresh_callback;self.editing_card_id=None
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
            if db_manager.update_card(self.editing_card_id,nome,bandeira=bandeira,cor=cor_hex,limite=limite,dia_fechamento=dia_f,dia_vencimento=dia_v,banco=banco):
                messagebox.showinfo("Sucesso",f"Cartão '{nome}' atualizado!",parent=self.master); success_flag=True
            else:messagebox.showerror("Erro","Não foi possível atualizar o cartão.",parent=self)
        else:
            new_id = db_manager.add_card(nome=nome,bandeira=bandeira,cor=cor_hex,limite=limite,dia_fechamento=dia_f,dia_vencimento=dia_v,banco=banco)
            if new_id:
                messagebox.showinfo("Sucesso",f"Cartão '{nome}' adicionado!",parent=self.master); success_flag=True
            else:messagebox.showerror("Erro","Não foi possível adicionar o cartão.",parent=self)
        if success_flag: self.refresh_callback(); self.destroy()

class UpsertInvoiceDialog(ctk.CTkToplevel): # Como no Passo 68
    def __init__(self, master, controller, refresh_callback, card_id, year, month=None, current_value=0.0, edit_mode=False):
        local_kwargs = {k: v for k, v in {} if k != 'controller'}
        super().__init__(master, **local_kwargs)
        self.controller = controller; self.refresh_callback = refresh_callback
        self.card_id_to_affect = card_id; self.year_to_affect = year
        self.month_to_affect = month; self.current_value = current_value
        self.edit_mode = edit_mode 
        self.cards_map = {} 
        self.month_names_map = {"Janeiro":1, "Fevereiro":2, "Março":3, "Abril":4, "Maio":5, "Junho":6, "Julho":7, "Agosto":8, "Setembro":9, "Outubro":10, "Novembro":11, "Dezembro":12}
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
        ctk.CTkLabel(form_frame, text=card_name_for_title).grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        ctk.CTkLabel(form_frame, text="Ano:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.year_entry = ctk.CTkEntry(form_frame, placeholder_text="YYYY"); self.year_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.year_entry.insert(0, str(self.year_to_affect))
        self.year_entry.configure(state="disabled" if self.edit_mode else "normal") 
        ctk.CTkLabel(form_frame, text="Mês:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.month_var = ctk.StringVar()
        month_display_names = list(self.month_names_map.keys())
        default_month_name = self.month_numbers_map.get(self.month_to_affect) if self.edit_mode and self.month_to_affect else month_display_names[date.today().month -1]
        self.month_var.set(default_month_name)
        self.month_menu = ctk.CTkOptionMenu(form_frame, variable=self.month_var, values=month_display_names)
        self.month_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        if self.edit_mode: self.month_menu.configure(state="disabled")
        ctk.CTkLabel(form_frame, text="Valor da Fatura (R$):").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.value_entry = ctk.CTkEntry(form_frame, placeholder_text="Ex: 250.00"); self.value_entry.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        if self.edit_mode: self.value_entry.insert(0, f"{self.current_value:.2f}")
        bf=ctk.CTkFrame(self,fg_color="transparent");bf.pack(pady=(20,20),padx=20,side="bottom",fill="x",anchor="e")
        ctk.CTkButton(bf,text="Salvar",command=self._save_action).pack(side="left",padx=(0,5))
        ctk.CTkButton(bf,text="Cancelar",command=self.destroy,fg_color="gray").pack(side="left")
        self.value_entry.focus()
        if self.edit_mode: self.value_entry.select_range(0,ctk.END)

    def _save_action(self):
        card_id_final = self.card_id_to_affect 
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
    def __init__(self, master, controller, **kwargs):
        # ... (corpo do seu __init__ ... )
        local_kwargs = {k: v for k, v in kwargs.items() if k != 'controller'}
        super().__init__(master, **local_kwargs)
        self.controller = controller
        # ...
        self.category_management_window = None # Para rastrear a janela de categorias
        self.configure(fg_color="transparent")
        
        print("DEBUG_MainAppFrame: __init__ - INÍCIO")
        self.dialog_add_edit_credit = None 
        self.dialog_add_edit_debit = None
        self.dialog_add_edit_card = None 
        self.dialog_upsert_invoice = None 

        self.selected_card_id = None 
        self.last_selected_card_row_frame = None 
        
        self.card_row_default_fg_color = ("gray92", "gray20") 
        self.card_row_selected_fg_color = ("#3B8ED0", "#1F6AA5") 
        
        self.year_tab_selected_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        self.year_tab_selected_hover_color = ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        self.year_tab_unselected_color = ("gray75", "gray28") 
        self.year_tab_unselected_hover_color = ("gray70", "gray35")

        self.current_invoice_year = date.today().year 
        self.selected_invoice_details = None 
        self.last_selected_invoice_cell_frame = None 
        
        self.invoice_cell_default_fg_color = ("#FFFFFF", "#333333") 
        self.invoice_cell_selected_border_color = self.card_row_selected_fg_color 
        self.invoice_cell_default_border_color = ("gray75", "gray28") 

        self.canvas_chart1 = None 
        self.canvas_chart2 = None
        self.canvas_chart3 = None
        self.canvas_chart4 = None

        self._setup_menu()
        self._create_tabs() 
        print("DEBUG_MainAppFrame: __init__ - FIM")

    def _setup_menu(self):
        menubar = tkinter.Menu(self.controller)
        try: menu_font = tkFont.Font(family="Segoe UI", size=10)
        except: menu_font = None 
        menu_sistema = tkinter.Menu(menubar, tearoff=0)
        menu_sistema.add_command(label="Gerenciar Categorias", command=self._open_category_management_window, font=menu_font)
        menu_sistema.add_separator(); menu_sistema.add_command(label="Sair", command=self.controller._on_app_closing, font=menu_font)
        menubar.add_cascade(label="Sistema", menu=menu_sistema, font=menu_font)
        menu_ferramentas = tkinter.Menu(menubar, tearoff=0)
        menu_ferramentas.add_command(label="Gerar Dados de Teste", command=self._on_generate_test_data_click, font=menu_font)
        menu_ferramentas.add_command(label="Apagar Dados de Teste", command=self._on_delete_test_data_click, font=menu_font)
        menubar.add_cascade(label="Ferramentas", menu=menu_ferramentas, font=menu_font)
        menu_ajuda = tkinter.Menu(menubar, tearoff=0)
        menu_ajuda.add_command(label="Sobre Confia", command=self._sobre_confia, font=menu_font)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda, font=menu_font)
        self.controller.config(menu=menubar)
        
    def _open_category_management_window(self):
        print("DEBUG_MainAppFrame: Abrindo janela de Gerenciar Categorias...")
        
        try:
            from category_management_frame import CategoryManagementFrame
        except ImportError as e:
            messagebox.showerror("Erro de Importação", f"Não foi possível carregar CategoryManagementFrame: {e}")
            return

        if self.category_management_window is None or not self.category_management_window.winfo_exists():
            # --- CORREÇÃO AQUI: Usar 'master_app_controller' como nome do argumento ---
            self.category_management_window = CategoryManagementFrame(
                master_app_controller=self.controller # Passa a instância da App
            )
            # --- FIM DA CORREÇÃO ---
            self.category_management_window.focus() 
        else:
            self.category_management_window.focus()

    def _create_tabs(self):
        print("DEBUG_TABS: _create_tabs - INÍCIO")
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)
        tab_names = ["Dashboard", "Créditos", "Débitos", "Cartões", "Relatórios/Insights"]
        tab_setup_methods = {
            "Dashboard": self._setup_dashboard_tab, "Créditos": self._setup_credits_tab,
            "Débitos": self._setup_debits_tab, "Cartões": self._setup_cards_tab,
            "Relatórios/Insights": self._setup_reports_tab
        }
        for name in tab_names:
            print(f"DEBUG_TABS: Adicionando e configurando aba {name}...")
            tab = self.tab_view.add(name)
            setattr(self, f"tab_{name.lower().replace('/','_').replace(' ','_')}", tab)
            if name in tab_setup_methods and hasattr(self, tab_setup_methods[name].__name__):
                tab_setup_methods[name](tab)
            else: print(f"AVISO: Método de setup para '{name}' NÃO ENCONTRADO.")
        print("DEBUG_TABS: Definindo aba inicial para 'Dashboard' com set()...")
        self.tab_view.set("Dashboard") 
        current_set_tab = self.tab_view.get()
        print(f"DEBUG_TABS: Aba atual APÓS set() é: '{current_set_tab}'")
        self.tab_view.configure(command=self._on_tab_change)
        if hasattr(self, "_on_tab_change") and callable(self._on_tab_change):
            print(f"DEBUG_TABS: Chamando _on_tab_change() para carregar conteúdo da aba '{current_set_tab}'...")
            self._on_tab_change() 
        print("DEBUG_TABS: _create_tabs - FIM")

    def _on_tab_change(self):
        selected_tab_name = self.tab_view.get() 
        print(f"DEBUG: _on_tab_change - Aba selecionada: {selected_tab_name}")
        if selected_tab_name == "Dashboard":
             if hasattr(self, '_update_all_dashboard_charts'): self._update_all_dashboard_charts()
        elif selected_tab_name == "Créditos":
            if hasattr(self, '_load_initial_credits_data'): self._load_initial_credits_data()
        elif selected_tab_name == "Débitos":
            if hasattr(self, '_load_initial_debits_data'): self._load_initial_debits_data()
        elif selected_tab_name == "Cartões": 
            if hasattr(self, '_load_and_display_cards'): self._load_and_display_cards()
            if self.selected_card_id is None and hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                 self.invoice_details_block_frame.grid_remove()
                 self._reset_invoice_selection_and_buttons() 
    
    def _setup_dashboard_tab(self, tab_dashboard):
        print("DEBUG_DASH: _setup_dashboard_tab - INÍCIO")
        for widget in tab_dashboard.winfo_children(): widget.destroy()
        dashboard_main_frame = ctk.CTkFrame(tab_dashboard, fg_color="transparent")
        dashboard_main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        dashboard_main_frame.grid_columnconfigure(0, weight=1)
        dashboard_main_frame.grid_rowconfigure(0, weight=0); dashboard_main_frame.grid_rowconfigure(1, weight=0); dashboard_main_frame.grid_rowconfigure(2, weight=1)
        main_filter_frame = ctk.CTkFrame(dashboard_main_frame)
        main_filter_frame.grid(row=0, column=0, padx=0, pady=(0,10), sticky="ew")
        ctk.CTkLabel(main_filter_frame, text="Mês:").pack(side="left", padx=(10,5), pady=5)
        today = date.today()
        if not hasattr(self, 'month_names'): 
            self.month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.dashboard_month_var = ctk.StringVar(value=self.month_names[today.month - 1])
        self.dashboard_month_menu = ctk.CTkOptionMenu(main_filter_frame, variable=self.dashboard_month_var, values=self.month_names)
        self.dashboard_month_menu.pack(side="left", padx=(0,10), pady=5)
        ctk.CTkLabel(main_filter_frame, text="Ano:").pack(side="left", padx=(10,5), pady=5)
        self.dashboard_year_entry = ctk.CTkEntry(main_filter_frame, placeholder_text="YYYY", width=80)
        self.dashboard_year_entry.pack(side="left", padx=(0,10), pady=5)
        self.dashboard_year_entry.insert(0, str(today.year))
        apply_filter_button = ctk.CTkButton(main_filter_frame, text="Aplicar Filtro", width=100, command=self._update_all_dashboard_charts)
        apply_filter_button.pack(side="left", padx=10, pady=5)
        card_year_filter_frame = ctk.CTkFrame(dashboard_main_frame)
        card_year_filter_frame.grid(row=1, column=0, padx=0, pady=(0,10), sticky="ew")
        ctk.CTkLabel(card_year_filter_frame, text="Ano (Gráficos de Cartão):").pack(side="left", padx=(5,0), pady=5)
        current_year = date.today().year
        year_options = [str(current_year - 1), str(current_year), str(current_year + 1)]
        self.dashboard_card_year_var = ctk.StringVar(value=str(current_year))
        self.dashboard_card_year_selector = ctk.CTkSegmentedButton(card_year_filter_frame, values=year_options, variable=self.dashboard_card_year_var, command=self._update_all_dashboard_charts)
        self.dashboard_card_year_selector.pack(side="left", padx=10, pady=5)
        charts_container_frame = ctk.CTkFrame(dashboard_main_frame, fg_color="transparent")
        charts_container_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        charts_container_frame.grid_columnconfigure(0, weight=1); charts_container_frame.grid_columnconfigure(1, weight=1)
        charts_container_frame.grid_rowconfigure(0, weight=1); charts_container_frame.grid_rowconfigure(1, weight=1)
        self.chart_frame_1 = ctk.CTkFrame(charts_container_frame, fg_color=("gray90", "gray25")); self.chart_frame_1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.chart_frame_2 = ctk.CTkFrame(charts_container_frame, fg_color=("gray90", "gray25")); self.chart_frame_2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        self.chart_frame_3 = ctk.CTkFrame(charts_container_frame, fg_color=("gray90", "gray25")); self.chart_frame_3.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.chart_frame_4 = ctk.CTkFrame(charts_container_frame, fg_color=("gray90", "gray25")); self.chart_frame_4.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        print("DEBUG_DASH: _setup_dashboard_tab - Estrutura criada.")

    def _update_all_dashboard_charts(self, segmented_button_value=None):
        print("DEBUG_DASH: _update_all_dashboard_charts - INÍCIO")
        # ... (lógica para pegar start_date_filter e year_for_cards como estava) ...
        if not (hasattr(self, 'dashboard_month_var') and 
                hasattr(self, 'dashboard_year_entry') and 
                hasattr(self, 'dashboard_card_year_var')):
            print("DEBUG_DASH: Widgets do dashboard ainda não totalmente inicializados. Saindo de _update_all_dashboard_charts.")
            if hasattr(self, 'tab_dashboard'):
                for widget in self.tab_dashboard.winfo_children(): widget.destroy() 
                ctk.CTkLabel(self.tab_dashboard, text="Inicializando Dashboard...", font=ctk.CTkFont(size=18)).pack(expand=True)
            return

        selected_month_name = self.dashboard_month_var.get()
        year_str = self.dashboard_year_entry.get()
        try:
            year = int(year_str)
            if not hasattr(self, 'month_names'): 
                 self.month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            month_num = self.month_names.index(selected_month_name) + 1
            _, last_day = calendar.monthrange(year, month_num) 
            start_date_filter = f"{year}-{month_num:02d}-01"
            end_date_filter = f"{year}-{month_num:02d}-{last_day:02d}"
        except (ValueError, IndexError, AttributeError) as e:
            print(f"Erro ao processar filtro Mês/Ano: {e}")
            messagebox.showerror("Erro de Filtro", f"Mês ou Ano inválido no filtro principal: {e}", parent=self.controller)
            return

        year_for_cards_str = self.dashboard_card_year_var.get() 
        try: year_for_cards = int(year_for_cards_str)
        except ValueError: messagebox.showerror("Erro de Ano", "Ano inválido para cartões.", parent=self.controller); return

        print(f"DEBUG_DASH: Atualizando dashboard: Período Principal [{start_date_filter}-{end_date_filter}], Ano Cartões [{year_for_cards}]")
        
        # Limpa os frames principais dos gráficos (self.chart_frame_1, etc.)
        # A limpeza do conteúdo interno (canvas, legenda específica) é feita pelos métodos de criação de gráfico.
        for chart_frame_attr in ["chart_frame_1", "chart_frame_2", "chart_frame_3", "chart_frame_4"]:
            if hasattr(self, chart_frame_attr):
                frame = getattr(self, chart_frame_attr)
                # Limpa o frame antes de adicionar novo título e conteúdo do gráfico
                for widget in frame.winfo_children(): 
                    widget.destroy() 
        
        # Gráfico 1: Pizza Despesas por Categoria
        expenses_data = db_manager.get_total_spending_by_category(start_date_filter, end_date_filter)
        # --- CORREÇÃO/VERIFICAÇÃO AQUI ---
        # A chamada deve passar os frames corretos para a pizza e para a legenda,
        # que são criados dentro de _setup_dashboard_tab como self.chart_frame_1_pie e self.legend_frame_1
        # e são filhos de self.chart_frame_1 (que é o container geral do gráfico 1).
        if hasattr(self, 'chart_frame_1'): # chart_frame_1 é o container principal do gráfico 1
            # _create_or_update_pie_chart_expenses agora recebe o frame pai (self.chart_frame_1)
            # e internamente cria os frames para pizza e legenda.
            self._create_or_update_pie_chart_expenses(expenses_data, self.chart_frame_1)
        # --- FIM DA CORREÇÃO/VERIFICAÇÃO ---
        
        # Placeholders para outros gráficos
        if hasattr(self, 'chart_frame_2'):
            # ... (lógica para Gráfico 2 como estava) ...
            income_expense_data = db_manager.get_total_income_vs_expenses(start_date_filter, end_date_filter)
            self._create_or_update_bar_chart_income_expense(income_expense_data, self.chart_frame_2)

        if hasattr(self, 'chart_frame_3'):
            # ... (lógica para Gráfico 3 como estava) ...
            self._create_or_update_line_chart_card_evolution(self.chart_frame_3, year_for_cards)

        if hasattr(self, 'chart_frame_4'):
            # ... (lógica para Gráfico 4 como estava) ...
            self._create_or_update_line_chart_consolidated_cards(self.chart_frame_4, year_for_cards)
        
        print("DEBUG_DASH: Gráficos do dashboard atualizados.")

    def _create_or_update_pie_chart_expenses(self, data, parent_frame):
        print(f"DEBUG_DASH_CHART1: Pizza. Dados: {len(data) if data else 'Sem dados'}")
        
        # Limpa o frame e o canvas
        if hasattr(self, 'canvas_chart1') and self.canvas_chart1:
            self.canvas_chart1.get_tk_widget().destroy(); self.canvas_chart1 = None
        for widget in parent_frame.winfo_children(): widget.destroy()

        # Título
        ctk.CTkLabel(parent_frame, text="Despesas por Categoria", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,10), padx=10, anchor="n")

        # Container para pizza e legenda
        chart_content_area = ctk.CTkFrame(parent_frame, fg_color="transparent")
        chart_content_area.pack(fill="both", expand=True, padx=0, pady=0)
        chart_content_area.grid_columnconfigure(0, weight=3); 
        chart_content_area.grid_columnconfigure(1, weight=2); 
        chart_content_area.grid_rowconfigure(0, weight=1)

        pie_canvas_frame = ctk.CTkFrame(chart_content_area, fg_color="transparent")
        pie_canvas_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        legend_scroll_frame = ctk.CTkScrollableFrame(chart_content_area, label_text="", fg_color="transparent", corner_radius=0)
        legend_scroll_frame.grid(row=0, column=1, padx=(5,0), pady=0, sticky="nsew")

        if not data:
            ctk.CTkLabel(pie_canvas_frame, text="Sem despesas no período.").pack(padx=10, pady=10, expand=True, fill="both")
            for widget in legend_scroll_frame.winfo_children(): widget.destroy() 
            ctk.CTkLabel(legend_scroll_frame, text="").pack()
            return

        category_names_for_pie = [item[0] for item in data]      
        hex_colors_from_db = [item[1] if (item[1] and item[1].startswith("#") and len(item[1]) == 7) else "#808080" for item in data]       
        sizes = [item[2] for item in data]        
        
        current_theme_mode = ctk.get_appearance_mode()
        if current_theme_mode == "Dark": 
            safe_fig_bg_color = "#2B2B2B"
            pie_label_text_color = "white" # Cor para nomes de categoria no tema escuro
        else: # Light
            safe_fig_bg_color = "#EBEBEB"
            pie_label_text_color = "black" # Cor para nomes de categoria no tema claro
        
        pie_edge_color = safe_fig_bg_color
        
        try:
            fig = Figure(figsize=(3.3, 3.3), dpi=90, facecolor=safe_fig_bg_color) 
            ax = fig.add_subplot(111); ax.set_facecolor(safe_fig_bg_color)
            valid_mpl_colors = [c if mcolors.is_color_like(c) else "#808080" for c in hex_colors_from_db]
            if not valid_mpl_colors and sizes : valid_mpl_colors = None 

            if not sizes: 
                ctk.CTkLabel(pie_canvas_frame, text="Sem dados para exibir.").pack(padx=10, pady=10, expand=True); return

            # Define se os nomes das categorias serão exibidos e suas propriedades de texto
            display_pie_labels = category_names_for_pie if len(category_names_for_pie) <= 6 else None
            # --- CORREÇÃO FINAL: Cor do texto fixa baseada no tema ---
            pie_textprops = {'fontsize': 8, 'color': pie_label_text_color, 'fontweight': 'normal'} if display_pie_labels else None
            # --- FIM DA CORREÇÃO ---

            # Cria o gráfico de pizza
            wedges, texts_on_pie = ax.pie( 
                sizes, 
                colors=valid_mpl_colors, 
                labels=display_pie_labels,    
                labeldistance=1.1,          
                autopct=None, # Sem porcentagem                   
                startangle=90, 
                wedgeprops={'edgecolor': pie_edge_color, 'linewidth': 0.7, 'antialiased': True},
                textprops=pie_textprops     
            ) 
            
            # REMOVIDO: Loop que alterava a cor do texto dinamicamente. A cor agora é fixa pelo 'textprops'.
            
            # Círculo central para criar o efeito "donut"
            centre_circle = plt.Circle((0,0),0.60,fc=safe_fig_bg_color) 
            ax.add_artist(centre_circle); ax.axis('equal')  
            fig.tight_layout(pad=0.1) 

            # Adiciona o gráfico ao frame Tkinter
            self.canvas_chart1 = FigureCanvasTkAgg(fig, master=pie_canvas_frame)
            self.canvas_chart1.draw()
            canvas_widget = self.canvas_chart1.get_tk_widget()
            canvas_widget.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            
            # Cria a legenda customizada à direita
            self._create_custom_pie_legend(data, legend_scroll_frame)

            print(f"DEBUG_DASH_CHART1: Gráfico de pizza (com nomes e cor de fonte fixa) e legenda criados.")
        except Exception as e:
            print(f"DEBUG_DASH_CHART1: Erro crítico ao criar/desenhar gráfico de pizza: {e}")
            import traceback; traceback.print_exc() 
            ctk.CTkLabel(pie_canvas_frame, text=f"Erro gráfico:\n{str(e)[:100]}").pack(padx=10,pady=10)

    def _create_custom_pie_legend(self, data, legend_parent_frame):
        for widget in legend_parent_frame.winfo_children(): widget.destroy()

        total_gastos_para_pct = sum(item[2] for item in data) 
        if total_gastos_para_pct == 0: 
            ctk.CTkLabel(legend_parent_frame, text="Sem gastos para detalhar.").pack(padx=5, pady=5)
            return

        legend_parent_frame.grid_columnconfigure(0, weight=0, minsize=20)  
        legend_parent_frame.grid_columnconfigure(1, weight=3) # Mais peso para o nome da categoria         
        legend_parent_frame.grid_columnconfigure(2, weight=1, minsize=80) 
        legend_parent_frame.grid_columnconfigure(3, weight=1, minsize=50) 

        # --- AJUSTE DE FONTE DOS CABEÇALHOS DA LEGENDA ---
        header_font = ctk.CTkFont(family="Segoe UI", size=13, weight="bold") # Aumentado
        legend_font = ctk.CTkFont(family="Segoe UI", size=12) # Aumentado e definido família
        # --- FIM DO AJUSTE DE FONTE ---

        # Cabeçalhos da Legenda (opcional, mas pode ser útil)
        # ctk.CTkLabel(legend_parent_frame, text="", width=20).grid(row=0, column=0) # Espaço para cor
        # ctk.CTkLabel(legend_parent_frame, text="Categoria", font=header_font, anchor="w").grid(row=0, column=1, sticky="w", padx=2)
        # ctk.CTkLabel(legend_parent_frame, text="Valor", font=header_font, anchor="e").grid(row=0, column=2, sticky="e", padx=2)
        # ctk.CTkLabel(legend_parent_frame, text="%", font=header_font, anchor="e").grid(row=0, column=3, sticky="e", padx=2)
        # current_row = 1 # Se usar cabeçalhos, começa na linha 1
        
        current_row = 0 # Começa na linha 0 se não houver cabeçalhos explícitos

        for nome_categoria, cor_hex, valor_gasto in data:
            color_box = ctk.CTkFrame(legend_parent_frame, width=15, height=15, 
                                     fg_color=cor_hex if (cor_hex and cor_hex.startswith("#")) else "#808080", 
                                     corner_radius=3)
            color_box.grid(row=current_row, column=0, padx=(0,5), pady=3, sticky="w")

            name_label = ctk.CTkLabel(legend_parent_frame, text=nome_categoria, anchor="w", font=legend_font, wraplength=120) # Aumentar wraplength se necessário
            name_label.grid(row=current_row, column=1, padx=0, pady=3, sticky="w")

            value_label = ctk.CTkLabel(legend_parent_frame, text=f"R$ {valor_gasto:.2f}", anchor="e", font=legend_font)
            value_label.grid(row=current_row, column=2, padx=5, pady=3, sticky="e")
            
            percent = (valor_gasto / total_gastos_para_pct) * 100
            percent_label = ctk.CTkLabel(legend_parent_frame, text=f"{percent:.1f}%", anchor="e", font=legend_font)
            percent_label.grid(row=current_row, column=3, padx=(5,0), pady=3, sticky="e")
            
            current_row += 1
        
        if current_row == 0: # (ou 1 se usar cabeçalhos)
             ctk.CTkLabel(legend_parent_frame, text="Sem dados para legenda.").pack(padx=5, pady=5)


    def _create_or_update_bar_chart_income_expense(self, data, parent_frame):
        print(f"DEBUG_DASH_CHART2: Barras Entradas/Saídas/Saldo. Dados: {data}")
        
        if hasattr(self, 'canvas_chart2') and self.canvas_chart2:
            self.canvas_chart2.get_tk_widget().destroy(); self.canvas_chart2 = None
        for widget in parent_frame.winfo_children(): widget.destroy()

        ctk.CTkLabel(parent_frame, text="Fluxo de Caixa do Período", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(5,10), padx=10, anchor="n")

        chart_actual_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        chart_actual_frame.pack(fill="both", expand=True, padx=0, pady=0)

        if not data or (data.get('total_creditos', 0) == 0 and data.get('total_debitos', 0) == 0):
            ctk.CTkLabel(chart_actual_frame, text="Sem dados de entradas/saídas para o período.").pack(padx=10, pady=10, expand=True, fill="both")
            return

        total_creditos = data.get('total_creditos', 0.0)
        total_debitos = data.get('total_debitos', 0.0)
        saldo_atual = total_creditos - total_debitos

        labels = ['Créditos', 'Débitos', 'Saldo']
        values = [total_creditos, total_debitos, saldo_atual]
        
        color_creditos = '#2ECC71'; color_debitos = '#E74C3C'; color_saldo = '#3B8ED0'
        bar_colors = [color_creditos, color_debitos, color_saldo] 

        current_theme_mode = ctk.get_appearance_mode()
        if current_theme_mode == "Dark":
            safe_fig_bg_color = "#2B2B2B"; safe_text_color = "#DCE4EE"; grid_color = "#4A4D50"
            zero_line_color = "gray" # Linha do zero mais visível no tema escuro
        else: 
            safe_fig_bg_color = "#EBEBEB"; safe_text_color = "#1F1F1F"; grid_color = "#DCDCDC"
            zero_line_color = "dimgray" # Linha do zero mais visível no tema claro
        
        try:
            fig = Figure(figsize=(5, 3.8), dpi=90, facecolor=safe_fig_bg_color)
            ax = fig.add_subplot(111); ax.set_facecolor(safe_fig_bg_color)
            bars = ax.bar(labels, values, color=bar_colors, width=0.5)

            for bar in bars:
                yval = bar.get_height()
                text_color_for_bar_value = safe_text_color
                if bar.get_label() == 'Saldo' and yval < 0: text_color_for_bar_value = color_debitos 
                ax.text(bar.get_x() + bar.get_width()/2.0, 
                        yval + (max(abs(v) for v in values) * 0.02 if any(v != 0 for v in values) else 0.1), 
                        f"R$ {yval:.2f}", ha='center', va='bottom' if yval >= 0 else 'top', 
                        color=text_color_for_bar_value, fontsize=9, fontweight='bold') # Fonte um pouco menor

            ax.set_ylabel('Valor (R$)', color=safe_text_color, fontsize=10)
            
            ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(safe_text_color); ax.spines['bottom'].set_color(safe_text_color)
            ax.tick_params(axis='x', colors=safe_text_color, labelsize=10)
            ax.tick_params(axis='y', colors=safe_text_color, labelsize=9)
            
            ax.yaxis.grid(True, linestyle=':', linewidth=0.6, color=grid_color, alpha=0.7); ax.set_axisbelow(True) 
            
            # --- ADICIONAR LINHA DO ZERO MAIS FORTE ---
            ax.axhline(0, color=zero_line_color, linewidth=1.2, linestyle='-') 
            # --- FIM DA ADIÇÃO ---
            
            min_val = min(0, min(values) if values else 0); max_val = max(0, max(values) if values else 0)
            padding = (max_val - min_val) * 0.1 if (max_val - min_val) > 0 else 0.1 # Evita padding zero
            ax.set_ylim(min_val - padding if min_val <= 0 else 0, # Garante que o eixo Y comece no ou abaixo do menor valor
                        max_val + padding if max_val >= 0 else 0.1) # Garante que o eixo Y vá até ou acima do maior valor

            fig.tight_layout(pad=0.5)

            self.canvas_chart2 = FigureCanvasTkAgg(fig, master=chart_actual_frame); self.canvas_chart2.draw()
            self.canvas_chart2.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        except Exception as e:
            print(f"DEBUG_DASH_CHART2: Erro: {e}"); import traceback; traceback.print_exc() 
            ctk.CTkLabel(chart_actual_frame, text=f"Erro gráfico:\n{str(e)[:100]}").pack()


    def _create_or_update_line_chart_card_evolution(self, parent_frame, year: int): # Como no Passo 94
        # ... (Código completo do _create_or_update_line_chart_card_evolution como no Passo 94) ...
        for widget in parent_frame.winfo_children(): widget.destroy()
        if hasattr(self, 'canvas_chart3') and self.canvas_chart3: self.canvas_chart3.get_tk_widget().destroy(); self.canvas_chart3 = None
        ctk.CTkLabel(parent_frame, text=f"Evolução Mensal por Cartão - {year}",font=ctk.CTkFont(size=16,weight="bold")).pack(pady=(5,10),padx=10,anchor="n")
        all_cards = db_manager.get_all_cards()
        if not all_cards: ctk.CTkLabel(parent_frame,text=f"Nenhum cartão.").pack(expand=True); return
        chart_actual_frame=ctk.CTkFrame(parent_frame,fg_color="transparent"); chart_actual_frame.pack(fill="both",expand=True,padx=0,pady=0)
        meses_n=range(1,13); mode=ctk.get_appearance_mode()
        if mode=="Dark": safe_bg="#2B2B2B";safe_txt="#DCE4EE";grid_c="#4A4D50"
        else: safe_bg="#EBEBEB";safe_txt="#1F1F1F";grid_c="#DCDCDC"
        try:
            fig=Figure(figsize=(5,3.8),dpi=90,facecolor=safe_bg); ax=fig.add_subplot(111); ax.set_facecolor(safe_bg)
            has_data=False
            for card in all_cards:
                card_id=card['id'];card_name=card['nome'];card_color=card.get('cor','#808080')
                if not (card_color and card_color.startswith("#") and len(card_color)==7): card_color="#808080"
                faturas=db_manager.get_faturas(card_id,year); valores=[faturas.get(m,0.0) for m in meses_n]
                if any(v>0 for v in valores): ax.plot(meses_n,valores,marker='o',ls='-',lw=2,label=card_name,color=card_color,ms=5); has_data=True
            if not has_data: ctk.CTkLabel(chart_actual_frame,text=f"Sem dados em {year}.").pack(expand=True); return
            ax.set_ylabel('Valor Fatura (R$)',color=safe_txt,fontsize=10)
            mes_labels=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
            ax.set_xticks(meses_n);ax.set_xticklabels(mes_labels,rotation=45,ha="right",fontsize=8)
            ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.spines['left'].set_color(safe_txt);ax.spines['bottom'].set_color(safe_txt)
            ax.tick_params(axis='x',colors=safe_txt);ax.tick_params(axis='y',colors=safe_txt,labelsize=9)
            ax.yaxis.grid(True,ls=':',lw=0.6,color=grid_c,alpha=0.7);ax.set_axisbelow(True);ax.set_ylim(bottom=0)
            if len(all_cards)>0 and has_data: 
                leg=ax.legend(title="Cartões",fontsize=8,title_fontsize=9,labelcolor=safe_txt,facecolor=safe_bg,edgecolor=safe_bg,frameon=True)
                if leg: leg.get_title().set_color(safe_txt); leg.get_frame().set_alpha(None); leg.get_frame().set_facecolor(safe_bg)
            fig.tight_layout(pad=0.8)
            self.canvas_chart3=FigureCanvasTkAgg(fig,master=chart_actual_frame);self.canvas_chart3.draw()
            self.canvas_chart3.get_tk_widget().pack(side="top",fill="both",expand=True,padx=0,pady=0)
        except Exception as e: print(f"Erro Chart3: {e}");ctk.CTkLabel(chart_actual_frame,text="Erro gráfico.").pack()

    def _create_or_update_line_chart_consolidated_cards(self, parent_frame, year: int): # Como no Passo 95
        # ... (Código completo do _create_or_update_line_chart_consolidated_cards como no Passo 95) ...
        for widget in parent_frame.winfo_children(): widget.destroy()
        if hasattr(self, 'canvas_chart4') and self.canvas_chart4: self.canvas_chart4.get_tk_widget().destroy(); self.canvas_chart4 = None
        ctk.CTkLabel(parent_frame,text=f"Gastos Consolidados Cartões - {year}",font=ctk.CTkFont(size=16,weight="bold")).pack(pady=(5,0),padx=10,anchor="n")
        chart_actual_frame=ctk.CTkFrame(parent_frame,fg_color="transparent"); chart_actual_frame.pack(fill="both",expand=True,padx=0,pady=0)
        totalizer_frame=ctk.CTkFrame(parent_frame,fg_color="transparent",height=40); totalizer_frame.pack(fill="x",side="bottom",pady=(5,0))
        totalizer_frame.grid_columnconfigure(list(range(12)),weight=1)
        faturas=db_manager.get_consolidated_faturas_for_year(year)
        if not faturas or all(v==0.0 for v in faturas.values()): ctk.CTkLabel(chart_actual_frame,text=f"Sem dados em {year}.").pack(expand=True); return
        meses_n=range(1,13); valores=[faturas.get(m,0.0) for m in meses_n]; mode=ctk.get_appearance_mode()
        if mode=="Dark": safe_bg="#2B2B2B";safe_txt="#DCE4EE";grid_c="#4A4D50";line_c="#5694F8"
        else: safe_bg="#EBEBEB";safe_txt="#1F1F1F";grid_c="#DCDCDC";line_c="#1F6AA5"
        try:
            fig=Figure(figsize=(5,3.3),dpi=90,facecolor=safe_bg);ax=fig.add_subplot(111);ax.set_facecolor(safe_bg)
            ax.plot(meses_n,valores,marker='o',ls='-',lw=2.5,color=line_c,ms=6,label="Total Faturas")
            ax.set_ylabel('Valor Total (R$)',color=safe_txt,fontsize=10)
            mes_labels=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
            ax.set_xticks(meses_n);ax.set_xticklabels(mes_labels,rotation=45,ha="right",fontsize=8)
            ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False);ax.spines['left'].set_color(safe_txt);ax.spines['bottom'].set_color(safe_txt)
            ax.tick_params(axis='x',colors=safe_txt);ax.tick_params(axis='y',colors=safe_txt,labelsize=9)
            ax.yaxis.grid(True,ls=':',lw=0.6,color=grid_c,alpha=0.7);ax.set_axisbelow(True);ax.set_ylim(bottom=0)
            fig.tight_layout(pad=0.8)
            self.canvas_chart4=FigureCanvasTkAgg(fig,master=chart_actual_frame);self.canvas_chart4.draw()
            self.canvas_chart4.get_tk_widget().pack(side="top",fill="both",expand=True,padx=0,pady=0)
            for i,m_num in enumerate(meses_n): val_mes=valores[i]; ctk.CTkLabel(totalizer_frame,text=f"R$\n{val_mes:.2f}",font=ctk.CTkFont(size=9),text_color=safe_txt).grid(row=0,column=i,padx=1,pady=1,sticky="ew")
        except Exception as e:print(f"Erro Chart4: {e}");ctk.CTkLabel(chart_actual_frame,text="Erro gráfico.").pack()

    # --- MÉTODOS DAS ABAS CRÉDITOS E DÉBITOS (COMO ESTAVAM NA VERSÃO ESTÁVEL) ---
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
        print("DEBUG_CREDITS: _load_initial_credits_data - INÍCIO")
        today = date.today()
        # Define o período padrão para o mês atual
        start_of_month_dt = today.replace(day=1)
        if today.month == 12:
            end_of_month_dt = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_of_month_dt = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        start_str = start_of_month_dt.strftime("%Y-%m-%d")
        end_str = end_of_month_dt.strftime("%Y-%m-%d")
        
        print(f"DEBUG_CREDITS: Período padrão definido para créditos: {start_str} a {end_str}")
        
        if hasattr(self, 'credits_start_date_entry') and self.credits_start_date_entry: # Verifica se o widget existe
            self.credits_start_date_entry.delete(0, ctk.END)
            self.credits_start_date_entry.insert(0, start_str)
        if hasattr(self, 'credits_end_date_entry') and self.credits_end_date_entry: # Verifica se o widget existe
            self.credits_end_date_entry.delete(0, ctk.END)
            self.credits_end_date_entry.insert(0, end_str)
        
        self._load_and_display_credits(start_str, end_str)
        print("DEBUG_CREDITS: _load_initial_credits_data - FIM")

    def _load_and_display_credits(self, start_date=None, end_date=None):
        print(f"DEBUG_CREDITS: _load_and_display_credits - Buscando de {start_date} a {end_date}")
        
        # Garante que o container da tabela exista
        if not hasattr(self, 'credits_table_grid_container') or not self.credits_table_grid_container:
            print("ERRO_CREDITS: credits_table_grid_container não encontrado!")
            return

        for w in self.credits_table_grid_container.winfo_children():
            if w.grid_info().get("row", 0) >= 2: # Mantém cabeçalhos na linha 0 e separador na linha 1
                w.destroy()
        
        transactions = db_manager.get_transactions('Crédito', start_date, end_date)
        print(f"DEBUG_CREDITS: Transações de crédito encontradas no DB: {len(transactions) if transactions else 0}")
        if transactions:
            for i, trans in enumerate(transactions):
                if i < 5: # Imprime apenas os primeiros 5 para não poluir o log
                    print(f"  DEBUG_CREDITS_DATA: {trans}")


        if not transactions:
            # Limpa qualquer label "sem dados" anterior para evitar duplicação
            for widget in self.credits_table_grid_container.winfo_children():
                if isinstance(widget, ctk.CTkLabel) and widget.grid_info().get("row", 0) >=2:
                    widget.destroy()
            ctk.CTkLabel(self.credits_table_grid_container, text="Nenhum crédito encontrado para o período.").grid(
                row=2, column=0, columnspan=len(self.credit_col_config) if hasattr(self, 'credit_col_config') else 5, pady=10)
            return
        
        current_row = 2 # Linhas de dados começam abaixo do cabeçalho e separador
        for t_id, data_val, valor, cat_nome, obs in transactions:
            print(f"DEBUG_CREDITS: Adicionando linha para crédito ID {t_id}, Data {data_val}")
            row_fg_color = ("gray98", "gray22") if current_row % 2 == 0 else ("gray92", "gray18")
            
            col_details = [
                (data_val, 0), 
                (f"R$ {valor:.2f}", 1), 
                (cat_nome, 2), 
                (obs if obs else "-", 3) # Adiciona '-' se obs for None ou vazia
            ]

            for col_idx_loop, (text_val, config_idx) in enumerate(col_details):
                cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
                cell_frame.grid(row=current_row, column=col_idx_loop, sticky="nsew")
                
                # Garante que self.credit_col_config existe e tem o índice esperado
                anchor_val = "w" # Padrão
                min_size_val = 100 # Padrão
                if hasattr(self, 'credit_col_config') and len(self.credit_col_config) > config_idx:
                    anchor_val = self.credit_col_config[config_idx]["anchor"]
                    min_size_val = self.credit_col_config[config_idx]["minsize"]

                wraplen_val = min_size_val - 10 if config_idx == 3 and min_size_val > 10 else 0 # Coluna de Observação
                
                label = ctk.CTkLabel(cell_frame, text=text_val, anchor=anchor_val, 
                                     wraplength=wraplen_val if wraplen_val > 0 else 0, 
                                     justify="left")
                label.pack(padx=5, pady=3, fill="both", expand=True)

            # Frame para botões de Ação
            actions_cell_frame = ctk.CTkFrame(self.credits_table_grid_container, fg_color=row_fg_color, corner_radius=0)
            actions_cell_frame.grid(row=current_row, column=4, sticky="nsew") # Coluna de Ações
            actions_cell_frame.grid_columnconfigure(0, weight=1); actions_cell_frame.grid_columnconfigure(1, weight=1)
            actions_cell_frame.grid_rowconfigure(0, weight=1)
            
            ctk.CTkButton(actions_cell_frame,text="✎",width=28,height=28,fg_color="transparent",text_color=("gray10","gray90"),hover_color=("gray70","gray30"),command=lambda edit_id=t_id:self._on_edit_credit_button_click(edit_id)).grid(row=0,column=0,padx=(0,2),pady=2,sticky="e")
            ctk.CTkButton(actions_cell_frame,text="✕",width=28,height=28,fg_color="transparent",text_color=("gray10","gray90"),hover_color=("gray70","gray30"),command=lambda del_id=t_id,del_desc=obs:self._confirm_delete_credit(del_id,del_desc)).grid(row=0,column=1,padx=(2,0),pady=2,sticky="w")
            current_row += 1
        print(f"DEBUG_CREDITS: _load_and_display_credits - FIM, {current_row - 2} linhas adicionadas.")
            
    def _on_filter_credits_button_click(self):
        start_date = self.credits_start_date_entry.get()
        end_date = self.credits_end_date_entry.get()
        try:
            datetime.strptime(start_date, "%Y-%m-%d"); datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Erro de Data", "Formato de data inválido. Use YYYY-MM-DD.", parent=self.controller)
            return
        self._load_and_display_credits(start_date, end_date)
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
        
        # --- ABA CARTÕES (COM CORREÇÕES E PREPARAÇÃO PARA EDIÇÃO DE FATURA) ---
    def _setup_cards_tab(self, tab_cards):
        # ... (incluindo os botões de fatura)
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
        self.card_list_col_config = [{"weight":1, "minsize": 120, "text":"Nome", "anchor":"w"}, {"weight":1, "minsize": 100, "text":"Bandeira", "anchor":"w"}]
        for i,cfg in enumerate(self.card_list_col_config):
            self.cards_list_grid_container.grid_columnconfigure(i,weight=cfg["weight"],minsize=cfg["minsize"]) 
            h_lbl=ctk.CTkLabel(self.cards_list_grid_container,text=cfg["text"],font=ctk.CTkFont(weight="bold"),anchor=cfg["anchor"],fg_color=("gray80","gray25"),padx=5,pady=3)
            h_lbl.grid(row=0,column=i,padx=(0,1 if i<len(self.card_list_col_config)-1 else 0),pady=(0,1),sticky="ew")
        
        self.invoice_details_block_frame = ctk.CTkFrame(cards_content_frame, fg_color=("gray90","gray17"))
        self.invoice_details_block_frame.grid(row=0, column=1, sticky="nsew", padx=(5,0), pady=0)
        self.invoice_details_block_frame.grid_remove() 
        
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
            if s:messagebox.showinfo("Sucesso",m if m else "Débito excluído.",parent=self.controller);self._on_filter_debits_button_click()
            else:messagebox.showerror("Erro",m if m else "Não foi possível excluir.",parent=self.controller)

    # --- NOVOS MÉTODOS PARA OS COMANDOS DO MENU FERRAMENTAS ---

    def _refresh_all_views(self):
        """Método auxiliar para atualizar os dados em todas as abas visíveis."""
        print("Atualizando todas as visualizações de dados...")
        # Atualiza a aba de créditos, se existir
        if hasattr(self, '_load_initial_credits_data'):
            self._load_initial_credits_data()
        
        # Atualiza a aba de débitos, se existir
        if hasattr(self, '_load_initial_debits_data'):
            self._load_initial_debits_data()
            
        # Atualiza a aba de cartões, se existir
        if hasattr(self, '_load_and_display_cards'):
            self._load_and_display_cards()
            # Garante que o painel de faturas seja escondido se nenhum cartão estiver selecionado
            if self.selected_card_id is None and hasattr(self, 'invoice_details_block_frame') and self.invoice_details_block_frame.winfo_ismapped():
                 self.invoice_details_block_frame.grid_remove()
                 self._reset_invoice_selection_and_buttons()
        
        # Atualiza a aba do dashboard, se existir
        if hasattr(self, '_update_all_dashboard_charts'):
            self._update_all_dashboard_charts()
        
        print("Atualização das visualizações concluída.")

    def _on_generate_test_data_click(self):
        """
        Lida com o clique em 'Gerar Dados de Teste'. Apaga os dados antigos e gera novos.
        """
        # Pergunta ao usuário se ele tem certeza, avisando que os dados atuais serão apagados.
        confirm = messagebox.askyesno(
            "Gerar Dados de Teste",
            "Isso irá apagar TODAS as transações, cartões e faturas existentes antes de gerar novos dados de teste.\n\nAs suas categorias NÃO serão afetadas.\n\nDeseja continuar?",
            icon='warning',
            parent=self.controller
        )
        
        if confirm:
            print("Confirmado. Apagando dados transacionais antigos...")
            # Primeiro, apaga os dados antigos
            db_manager.delete_all_transactional_data()
            
            print("Gerando novos dados de teste...")
            # Em seguida, gera os novos dados de teste
            db_manager.generate_test_data()
            
            messagebox.showinfo("Sucesso", "Novos dados de teste foram gerados com sucesso!", parent=self.controller)
            
            # Por fim, atualiza todas as telas para refletir os novos dados
            self._refresh_all_views()

    def _on_delete_test_data_click(self):
        """
        Lida com o clique em 'Apagar Dados de Teste'.
        """
        # Pergunta ao usuário se ele tem certeza da exclusão.
        confirm = messagebox.askyesno(
            "Apagar Dados de Teste",
            "Tem certeza que deseja apagar TODAS as transações (créditos e débitos), TODOS os cartões e TODAS as faturas de cartão?\n\nEsta ação não pode ser desfeita.\n\nAs suas categorias NÃO serão afetadas.",
            icon='warning',
            parent=self.controller
        )

        if confirm:
            print("Confirmado. Apagando todos os dados transacionais...")
            # Apaga todos os dados transacionais
            db_manager.delete_all_transactional_data()
            
            messagebox.showinfo("Sucesso", "Todos os dados de transações, cartões e faturas foram apagados.", parent=self.controller)
            
            # Atualiza todas as telas para refletir que os dados foram removidos
            self._refresh_all_views()

    # --- REMOVER OS MÉTODOS PLACEHOLDER ANTIGOS ---
    # def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste'")
    # def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste'")
    # Substituímos os dois acima pelos novos métodos _on_generate_test_data_click e _on_delete_test_data_click

    # ... (RESTANTE DA SUA CLASSE MAINAPPFRAME E O BLOCO if __name__ == '__main__' COMO ESTAVAM) ...
    def _sobre_confia(self): # Mantém este e os outros que não foram substituídos
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

    def _create_tabs(self):
        print("DEBUG_TABS: _create_tabs - INÍCIO")
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.pack(pady=10, padx=10, fill="both", expand=True)

        # Lista de nomes de abas (SEM "Cálculos")
        tab_names = ["Dashboard", "Créditos", "Débitos", "Cartões", "Relatórios/Insights"] 
        
        # Dicionário mapeando nome da aba para seu método de setup
        # --- GARANTA QUE "Cálculos" FOI REMOVIDO DESTE DICIONÁRIO ---
        tab_setup_methods = {
            "Dashboard": self._setup_dashboard_tab, 
            "Créditos": self._setup_credits_tab,
            "Débitos": self._setup_debits_tab, 
            "Cartões": self._setup_cards_tab,
            "Relatórios/Insights": self._setup_reports_tab
        }
        # --- FIM DA VERIFICAÇÃO ---

        for name in tab_names:
            print(f"DEBUG_TABS: Adicionando e configurando aba {name}...")
            tab = self.tab_view.add(name)
            attr_name = f"tab_{name.lower().replace('/','_').replace(' ','_')}"
            setattr(self, attr_name, tab)
            
            if name in tab_setup_methods: 
                # Verifica se o método de setup realmente existe antes de chamar
                if hasattr(self, tab_setup_methods[name].__name__):
                    tab_setup_methods[name](tab) 
                else:
                    print(f"AVISO: Método de setup para '{name}' NÃO ENCONTRADO, criando placeholder.")
                    ctk.CTkLabel(tab, text=f"Conteúdo de {name} em desenvolvimento.").pack(expand=True)
            # else: # Este else não é mais necessário se tab_names só tem chaves de tab_setup_methods
            #     ctk.CTkLabel(tab, text=f"Conteúdo de {name} Aqui").pack(expand=True) # Fallback
        
        print("DEBUG_TABS: Definindo aba inicial para 'Dashboard' com set()...")
        self.tab_view.set("Dashboard") 
        current_set_tab = self.tab_view.get()
        print(f"DEBUG_TABS: Aba atual APÓS set() é: '{current_set_tab}'")
        
        self.tab_view.configure(command=self._on_tab_change)
        
        if hasattr(self, "_on_tab_change") and callable(self._on_tab_change):
            print(f"DEBUG_TABS: Chamando _on_tab_change() para carregar conteúdo da aba '{current_set_tab}'...")
            self._on_tab_change() 
        print("DEBUG_TABS: _create_tabs - FIM")


    def _setup_dashboard_content_or_update(self, selected_year_value_for_cards=None): # Chamado por _on_tab_change para Dashboard
        print("DEBUG_DASH: _setup_dashboard_content_or_update - Chamado.")
        if hasattr(self, 'tab_dashboard'): 
            for widget in self.tab_dashboard.winfo_children(): widget.destroy()
            # Aqui virá a lógica de filtros e gráficos do Passo 73 quando formos implementar de fato
            ctk.CTkLabel(self.tab_dashboard, text="Dashboard - Conteúdo Real (Filtros e Gráficos) em Preparação",
                         font=ctk.CTkFont(size=18)).pack(pady=20, padx=20, expand=True, fill="both")
            print("DEBUG_DASH: Placeholder de conteúdo do dashboard (filtros/gráficos) renderizado.")
        else: print("DEBUG_DASH: ERRO - self.tab_dashboard não encontrado.")
        
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

    def _load_and_display_cards(self):
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

    def _on_card_selected(self,card_id,selected_rf):
        if self.last_selected_card_row_frame and self.last_selected_card_row_frame.winfo_exists():
            if hasattr(self.last_selected_card_row_frame,'original_bg_color'): self.last_selected_card_row_frame.configure(fg_color=self.last_selected_card_row_frame.original_bg_color)
            else: self.last_selected_card_row_frame.configure(fg_color=self.card_row_default_fg_color) 
        self.selected_card_id=card_id;self.edit_card_button.configure(state="normal");self.remove_card_button.configure(state="normal")
        if selected_rf and selected_rf.winfo_exists():
            if not hasattr(selected_rf,'original_bg_color'): selected_rf.original_bg_color = selected_rf.cget("fg_color")
            selected_rf.configure(fg_color=self.card_row_selected_fg_color);self.last_selected_card_row_frame=selected_rf
        self.current_invoice_year = date.today().year 
        if hasattr(self,'invoice_details_block_frame'):self.invoice_details_block_frame.grid(row=0,column=1,sticky="nsew",padx=(5,0),pady=0)
        self._setup_year_tabs()
        self._reset_invoice_selection_and_buttons()

    def _setup_year_tabs(self):
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

    def _on_year_tab_change(self):
        if not self.selected_card_id or not hasattr(self,'year_tab_view') or not self.year_tab_view.winfo_exists():return
        try:
            sel_y_str=self.year_tab_view.get()
            if sel_y_str:
                self.current_invoice_year=int(sel_y_str)
                self._load_and_display_invoice_details(self.selected_card_id,self.current_invoice_year)
        except ValueError:print(f"Erro: Aba ano '{sel_y_str}'")
        except Exception as e:print(f"Erro _on_year_tab_change: {e}")

    def _clear_invoice_details_panel(self): 
        if hasattr(self,'year_tab_view') and self.year_tab_view and self.year_tab_view.winfo_exists():self.year_tab_view.destroy();self.year_tab_view=None
        if hasattr(self,'invoice_details_grid_container'):
            for w in self.invoice_details_grid_container.winfo_children():
                if w.grid_info().get("row",0)>0:w.destroy() 
            ctk.CTkLabel(self.invoice_details_grid_container,text="Selecione um cartão e um ano.").grid(row=1,column=0,columnspan=12,pady=20)
        if hasattr(self,'invoice_details_block_frame') and self.selected_card_id is None and self.invoice_details_block_frame.winfo_ismapped():
            self.invoice_details_block_frame.grid_remove()
        self._reset_invoice_selection_and_buttons()

    def _reset_invoice_selection_and_buttons(self):
        self.selected_invoice_details = None
        if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="disabled")
        if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="disabled")
        if self.last_selected_invoice_cell_frame and self.last_selected_invoice_cell_frame.winfo_exists():
             if hasattr(self.last_selected_invoice_cell_frame, 'original_border_color_tuple'): # Usa a tupla
                self.last_selected_invoice_cell_frame.configure(
                    border_width=self.last_selected_invoice_cell_frame.original_border_width,
                    border_color=self.last_selected_invoice_cell_frame.original_border_color_tuple[0 if ctk.get_appearance_mode() == "Light" else 1]
                )
             else: # Fallback
                 self.last_selected_invoice_cell_frame.configure(border_width=1, border_color=self.invoice_cell_default_border_color[0 if ctk.get_appearance_mode() == "Light" else 1])
        self.last_selected_invoice_cell_frame = None

    def _load_and_display_invoice_details(self,card_id,year): # Implementa seleção de célula de fatura
        if not hasattr(self,'invoice_details_grid_container'):return
        for w in self.invoice_details_grid_container.winfo_children():
            if w.grid_info().get("row", 0) > 0: w.destroy()
        self._reset_invoice_selection_and_buttons()
        faturas=db_manager.get_faturas(card_id,year)
        if not faturas or all(v==0.0 for v in faturas.values()):
            ctk.CTkLabel(self.invoice_details_grid_container,text=f"Nenhuma fatura para {year}.").grid(row=1,column=0,columnspan=12,pady=10)
            return
        current_data_row = 1 
        for i in range(12): 
            month_number = i + 1
            valor_fatura = faturas.get(month_number,0.0)
            
            # Frame para cada célula que será clicável
            invoice_value_cell_frame = ctk.CTkFrame(self.invoice_details_grid_container, 
                                                    fg_color=self.invoice_cell_default_fg_color, 
                                                    corner_radius=3, cursor="hand2",
                                                    height=35, # Altura consistente
                                                    border_width=1, 
                                                    border_color=self.invoice_cell_default_border_color[0 if ctk.get_appearance_mode()=="Light" else 1])
            invoice_value_cell_frame.grid(row=current_data_row, column=i, padx=1, pady=1, sticky="nsew")
            invoice_value_cell_frame.grid_propagate(False) 
            
            invoice_value_cell_frame.invoice_details_data = {'card_id': card_id, 'year': year, 'month': month_number, 'value': valor_fatura}
            invoice_value_cell_frame.original_border_color_tuple = self.invoice_cell_default_border_color
            invoice_value_cell_frame.original_border_width = 1

            fatura_value_label = ctk.CTkLabel(invoice_value_cell_frame, text=f"R$ {valor_fatura:.2f}", anchor="center") # Centralizado na célula
            fatura_value_label.pack(padx=5, pady=5, fill="both", expand=True)
            
            invoice_value_cell_frame.bind("<Button-1>", lambda event, cell=invoice_value_cell_frame: self._on_invoice_cell_selected(cell))
            fatura_value_label.bind("<Button-1>", lambda event, cell=invoice_value_cell_frame: self._on_invoice_cell_selected(cell))
            
    def _on_invoice_cell_selected(self, cell_widget):
        if self.last_selected_invoice_cell_frame and self.last_selected_invoice_cell_frame.winfo_exists():
            if hasattr(self.last_selected_invoice_cell_frame, 'original_border_color_tuple'):
                self.last_selected_invoice_cell_frame.configure(
                    border_width=self.last_selected_invoice_cell_frame.original_border_width,
                    border_color=self.last_selected_invoice_cell_frame.original_border_color_tuple[0 if ctk.get_appearance_mode() == "Light" else 1]
                )
        self.selected_invoice_details = cell_widget.invoice_details_data
        if cell_widget and cell_widget.winfo_exists():
            if not hasattr(cell_widget, 'original_border_color_tuple'): 
                cell_widget.original_border_color_tuple = self.invoice_cell_default_border_color
                cell_widget.original_border_width = 1
            cell_widget.configure(border_width=2, border_color=self.invoice_cell_selected_border_color[0 if ctk.get_appearance_mode() == "Light" else 1]) 
            self.last_selected_invoice_cell_frame = cell_widget
        
        print(f"Fatura selecionada: {self.selected_invoice_details}")
        if hasattr(self, 'edit_invoice_button'): self.edit_invoice_button.configure(state="normal")
        if hasattr(self, 'remove_invoice_button'): self.remove_invoice_button.configure(state="normal")

    def _on_add_invoice_button_click(self):
        if not self.selected_card_id:
            messagebox.showwarning("Atenção", "Selecione um cartão.", parent=self.controller); return
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
            messagebox.showwarning("Atenção", "Selecione uma fatura para editar.", parent=self.controller); return
        if hasattr(self, 'dialog_upsert_invoice') and self.dialog_upsert_invoice is not None and self.dialog_upsert_invoice.winfo_exists():
            self.dialog_upsert_invoice.focus(); return
        data = self.selected_invoice_details 
        refresh_func = lambda c_id=data['card_id'], y=data['year']: self._load_and_display_invoice_details(c_id, y)
        self.dialog_upsert_invoice = UpsertInvoiceDialog(
            master=self.controller, controller=self.controller,
            refresh_callback=refresh_func,
            card_id=data['card_id'], year=data['year'], month=data['month'],
            current_value=data['value'], edit_mode=True
        )

    def _on_remove_invoice_button_click(self):
        if not self.selected_invoice_details:
            messagebox.showwarning("Atenção", "Selecione uma fatura para remover.", parent=self.controller); return
        data = self.selected_invoice_details
        month_names=["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
        month_name_str = month_names[data['month']-1] if 0 < data['month'] <= 12 else f"Mês {data['month']}"
        confirm = messagebox.askyesno("Confirmar Remoção", f"Remover fatura de {month_name_str}/{data['year']} (valor R$ {data['value']:.2f})?\n(Isso definirá o valor para 0.00).", parent=self.controller )
        if confirm:
            if db_manager.upsert_fatura(data['card_id'], data['year'], data['month'], 0.0): 
                messagebox.showinfo("Sucesso", "Fatura removida (valor definido para 0).", parent=self.controller)
                self._load_and_display_invoice_details(data['card_id'], data['year']) 
            else: messagebox.showerror("Erro", "Não foi possível remover a fatura.", parent=self.controller)
            
    # Placeholders para outras abas e callbacks de menu
    def _setup_reports_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Relatórios/Insights Aqui"); label.pack(pady=20, padx=20)
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário'")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha'")
    def _gerar_dados_teste(self): print("MainAppFrame: Ação 'Gerar Dados de Teste'")
    def _apagar_dados_teste(self): print("MainAppFrame: Ação 'Apagar Dados de Teste'")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", 
                      message="Confia - Seu App de Controle Financeiro Pessoal\nVersão 0.1.0\nDesenvolvido com Python e CustomTkinter")

    # --- Callbacks de Menu e Placeholders para abas restantes ---
    def _setup_calculations_tab(self, tab): pass # Aba removida
    def _setup_reports_tab(self, tab): label = ctk.CTkLabel(tab, text="Conteúdo de Relatórios/Insights Aqui"); label.pack(pady=20, padx=20)
    def _criar_novo_usuario(self): print("MainAppFrame: Ação 'Criar Novo Usuário'")
    def _alterar_senha(self): print("MainAppFrame: Ação 'Alterar Senha'")
    def _on_generate_test_data_click(self): 
        if messagebox.askyesno("Gerar Dados de Teste", "Apagar dados existentes (exceto categorias) e gerar novos dados de teste?", icon='warning', parent=self.controller):
            db_manager.delete_all_transactional_data(); db_manager.generate_test_data()
            messagebox.showinfo("Sucesso", "Novos dados de teste gerados!", parent=self.controller); self._refresh_all_views()
    def _on_delete_test_data_click(self):
        if messagebox.askyesno("Apagar Dados de Teste", "Apagar TODAS as transações, cartões e faturas?\nCategorias NÃO serão afetadas.", icon='warning', parent=self.controller):
            db_manager.delete_all_transactional_data()
            messagebox.showinfo("Sucesso", "Dados transacionais apagados.", parent=self.controller); self._refresh_all_views()
    def _refresh_all_views(self):
        print("Atualizando todas as visualizações..."); 
        if hasattr(self,'_load_initial_credits_data'):self._load_initial_credits_data()
        if hasattr(self,'_load_initial_debits_data'):self._load_initial_debits_data()
        if hasattr(self,'_load_and_display_cards'):self._load_and_display_cards()
        if hasattr(self,'_update_all_dashboard_charts'):self._update_all_dashboard_charts()
        print("Visualizações atualizadas.")
    def _sobre_confia(self):
        from customtkinter import CTkMessagebox 
        CTkMessagebox(master=self.controller, title="Sobre Confia", message="Confia - App Financeiro\nVersão 0.2.0")

# --- Bloco if __name__ == '__main__' (COMO NO PASSO 88) ---
if __name__ == '__main__':
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__(); self.title("Teste MainAppFrame - Dashboard"); self.geometry("1200x800"); ctk.set_appearance_mode("light")
            db_path = db_manager.DATABASE_PATH
            if not os.path.exists(db_manager.DATABASE_DIR): os.makedirs(db_manager.DATABASE_DIR)
            if os.path.exists(db_path): 
                try: os.remove(db_path)
                except PermissionError: print(f"AVISO: Não foi possível remover {db_path}.")
                except Exception as e: print(f"Erro ao remover DB: {e}")
            db_manager.initialize_database()
            # Adicionar dados de teste para popular os gráficos
            cat_alim_id = next((c[0] for c in db_manager.get_categories_by_type("Débito") if c[1] == "Alimentação"), 5)
            cat_trans_id = next((c[0] for c in db_manager.get_categories_by_type("Débito") if c[1] == "Transporte"), 6)
            cat_sal_id = next((c[0] for c in db_manager.get_categories_by_type("Crédito") if c[1] == "Salário"), 1)
            if cat_alim_id: db_manager.add_transaction(date.today().strftime("%Y-%m-%d"), "Supermercado Mês", 230.55, "Débito", cat_alim_id) 
            if cat_trans_id: db_manager.add_transaction((date.today() - timedelta(days=3)).strftime("%Y-%m-%d"), "Combustível", 150.00, "Débito", cat_trans_id) 
            if cat_sal_id: db_manager.add_transaction(date.today().strftime("%Y-%m-%d"), "Salário Maio", 3500.00, "Crédito", cat_sal_id)
            card_id = db_manager.add_card(nome="Visa Platinum Teste", bandeira="Visa", cor="#1E90FF")
            if card_id: db_manager.upsert_fatura(card_id, date.today().year, 1, 250.55)
            container=ctk.CTkFrame(self,fg_color="transparent"); container.pack(fill="both",expand=True)
            self.main_frame_instance = MainAppFrame(parent=container, controller=self); self.main_frame_instance.pack(fill="both",expand=True)
            # A aba Dashboard já deve ser a padrão pelo _create_tabs
        def _on_app_closing(self): self.destroy()
        def show_frame(self, name): print(f"Mock: show {name}")
    MockAppController().mainloop()