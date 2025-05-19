# Arquivo principal da aplicação Confia

from login_view import LoginView # Importa a classe LoginView do módulo login_view

def main():
    """
    Função principal para iniciar a aplicação.
    """
    app = LoginView() # Cria uma instância da tela de login
    app.mainloop()    # Inicia o loop principal da interface gráfica

if __name__ == "__main__":
    # Este bloco é executado quando o script main.py é rodado diretamente
    main()