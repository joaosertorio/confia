# C:\Confia\confia_app\login_frame.py
# Módulo responsável pelo frame (tela) de login.

import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    # ... (__init__, _set_initial_focus, _create_widgets, _on_enter_key, _cancel_pending_after_jobs como estavam) ...
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent") 
        self._focus_after_id = None 
        self._create_widgets() 
        if self.winfo_exists() and hasattr(self, 'user_entry') and self.user_entry.winfo_exists(): # Checagem adicional
            self._focus_after_id = self.after(200, self._set_initial_focus)

    def _set_initial_focus(self):
        if self.winfo_exists() and hasattr(self, 'user_entry') and self.user_entry.winfo_exists(): 
            self.user_entry.focus()

    def _create_widgets(self):
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
        self._login_event()

    def _cancel_pending_after_jobs(self):
        if self._focus_after_id:
            if self.winfo_exists(): 
                self.after_cancel(self._focus_after_id) 
            self._focus_after_id = None 
            
    def _login_event(self):
        username = self.user_entry.get() # Ainda pegamos para o caso de você querer reabilitar
        password = self.password_entry.get() # Mesmo motivo

        # --- MODIFICAÇÃO PARA LOGIN DE TESTE ---
        # Comente a verificação de login para facilitar os testes
        # if username == "admin" and password == "admin":
        if True: # Permite o login direto
        # --- FIM DA MODIFICAÇÃO ---
            self.message_label.configure(text="") 
            print("LoginFrame: Login (teste) bem-sucedido!") 
            self._cancel_pending_after_jobs() 
            self.controller.show_frame("MainAppFrame") 
        else:
            # Esta parte não será alcançada com a modificação acima, mas mantenha para quando reabilitar
            self.message_label.configure(text="Usuário ou senha incorretos.", text_color="red")
            self.password_entry.delete(0, ctk.END) 
            if self.winfo_exists() and self.user_entry.winfo_exists(): 
                self.user_entry.focus() 

# ... (bloco if __name__ == '__main__' como estava) ...
if __name__ == '__main__':
    class MockApp(ctk.CTk):
        def __init__(self):
            super().__init__();self.title("Teste LoginFrame");self.geometry("450x600");ctk.set_appearance_mode("light")
            container=ctk.CTkFrame(self,fg_color="transparent");container.pack(fill="both",expand=True)
            self.login_frame_instance=LoginFrame(container,self);self.login_frame_instance.pack(fill="both",expand=True,padx=10,pady=10)
        def show_frame(self,frame_name):
            print(f"MockApp: show_frame para '{frame_name}'")
            if frame_name == "MainAppFrame": print("MockApp: Login OK!");self.destroy()
    MockApp().mainloop()