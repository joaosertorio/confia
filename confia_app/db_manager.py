# C:\Confia\confia_app\db_manager.py
# Módulo responsável por todas as interações com o banco de dados SQLite.

import sqlite3
import os

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
DATABASE_NAME = 'confia.db'
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

def connect_db():
    """
    Estabelece uma conexão com o banco de dados SQLite.
    Cria a pasta 'database' se ela não existir.
    Retorna um objeto de conexão.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def create_tables(conn):
    """
    Cria as tabelas no banco de dados se elas ainda não existirem.
    """
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE, -- Garante que nomes de categorias sejam únicos
        tipo TEXT NOT NULL CHECK(tipo IN ('Crédito', 'Débito'))
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        limite REAL,
        dia_fechamento INTEGER,
        dia_vencimento INTEGER
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL, 
        descricao TEXT NOT NULL,
        valor REAL NOT NULL,
        tipo TEXT NOT NULL CHECK(tipo IN ('Crédito', 'Débito')),
        categoria_id INTEGER,
        cartao_id INTEGER,
        efetivada INTEGER NOT NULL DEFAULT 1, 
        FOREIGN KEY (categoria_id) REFERENCES categorias (id),
        FOREIGN KEY (cartao_id) REFERENCES cartoes (id)
    );
    """)
    
    conn.commit()

# --- NOVA FUNÇÃO ADICIONADA ---
def _populate_default_categories(conn):
    """
    Popula a tabela 'categorias' com valores padrão se ela estiver vazia ou
    se as categorias específicas não existirem (devido à restrição UNIQUE no nome).
    """
    cursor = conn.cursor()

    # Lista de categorias de Crédito padrão
    categorias_credito = [
        ('Salário', 'Crédito'),
        ('PPR', 'Crédito'), # Participação nos Lucros e Resultados
        ('Acerto', 'Crédito'), # Pode ser um acerto de contas, reembolso, etc.
        ('Venda', 'Crédito'), # Venda de algum bem ou serviço
        ('Outras Rendas', 'Crédito')
    ]

    # Lista de categorias de Débito padrão
    categorias_debito = [
        ('Alimentação', 'Débito'),
        ('Transporte', 'Débito'),
        ('Moradia', 'Débito'), # Aluguel, condomínio, financiamento imobiliário
        ('Saúde', 'Débito'), # Plano de saúde, medicamentos, consultas
        ('Educação', 'Débito'), # Cursos, material escolar, mensalidades
        ('Lazer', 'Débito'), # Cinema, restaurantes, viagens
        ('Outros', 'Débito') # Despesas diversas não categorizadas
    ]

    # Insere as categorias de crédito
    # A cláusula OR IGNORE faz com que o SQLite ignore a inserção se ela violar uma restrição
    # (neste caso, a restrição UNIQUE na coluna 'nome' da tabela 'categorias').
    # Assim, se uma categoria com o mesmo nome já existir, ela não será inserida novamente.
    for nome_cat, tipo_cat in categorias_credito:
        try:
            cursor.execute("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", (nome_cat, tipo_cat))
        except sqlite3.IntegrityError:
            # Esta exceção ocorreria se, por algum motivo além do UNIQUE no nome, a inserção falhasse.
            # Com INSERT OR IGNORE (ou INSERT ... ON CONFLICT DO NOTHING), a exceção de violação UNIQUE é suprimida.
            # Para maior robustez e para usar a funcionalidade do SQLite que lida com isso diretamente:
            # cursor.execute("INSERT OR IGNORE INTO categorias (nome, tipo) VALUES (?, ?)", (nome_cat, tipo_cat))
            # Vamos usar INSERT OR IGNORE para simplificar e garantir que não haja erro se a categoria já existir.
            pass # Se usarmos try/except, o pass aqui significa que ignoramos o erro de integridade.

    # Usando INSERT OR IGNORE diretamente (forma preferida para este caso)
    cursor.executemany("INSERT OR IGNORE INTO categorias (nome, tipo) VALUES (?, ?)", categorias_credito)
    cursor.executemany("INSERT OR IGNORE INTO categorias (nome, tipo) VALUES (?, ?)", categorias_debito)
    
    conn.commit() # Salva as inserções
    print("Verificação/atualização de categorias padrão concluída.")


def initialize_database():
    """
    Função principal para inicializar o banco de dados.
    Conecta, cria as tabelas e popula com dados padrão se necessário.
    """
    conn = connect_db()
    create_tables(conn)
    _populate_default_categories(conn) # --- CHAMADA DA NOVA FUNÇÃO ---
    conn.close()
    print(f"Banco de dados inicializado em: {DATABASE_PATH}")

if __name__ == '__main__':
    initialize_database()
    # Você pode adicionar um SELECT aqui para verificar as categorias inseridas, se rodar isoladamente
    # conn_test = connect_db()
    # cursor_test = conn_test.cursor()
    # cursor_test.execute("SELECT nome, tipo FROM categorias")
    # print("\nCategorias no banco:")
    # for row in cursor_test.fetchall():
    #     print(row)
    # conn_test.close()