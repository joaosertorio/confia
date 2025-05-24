# C:\Confia\confia_app\login_frame.py
# Módulo responsável pelo frame (tela) de login.

import customtkinter as ctk

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        """
        Construtor do LoginFrame.
        :param parent: O widget pai onde este frame será colocado.
        :param controller: A instância da classe App (controlador principal).
        """
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.configure(fg_color="transparent") # Fundo do frame transparente

        self._focus_after_id = None # Para armazenar o ID do 'after' job do foco

        self._create_widgets() # Cria os widgets dentro deste frame
        
        # Agenda o foco inicial após a interface gráfica estar pronta
        # Usamos self.after, que é um método de widgets Tkinter.
        # Aumentei o delay para 200ms para garantir que a janela/frame esteja totalmente renderizado.
        if self.winfo_exists() and self.user_entry.winfo_exists():
            self._focus_after_id = self.after(200, self._set_initial_focus)

    def _set_initial_focus(self):
        """Define o foco no campo de usuário se o widget e o frame ainda existirem."""
        if self.winfo_exists() and self.user_entry.winfo_exists(): 
            self.user_entry.focus()

    def _create_widgets(self):
        """Cria e posiciona os widgets na tela de login."""
        # Frame interno para melhor organização e padding do conteúdo do login
        main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_content_frame.pack(pady=20, padx=60, fill="both", expand=True)

        title_label = ctk.CTkLabel(main_content_frame, text="Confia", font=ctk.CTkFont(family="Montserrat", size=36, weight="bold"))
        title_label.pack(pady=(20, 30))

        user_label = ctk.CTkLabel(main_content_frame, text="Usuário")
        user_label.pack(pady=(10,0), padx=10, anchor="w") # Alinha o label à esquerda
        self.user_entry = ctk.CTkEntry(main_content_frame, placeholder_text="Seu nome de usuário")
        self.user_entry.pack(pady=(0,10), padx=10, fill="x") # Preenche horizontalmente

        password_label = ctk.CTkLabel(main_content_frame, text="Senha")
        password_label.pack(pady=(10,0), padx=10, anchor="w")
        self.password_entry = ctk.CTkEntry(main_content_frame, placeholder_text="Sua senha", show="*")
        self.password_entry.pack(pady=(0,20), padx=10, fill="x")

        login_button = ctk.CTkButton(main_content_frame, text="Login", command=self._login_event)
        login_button.pack(pady=20, padx=10, fill="x")

        self.message_label = ctk.CTkLabel(main_content_frame, text="", text_color="red") 
        self.message_label.pack(pady=(5,10)) 

        # Labels para funcionalidades futuras
        forgot_password_label = ctk.CTkLabel(main_content_frame, text="Esqueci a senha",
                                             text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], # Cor do tema
                                             cursor="hand2") # Cursor de mãozinha
        forgot_password_label.pack(pady=(10,5))

        new_user_label = ctk.CTkLabel(main_content_frame, text="Novo Cadastro",
                                      text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"][0], # Cor do tema
                                      cursor="hand2")
        new_user_label.pack(pady=5)

        # Associa a tecla Enter aos campos para tentar o login
        self.user_entry.bind("<Return>", self._on_enter_key)
        self.password_entry.bind("<Return>", self._on_enter_key)

    def _on_enter_key(self, event=None): # event=None para compatibilidade
        """Chamado quando Enter é pressionado nos campos; aciona o login."""
        self._login_event()

    def _cancel_pending_after_jobs(self):
        """Cancela o 'after' job pendente do foco, se existir."""
        if self._focus_after_id:
            if self.winfo_exists(): # Só tenta cancelar se o widget base (frame) ainda existir
                self.after_cancel(self._focus_after_id) 
            self._focus_after_id = None # Reseta o ID de qualquer forma
            
    def _login_event(self):
        """
        Processa o evento de login.
        Se sucesso, pede ao controller para mostrar o frame principal.
        Se falha, mostra mensagem de erro.
        """
        username = self.user_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            self.message_label.configure(text="") # Limpa mensagem de erro
            print("LoginFrame: Login bem-sucedido!") 
            self._cancel_pending_after_jobs() # Cancela 'after' jobs antes de transicionar
            
            # Pede ao controller (App) para mostrar o frame principal usando a string nome da classe
            self.controller.show_frame("MainAppFrame") 
        else:
            self.message_label.configure(text="Usuário ou senha incorretos.", text_color="red")
            self.password_entry.delete(0, 'end') # Limpa o campo de senha
            if self.winfo_exists() and self.user_entry.winfo_exists(): # Verifica se ainda existe antes de focar
                self.user_entry.focus() # Devolve o foco ao campo de usuário

if __name__ == '__main__':
    # Bloco para teste isolado do LoginFrame
    # Este mock permite rodar o login_frame.py diretamente para verificar sua UI e interações básicas.
    class MockApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Teste Isolado do LoginFrame")
            self.geometry("450x600")
            ctk.set_appearance_mode("light") # Define um tema para o teste

            # Container para o frame de login
            container = ctk.CTkFrame(self, fg_color="transparent")
            container.pack(side="top", fill="both", expand=True)
            
            # Instancia o LoginFrame, passando o container e o próprio MockApp como controller
            self.login_frame_instance = LoginFrame(parent=container, controller=self) 
            self.login_frame_instance.pack(fill="both", expand=True, padx=10, pady=10)

        def show_frame(self, frame_name): # Mock da função do controller
            print(f"MockApp: show_frame chamada para '{frame_name}'")
            if frame_name == "MainAppFrame":
                print("MockApp: Login bem-sucedido! Transição para MainAppFrame ocorreria aqui.")
                # Em um teste real, você poderia mostrar outro frame mock ou fechar.
                self.destroy() # Fecha a janela de teste após um login bem-sucedido no mock

    # Cria e roda o app de mock para testar o LoginFrame
    mock_app_instance = MockApp()
    mock_app_instance.mainloop()