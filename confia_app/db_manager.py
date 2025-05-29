# C:\Confia\confia_app\db_manager.py
import sqlite3 
import os      
from datetime import date, timedelta, datetime # Adicionado datetime completo
import random # Novo import

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database')
DATABASE_NAME = 'confia.db'
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_NAME)

def connect_db():
    print("DEBUG_DB: Tentando criar diretório e conectar ao BD...")
    os.makedirs(DATABASE_DIR, exist_ok=True) 
    conn = sqlite3.connect(DATABASE_PATH) 
    conn.execute("PRAGMA foreign_keys = ON;") 
    print(f"DEBUG_DB: Conectado a {DATABASE_PATH}")
    return conn

def create_tables(conn):
    print("DEBUG_DB: Entrou em create_tables.")
    cursor = conn.cursor() 
    
    print("DEBUG_DB: Executando CREATE TABLE IF NOT EXISTS categorias...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        tipo TEXT NOT NULL CHECK(tipo IN ('Crédito', 'Débito')),
        cor TEXT DEFAULT '#808080', 
        fixa INTEGER NOT NULL DEFAULT 0 
    );
    """)
    print("DEBUG_DB: Tabela 'categorias' verificada/criada.")

    print("DEBUG_DB: Executando CREATE TABLE IF NOT EXISTS cartoes...")
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
    print("DEBUG_DB: Tabela 'cartoes' verificada/criada.")

    print("DEBUG_DB: Executando CREATE TABLE IF NOT EXISTS transacoes...")
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
    print("DEBUG_DB: Tabela 'transacoes' verificada/criada.")
    
    print("DEBUG_DB: Executando CREATE TABLE IF NOT EXISTS faturas_cartao...")
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
    print("DEBUG_DB: Tabela 'faturas_cartao' verificada/criada.")
    
    print("DEBUG_DB: Executando conn.commit() em create_tables...")
    conn.commit()
    print("DEBUG_DB: Saindo de create_tables.")

def _populate_default_categories(conn):
    print("DEBUG_DB: Entrou em _populate_default_categories.")
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
        print("DEBUG_DB: Categorias padrão fixas verificadas/atualizadas com SUCESSO.")
    except sqlite3.Error as e:
        print(f"DEBUG_DB: ERRO ao popular categorias padrão: {e}")
        conn.rollback()
    print("DEBUG_DB: Saindo de _populate_default_categories.")


def initialize_database():
    print("DEBUG_DB: Entrou em initialize_database.")
    conn = None # Inicializa conn como None
    try:
        conn = connect_db()
        print("DEBUG_DB: Conexão estabelecida em initialize_database.")
        
        create_tables(conn) 
        print("DEBUG_DB: create_tables CONCLUÍDO em initialize_database.")

        cursor = conn.cursor()
        # Lógica de migração para 'categorias'
        try:
            cursor.execute("PRAGMA table_info(categorias)") 
            column_names = [info[1] for info in cursor.fetchall()] 
            altered_categorias = False
            if 'cor' not in column_names:
                print("DEBUG_DB: Tentando adicionar coluna 'cor' à tabela 'categorias' (migração)...")
                cursor.execute("ALTER TABLE categorias ADD COLUMN cor TEXT DEFAULT '#808080'")
                altered_categorias = True
            if 'fixa' not in column_names:
                print("DEBUG_DB: Tentando adicionar coluna 'fixa' à tabela 'categorias' (migração)...")
                cursor.execute("ALTER TABLE categorias ADD COLUMN fixa INTEGER NOT NULL DEFAULT 0")
                altered_categorias = True
            if altered_categorias: conn.commit(); print("DEBUG_DB: Tabela 'categorias' migrada (se necessário).")
        except sqlite3.Error as e: print(f"DEBUG_DB: Aviso durante migração da tabela 'categorias': {e}")

        # Lógica de migração para 'cartoes'
        try:
            cursor.execute("PRAGMA table_info(cartoes)")
            column_names_cartoes = [info[1] for info in cursor.fetchall()]
            if 'cor' not in column_names_cartoes:
                print("DEBUG_DB: Tentando adicionar coluna 'cor' à tabela 'cartoes' (migração)...")
                cursor.execute("ALTER TABLE cartoes ADD COLUMN cor TEXT DEFAULT '#808080'")
                conn.commit()
                print("DEBUG_DB: Coluna 'cor' adicionada à tabela 'cartoes' (se necessário).")
        except sqlite3.Error as e: print(f"DEBUG_DB: Aviso durante migração da tabela 'cartoes' para 'cor': {e}")

        _populate_default_categories(conn)
        print("DEBUG_DB: _populate_default_categories CONCLUÍDO em initialize_database.")
        
        print(f"Banco de dados inicializado e verificado em: {DATABASE_PATH}") # Mensagem final original
    except sqlite3.Error as e:
        print(f"DEBUG_DB: ERRO CRÍTICO em initialize_database: {e}")
    finally:
        if conn:
            conn.close()
            print("DEBUG_DB: Conexão fechada em initialize_database.")
        else:
            print("DEBUG_DB: Conexão não foi estabelecida ou já foi fechada em initialize_database.")
    print("DEBUG_DB: Saindo de initialize_database.")


# ... (get_categories_by_type, add_category, delete_category, add_transaction, 
#      get_transaction_by_id, update_transaction, get_transactions, delete_transaction,
#      add_card, get_all_cards, get_card_by_id, update_card, delete_card,
#      get_faturas, upsert_fatura - MANTENHA ESTAS FUNÇÕES COMO ESTAVAM NO PASSO 70) ...
def get_categories_by_type(tipo: str):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, cor, fixa FROM categorias WHERE tipo = ? ORDER BY fixa DESC, nome ASC", (tipo,))
        return cursor.fetchall()
    finally: conn.close() if conn else None

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
    except sqlite3.Error as e: print(f"Erro BD ao adicionar transação: {e}"); conn.rollback(); return False
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
    except sqlite3.Error as e: print(f"Erro BD ao atualizar transação: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def get_transactions(tipo_transacao: str, data_inicio: str = None, data_fim: str = None):
    conn = connect_db(); cursor = conn.cursor()
    query = "SELECT t.id, t.data, t.valor, c.nome, t.descricao FROM transacoes t JOIN categorias c ON t.categoria_id = c.id WHERE t.tipo = ?"
    params = [tipo_transacao]
    if data_inicio and data_fim: query += " AND t.data BETWEEN ? AND ?"; params.extend([data_inicio, data_fim])
    query += " ORDER BY t.data DESC, t.id DESC"
    try:
        cursor.execute(query, tuple(params)); return cursor.fetchall()
    except sqlite3.Error as e: print(f"Erro BD ao buscar transações: {e}"); return []
    finally: conn.close() if conn else None

def delete_transaction(transaction_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transacoes WHERE id = ?", (transaction_id,)); conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e: print(f"Erro BD ao deletar transação: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def add_card(nome: str, bandeira: str = None, cor: str = '#808080', limite: float = None, 
             dia_fechamento: int = None, dia_vencimento: int = None, banco: str = None):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cartoes (nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento)
            VALUES (?, ?, ?, ?, ?, ?, ?) 
        """, (nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento))
        conn.commit(); return cursor.lastrowid
    except sqlite3.IntegrityError: print(f"Cartão '{nome}' já existe."); return None
    except sqlite3.Error as e: print(f"Erro BD ao adicionar cartão: {e}"); conn.rollback(); return None
    finally: conn.close() if conn else None

def get_all_cards():
    conn = connect_db(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, bandeira, cor FROM cartoes ORDER BY nome ASC")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e: print(f"Erro BD ao buscar cartões: {e}"); return []
    finally: conn.close() if conn else None

def get_card_by_id(card_id: int):
    conn = connect_db(); conn.row_factory = sqlite3.Row; cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento FROM cartoes WHERE id = ?", (card_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e: print(f"Erro BD ao buscar cartão por ID: {e}"); return None
    finally: conn.close() if conn else None

def update_card(card_id: int, nome: str, bandeira: str = None, cor: str = '#808080', limite: float = None, 
                dia_fechamento: int = None, dia_vencimento: int = None, banco: str = None):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE cartoes SET nome = ?, banco = ?, bandeira = ?, cor = ?, limite = ?, dia_fechamento = ?, dia_vencimento = ?
            WHERE id = ?
        """, (nome, banco, bandeira, cor, limite, dia_fechamento, dia_vencimento, card_id))
        conn.commit(); return cursor.rowcount > 0
    except sqlite3.IntegrityError: print(f"Nome de cartão '{nome}' duplicado."); return False
    except sqlite3.Error as e: print(f"Erro BD ao atualizar cartão: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def delete_card(card_id: int):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM transacoes WHERE cartao_id = ?", (card_id,))
        if cursor.fetchone()[0] > 0: return False, "Cartão em uso em transações."
        cursor.execute("DELETE FROM cartoes WHERE id = ?", (card_id,)); conn.commit()
        return (True, "Cartão excluído.") if cursor.rowcount > 0 else (False, "Cartão não encontrado.")
    except sqlite3.Error as e: conn.rollback(); return False, f"Erro BD ao deletar cartão: {e}"
    finally: conn.close() if conn else None

def get_faturas(cartao_id: int, ano: int):
    conn = connect_db(); cursor = conn.cursor()
    faturas = {m: 0.0 for m in range(1, 13)}
    try:
        cursor.execute("SELECT mes, valor_fatura FROM faturas_cartao WHERE cartao_id = ? AND ano = ?", (cartao_id, ano))
        for mes, valor in cursor.fetchall(): faturas[mes] = valor if valor is not None else 0.0
        return faturas
    except sqlite3.Error as e: print(f"Erro BD ao buscar faturas: {e}"); return faturas
    finally: conn.close() if conn else None

def upsert_fatura(cartao_id: int, ano: int, mes: int, valor_fatura: float):
    conn = connect_db(); cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO faturas_cartao (cartao_id, ano, mes, valor_fatura) VALUES (?, ?, ?, ?)
            ON CONFLICT(cartao_id, ano, mes) DO UPDATE SET valor_fatura = excluded.valor_fatura;
        """, (cartao_id, ano, mes, valor_fatura))
        conn.commit(); return True
    except sqlite3.Error as e: print(f"Erro BD ao inserir/atualizar fatura: {e}"); conn.rollback(); return False
    finally: conn.close() if conn else None

def get_consolidated_faturas_for_year(ano: int):
    conn = connect_db(); cursor = conn.cursor()
    faturas_consolidadas = {mes: 0.0 for mes in range(1, 13)} 
    try:
        cursor.execute("SELECT mes, SUM(valor_fatura) FROM faturas_cartao WHERE ano = ? GROUP BY mes ORDER BY mes ASC", (ano,))
        for row in cursor.fetchall():
            mes, soma_valor_fatura = row
            if soma_valor_fatura is not None: faturas_consolidadas[mes] = soma_valor_fatura
        return faturas_consolidadas
    except sqlite3.Error as e: print(f"Erro ao buscar faturas consolidadas para o ano {ano}: {e}"); return faturas_consolidadas 
    finally: conn.close() if conn else None
    
def get_total_spending_by_category(start_date: str, end_date: str):
    """
    Calcula o total de gastos (Débito) por categoria dentro de um período.
    Retorna uma lista de tuplas: (nome_categoria, cor_categoria, total_gasto).
    Apenas categorias com gastos no período são retornadas.
    """
    conn = connect_db()
    cursor = conn.cursor()
    query = """
        SELECT c.nome, c.cor, SUM(t.valor) as total_gasto
        FROM transacoes t
        JOIN categorias c ON t.categoria_id = c.id
        WHERE t.tipo = 'Débito' AND t.data BETWEEN ? AND ?
        GROUP BY c.id, c.nome, c.cor
        HAVING SUM(t.valor) > 0  -- Apenas categorias com gastos
        ORDER BY total_gasto DESC
    """
    params = (start_date, end_date)
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        # Retorna como lista de tuplas (nome, cor, valor)
        return [(row[0], row[1], row[2]) for row in results]
    except sqlite3.Error as e:
        print(f"Erro ao buscar gastos por categoria: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_total_income_vs_expenses(start_date: str, end_date: str):
    """
    Calcula o total de entradas (Crédito) e saídas (Débito) dentro de um período.
    Retorna um dicionário: {'total_creditos': valor, 'total_debitos': valor}.
    """
    conn = connect_db()
    cursor = conn.cursor()
    # Inicializa com 0 para o caso de não haver transações de um tipo no período
    totals = {'total_creditos': 0.0, 'total_debitos': 0.0}
    try:
        # Query para Créditos
        cursor.execute("""
            SELECT SUM(valor) 
            FROM transacoes 
            WHERE tipo = 'Crédito' AND data BETWEEN ? AND ?
        """, (start_date, end_date))
        result_credit = cursor.fetchone()
        if result_credit and result_credit[0] is not None:
            totals['total_creditos'] = result_credit[0]

        # Query para Débitos
        cursor.execute("""
            SELECT SUM(valor) 
            FROM transacoes 
            WHERE tipo = 'Débito' AND data BETWEEN ? AND ?
        """, (start_date, end_date))
        result_debit = cursor.fetchone()
        if result_debit and result_debit[0] is not None:
            totals['total_debitos'] = result_debit[0]
            
        return totals
    except sqlite3.Error as e:
        print(f"Erro ao buscar totais de entradas/saídas: {e}")
        return totals # Retorna os totais zerados em caso de erro
    finally:
        if conn:
            conn.close()

# ... (bloco if __name__ == '__main__': existente) ...
# Adicione testes para as novas funções no bloco if __name__ == '__main__':
if __name__ == '__main__':
    # ... (código de teste existente no if __name__ ...)
    # Mantenha os testes anteriores.

    print("\n--- Testando Funções do Dashboard ---")
    # Define um período de teste (ex: mês atual, ou um período com dados)
    # Para o teste, vamos assumir que as transações de exemplo do db_manager 
    # (Salário, Bônus, Compra online, Supermercado Abril) caem em Maio/2025 e Abril/2025
    
    # Os dados de teste já adicionam transações em 2025-05-01, 2025-05-15, 2025-05-05, 2025-04-20
    start_test_period = "2025-04-01"
    end_test_period = "2025-05-31"

    print(f"\n--- Testando get_total_spending_by_category para {start_test_period} a {end_test_period} ---")
    gastos_por_categoria = get_total_spending_by_category(start_test_period, end_test_period)
    if gastos_por_categoria:
        print("Gastos por Categoria:")
        for nome, cor, total in gastos_por_categoria:
            print(f" - {nome} (Cor: {cor}): R$ {total:.2f}")
    else:
        print("Nenhum gasto por categoria encontrado para o período.")

    print(f"\n--- Testando get_total_income_vs_expenses para {start_test_period} a {end_test_period} ---")
    entradas_saidas = get_total_income_vs_expenses(start_test_period, end_test_period)
    print(f"Totais para o período:")
    print(f" - Créditos: R$ {entradas_saidas['total_creditos']:.2f}")
    print(f" - Débitos: R$ {entradas_saidas['total_debitos']:.2f}")

if __name__ == '__main__':
    db_file_path = DATABASE_PATH
    if os.path.exists(db_file_path):
        print(f"Removendo banco de dados existente para teste: {db_file_path}")
        try:
            os.remove(db_file_path)
            print(f"Arquivo de banco de dados '{db_file_path}' removido com sucesso.")
        except PermissionError:
             print(f"AVISO: Não foi possível remover {db_file_path}. Pode estar em uso. Feche outros visualizadores de SQLite.")
        except Exception as e:
            print(f"Erro desconhecido ao tentar remover o banco de dados: {e}")
    
    print("\n--- Inicializando Banco de Dados ---")
    initialize_database() # Recria com ON DELETE RESTRICT

    print("\n--- Testando CRUD de Cartões ---")
    card1_id = add_card(nome="Cartão Principal Teste", bandeira="Visa", cor="#1E90FF", limite=5000.0, banco="Banco X")
    card2_id = add_card(nome="Cartão Viagem Teste", bandeira="Mastercard", cor="#32CD32", banco="Banco Y")

    print("\n--- Testando get_consolidated_faturas_for_year ---")
    ano_teste_consolidado = date.today().year 
    
    if card1_id:
        upsert_fatura(card1_id, ano_teste_consolidado, 1, 100.50) # Jan
        upsert_fatura(card1_id, ano_teste_consolidado, 3, 200.00) # Mar
    if card2_id:
        upsert_fatura(card2_id, ano_teste_consolidado, 1, 50.0)   # Jan
        upsert_fatura(card2_id, ano_teste_consolidado, 3, 150.0)  # Mar

    faturas_consolidadas_ano_atual = get_consolidated_faturas_for_year(ano_teste_consolidado)
    print(f"\nFaturas Consolidadas para o Ano {ano_teste_consolidado}:")
    if faturas_consolidadas_ano_atual:
        for mes_teste, valor_total_teste in faturas_consolidadas_ano_atual.items():
            if valor_total_teste > 0: 
                print(f"Mês {mes_teste:02d}: R$ {valor_total_teste:.2f}")
    else:
        print(f"Nenhuma fatura consolidada encontrada para {ano_teste_consolidado} ou erro na busca.")

    # Outros testes podem ser adicionados ou mantidos aqui...
    
def delete_all_transactional_data():
    """
    Exclui TODAS as transações, TODAS as faturas de cartão e TODOS os cartões.
    Categorias NÃO são afetadas.
    Retorna True se bem-sucedido, False caso contrário.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        # A ordem importa devido às chaves estrangeiras (embora ON DELETE CASCADE e SET NULL ajudem)
        # 1. Excluir todas as transações
        cursor.execute("DELETE FROM transacoes")
        print(f"{cursor.rowcount} transações excluídas.")
        
        # 2. Excluir todas as faturas de cartão (seriam excluídas por CASCADE ao deletar cartões, mas fazemos explicitamente para clareza)
        cursor.execute("DELETE FROM faturas_cartao")
        print(f"{cursor.rowcount} faturas de cartão excluídas.")

        # 3. Excluir todos os cartões
        cursor.execute("DELETE FROM cartoes")
        print(f"{cursor.rowcount} cartões excluídos.")
        
        conn.commit()
        print("Todos os dados transacionais (transações, faturas, cartões) foram excluídos.")
        return True
    except sqlite3.Error as e:
        print(f"Erro ao excluir dados transacionais: {e}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def generate_test_data():
    """
    Gera um conjunto de dados de teste: cartões, faturas, créditos e débitos.
    É recomendável chamar delete_all_transactional_data() antes para evitar duplicatas
    ou conflitos se esta função for chamada múltiplas vezes.
    """
    print("Iniciando geração de dados de teste...")
    
    # --- 1. Adicionar Cartões de Teste ---
    cards_to_add = [
        {"nome": "Cartão Principal Azul", "bandeira": "Visa", "cor": "#3B8ED0", "limite": 5000, "dia_fechamento": 20, "dia_vencimento": 28},
        {"nome": "Cartão Viagem Verde", "bandeira": "Mastercard", "cor": "#2ECC71", "limite": 10000, "dia_fechamento": 15, "dia_vencimento": 25}
    ]
    card_ids = []
    for card_data in cards_to_add:
        # Adiciona banco como None, pois removemos do formulário principal
        card_id = add_card(card_data["nome"], card_data["bandeira"], card_data["cor"], 
                           card_data["limite"], card_data["dia_fechamento"], card_data["dia_vencimento"], banco=None)
        if card_id:
            card_ids.append(card_id)
    
    if not card_ids:
        print("Não foi possível adicionar cartões de teste. Geração de dados de teste interrompida para faturas.")
        # Ainda tenta gerar transações gerais
    
    # --- 2. Gerar Faturas para os Cartões de Teste ---
    today = date.today()
    current_year = today.year
    previous_year = current_year - 1
    
    for card_id in card_ids:
        # Faturas para o ano anterior completo
        for month in range(1, 13):
            valor = round(random.uniform(50.0, 800.0), 2)
            upsert_fatura(card_id, previous_year, month, valor)
        
        # Faturas para o ano atual, até o mês anterior ao atual
        # (ou até o mês atual se preferir simular uma fatura já fechada)
        for month in range(1, today.month + 1): # Inclui o mês atual
            valor = round(random.uniform(70.0, 900.0), 2)
            upsert_fatura(card_id, current_year, month, valor)
    print(f"{len(card_ids) * (12 + today.month)} faturas de teste geradas (aprox).")

    # --- 3. Gerar Transações de Crédito ---
    credit_categories = get_categories_by_type('Crédito')
    if not credit_categories:
        print("Nenhuma categoria de crédito encontrada. Pulando geração de créditos de teste.")
    else:
        num_credits_to_add = min(len(credit_categories), 3) # Pelo menos 3 ou o total de categorias de crédito
        selected_credit_categories = random.sample(credit_categories, num_credits_to_add)
        
        for i in range(num_credits_to_add): # Garante pelo menos uma transação por categoria selecionada
            cat_id = selected_credit_categories[i][0] # ID da categoria
            desc = f"Renda de Teste {i+1} ({selected_credit_categories[i][1]})"
            val = round(random.uniform(1000.0, 7000.0), 2)
            # Data aleatória nos últimos 2 meses
            day_offset = random.randint(1, 60)
            trans_date = (today - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            add_transaction(trans_date, desc, val, 'Crédito', cat_id)
        print(f"{num_credits_to_add} transações de crédito de teste geradas.")

    # --- 4. Gerar Transações de Débito ---
    debit_categories = get_categories_by_type('Débito')
    if not debit_categories:
        print("Nenhuma categoria de débito encontrada. Pulando geração de débitos de teste.")
    else:
        num_debits_to_add = min(len(debit_categories), 10) # Até 10 ou o total de categorias de débito
        selected_debit_categories = random.sample(debit_categories, num_debits_to_add)

        for i in range(num_debits_to_add): # Garante pelo menos uma transação por categoria selecionada
            cat_id = selected_debit_categories[i][0]
            desc = f"Gasto de Teste {i+1} ({selected_debit_categories[i][1]})"
            val = round(random.uniform(10.0, 300.0), 2)
            day_offset = random.randint(1, 60)
            trans_date = (today - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            add_transaction(trans_date, desc, val, 'Débito', cat_id)
        print(f"{num_debits_to_add} transações de débito de teste geradas.")
        
    print("Geração de dados de teste concluída.")

# Bloco if __name__ == '__main__': para testes
if __name__ == '__main__':
    db_file_path = DATABASE_PATH
    if os.path.exists(db_file_path):
        print(f"Removendo banco de dados existente para teste completo: {db_file_path}")
        try:
            os.remove(db_file_path)
            print(f"Arquivo de banco de dados '{db_file_path}' removido com sucesso.")
        except PermissionError:
             print(f"AVISO: Não foi possível remover {db_file_path}. Pode estar em uso.")
        except Exception as e:
            print(f"Erro desconhecido ao tentar remover o banco de dados: {e}")
    
    print("\n--- Inicializando Banco de Dados ---")
    initialize_database() # Cria tabelas e categorias padrão

    print("\n--- Gerando Dados de Teste ---")
    generate_test_data()

    print("\n--- Verificando Dados Gerados (Exemplos) ---")
    print("\nCartões de Teste:")
    for card in get_all_cards(): print(card)
    
    print("\nFaturas Consolidadas (Ano Atual):")
    faturas_consol = get_consolidated_faturas_for_year(date.today().year)
    for mes, val in faturas_consol.items():
        if val > 0 : print(f"Mês {mes:02d}: R$ {val:.2f}")

    print("\nTransações de Crédito (Últimas):")
    for tr in get_transactions('Crédito')[:5]: print(tr) # Mostra as 5 primeiras
    
    print("\nTransações de Débito (Últimas):")
    for tr in get_transactions('Débito')[:5]: print(tr) # Mostra as 5 primeiras

    print("\n--- Apagando Dados Transacionais de Teste ---")
    delete_all_transactional_data()

    print("\n--- Verificando Após Exclusão ---")
    print(f"Total de Cartões: {len(get_all_cards())}") # Deve ser 0
    print(f"Total de Transações de Crédito: {len(get_transactions('Crédito'))}") # Deve ser 0
    print(f"Total de Transações de Débito: {len(get_transactions('Débito'))}") # Deve ser 0
    print(f"Faturas Consolidadas (Ano Atual) após exclusão:")
    faturas_consol_depois = get_consolidated_faturas_for_year(date.today().year)
    has_faturas = False
    for mes, val in faturas_consol_depois.items():
        if val > 0 : print(f"Mês {mes:02d}: R$ {val:.2f}"); has_faturas = True
    if not has_faturas: print("Nenhuma fatura encontrada.")