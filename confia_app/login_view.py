# Módulo responsável pela interface gráfica da tela de login.

import customtkinter as ctk

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Confia - Login")
        self.geometry("400x550") # Aumentei um pouco a altura para a mensagem de erro
        ctk.set_appearance_mode("light")

        self._create_widgets()
        self.user_entry.after(10, self.user_entry.focus)

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(pady=20, padx=60, fill="both", expand=True)

        title_label = ctk.CTkLabel(main_frame, text="Confia", font=ctk.CTkFont(family="Montserrat", size=36, weight="bold"))
        title_label.pack(pady=(20, 30))

        user_label = ctk.CTkLabel(main_frame, text="Usuário")
        user_label.pack(pady=(10,0), padx=10, anchor="w")
        self.user_entry = ctk.CTkEntry(main_frame, placeholder_text="Seu nome de usuário")
        self.user_entry.pack(pady=(0,10), padx=10, fill="x")

        password_label = ctk.CTkLabel(main_frame, text="Senha")
        password_label.pack(pady=(10,0), padx=10, anchor="w")
        self.password_entry = ctk.CTkEntry(main_frame, placeholder_text="Sua senha", show="*")
        self.password_entry.pack(pady=(0,20), padx=10, fill="x")

        login_button = ctk.CTkButton(main_frame, text="Login", command=self._login_event)
        login_button.pack(pady=20, padx=10, fill="x")

        # NOVO WIDGET: Label para mensagens de erro/status
        self.message_label = ctk.CTkLabel(main_frame, text="", text_color="red") # Cor padrão para erro
        self.message_label.pack(pady=(5,10)) # Adiciona um pouco de espaço

        forgot_password_label = ctk.CTkLabel(main_frame, text="Esqueci a senha",
                                             text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0],
                                             cursor="hand2")
        forgot_password_label.pack(pady=(10,5))

        new_user_label = ctk.CTkLabel(main_frame, text="Novo Cadastro",
                                      text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0],
                                      cursor="hand2")
        new_user_label.pack(pady=5)

        self.user_entry.bind("<Return>", self._on_enter_key)
        self.password_entry.bind("<Return>", self._on_enter_key)

    def _on_enter_key(self, event=None):
        self._login_event()

    def _login_event(self):
        username = self.user_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            # Limpa qualquer mensagem de erro anterior
            self.message_label.configure(text="")
            print("Login bem-sucedido! Abrindo aplicativo principal...")
            self.destroy() # Fecha a janela de login
            # Aqui, no futuro, chamaremos a função para abrir a janela principal do app
        else:
            # Mostra a mensagem de erro na interface
            self.message_label.configure(text="Usuário ou senha incorretos.", text_color="red")
            # Limpa o campo de senha
            self.password_entry.delete(0, 'end')
            # Opcional: Retorna o foco para o campo de usuário ou senha
            self.user_entry.focus() # Ou self.password_entry.focus()


if __name__ == "__main__":
    app = LoginView()
    app.mainloop()