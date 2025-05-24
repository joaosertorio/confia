# C:\Confia\confia_app\main.py
# Arquivo principal e controlador da aplicação Confia.

import customtkinter as ctk
import tkinter # Necessário para criar o menu vazio na tela de login
import db_manager # Módulo de gerenciamento do banco de dados

# Importa as classes de frame refatoradas
from login_frame import LoginFrame
from main_app_frame import MainAppFrame
from category_management_frame import CategoryManagementFrame

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Confia") # Título inicial, será alterado por show_frame
        self.geometry("450x600") # Tamanho inicial para a tela de login (pode ser ajustado)
        ctk.set_appearance_mode("light") # Define o tema inicial

        # Container principal onde os diferentes frames (telas) serão colocados
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1) # Permite que a linha do frame expanda
        container.grid_columnconfigure(0, weight=1) # Permite que a coluna do frame expanda

        self.frames = {} # Dicionário para armazenar as instâncias dos frames

        # Cria e armazena cada frame que a aplicação usará
        for F in (LoginFrame, MainAppFrame, CategoryManagementFrame): 
            page_name = F.__name__ # Usa o nome da classe como chave (ex: "LoginFrame")
            frame = F(parent=container, controller=self) # Cria a instância do frame
            self.frames[page_name] = frame # Armazena o frame
            # Coloca o frame no container usando grid. Todos ocupam a mesma célula (0,0)
            # e são empilhados. tkraise() trará o desejado para frente.
            frame.grid(row=0, column=0, sticky="nsew") # "nsew" faz o frame preencher a célula

        self.show_frame("LoginFrame") # Mostra o frame de login inicialmente
        
        self.protocol("WM_DELETE_WINDOW", self._on_app_closing) # Handler para fechar a janela

    def show_frame(self, page_name: str):
        """
        Traz um frame (tela) para o topo para ser visível e ajusta a janela.
        :param page_name: O nome da classe do frame a ser mostrado.
        """
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise() # Traz o frame para o topo da pilha de widgets

            # Configurações específicas da janela App dependendo do frame mostrado
            if page_name == "MainAppFrame":
                self.title("Confia - Principal")
                self.geometry("1000x700")
                # O menu é configurado pelo MainAppFrame em seu __init__ (self.controller.config(menu=...))
                # Se o menu pudesse ser alterado por outros frames, precisaríamos reconfigurá-lo aqui.
                # Para garantir, podemos chamar o _setup_menu do MainAppFrame.
                if hasattr(frame, '_setup_menu'):
                     frame._setup_menu()
            elif page_name == "LoginFrame":
                self.title("Confia - Login")
                self.geometry("450x600")
                empty_menu = tkinter.Menu(self) # Cria uma barra de menu vazia
                self.config(menu=empty_menu)    # Remove o menu na tela de login
            elif page_name == "CategoryManagementFrame":
                self.title("Confia - Gerenciar Categorias")
                self.geometry("700x550") # Ajustado para melhor visualização das listas
                # Assume que o menu do MainAppFrame (menu principal) deve permanecer visível.
                # Se MainAppFrame não estiver visível, seu menu pode não ter sido configurado na App ainda.
                # Para garantir que o menu principal esteja lá:
                main_app_fr = self.frames.get("MainAppFrame")
                if main_app_fr and hasattr(main_app_fr, '_setup_menu'):
                    main_app_fr._setup_menu()


            # Chama um método 'on_show_frame' no frame que está sendo exibido, se ele existir.
            # Útil para carregar/atualizar dados no frame.
            if hasattr(frame, 'on_show_frame'):
                frame.on_show_frame()
        else:
            print(f"Erro CRÍTICO: Frame '{page_name}' não encontrado.")
            
    def _on_app_closing(self):
        """Chamado quando a janela principal da aplicação é fechada pelo 'X'."""
        print("Fechando a aplicação Confia...")
        self.destroy() # Destrói a janela raiz, encerrando o mainloop

# Função principal que inicia a aplicação
def main():
    """
    Inicializa o banco de dados e roda a aplicação principal.
    """
    # Para testar a criação do banco do zero, você pode excluir o arquivo .db antes de rodar.
    # Exemplo:
    # db_file_path = os.path.join(os.path.dirname(__file__), 'database', 'confia.db')
    # if os.path.exists(db_file_path) and __name__ == '__main__': # Apenas se rodando main.py diretamente
    #     try:
    #         os.remove(db_file_path)
    #         print(f"Arquivo de banco de dados '{db_file_path}' removido para novo teste.")
    #     except OSError as e:
    #         print(f"Não foi possível remover o arquivo de banco de dados: {e}")

    db_manager.initialize_database() # Garante que o DB e as tabelas estejam prontos

    app = App() # Cria a instância da nossa aplicação raiz
    app.mainloop() # Inicia o loop principal do Tkinter

if __name__ == "__main__":
    main()