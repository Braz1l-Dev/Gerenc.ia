from database import get_db, close_db


def get_categories_by_user(user_id, cat_type=None):
    """Busca categorias do usuário, opcionalmente filtradas por tipo."""
    conn = get_db()
    cursor = conn.cursor()

    if cat_type:
        cursor.execute('''
            SELECT * FROM categories
            WHERE user_id = ? AND type = ?
            ORDER BY name ASC
        ''', (user_id, cat_type))
    else:
        cursor.execute('''
            SELECT * FROM categories
            WHERE user_id = ?
            ORDER BY type ASC, name ASC
        ''', (user_id,))

    categories = cursor.fetchall()
    close_db(conn)
    return categories


def get_expense_categories(user_id):
    """Busca apenas categorias de despesa (para orçamentos)."""
    return get_categories_by_user(user_id, 'despesa')


def get_income_categories(user_id):
    """Busca apenas categorias de receita."""
    return get_categories_by_user(user_id, 'receita')


def get_category_by_id(category_id, user_id):
    """Busca uma categoria específica do usuário."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM categories
        WHERE id = ? AND user_id = ?
    ''', (category_id, user_id))
    category = cursor.fetchone()
    close_db(conn)
    return category


def create_category(user_id, name, cat_type, icon='📁', color='#6366F1'):
    """Cria uma nova categoria."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO categories (user_id, name, type, icon, color)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, cat_type, icon, color))
        conn.commit()
        category_id = cursor.lastrowid
        close_db(conn)
        return category_id
    except Exception as e:
        conn.rollback()
        close_db(conn)
        raise e


def update_category(category_id, user_id, name, cat_type, icon, color):
    """Atualiza uma categoria existente."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE categories
            SET name = ?, type = ?, icon = ?, color = ?
            WHERE id = ? AND user_id = ?
        ''', (name, cat_type, icon, color, category_id, user_id))
        conn.commit()
        rows = cursor.rowcount
        close_db(conn)
        return rows > 0
    except Exception as e:
        conn.rollback()
        close_db(conn)
        raise e


def delete_category(category_id, user_id):
    """Exclui uma categoria (se não estiver em uso por orçamentos)."""
    conn = get_db()
    cursor = conn.cursor()

    # Verifica se a categoria está vinculada a orçamentos
    cursor.execute('''
        SELECT COUNT(*) as count FROM budgets
        WHERE category_id = ? AND user_id = ?
    ''', (category_id, user_id))
    budget_count = cursor.fetchone()['count']

    if budget_count > 0:
        close_db(conn)
        return False, 'Categoria vinculada a orçamentos. Remova os orçamentos primeiro.'

    # Desvincula transações (SET NULL)
    cursor.execute('''
        UPDATE transactions SET category_id = NULL
        WHERE category_id = ? AND user_id = ?
    ''', (category_id, user_id))

    # Exclui a categoria
    cursor.execute('''
        DELETE FROM categories
        WHERE id = ? AND user_id = ?
    ''', (category_id, user_id))

    conn.commit()
    close_db(conn)
    return True, 'Categoria excluída com sucesso.'


def count_transactions_by_category(category_id, user_id):
    """Conta quantas transações usam essa categoria."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) as count FROM transactions
        WHERE category_id = ? AND user_id = ?
    ''', (category_id, user_id))
    count = cursor.fetchone()['count']
    close_db(conn)
    return count
