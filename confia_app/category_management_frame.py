# C:\Confia\confia_app\category_management_frame.py
# Módulo para o frame de gerenciamento de categorias.

import customtkinter as ctk
from tkinter import ttk, messagebox
import db_manager # Para interagir com o banco de dados

class AddCategoryDialog(ctk.CTkToplevel):
    def __init__(self, master, controller, refresh_callback):
        super().__init__(master)
        self.controller = controller
        self.refresh_callback = refresh_callback
        
        self.title("Adicionar Nova Categoria")
        self.geometry("450x300")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        # Paleta de cores sugeridas
        self.color_map = {
            "Vermelho": "#FF0000", "Verde": "#00FF00", "Azul": "#0000FF",
            "Amarelo": "#FFFF00", "Laranja": "#FFA500", "Roxo": "#800080",
            "Rosa": "#FFC0CB", "Marrom": "#A52A2A", "Cinza": "#808080",
            "Preto": "#000000", "Branco": "#FFFFFF", 
            "Turquesa": "#40E0D0", "Magenta": "#FF00FF", "Lima": "#00FF00",
            "Oliva": "#808000", "Salmão": "#FA8072"
        }
        self.color_names = list(self.color_map.keys())

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        main_frame.grid_columnconfigure(1, weight=1) # Para o entry expandir

        # Nome da Categoria
        ctk.CTkLabel(main_frame, text="Nome da Categoria:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(main_frame, width=250)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky="ew")

        # Tipo da Categoria (Crédito ou Débito)
        ctk.CTkLabel(main_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Débito") # Padrão para Débito
        self.type_menu = ctk.CTkOptionMenu(main_frame, variable=self.type_var, values=["Débito", "Crédito"], width=250)
        self.type_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=10, sticky="ew")

        # Cor da Categoria
        ctk.CTkLabel(main_frame, text="Cor:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.color_var = ctk.StringVar(value=self.color_names[0]) # Padrão para a primeira cor da lista
        self.color_menu = ctk.CTkOptionMenu(main_frame, variable=self.color_var, values=self.color_names, command=self._update_color_preview, width=180)
        self.color_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        self.color_preview_box = ctk.CTkFrame(main_frame, width=30, height=30, border_width=1)
        self.color_preview_box.grid(row=2, column=2, padx=(5,10), pady=10, sticky="w")
        self._update_color_preview() # Chama para definir a cor inicial do preview

        # Botões
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=(10,20), padx=20, side="bottom", fill="x") # anchor="e" para alinhar à direita
        
        # Centralizar botões no button_frame
        button_frame.grid_columnconfigure(0, weight=1) # Coluna vazia para empurrar
        button_frame.grid_columnconfigure(1, weight=0) # Botão Salvar
        button_frame.grid_columnconfigure(2, weight=0) # Botão Cancelar
        button_frame.grid_columnconfigure(3, weight=1) # Coluna vazia para empurrar

        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_category_action)
        self.save_button.grid(row=0, column=1, padx=(0,5))

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.grid(row=0, column=2)
        
        self.name_entry.focus() # Foco inicial no campo de nome

    def _update_color_preview(self, selected_color_name_event=None):
        """Atualiza a cor da caixa de preview baseada na seleção do OptionMenu."""
        selected_name = self.color_var.get()
        hex_color = self.color_map.get(selected_name, "#FFFFFF") # Padrão branco se não encontrar
        self.color_preview_box.configure(fg_color=hex_color)

    def _save_category_action(self):
        nome = self.name_entry.get().strip()
        tipo = self.type_var.get()
        cor_nome = self.color_var.get()
        cor_hex = self.color_map.get(cor_nome, "#808080") # Pega o HEX, default cinza

        if not nome:
            messagebox.showerror("Erro de Validação", "O nome da categoria é obrigatório.", parent=self)
            return
        if not tipo: # Deveria sempre ter um valor, mas por segurança
            messagebox.showerror("Erro de Validação", "O tipo da categoria é obrigatório.", parent=self)
            return

        if db_manager.add_category(nome, tipo, cor_hex):
            messagebox.showinfo("Sucesso", f"Categoria '{nome}' adicionada com sucesso!", parent=self.master.master) # parent do master para MainAppFrame
            self.refresh_callback() # Chama a função para atualizar a lista de categorias
            self.destroy() # Fecha o diálogo
        else:
            # A função add_category já imprime um erro no console em caso de falha ou duplicidade
            messagebox.showerror("Erro no Banco", f"Não foi possível adicionar a categoria '{nome}'.\nVerifique se já existe uma categoria com este nome.", parent=self)

class CategoryManagementFrame(ctk.CTkFrame):
    def __init__(self, master, controller, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Faz a Treeview expandir

        self.dialog_add_category = None

        # Título do Frame
        title_label = ctk.CTkLabel(self, text="Gerenciamento de Categorias", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, padx=20, pady=(20,10), sticky="w")

        # Frame para botões e filtros (se houver)
        top_action_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_action_frame.grid(row=1, column=0, padx=20, pady=(0,10), sticky="ew")

        self.add_category_button = ctk.CTkButton(top_action_frame, text="Adicionar Nova Categoria", command=self._on_add_category_click)
        self.add_category_button.pack(side="left")
        
        # Frame para a Treeview e Scrollbar
        tree_frame = ctk.CTkFrame(self)
        tree_frame.grid(row=2, column=0, padx=20, pady=(0,10), sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Estilo da Treeview
        style = ttk.Style(self)
        # Configurações gerais do tema da treeview
        style.theme_use("default") # Pode ser 'clam', 'alt', 'default', 'classic'

        # Cores baseadas no tema do CustomTkinter
        bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"]) # Azul do botão para seleção
        
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color, 
                        rowheight=25,
                        font=('Segoe UI', 10)) # Fonte um pouco menor para a tabela
        style.map("Treeview", background=[('selected', selected_color)], foreground=[('selected', "white")])
        style.configure("Treeview.Heading", 
                        background=self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"]), 
                        foreground=text_color, 
                        font=('Segoe UI', 11, 'bold'),
                        relief="flat")
        style.map("Treeview.Heading", background=[('active', self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"]))])


        # Treeview para exibir categorias
        self.category_tree = ttk.Treeview(tree_frame, columns=("id", "nome", "tipo", "cor_display", "fixa"), show="headings", style="Treeview")
        self.category_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar para a Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.category_tree.configure(yscrollcommand=scrollbar.set)

        # Definindo os cabeçalhos
        self.category_tree.heading("id", text="ID")
        self.category_tree.heading("nome", text="Nome")
        self.category_tree.heading("tipo", text="Tipo")
        self.category_tree.heading("cor_display", text="Cor")
        self.category_tree.heading("fixa", text="Status")

        # Definindo a largura das colunas e alinhamento
        self.category_tree.column("id", width=50, anchor="center", stretch=False)
        self.category_tree.column("nome", width=200, stretch=True)
        self.category_tree.column("tipo", width=100, anchor="center")
        self.category_tree.column("cor_display", width=80, anchor="center") # Coluna para o quadrado de cor
        self.category_tree.column("fixa", width=80, anchor="center")
        
        # Canvas para desenhar cores (será usado ao popular a treeview)
        # Não é mais necessário criar um canvas separado para cada cor,
        # podemos usar um truque com tags e a coluna "cor_display" mais tarde,
        # ou simplesmente exibir o código HEX da cor.
        # Por simplicidade, vamos exibir o HEX e o usuário pode adicionar um preview visual se desejar.

        # Adicionar tag para cores de fundo das células de cor
        self.category_tree.tag_configure('color_cell_tag', background='white') # Placeholder, será configurado dinamicamente


        # Botão para voltar ao MainAppFrame
        back_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        back_button_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.back_button = ctk.CTkButton(back_button_frame, text="Voltar ao Menu Principal", command=lambda: controller.show_frame("MainAppFrame"))
        self.back_button.pack(side="left") # Alinha à esquerda

        # Botão para excluir categoria selecionada
        self.delete_category_button = ctk.CTkButton(back_button_frame, text="Excluir Selecionada", command=self._on_delete_category_click, fg_color="red", hover_color="#B22222")
        self.delete_category_button.pack(side="right") # Alinha à direita

        # Carregar categorias na Treeview
        self.load_categories()

    def _on_add_category_click(self):
        """Abre o diálogo para adicionar uma nova categoria."""
        if self.dialog_add_category is None or not self.dialog_add_category.winfo_exists():
            self.dialog_add_category = AddCategoryDialog(self, self.controller, self.load_categories)
            self.dialog_add_category.focus() # Traz o diálogo para frente e foca
        else:
            self.dialog_add_category.focus()

    def _on_delete_category_click(self):
        """Exclui a categoria selecionada na Treeview."""
        selected_item = self.category_tree.focus() # Pega o item focado/selecionado
        if not selected_item:
            messagebox.showwarning("Nenhuma Seleção", "Por favor, selecione uma categoria para excluir.", parent=self)
            return

        category_data = self.category_tree.item(selected_item)
        category_id = category_data["values"][0]
        category_name = category_data["values"][1]
        is_fixed_status = category_data["values"][4]

        if is_fixed_status == "Fixa":
            messagebox.showerror("Exclusão Não Permitida", f"A categoria '{category_name}' é fixa e não pode ser excluída.", parent=self)
            return

        confirm = messagebox.askyesno("Confirmar Exclusão", 
                                      f"Tem certeza que deseja excluir a categoria '{category_name}'?\nEsta ação não pode ser desfeita.", 
                                      parent=self)
        if confirm:
            success, message = db_manager.delete_category(category_id)
            if success:
                messagebox.showinfo("Sucesso", message, parent=self)
                self.load_categories() # Recarrega a lista
            else:
                messagebox.showerror("Erro ao Excluir", message, parent=self)


    def load_categories(self):
        """Carrega as categorias do banco de dados e as exibe na Treeview."""
        # Limpa a treeview antes de carregar novos dados
        for i in self.category_tree.get_children():
            self.category_tree.delete(i)

        # Busca categorias de Crédito e Débito
        categories = []
        credit_categories = db_manager.get_categories_by_type('Crédito')
        if credit_categories:
            categories.extend(credit_categories)
        
        debit_categories = db_manager.get_categories_by_type('Débito')
        if debit_categories:
            categories.extend(debit_categories)

        if not categories:
            # Exibe uma mensagem se não houver categorias
            self.category_tree.insert("", "end", values=("", "Nenhuma categoria encontrada", "", "", ""))
            return

        # Adiciona categorias à Treeview
        for cat_id, nome, cor_hex, fixa_status_db in categories:
            status_text = "Fixa" if fixa_status_db == 1 else "Editável"
            # Para a coluna 'cor_display', podemos mostrar o HEX ou um pequeno quadrado de cor
            # Por enquanto, vamos mostrar o HEX.
            # Para desenhar um quadrado de cor, precisaríamos de um Canvas por linha ou usar tags com `itemconfigure`
            
            # Adiciona os dados
            item_id = self.category_tree.insert("", "end", values=(cat_id, nome, 
                                                                   "Crédito" if any(c[0] == cat_id for c in credit_categories) else "Débito", 
                                                                   cor_hex, 
                                                                   status_text))
            
            # Configura a tag para a cor da célula "cor_display"
            # O nome da tag deve ser único por cor para funcionar corretamente.
            # Se for apenas para cor de texto, é mais simples.
            # Para cor de fundo da célula é mais complexo com ttk.Treeview.
            # Vamos apenas mostrar o código HEX por enquanto para simplificar.
            # Se quisermos um quadrado colorido, precisaríamos de um truque ou usar uma imagem de 1x1 pixel colorida.

        # Se você quiser tentar colorir o texto da cor:
        # for child_item in self.category_tree.get_children():
        #     item_values = self.category_tree.item(child_item, 'values')
        #     color_hex_for_text = item_values[3] # O código HEX da cor
        #     try:
        #         self.category_tree.tag_configure(f"color_{color_hex_for_text}", foreground=color_hex_for_text)
        #         self.category_tree.item(child_item, tags=(f"color_{color_hex_for_text}",))
        #     except Exception as e:
        #         print(f"Erro ao aplicar tag de cor {color_hex_for_text}: {e}")


if __name__ == '__main__':
    # Código de teste para o CategoryManagementFrame (opcional)
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste Gerenciamento de Categorias")
            self.geometry("700x500")
            ctk.set_appearance_mode("light") # or "dark"

            # Garante que o DB exista para os testes
            db_manager.initialize_database() 
            # Adicionar algumas categorias de teste se o DB estiver vazio
            if not db_manager.get_categories_by_type("Crédito") and not db_manager.get_categories_by_type("Débito"):
                db_manager.add_category("Salário Teste", "Crédito", "#4CAF50")
                db_manager.add_category("Alimentação Teste", "Débito", "#F44336")


            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(fill="both", expand=True)
            
            self.category_frame = CategoryManagementFrame(parent=container, controller=self)
            self.category_frame.pack(fill="both", expand=True)

        def show_frame(self, page_name):
            print(f"MockApp: Tentando mostrar frame: {page_name}")
            if page_name == "MainAppFrame":
                # Simula voltar para uma tela principal (que não existe neste mock)
                print("MockApp: Voltaria para MainAppFrame")
                self.category_frame.pack_forget() # Esconde o frame de categorias
                # Poderia recriar um label simples para simular
                ctk.CTkLabel(self, text="Simulando MainAppFrame").pack(expand=True, fill="both")


    app = MockAppController()
    app.mainloop()