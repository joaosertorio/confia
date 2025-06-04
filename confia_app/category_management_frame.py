# C:\Confia\confia_app\category_management_frame.py
import customtkinter as ctk
from tkinter import ttk, messagebox, font as tkFont # Adicionado tkFont
import db_manager
import matplotlib.colors as mcolors

class AddCategoryDialog(ctk.CTkToplevel):
    def __init__(self, master, controller, refresh_callback): 
        super().__init__(master)
        self.controller = controller 
        self.refresh_callback = refresh_callback
        self.title("Adicionar Nova Categoria")
        self.geometry("450x300"); self.resizable(False, False); self.transient(master); self.grab_set()
        self.color_map = { "Vermelho": "#FF0000", "Verde": "#00FF00", "Azul": "#0000FF", "Amarelo": "#FFFF00", "Laranja": "#FFA500", "Roxo": "#800080", "Rosa": "#FFC0CB", "Marrom": "#A52A2A", "Cinza": "#808080", "Preto": "#000000", "Branco": "#FFFFFF", "Turquesa": "#40E0D0", "Magenta": "#FF00FF", "Lima": "#32CD32", "Oliva": "#808000", "Salmão": "#FA8072", "Ciano": "#00FFFF", "Azul Claro": "#ADD8E6", "Verde Claro": "#90EE90"}
        self.color_names = list(self.color_map.keys())
        main_frame = ctk.CTkFrame(self, fg_color="transparent"); main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1) 
        ctk.CTkLabel(main_frame, text="Nome da Categoria:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(main_frame, width=250); self.name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky="ew")
        ctk.CTkLabel(main_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Débito") 
        self.type_menu = ctk.CTkOptionMenu(main_frame, variable=self.type_var, values=["Débito", "Crédito"], width=250); self.type_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=10, sticky="ew")
        ctk.CTkLabel(main_frame, text="Cor:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.color_var = ctk.StringVar(value=self.color_names[0]) 
        self.color_menu = ctk.CTkOptionMenu(main_frame, variable=self.color_var, values=self.color_names, command=self._update_color_preview, width=180); self.color_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        self.color_preview_box = ctk.CTkFrame(main_frame, width=30, height=30, border_width=1); self.color_preview_box.grid(row=2, column=2, padx=(5,10), pady=10, sticky="w")
        self._update_color_preview() 
        button_frame = ctk.CTkFrame(self, fg_color="transparent"); button_frame.pack(pady=(10,20), padx=20, side="bottom", fill="x") 
        button_frame.grid_columnconfigure(0, weight=1); button_frame.grid_columnconfigure(1, weight=0); button_frame.grid_columnconfigure(2, weight=0); button_frame.grid_columnconfigure(3, weight=1)
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_category_action); self.save_button.grid(row=0, column=1, padx=(0,5))
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray"); self.cancel_button.grid(row=0, column=2)
        self.name_entry.focus()
    def _update_color_preview(self, selected_color_name_event=None):
        selected_name = self.color_var.get(); hex_color = self.color_map.get(selected_name, "#FFFFFF"); self.color_preview_box.configure(fg_color=hex_color)
    def _save_category_action(self):
        nome = self.name_entry.get().strip(); tipo = self.type_var.get(); cor_nome = self.color_var.get()
        cor_hex = self.color_map.get(cor_nome, "#808080")
        if not nome: messagebox.showerror("Erro", "Nome da categoria é obrigatório.", parent=self); return
        if not tipo: messagebox.showerror("Erro", "Tipo da categoria é obrigatório.", parent=self); return
        if db_manager.add_category(nome, tipo, cor_hex, fixa=0): 
            messagebox.showinfo("Sucesso", f"Categoria '{nome}' adicionada!", parent=self.master) 
            self.refresh_callback(); self.destroy()
        else: messagebox.showerror("Erro", f"Não foi possível adicionar '{nome}'. Verifique se já existe.", parent=self)
    pass
class CategoryManagementFrame(ctk.CTkToplevel):
    def __init__(self, master_app_controller, **kwargs):
        super().__init__(master_app_controller, **kwargs)
        
        print("DEBUG_CAT: CategoryManagementFrame (Toplevel) __init__ - INÍCIO")
        self.app_controller = master_app_controller 
        
        self.title("Gerenciar Categorias")
        self.geometry("700x550")
        self.resizable(False, False)
        self.transient(master_app_controller) 
        self.grab_set() 

        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            bg_app_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1] if isinstance(ctk.ThemeManager.theme["CTkFrame"]["fg_color"], tuple) else ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        else:
            bg_app_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][0] if isinstance(ctk.ThemeManager.theme["CTkFrame"]["fg_color"], tuple) else ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        self.configure(fg_color=bg_app_color) 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0) 
        self.grid_rowconfigure(2, weight=1) # Linha da Treeview para expandir
        self.grid_rowconfigure(3, weight=0) 

        self.dialog_add_category = None
        
        # Chamada para o método que cria os widgets
        self._create_widgets() 
        
        # Carrega as categorias na Treeview
        self.load_categories() 
        print("DEBUG_CAT: CategoryManagementFrame (Toplevel) __init__ - FIM") 

    def _create_widgets(self):
        print("DEBUG_CAT: _create_widgets - INÍCIO")
        # Título do Frame
        title_label = ctk.CTkLabel(self, text="Gerenciamento de Categorias", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20,10), sticky="w")

        # Frame para botões e filtros (se houver)
        top_action_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_action_frame.grid(row=1, column=0, padx=20, pady=(0,10), sticky="ew")

        self.add_category_button = ctk.CTkButton(top_action_frame, text="Adicionar Nova Categoria", command=self._on_add_category_click)
        self.add_category_button.pack(side="left")
        
        # Frame para a Treeview e Scrollbar
        tree_frame = ctk.CTkFrame(self) # Sem cor de fundo explícita, herda do Toplevel
        tree_frame.grid(row=2, column=0, padx=20, pady=(0,10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Estilo da Treeview (Simplificado por enquanto, mas funcional)
        style = ttk.Style(self)
        style.theme_use("default") 

        # Tenta aplicar cores do tema CustomTkinter de forma segura
        try:
            current_mode = ctk.get_appearance_mode()
            tree_bg_color_tuple = ctk.ThemeManager.theme["CTkScrollableFrame"]["fg_color"]
            tree_text_color_tuple = ctk.ThemeManager.theme["CTkLabel"]["text_color"]
            tree_selected_color_tuple = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
            heading_bg_tuple = ctk.ThemeManager.theme["CTkButton"]["hover_color"]
            heading_active_bg_tuple = ctk.ThemeManager.theme["CTkButton"]["fg_color"]

            tree_bg_color = tree_bg_color_tuple[0] if current_mode == "Light" else tree_bg_color_tuple[1]
            tree_text_color = tree_text_color_tuple[0] if current_mode == "Light" else tree_text_color_tuple[1]
            tree_selected_color = tree_selected_color_tuple[0] if current_mode == "Light" else tree_selected_color_tuple[1]
            
            # Verifica se a cor é uma string de nome de cor CTk e converte para HEX se necessário
            # Esta é uma suposição, pode precisar de uma função de conversão mais robusta do CTk
            if isinstance(tree_bg_color, str) and "gray" in tree_bg_color: tree_bg_color = "#EBEBEB" if current_mode == "Light" else "#2B2B2B"
            if isinstance(tree_text_color, str) and "gray" in tree_text_color: tree_text_color = "#1F1F1F" if current_mode == "Light" else "#DCE4EE"
            if isinstance(tree_selected_color, str) and "gray" in tree_selected_color: tree_selected_color = "#3B8ED0" # Azul padrão

            style.configure("Treeview", background=tree_bg_color, foreground=tree_text_color, fieldbackground=tree_bg_color, rowheight=28, font=('Segoe UI', 11))
            selected_text_color = "white" if sum(mcolors.to_rgb(tree_selected_color if mcolors.is_color_like(tree_selected_color) else "#0000FF")) < 1.5 else "black"
            style.map("Treeview", background=[('selected', tree_selected_color)], foreground=[('selected', selected_text_color)])
            
            style.configure("Treeview.Heading", background=self._apply_appearance_mode(heading_bg_tuple), foreground=tree_text_color, font=('Segoe UI', 12, 'bold'), relief="flat", padding=(5,5))
            style.map("Treeview.Heading", background=[('active', self._apply_appearance_mode(heading_active_bg_tuple))])
            print("DEBUG_CAT: Estilo da Treeview configurado com cores do tema.")
        except Exception as e_style:
            print(f"AVISO_CAT_STYLE: Erro ao aplicar estilo completo da Treeview: {e_style}. Usando estilo default.")
            style.configure("Treeview", rowheight=28, font=('Segoe UI', 11)) # Estilo mínimo de fallback
            style.configure("Treeview.Heading", font=('Segoe UI', 12, 'bold'), padding=(5,5))


        # Treeview para exibir categorias (coluna 'id' não será exibida)
        self.column_keys = ("id", "nome", "tipo", "cor_hex", "status")
        self.display_columns = ("nome", "tipo", "cor_hex", "status")
        
        self.category_tree = ttk.Treeview(tree_frame, columns=self.column_keys, displaycolumns=self.display_columns, show="headings", style="Treeview")
        self.category_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.category_tree.configure(yscrollcommand=scrollbar.set)

        # Definindo os cabeçalhos para as colunas visíveis
        self.category_tree.heading("nome", text="Nome da Categoria")
        self.category_tree.heading("tipo", text="Tipo")
        self.category_tree.heading("cor_hex", text="Cor (Hex)")
        self.category_tree.heading("status", text="Status")

        # Definindo a largura das colunas visíveis
        self.category_tree.column("nome", width=250, stretch=True)
        self.category_tree.column("tipo", width=100, anchor="center")
        self.category_tree.column("cor_hex", width=120, anchor="w") 
        self.category_tree.column("status", width=100, anchor="center")
        
        back_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        back_button_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.back_button = ctk.CTkButton(back_button_frame, text="Fechar Janela", command=self.destroy) 
        self.back_button.pack(side="left")
        self.delete_category_button = ctk.CTkButton(back_button_frame, text="Excluir Selecionada", command=self._on_delete_category_click, fg_color="red", hover_color="#B22222")
        self.delete_category_button.pack(side="right")
        print("DEBUG_CAT: _create_widgets - FIM")

    def _on_add_category_click(self):
        if self.dialog_add_category is None or not self.dialog_add_category.winfo_exists():
            self.dialog_add_category = AddCategoryDialog(master=self, controller=self.app_controller, refresh_callback=self.load_categories)
            self.dialog_add_category.focus()
        else:
            self.dialog_add_category.focus()

    def _on_delete_category_click(self):
        selected_item = self.category_tree.focus() 
        if not selected_item: messagebox.showwarning("Nenhuma Seleção", "Selecione uma categoria para excluir.", parent=self); return
        
        item_values = self.category_tree.item(selected_item, "values")
        if not item_values or len(item_values) < len(self.column_keys):
            messagebox.showerror("Erro", "Não foi possível obter os dados da categoria selecionada.", parent=self)
            return

        # Mapeia os valores para um dicionário baseado em column_keys para segurança
        category_data_dict = dict(zip(self.column_keys, item_values))

        category_id = category_data_dict.get("id")
        category_name = category_data_dict.get("nome")
        is_fixed_status_text = category_data_dict.get("status")

        if category_id is None or category_name is None or is_fixed_status_text is None:
            messagebox.showerror("Erro", "Dados da categoria incompletos ou inválidos.", parent=self)
            return
        
        if is_fixed_status_text == "Fixa": 
            messagebox.showerror("Exclusão Não Permitida", f"A categoria '{category_name}' é fixa e não pode ser excluída.", parent=self)
            return
        
        confirm = messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir a categoria '{category_name}'?\nEsta ação não pode ser desfeita.", parent=self)
        if confirm:
            success, message = db_manager.delete_category(int(category_id)) # Garante que ID é int
            if success: messagebox.showinfo("Sucesso", message, parent=self); self.load_categories()
            else: messagebox.showerror("Erro ao Excluir", message, parent=self)

    def load_categories(self):
        print("DEBUG_CAT: load_categories - INÍCIO")
        if not hasattr(self, 'category_tree'): # Verifica se a treeview existe
            print("DEBUG_CAT: Treeview ainda não criada, load_categories abortado.")
            return
            
        for i in self.category_tree.get_children(): self.category_tree.delete(i)
        
        categories = []
        credit_categories = db_manager.get_categories_by_type('Crédito')
        if credit_categories: categories.extend(credit_categories)
        debit_categories = db_manager.get_categories_by_type('Débito')
        if debit_categories: categories.extend(debit_categories)

        if not categories: 
            self.category_tree.insert("", "end", values=("", "Nenhuma categoria encontrada", "", "", ""))
            return
        
        for cat_id, nome, cor_hex, fixa_status_db in categories:
            status_text = "Fixa" if fixa_status_db == 1 else "Editável"
            tipo_texto = ""
            if credit_categories and any(c[0] == cat_id for c in credit_categories): tipo_texto = "Crédito"
            elif debit_categories and any(c[0] == cat_id for c in debit_categories): tipo_texto = "Débito"
            
            # values deve corresponder à ordem em self.column_keys
            self.category_tree.insert("", "end", values=(cat_id, nome, tipo_texto, cor_hex, status_text))
        print("DEBUG_CAT: load_categories - FIM")