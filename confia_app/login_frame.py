# C:\Confia\confia_app\login_frame.py
import customtkinter as ctk
# Não precisamos importar MainAppFrame aqui. O controller cuidará disso.

# C:\Confia\confia_app\login_frame.py
import customtkinter as ctk

class LoginFrame(ctk.CTkFrame): 
    def __init__(self, master, controller, **kwargs): # controller é um parâmetro nomeado
        # Remove 'controller' de kwargs se ele estiver lá (improvável com a chamada atual, mas seguro)
        # A forma como chamamos em main.py (controller=self) já o separa de kwargs
        # No entanto, para garantir robustez em como CTkFrame pode passar kwargs para CTkBaseClass:
        
        # Opção mais segura: passar explicitamente apenas os kwargs que CTkFrame espera, 
        # ou garantir que 'controller' não esteja em kwargs.
        # Como 'controller' é nomeado na nossa assinatura, ele não estará em kwargs aqui.
        # O problema é mais abaixo na cadeia de super().
        
        # Vamos tentar uma abordagem mais explícita para o super()
        # Pegamos os kwargs que CTkFrame aceita e passamos apenas eles.
        # Ou, mais simples, CTkFrame deve lidar com kwargs extras e não passar para CTkBaseClass
        # se não forem dele.
        # O erro indica que 'controller' está chegando ao check_kwargs_empty do CTkBaseClass.

        # Solução: Não passar controller para o super().__init__
        # kwargs aqui não deve conter 'controller' porque ele foi pego pela assinatura.
        # O problema é que o CTkFrame pode passar **kwargs para seu super,
        # e esse kwargs ainda pode conter controller se não foi "consumido".
        
        # Tentativa mais robusta:
        # Assegura que kwargs não contenha 'controller' ao chamar o super construtor de CTkFrame
        local_kwargs = {k: v for k, v in kwargs.items() if k != 'controller'}
        super().__init__(master, **local_kwargs)
        
        self.controller = controller 
        self.configure(fg_color="transparent")

        self._focus_after_id = None 
        self._create_widgets()
        
        if self.winfo_exists() and hasattr(self, 'user_entry') and self.user_entry.winfo_exists():
            self._focus_after_id = self.after(200, self._set_initial_focus)

    def _set_initial_focus(self):
        # Garante que o foco seja definido apenas se o widget ainda existir
        if self.winfo_exists() and hasattr(self, 'user_entry') and self.user_entry.winfo_exists(): 
            self.user_entry.focus()

    def _create_widgets(self):
        # ... (o restante do método _create_widgets como estava na sua versão funcional)
        main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_content_frame.pack(pady=20, padx=60, fill="both", expand=True)

        title_label = ctk.CTkLabel(main_content_frame, text="Confia", font=ctk.CTkFont(family="Montserrat", size=36, weight="bold"))
        title_label.pack(pady=(20, 30))

        user_label = ctk.CTkLabel(main_content_frame, text="Usuário")
        user_label.pack(pady=(10,0), padx=10, anchor="w")
        self.user_entry = ctk.CTkEntry(main_content_frame, placeholder_text="Seu nome de usuário")
        self.user_entry.pack(pady=(0,10), padx=10, fill="x")

        password_label = ctk.CTkLabel(main_content_frame, text="Senha")
        password_label.pack(pady=(10,0), padx=10, anchor="w")
        self.password_entry = ctk.CTkEntry(main_content_frame, placeholder_text="Sua senha", show="*")
        self.password_entry.pack(pady=(0,20), padx=10, fill="x")

        login_button = ctk.CTkButton(main_content_frame, text="Login", command=self._login_event)
        login_button.pack(pady=20, padx=10, fill="x")

        self.message_label = ctk.CTkLabel(main_content_frame, text="", text_color="red") 
        self.message_label.pack(pady=(5,10)) 

        forgot_password_label = ctk.CTkLabel(main_content_frame, text="Esqueci a senha",
                                             text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], # Pega a cor do tema
                                             cursor="hand2")
        forgot_password_label.pack(pady=(10,5))
        # forgot_password_label.bind("<Button-1>", lambda e: print("Esqueci a senha clicado")) # Placeholder

        new_user_label = ctk.CTkLabel(main_content_frame, text="Novo Cadastro",
                                      text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], # Pega a cor do tema
                                      cursor="hand2")
        new_user_label.pack(pady=5)
        # new_user_label.bind("<Button-1>", lambda e: print("Novo cadastro clicado")) # Placeholder

        self.user_entry.bind("<Return>", self._on_enter_key)
        self.password_entry.bind("<Return>", self._on_enter_key)


    def _on_enter_key(self, event=None):
        self._login_event()

    def _cancel_pending_after_jobs(self):
        if self._focus_after_id:
            # Verifica se o widget ainda existe antes de cancelar o 'after'
            if self.winfo_exists(): 
                self.after_cancel(self._focus_after_id) 
            self._focus_after_id = None
            
    def _login_event(self):
        username = self.user_entry.get()
        password = self.password_entry.get()

        # Login padrão para teste (substituir por lógica de banco de dados no futuro)
        if username == "admin" and password == "admin": 
            self.message_label.configure(text="") 
            print("LoginFrame: Login bem-sucedido!") 
            self._cancel_pending_after_jobs() # Cancela o 'after' antes de mudar de frame
            self.controller.show_frame("MainAppFrame") 
        else:
            self.message_label.configure(text="Usuário ou senha incorretos.", text_color="red")
            self.password_entry.delete(0, ctk.END) # Limpa o campo de senha
            # Garante que o foco seja definido apenas se o widget ainda existir
            if self.winfo_exists() and self.user_entry.winfo_exists():
                self.user_entry.focus()

if __name__ == '__main__':
    class MockApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste LoginFrame")
            self.geometry("450x600")
            ctk.set_appearance_mode("light")
            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(side="top", fill="both", expand=True)
            self.frames = {}
            frame = LoginFrame(parent=container, controller=self)
            self.frames["LoginFrame"] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            self.show_frame("LoginFrame")
        def show_frame(self, page_name):
            frame = self.frames.get(page_name)
            if frame: frame.tkraise()
            if page_name == "MainAppFrame":
                print("MockApp: Login bem-sucedido, deveria mostrar MainAppFrame.")
                self.destroy()
    mock_app_instance = MockApp()
    mock_app_instance.mainloop()