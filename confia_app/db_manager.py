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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        tipo TEXT NOT NULL CHECK(tipo IN ('Crédito', 'Débito')),
        cor TEXT DEFAULT '#808080', 
        fixa INTEGER NOT NULL DEFAULT 0 
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cartoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        banco TEXT,                      
        bandeira TEXT,                   
        cor TEXT DEFAULT '#808080',      
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
        FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE RESTRICT,
        FOREIGN KEY (cartao_id) REFERENCES cartoes (id) ON DELETE SET NULL 
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faturas_cartao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cartao_id INTEGER NOT NULL,
        ano INTEGER NOT NULL,
        mes INTEGER NOT NULL, 
        valor_fatura REAL,
        FOREIGN KEY (cartao_id) REFERENCES cartoes (id) ON DELETE CASCADE,
        UNIQUE (cartao_id, ano, mes) 
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
        altered_categorias = False
        if 'cor' not in column_names:
            print("Adicionando coluna 'cor' à tabela 'categorias' (migração)...")
            cursor.execute("ALTER TABLE categorias ADD COLUMN cor TEXT DEFAULT '#808080'")
            altered_categorias = True
        if 'fixa' not in column_names:
            print("Adicionando coluna 'fixa' à tabela 'categorias' (migração)...")
            cursor.execute("ALTER TABLE categorias ADD COLUMN fixa INTEGER NOT NULL DEFAULT 0")
            altered_categorias = True
        if altered_categorias: conn.commit(); print("Tabela 'categorias' migrada.")
    except sqlite3.Error as e: print(f"Aviso ao verificar/alterar tabela 'categorias': {e}")

    try:
        cursor.execute("PRAGMA table_info(cartoes)")
        column_names_cartoes = [info[1] for info in cursor.fetchall()]
        if 'cor' not in column_names_cartoes:
            print("Adicionando coluna 'cor' à tabela 'cartoes' (migração)...")
            cursor.execute("ALTER TABLE cartoes ADD COLUMN cor TEXT DEFAULT '#808080'")
            conn.commit()
            print("Coluna 'cor' adicionada à tabela 'cartoes'.")
    except sqlite3.Error as e: print(f"Aviso ao verificar/alterar tabela 'cartoes' para 'cor': {e}")

    _populate_default_categories(conn)
    conn.close()
    print(f"Banco de dados inicializado em: {DATABASE_PATH}")

def get_categories_by_type(tipo: str):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, cor, fixa FROM categorias WHERE tipo = ? ORDER BY fixa DESC, nome ASC", (tipo,))
        return cursor.fetchall()
    finally: conn.close() if conn else None # Garante fechamento

def add_category(nome: str, tipo: str, cor: str):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categorias (nome, tipo, cor, fixa) VALUES (?, ?, ?, 0)", (nome, tipo, cor))
        conn.commit(); return True
    except sqlite3.IntegrityError: print(f"Categoria '{nome}' já existe."); return False
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def delete_category(category_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT fixa FROM categorias WHERE id = ?", (category_id,))
        r = cursor.fetchone()
        if r and r[0] == 1: return False, "Categoria fixa não pode ser excluída."
        cursor.execute("DELETE FROM categorias WHERE id = ? AND fixa = 0", (category_id,))
        conn.commit()
        if cursor.rowcount > 0: return True, "Categoria excluída."
        return False, "Categoria não encontrada ou é fixa."
    except sqlite3.IntegrityError: return False, "Categoria em uso em transações."
    except sqlite3.Error as e: conn.rollback(); return False, f"Erro BD: {e}"
    finally: conn.close() if conn else None

def add_transaction(data: str, descricao: str, valor: float, tipo: str, categoria_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO transacoes (data, descricao, valor, tipo, categoria_id) VALUES (?, ?, ?, ?, ?)", 
                       (data, descricao, valor, tipo, categoria_id))
        conn.commit(); return True
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def get_transaction_by_id(transaction_id: int):
    conn = connect_db(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, data, descricao, valor, tipo, categoria_id FROM transacoes WHERE id = ?", (transaction_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally: conn.close() if conn else None

def update_transaction(transaction_id: int, data: str, descricao: str, valor: float, categoria_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("UPDATE transacoes SET data = ?, descricao = ?, valor = ?, categoria_id = ? WHERE id = ?", 
                       (data, descricao, valor, categoria_id, transaction_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def get_transactions(tipo_transacao: str, data_inicio: str = None, data_fim: str = None):
    conn = connect_db(); cursor = conn.cursor()
    query = "SELECT t.id, t.data, t.valor, c.nome, t.descricao FROM transacoes t JOIN categorias c ON t.categoria_id = c.id WHERE t.tipo = ?"
    params = [tipo_transacao]
    if data_inicio and data_fim: query += " AND t.data BETWEEN ? AND ?"; params.extend([data_inicio, data_fim])
    query += " ORDER BY t.data DESC, t.id DESC"
    try:
        cursor.execute(query, tuple(params)); return cursor.fetchall()
    finally: conn.close() if conn else None

def delete_transaction(transaction_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (transaction_id,)); conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def add_card(nome: str, bandeira: str = None, cor: str = '#808080', limite: float = None, 
             dia_fechamento: int = None, dia_vencimento: int = None, banco: str = None): # 7 parâmetros
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cartoes (nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento)
            VALUES (?, ?, ?, ?, ?, ?, ?) 
        """, (nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento)) # 7 placeholders
        conn.commit(); return cursor.lastrowid
    except sqlite3.IntegrityError: print(f"Cartão '{nome}' já existe."); return None
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return None
    finally: conn.close() if conn else None

def get_all_cards():
    conn = connect_db(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, bandeira, cor FROM cartoes ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally: conn.close() if conn else None

def get_card_by_id(card_id: int):
    conn = connect_db(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento FROM cartoes WHERE id = ?", (card_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally: conn.close() if conn else None

def update_card(card_id: int, nome: str, bandeira: str = None, cor: str = '#808080', limite: float = None, 
                dia_fechamento: int = None, dia_vencimento: int = None, banco: str = None): # 8 parâmetros incluindo id
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE cartoes SET nome = ?, banco = ?, bandeira = ?, cor = ?, limite = ?, dia_fechamento = ?, dia_vencimento = ?
            WHERE id = ?
        """, (nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento, card_id)) # 8 placeholders
        conn.commit(); return cursor.rowcount > 0
    except sqlite3.IntegrityError: print(f"Nome de cartão '{nome}' duplicado."); return False
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def delete_card(card_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM transacoes WHERE cartao_id = ?", (card_id,))
        if cursor.fetchone()[0] > 0: return False, "Cartão em uso em transações."
        cursor.execute("DELETE FROM cartoes WHERE id = ?", (card_id,)); conn.commit()
        return (True, "Cartão excluído.") if cursor.rowcount > 0 else (False, "Cartão não encontrado.")
    except sqlite3.Error as e: conn.rollback(); return False, f"Erro BD: {e}"
    finally: conn.close() if conn else None

def get_faturas(cartao_id: int, ano: int):
    conn = connect_db(); cursor = conn.cursor()
    faturas = {m: 0.0 for m in range(1, 13)}
    try:
        cursor.execute("SELECT mes, valor_fatura FROM faturas_cartao WHERE cartao_id = ? AND ano = ?", (cartao_id, ano))
        for mes, valor in cursor.fetchall(): faturas[mes] = valor if valor is not None else 0.0
        return faturas
    finally: conn.close() if conn else None

def upsert_fatura(cartao_id: int, ano: int, mes: int, valor_fatura: float):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO faturas_cartao (cartao_id, ano, mes, valor_fatura) VALUES (?, ?, ?, ?)
            ON CONFLICT(cartao_id, ano, mes) DO UPDATE SET valor_fatura = excluded.valor_fatura;
        """, (cartao_id, ano, mes, valor_fatura))
        conn.commit(); return True
    except sqlite3.Error as e: print(f"Erro BD: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

if __name__ == '__main__':
    # ... (bloco de teste principal como fornecido anteriormente, garantindo que as chamadas de função correspondam às novas assinaturas)
    # O bloco if __name__ == '__main__' do Passo 43 já estava bem completo para testar cartões e faturas.
    # Apenas garanta que as chamadas para add_card e update_card usem os parâmetros corretos.
    print("Executando testes do db_manager.py...")
    # (O código de teste completo do if __name__ == '__main__' do Passo 43 pode ser colado aqui)