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
    Habilita o suporte a chaves estrangeiras.
    Retorna um objeto de conexão.
    """
    os.makedirs(DATABASE_DIR, exist_ok=True) 
    conn = sqlite3.connect(DATABASE_PATH) 
    conn.execute("PRAGMA foreign_keys = ON;") 
    return conn

def create_tables(conn):
    """
    Cria as tabelas no banco de dados se elas ainda não existirem,
    com o esquema mais recente.
    """
    cursor = conn.cursor() 

    # Tabela de Categorias (com colunas 'cor' e 'fixa')
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        tipo TEXT NOT NULL CHECK(tipo IN ('Crédito', 'Débito')),
        cor TEXT DEFAULT '#808080', 
        fixa INTEGER NOT NULL DEFAULT 0 
    );
    """)

    # Tabela de Cartões
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        limite REAL,
        dia_fechamento INTEGER,
        dia_vencimento INTEGER
    );
    """)

    # Tabela de Transações (com ON DELETE RESTRICT para categoria_id)
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
        FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE RESTRICT,
        FOREIGN KEY (cartao_id) REFERENCES cartoes (id) ON DELETE SET NULL 
    );
    """)
    
    conn.commit()

def _populate_default_categories(conn):
    """
    Popula a tabela 'categorias' com valores padrão fixos e suas cores.
    """
    cursor = conn.cursor()
    categorias_credito_fixas = [
        ('Salário', 'Crédito', '#4CAF50', 1), ('PPR', 'Crédito', '#8BC34A', 1),
        ('Venda', 'Crédito', '#00BCD4', 1), ('Acerto', 'Crédito', '#FFC107', 1)
    ]
    categorias_debito_fixas = [
        ('Alimentação', 'Débito', '#F44336', 1), ('Transporte', 'Débito', '#9C27B0', 1),
        ('Casa', 'Débito', '#3F51B5', 1), ('Saúde', 'Débito', '#FF9800', 1),
        ('Educação', 'Débito', '#2196F3', 1), ('Diversão', 'Débito', '#E91E63', 1),
        ('Outros', 'Débito', '#9E9E9E', 1)
    ]
    default_categories = categorias_credito_fixas + categorias_debito_fixas
    try:
        cursor.executemany("INSERT OR IGNORE INTO categorias (nome, tipo, cor, fixa) VALUES (?, ?, ?, ?)", default_categories)
        for nome_cat, tipo_cat, cor_cat, fixa_status in default_categories:
            cursor.execute("UPDATE categorias SET cor = ?, fixa = ? WHERE nome = ? AND tipo = ?", 
                           (cor_cat, fixa_status, nome_cat, tipo_cat))
        conn.commit()
        print("Categorias padrão fixas verificadas/atualizadas.")
    except sqlite3.Error as e:
        print(f"Erro ao popular categorias padrão: {e}")
        conn.rollback()

def initialize_database():
    """
    Função principal para inicializar o banco de dados.
    """
    conn = connect_db()
    create_tables(conn) 

    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(categorias)") 
        column_names = [info[1] for info in cursor.fetchall()] 
        
        altered = False
        if 'cor' not in column_names:
            print("Tentando adicionar coluna 'cor' à tabela 'categorias' (migração)...")
            cursor.execute("ALTER TABLE categorias ADD COLUMN cor TEXT DEFAULT '#808080'")
            altered = True
            print("Coluna 'cor' adicionada.")
        if 'fixa' not in column_names:
            print("Tentando adicionar coluna 'fixa' à tabela 'categorias' (migração)...")
            cursor.execute("ALTER TABLE categorias ADD COLUMN fixa INTEGER NOT NULL DEFAULT 0")
            altered = True
            print("Coluna 'fixa' adicionada.")
        
        if altered:
            conn.commit() 

    except sqlite3.Error as e:
        print(f"Aviso durante a verificação/alteração da tabela 'categorias': {e}")

    _populate_default_categories(conn)
    
    conn.close()
    print(f"Banco de dados inicializado em: {DATABASE_PATH}")

def get_categories_by_type(tipo: str):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, cor, fixa FROM categorias WHERE tipo = ? ORDER BY fixa DESC, nome ASC", (tipo,))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar categorias por tipo ({tipo}): {e}")
        return []
    finally:
        if conn: conn.close()

def add_category(nome: str, tipo: str, cor: str):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nome, tipo, cor, fixa) VALUES (?, ?, ?, 0)", (nome, tipo, cor))
        conn.commit()
        print(f"Categoria '{nome}' adicionada com sucesso.")
        return True
    except sqlite3.IntegrityError:
        print(f"Erro de integridade: A categoria '{nome}' já existe.")
        return False
    except sqlite3.Error as e:
        print(f"Erro ao adicionar categoria '{nome}': {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def delete_category(category_id: int):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT fixa FROM categorias WHERE id = ?", (category_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            return False, "Esta é uma categoria fixa e não pode ser excluída."
        cursor.execute("DELETE FROM categorias WHERE id = ? AND fixa = 0", (category_id,))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Categoria excluída com sucesso."
        else:
            return False, "Categoria não encontrada ou não pôde ser excluída (pode ser fixa)."
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e) or "constraint failed" in str(e).lower():
            return False, "Esta categoria não pode ser excluída pois está sendo utilizada em transações."
        else: 
            return False, f"Erro de integridade ao excluir: {e}"
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Erro ao excluir categoria: {e}"
    finally:
        if conn: conn.close()

def add_transaction(data: str, descricao: str, valor: float, tipo: str, categoria_id: int, efetivada: int = 1):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO transacoes (data, descricao, valor, tipo, categoria_id, efetivada)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data, descricao, valor, tipo, categoria_id, efetivada))
        conn.commit()
        print(f"Transação '{descricao}' do tipo '{tipo}' adicionada com sucesso.")
        return True
    except sqlite3.Error as e:
        print(f"Erro ao adicionar transação '{descricao}': {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_transactions(tipo_transacao: str, data_inicio: str = None, data_fim: str = None):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT t.id, t.data, t.valor, c.nome, t.descricao
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        WHERE t.tipo = ?
    """
    params = [tipo_transacao]
    if data_inicio and data_fim:
        query += " AND t.data BETWEEN ? AND ?"
        params.extend([data_inicio, data_fim])
    query += " ORDER BY t.data DESC, t.id DESC"
    try:
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar transações do tipo '{tipo_transacao}': {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_transaction(transaction_id: int):
    """
    Exclui uma transação específica do banco de dados pelo seu ID.
    Retorna True se a exclusão for bem-sucedida (1 linha afetada), False caso contrário.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (transaction_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Transação ID {transaction_id} excluída com sucesso.")
            return True
        else:
            print(f"Nenhuma transação excluída para ID {transaction_id} (não encontrada).")
            return False
    except sqlite3.Error as e:
        print(f"Erro ao excluir transação ID {transaction_id}: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    db_file_path = DATABASE_PATH
    if os.path.exists(db_file_path):
        print(f"Removendo banco de dados existente para teste: {db_file_path}")
        os.remove(db_file_path)
    
    print("\n--- Inicializando Banco de Dados ---")
    initialize_database()

    print("\n--- Categorias de Crédito Iniciais ---")
    creditos_cats = get_categories_by_type('Crédito')
    for cat in creditos_cats: print(cat)
    
    print("\n--- Categorias de Débito Iniciais ---")
    debitos_cats = get_categories_by_type('Débito')
    for cat in debitos_cats: print(cat)

    salario_id = None
    outros_deb_id = None
    if creditos_cats:
        for cat_id, nome, _, _ in creditos_cats:
            if nome == "Salário": salario_id = cat_id; break
    if debitos_cats:
        for cat_id, nome, _, _ in debitos_cats:
            if nome == "Outros": outros_deb_id = cat_id; break
    
    print("\n--- Testando Adição de Transações ---")
    if salario_id:
        add_transaction('2025-05-01', 'Salário Mensal', 5000.00, 'Crédito', salario_id)
        add_transaction('2025-05-15', 'Bônus', 1500.00, 'Crédito', salario_id)
    if outros_deb_id:
        add_transaction('2025-05-05', 'Compra online', 75.50, 'Débito', outros_deb_id)
        add_transaction('2025-04-20', 'Supermercado Abril', 250.00, 'Débito', outros_deb_id)

    print("\n--- Testando Busca de Transações (Créditos) ---")
    for t_id, data, valor, cat_nome, desc in get_transactions('Crédito'):
        print(f"{t_id:2} | {data} | {valor:7.2f} | {cat_nome:9} | {desc}")

    print("\n--- Testando Exclusão de Transação ---")
    trans_creditos_antes_delete = get_transactions('Crédito')
    if trans_creditos_antes_delete:
        id_para_excluir_trans = trans_creditos_antes_delete[0][0]
        desc_para_excluir_trans = trans_creditos_antes_delete[0][4]
        print(f"Tentando excluir transação ID: {id_para_excluir_trans} (Descrição: {desc_para_excluir_trans})")
        if delete_transaction(id_para_excluir_trans):
            print(f"Transação '{desc_para_excluir_trans}' EXCLUÍDA.")
        else:
            print(f"Falha ao excluir transação '{desc_para_excluir_trans}'.")
    
    print("\n--- Créditos Após Exclusão ---")
    for t_id, data, valor, cat_nome, desc in get_transactions('Crédito'):
        print(f"{t_id:2} | {data} | {valor:7.2f} | {cat_nome:9} | {desc}")

    # Teste de exclusão de categoria em uso (como estava no Passo 31)
    print("\n--- Testando Exclusão de Categoria (em uso e não em uso) ---")
    add_category("Categoria Em Uso Teste Final", "Débito", "#123456")
    conn_test = connect_db()
    cursor_test = conn_test.cursor()
    cursor_test.execute("SELECT id FROM categorias WHERE nome = 'Categoria Em Uso Teste Final'")
    cat_teste_row_final = cursor_test.fetchone()
    if cat_teste_row_final:
        cat_teste_id_final = cat_teste_row_final[0]
        cursor_test.execute("INSERT INTO transacoes (data, descricao, valor, tipo, categoria_id) VALUES (?,?,?,?,?)",
                           ("2025-01-02", "Teste Transação para Categoria", 2.0, "Débito", cat_teste_id_final))
        conn_test.commit()
        print(f"Categoria 'Categoria Em Uso Teste Final' (ID: {cat_teste_id_final}) criada e usada.")
        sucesso, msg = delete_category(cat_teste_id_final)
        print(f"Tentativa de excluir categoria em uso: Sucesso={sucesso}, Msg='{msg}'")
        cursor_test.execute("DELETE FROM transacoes WHERE categoria_id = ?", (cat_teste_id_final,))
        conn_test.commit()
        print("Transação de teste removida.")
        sucesso, msg = delete_category(cat_teste_id_final)
        print(f"Tentativa de excluir categoria (não mais em uso): Sucesso={sucesso}, Msg='{msg}'")
    conn_test.close()