# C:\Confia\confia_app\category_management_frame.py
# Frame para gerenciar (visualizar e adicionar) categorias.

import customtkinter as ctk
import db_manager 
from tkinter import messagebox # Para diálogos de confirmação e informação

class AddCategoryDialog(ctk.CTkToplevel):
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.refresh_callback = refresh_callback

        self.title("Adicionar Nova Categoria")
        self.geometry("450x350") 
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Nome da Categoria:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(form_frame, width=250)
        self.name_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky="ew")

        ctk.CTkLabel(form_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.type_var = ctk.StringVar(value="Débito")
        type_options = ["Crédito", "Débito"]
        self.type_menu = ctk.CTkOptionMenu(form_frame, variable=self.type_var, values=type_options, width=250)
        self.type_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=10, sticky="ew")

        self.color_map = {
            "Verde": "#4CAF50", "Verde Claro": "#8BC34A", "Ciano": "#00BCD4", "Âmbar": "#FFC107",
            "Vermelho": "#F44336", "Roxo": "#9C27B0", "Índigo": "#3F51B5", "Laranja": "#FF9800",
            "Azul": "#2196F3", "Rosa": "#E91E63", "Cinza": "#9E9E9E", "Preto": "#000000"
        }
        color_names = list(self.color_map.keys())

        ctk.CTkLabel(form_frame, text="Cor:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.color_var = ctk.StringVar(value=color_names[0])
        self.color_menu = ctk.CTkOptionMenu(form_frame, variable=self.color_var, values=color_names, 
                                            command=self._update_color_preview, width=180)
        self.color_menu.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        self.color_preview_box = ctk.CTkFrame(form_frame, width=30, height=30, border_width=1)
        self.color_preview_box.grid(row=2, column=2, padx=(5,10), pady=10, sticky="w")
        self._update_color_preview() 

        form_frame.grid_columnconfigure(1, weight=1)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10, padx=20, side="bottom", fill="x")
        
        self.save_button = ctk.CTkButton(button_frame, text="Salvar", command=self._save_category)
        self.save_button.pack(side="right", padx=5)
        self.cancel_button = ctk.CTkButton(button_frame, text="Cancelar", command=self.destroy, fg_color="gray")
        self.cancel_button.pack(side="right", padx=5)
        
        self.name_entry.focus()

    def _update_color_preview(self, selected_color_name_event=None):
        selected_color_name = self.color_var.get()
        color_hex = self.color_map.get(selected_color_name, "#FFFFFF") 
        self.color_preview_box.configure(fg_color=color_hex)

    def _save_category(self):
        name = self.name_entry.get().strip()
        category_type = self.type_var.get()
        selected_color_name = self.color_var.get()
        color_hex = self.color_map.get(selected_color_name, "#808080")

        if not name:
            messagebox.showerror("Erro de Validação", "O nome da categoria não pode estar vazio.", parent=self)
            return
        
        if db_manager.add_category(name, category_type, color_hex):
            messagebox.showinfo("Sucesso", f"Categoria '{name}' adicionada com sucesso!", parent=self)
            self.refresh_callback()
            self.destroy()
        else:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível adicionar a categoria '{name}'.\nVerifique se já existe uma categoria com este nome.", parent=self)
            self.name_entry.focus()

class CategoryManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")

        title_label = ctk.CTkLabel(self, text="Gerenciar Categorias", 
                                   font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(10, 5), anchor="center")

        add_category_button = ctk.CTkButton(self, text="Adicionar Nova Categoria", 
                                            command=self._add_new_category_dialog)
        add_category_button.pack(pady=(5, 15), padx=20, anchor="w")

        main_lists_container = ctk.CTkFrame(self, fg_color="transparent")
        main_lists_container.pack(fill="both", expand=True, padx=10, pady=5)
        main_lists_container.grid_columnconfigure(0, weight=1)
        main_lists_container.grid_columnconfigure(1, weight=1)
        main_lists_container.grid_rowconfigure(0, weight=0) 
        main_lists_container.grid_rowconfigure(1, weight=1)

        credit_title = ctk.CTkLabel(main_lists_container, text="Categorias de Crédito", font=ctk.CTkFont(size=16))
        credit_title.grid(row=0, column=0, padx=5, pady=(5,5), sticky="w")
        self.scrollable_credit_list = ctk.CTkScrollableFrame(main_lists_container, label_text="")
        self.scrollable_credit_list.grid(row=1, column=0, padx=(0,5), pady=(0,5), sticky="nsew")

        debit_title = ctk.CTkLabel(main_lists_container, text="Categorias de Débito", font=ctk.CTkFont(size=16))
        debit_title.grid(row=0, column=1, padx=5, pady=(5,5), sticky="w")
        self.scrollable_debit_list = ctk.CTkScrollableFrame(main_lists_container, label_text="")
        self.scrollable_debit_list.grid(row=1, column=1, padx=(5,0), pady=(0,5), sticky="nsew")

    def _load_and_display_categories(self):
        for widget in self.scrollable_credit_list.winfo_children():
            widget.destroy()
        for widget in self.scrollable_debit_list.winfo_children():
            widget.destroy()

        credit_categories = db_manager.get_categories_by_type('Crédito')
        for cat_id, nome, cor, fixa in credit_categories:
            self._add_category_to_list_display(self.scrollable_credit_list, cat_id, nome, cor, fixa)

        debit_categories = db_manager.get_categories_by_type('Débito')
        for cat_id, nome, cor, fixa in debit_categories:
            self._add_category_to_list_display(self.scrollable_debit_list, cat_id, nome, cor, fixa)

    def _add_category_to_list_display(self, list_frame, cat_id: int, name: str, color_hex: str, is_fixed: int):
        entry_height = 35
        category_entry_frame = ctk.CTkFrame(list_frame, fg_color=("gray90", "gray25"), height=entry_height)
        category_entry_frame.pack_propagate(False) 
        category_entry_frame.pack(fill="x", pady=2, padx=2)

        category_entry_frame.grid_columnconfigure(0, weight=0, minsize=30) 
        category_entry_frame.grid_columnconfigure(1, weight=1)      
        category_entry_frame.grid_columnconfigure(2, weight=0, minsize=60) 
        category_entry_frame.grid_rowconfigure(0, weight=1)

        color_box = ctk.CTkFrame(category_entry_frame, width=20, height=20, 
                                 fg_color=color_hex if color_hex else "#808080", corner_radius=3)
        color_box.grid(row=0, column=0, padx=5, sticky="w") 

        category_name_label = ctk.CTkLabel(category_entry_frame, text=name, anchor="w")
        category_name_label.grid(row=0, column=1, padx=(0,5), sticky="ew")

        status_action_frame = ctk.CTkFrame(category_entry_frame, fg_color="transparent", height=entry_height-10)
        status_action_frame.grid(row=0, column=2, padx=5, sticky="e")
        status_action_frame.pack_propagate(False)
        status_action_frame.grid_rowconfigure(0, weight=1)
        status_action_frame.grid_columnconfigure(0, weight=1)

        if is_fixed:
            fixed_label = ctk.CTkLabel(status_action_frame, text="Fixa", text_color="gray", 
                                       font=ctk.CTkFont(size=10))
            fixed_label.grid(row=0, column=0, sticky="nsew")
        else:
            delete_button = ctk.CTkButton(
                status_action_frame, 
                text="✕", 
                width=28, height=28,
                fg_color="transparent", 
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda current_cat_id=cat_id, current_cat_name=name: self._confirm_delete_category(current_cat_id, current_cat_name)
            )
            delete_button.grid(row=0, column=0, sticky="nsew")

    def _confirm_delete_category(self, category_id: int, category_name: str):
        confirm = messagebox.askyesno(
            title="Confirmar Exclusão",
            message=f"Tem certeza que deseja excluir a categoria '{category_name}'?\nEsta ação não pode ser desfeita.",
            parent=self.controller 
        )
        if confirm:
            success, message = db_manager.delete_category(category_id) # Captura sucesso e mensagem
            if success:
                messagebox.showinfo("Sucesso", message, parent=self.controller)
                self._load_and_display_categories() 
            else:
                messagebox.showerror("Erro ao Excluir", message, parent=self.controller)
        else:
            print(f"Exclusão da categoria '{category_name}' cancelada pelo usuário.")

    def _add_new_category_dialog(self):
        if hasattr(self, 'dialog_add_category') and self.dialog_add_category is not None and self.dialog_add_category.winfo_exists():
            self.dialog_add_category.focus()
            return
        self.dialog_add_category = AddCategoryDialog(master=self.controller, 
                                                     refresh_callback=self._load_and_display_categories)

    def on_show_frame(self):
        self._load_and_display_categories()

if __name__ == '__main__':
    class MockAppController(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste CategoryManagementFrame")
            self.geometry("700x550") 
            ctk.set_appearance_mode("light")
            
            # Ajuste do caminho para o teste isolado funcionar corretamente
            # assumindo que db_manager.py está no mesmo nível que category_management_frame.py
            # e que a pasta 'database' está um nível acima de 'confia_app'
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_file_path_test = os.path.join(current_dir, '..', 'database', 'confia.db') 
            if os.path.exists(db_file_path_test):
                try:
                    os.remove(db_file_path_test)
                    print(f"BD de teste '{db_file_path_test}' removido.")
                except Exception as e:
                    print(f"Erro ao remover BD de teste: {e}")

            db_manager.initialize_database() 
            
            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(fill="both", expand=True)
            
            self.category_frame_instance = CategoryManagementFrame(parent=container, controller=self)
            self.category_frame_instance.pack(fill="both", expand=True)
            
            if hasattr(self.category_frame_instance, 'on_show_frame'):
                 self.category_frame_instance.on_show_frame()

        def show_frame(self, frame_name):
            print(f"MockAppController: show_frame chamada para '{frame_name}'")

        def _on_app_closing(self):
            print("MockAppController: _on_app_closing chamada.")
            self.destroy()

    mock_app = MockAppController()
    mock_app.mainloop()