# C:\Confia\confia_app\main.py
import customtkinter as ctk
import tkinter 
from tkinter import messagebox # Import para messagebox
import db_manager

from login_frame import LoginFrame 
from main_app_frame import MainAppFrame
# from category_management_frame import CategoryManagementFrame # Não precisa mais importar aqui diretamente se MainAppFrame o faz

class App(ctk.CTk): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("DEBUG_APP: App __init__ - INÍCIO")
        self.title("Confia") 
        self.geometry("450x600") 
        ctk.set_appearance_mode("light") 

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {} 
        print("DEBUG_APP: App.__init__ - Criando frames principais...")
        
        # Cria apenas LoginFrame e MainAppFrame inicialmente
        for F in (LoginFrame, MainAppFrame): 
            page_name = F.__name__
            frame = F(master=self.container, controller=self) 
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        print("DEBUG_APP: App.__init__ - Mostrando LoginFrame...")
        self.show_frame("LoginFrame") 
        self.protocol("WM_DELETE_WINDOW", self._on_app_closing) 
        print("DEBUG_APP: App __init__ - FIM")

    def show_frame(self, page_name: str):
        print(f"DEBUG_APP: show_frame - Tentando mostrar: {page_name}") 
            
        frame = self.frames.get(page_name) # Pega apenas frames gerenciados pela App (Login, Main)
        if frame:
            frame.tkraise() 
            print(f"DEBUG_APP: show_frame - Frame '{page_name}' elevado.")

            if page_name == "MainAppFrame":
                self.title("Confia - Principal"); self.geometry("1200x800") 
                if hasattr(frame, '_setup_menu'): frame._setup_menu() 
            elif page_name == "LoginFrame":
                self.title("Confia - Login"); self.geometry("450x600")
                self.config(menu=tkinter.Menu(self)) # Menu vazio para login
            # CategoryManagementFrame não é mais gerenciado aqui, pois será Toplevel
        else:
            print(f"AVISO em App.show_frame: Frame '{page_name}' não encontrado no dicionário self.frames (normal para CategoryManagementFrame agora).")
            # Não mostra erro se for CategoryManagementFrame, pois ele será um Toplevel
            if page_name != "CategoryManagementFrame":
                 messagebox.showerror("Erro de Navegação", f"A tela '{page_name}' não pôde ser carregada.")
            
    def _on_app_closing(self): 
        print("Fechando a aplicação Confia...")
        self.destroy() 

# ... (main() e if __name__ == "__main__" como estavam) ...
def main():
    print("DEBUG_MAIN: Função main() - INÍCIO")
    db_manager.initialize_database()
    app = App() 
    print("DEBUG_MAIN: App instanciada. Chamando mainloop().")
    app.mainloop()
    print("DEBUG_MAIN: Mainloop finalizado.")

if __name__ == "__main__":
    main()