# C:\Confia\confia_app\login_frame.py
# Módulo responsável pelo frame (tela) de login.

import customtkinter as ctk
# Remova 'from main_app_frame import MainAppFrame' se estiver aqui.
# LoginFrame não precisa mais conhecer a classe MainAppFrame diretamente.

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent")
        self._focus_after_id = None
        self._create_widgets()
        if self.user_entry.winfo_exists():
            self._focus_after_id = self.after(100, self._set_initial_focus)

    # ... (_set_initial_focus, _create_widgets, _on_enter_key, _cancel_pending_after_jobs permanecem os mesmos)
    def _set_initial_focus(self):
        """Define o foco no campo de usuário se o widget ainda existir."""
        if self.user_entry.winfo_exists(): # Verifica se o widget ainda é válido
            self.user_entry.focus()

    def _create_widgets(self):
        """
        Cria e posiciona os widgets na tela de login.
        Os widgets são adicionados a 'self' (que é o LoginFrame).
        """
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
                                             text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], 
                                             cursor="hand2")
        forgot_password_label.pack(pady=(10,5))

        new_user_label = ctk.CTkLabel(main_content_frame, text="Novo Cadastro",
                                      text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], 
                                      cursor="hand2")
        new_user_label.pack(pady=5)

        self.user_entry.bind("<Return>", self._on_enter_key)
        self.password_entry.bind("<Return>", self._on_enter_key)

    def _on_enter_key(self, event=None):
        """Chamado quando Enter é pressionado; aciona o login."""
        self._login_event()

    def _cancel_pending_after_jobs(self):
        """Cancela quaisquer 'after' jobs pendentes conhecidos."""
        if self._focus_after_id:
            self.after_cancel(self._focus_after_id) 
            self._focus_after_id = None
            
    def _login_event(self):
        username = self.user_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            self.message_label.configure(text="")
            print("LoginFrame: Login bem-sucedido!")
            self._cancel_pending_after_jobs()
            
            # MODIFICAÇÃO AQUI: Usa a string "MainAppFrame" diretamente.
            # Esta string deve corresponder à chave usada no dicionário self.frames da classe App.
            self.controller.show_frame("MainAppFrame") 
        else:
            # ... (lógica de falha de login)
            self.message_label.configure(text="Usuário ou senha incorretos.", text_color="red")
            self.password_entry.delete(0, 'end')
            if self.user_entry.winfo_exists():
                self.user_entry.focus()

# ... (bloco if __name__ == "__main__": permanece o mesmo)
if __name__ == '__main__':
    class MockApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste LoginFrame")
            self.geometry("450x600")
            container = ctk.CTkFrame(self)
            container.pack(fill="both", expand=True)
            self.login_frame = LoginFrame(parent=container, controller=self) 
            self.login_frame.pack(fill="both", expand=True)

        def show_frame(self, frame_name):
            print(f"MockApp: Tentando mostrar frame '{frame_name}'")
            if frame_name == "MainAppFrame":
                print("Login bem-sucedido! Transição para MainAppFrame ocorreria aqui.")
                self.destroy() 

    mock_app = MockApp()
    mock_app.mainloop()