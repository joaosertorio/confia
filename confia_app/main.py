# C:\Confia\confia_app\main.py
# Arquivo principal e controlador da aplicação Confia.

import customtkinter as ctk
import tkinter 
import db_manager
from login_frame import LoginFrame
from main_app_frame import MainAppFrame

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Confia")
        self.geometry("450x600") 
        ctk.set_appearance_mode("light")
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {} 
        print("DEBUG: App.__init__ - Criando frames...") # Print de depuração
        for F in (LoginFrame, MainAppFrame): 
            page_name = F.__name__
            print(f"DEBUG: App.__init__ - Criando frame: {page_name}") # Print de depuração
            frame = F(parent=container, controller=self) 
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        print("DEBUG: App.__init__ - Frames criados. Mostrando LoginFrame...") # Print de depuração
        self.show_frame("LoginFrame") 
        self.protocol("WM_DELETE_WINDOW", self._on_app_closing)

    def show_frame(self, page_name: str):
        print(f"DEBUG: App.show_frame - Tentando mostrar frame: {page_name}") # Print de depuração
        frame = self.frames.get(page_name)
        if frame:
            print(f"DEBUG: App.show_frame - Frame '{page_name}' encontrado. Chamando tkraise().") # Print de depuração
            frame.tkraise()

            if page_name == "MainAppFrame":
                self.title("Confia - Principal")
                self.geometry("1000x700")
                print("DEBUG: App.show_frame - Configurando para MainAppFrame.") # Print de depuração
                if hasattr(frame, '_setup_menu'):
                    print("DEBUG: App.show_frame - Chamando _setup_menu() do MainAppFrame.") # Print de depuração
                    frame._setup_menu() 
            elif page_name == "LoginFrame":
                self.title("Confia - Login")
                self.geometry("450x600")
                print("DEBUG: App.show_frame - Configurando para LoginFrame (limpando menu).") # Print de depuração
                empty_menu = tkinter.Menu(self)
                self.config(menu=empty_menu)
            
            if hasattr(frame, 'on_show_frame'): # Para futuras atualizações de tela
                print(f"DEBUG: App.show_frame - Chamando on_show_frame() para {page_name}, se existir.") # Print de depuração
                frame.on_show_frame()
            print(f"DEBUG: App.show_frame - Frame '{page_name}' deveria estar visível.") # Print de depuração
        else:
            print(f"Erro CRÍTICO: Frame '{page_name}' não encontrado no dicionário self.frames.") # Print de depuração

    def _on_app_closing(self):
        print("Fechando a aplicação Confia...")
        self.destroy()

def main():
    db_manager.initialize_database()
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()