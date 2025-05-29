# C:\Confia\confia_app\main.py
# Arquivo principal e controlador da aplicação Confia.

import customtkinter as ctk
import tkinter 
import db_manager

from login_frame import LoginFrame # Importa o frame de login
from main_app_frame import MainAppFrame
from category_management_frame import CategoryManagementFrame # Mantenha esta e outras importações de frame

class App(ctk.CTk): 
    # ... (__init__ como estava) ...
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("DEBUG_APP: App __init__ - INÍCIO")
        self.title("Confia") 
        self.geometry("450x600") 
        ctk.set_appearance_mode("light") 
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {} 
        print("DEBUG_APP: App.__init__ - Criando frames...")
        # As classes dos frames DEVEM ser importadas no topo do main.py
        from login_frame import LoginFrame
        from main_app_frame import MainAppFrame
        from category_management_frame import CategoryManagementFrame

        for F in (LoginFrame, MainAppFrame, CategoryManagementFrame): 
            page_name = F.__name__
            print(f"DEBUG_APP: App.__init__ - Criando frame: {page_name}")
            frame = F(parent=container, controller=self) 
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        print("DEBUG_APP: App.__init__ - Mostrando LoginFrame...")
        self.show_frame("LoginFrame") 
        self.protocol("WM_DELETE_WINDOW", self._on_app_closing)
        print("DEBUG_APP: App __init__ - FIM")

    def show_frame(self, page_name: str):
        print(f"DEBUG_APP: show_frame - Tentando mostrar: {page_name}") 
        frame = self.frames.get(page_name)
        if frame:
            frame.tkraise() 
            print(f"DEBUG_APP: show_frame - Frame '{page_name}' elevado.")

            if page_name == "MainAppFrame":
                self.title("Confia - Principal")
                self.geometry("1200x800")
                # --- ADIÇÃO/GARANTIA AQUI ---
                # Garante que o menu do MainAppFrame seja configurado/reaplicado
                if hasattr(frame, '_setup_menu') and callable(frame._setup_menu):
                    print(f"DEBUG_APP: show_frame - Reconfigurando menu para MainAppFrame.")
                    frame._setup_menu() 
                # --- FIM DA ADIÇÃO ---
            elif page_name == "LoginFrame":
                self.title("Confia - Login")
                self.geometry("450x600")
                empty_menu = tkinter.Menu(self) 
                self.config(menu=empty_menu)    
            elif page_name == "CategoryManagementFrame":
                self.title("Confia - Gerenciar Categorias")
                self.geometry("700x550") 
                # Garante que o menu principal esteja lá (MainAppFrame o configura)
                main_app_fr = self.frames.get("MainAppFrame")
                if main_app_fr and hasattr(main_app_fr, '_setup_menu'):
                    main_app_fr._setup_menu() # Reconfigura o menu do MainAppFrame
            
            if hasattr(frame, 'on_show_frame') and callable(frame.on_show_frame):
                print(f"DEBUG_APP: show_frame - Chamando on_show_frame para {page_name}.")
                frame.on_show_frame()
        else:
            print(f"ERRO CRÍTICO em App.show_frame: Frame '{page_name}' não encontrado.")
            
    def _on_app_closing(self):
        print("Fechando a aplicação Confia...")
        self.destroy()

# ... (função main() e if __name__ == "__main__" como estavam) ...
def main():
    print("DEBUG_MAIN: Função main() - INÍCIO")
    db_manager.initialize_database()
    app = App() 
    print("DEBUG_MAIN: App instanciada. Chamando mainloop().")
    app.mainloop()
    print("DEBUG_MAIN: Mainloop finalizado.")

if __name__ == "__main__":
    main()