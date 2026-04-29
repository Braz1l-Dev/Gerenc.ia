import sqlite3
from config import Config


def get_db():
    """Retorna conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def close_db(conn):
    """Fecha a conexão com o banco."""
    if conn:
        conn.close()


def init_db():
    """Cria todas as tabelas do sistema."""
    conn = get_db()
    cursor = conn.cursor()

    # ========================
    # TABELA: USUÁRIOS
    # ========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            currency TEXT DEFAULT 'BRL',
            theme TEXT DEFAULT 'light',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ========================
    # TABELA: CONTAS (banco, cartão, carteira)
    # ========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            balance REAL DEFAULT 0,
            icon TEXT DEFAULT '🏦',
            color TEXT DEFAULT '#4F46E5',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # ========================
    # TABELA: CATEGORIAS (fixas por usuário)
    # ========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            icon TEXT DEFAULT '📁',
            color TEXT DEFAULT '#6366F1',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # ========================
    # TABELA: TRANSAÇÕES
    # ========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER,
            category_id INTEGER,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            is_recurring INTEGER DEFAULT 0,
            recurring_day INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        )
    ''')

    # ========================
    # TABELA: ORÇAMENTOS
    # ========================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            month TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
            UNIQUE(user_id, category_id, month)
        )
    ''')

    conn.commit()
    close_db(conn)
    print("✅ Banco de dados inicializado com sucesso!")


def create_default_categories(user_id):
    """Cria as 9 categorias padrão para um novo usuário."""
    conn = get_db()
    cursor = conn.cursor()

    default_categories = [
        ('Alimentação', 'despesa', '🍔', '#EF4444'),
        ('Transporte',  'despesa', '🚗', '#F59E0B'),
        ('Moradia',     'despesa', '🏠', '#3B82F6'),
        ('Saúde',       'despesa', '🏥', '#10B981'),
        ('Educação',    'despesa', '📚', '#8B5CF6'),
        ('Lazer',       'despesa', '🎮', '#EC4899'),
        ('Compras',     'despesa', '🛒', '#F97316'),
        ('Contas',      'despesa', '📄', '#6366F1'),
        ('Outros',      'despesa', '📦', '#6B7280'),
        ('Salário',     'receita', '💰', '#10B981'),
        ('Freelance',   'receita', '💻', '#3B82F6'),
        ('Investimentos','receita', '📈', '#8B5CF6'),
        ('Outros',      'receita', '📦', '#6B7280'),
    ]

    for name, cat_type, icon, color in default_categories:
        cursor.execute('''
            INSERT INTO categories (user_id, name, type, icon, color)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, cat_type, icon, color))

    conn.commit()
    close_db(conn)
    print(f"✅ Categorias padrão criadas para o usuário {user_id}")
