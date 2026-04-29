from database import get_db, close_db


def get_transactions_by_user(user_id, month=None, limit=None):
    """Busca transações do usuário, opcionalmente filtradas por mês."""
    conn = get_db()
    cursor = conn.cursor()

    query = '''
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.color as category_color
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ?
    '''
    params = [user_id]

    if month:
        query += " AND strftime('%Y-%m', t.date) = ?"
        params.append(month)

    query += " ORDER BY t.date DESC, t.id DESC"

    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    transactions = cursor.fetchall()

    close_db(conn)
    return transactions


def get_transaction_by_id(transaction_id, user_id):
    """Busca uma transação específica."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT t.*, c.name as category_name, c.icon as category_icon, c.color as category_color
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id = ? AND t.user_id = ?
    ''', (transaction_id, user_id))

    transaction = cursor.fetchone()
    close_db(conn)
    return transaction


def create_transaction(user_id, category_id, type_, description, amount, date, account_id=None):
    """Cria uma nova transação."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO transactions (user_id, account_id, category_id, type, description, amount, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, account_id, category_id, type_, description, amount, date))

        conn.commit()
        return cursor.lastrowid

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)


def update_transaction(transaction_id, user_id, category_id, type_, description, amount, date):
    """Atualiza uma transação existente."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE transactions
            SET category_id = ?, type = ?, description = ?, amount = ?, date = ?
            WHERE id = ? AND user_id = ?
        ''', (category_id, type_, description, amount, date, transaction_id, user_id))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)


def delete_transaction(transaction_id, user_id):
    """Deleta uma transação."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?',
                        (transaction_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)


def get_monthly_summary(user_id, month):
    """Retorna o resumo mensal (receitas, despesas, saldo)."""
    conn = get_db()
    cursor = conn.cursor()

    # Total de receitas
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions
        WHERE user_id = ? AND type = 'receita' AND strftime('%Y-%m', date) = ?
    ''', (user_id, month))
    income = cursor.fetchone()['total']

    # Total de despesas
    cursor.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM transactions
        WHERE user_id = ? AND type = 'despesa' AND strftime('%Y-%m', date) = ?
    ''', (user_id, month))
    expenses = cursor.fetchone()['total']

    close_db(conn)

    return {
        'income': income,
        'expenses': expenses,
        'balance': income - expenses
    }


def get_expenses_by_category(user_id, month):
    """Retorna despesas agrupadas por categoria para o mês."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT c.name, c.icon, c.color, COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type = 'despesa' AND strftime('%Y-%m', t.date) = ?
        GROUP BY c.id
        ORDER BY total DESC
    ''', (user_id, month))

    result = cursor.fetchall()
    close_db(conn)
    return result


def get_daily_totals(user_id, month):
    """Retorna totais diários de receitas e despesas."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date,
               SUM(CASE WHEN type = 'receita' THEN amount ELSE 0 END) as income,
               SUM(CASE WHEN type = 'despesa' THEN amount ELSE 0 END) as expenses
        FROM transactions
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        GROUP BY date
        ORDER BY date ASC
    ''', (user_id, month))

    result = cursor.fetchall()
    close_db(conn)
    return result
