from database import get_db, close_db


def get_budgets_by_user(user_id, month):
    """Busca todos os orçamentos do usuário para o mês."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT b.*, c.name as category_name, c.icon as category_icon, c.color as category_color
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.month = ?
        ORDER BY c.name ASC
    ''', (user_id, month))

    budgets = cursor.fetchall()
    close_db(conn)
    return budgets


def get_budget_with_spent(user_id, month):
    """Busca orçamentos com o valor já gasto no mês."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT
            b.id,
            b.amount as budget_amount,
            b.month,
            c.id as category_id,
            c.name as category_name,
            c.icon as category_icon,
            c.color as category_color,
            COALESCE(
                (SELECT SUM(t.amount)
                 FROM transactions t
                 WHERE t.user_id = b.user_id
                   AND t.category_id = b.category_id
                   AND t.type = 'despesa'
                   AND strftime('%Y-%m', t.date) = b.month
                ), 0
            ) as spent
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.month = ?
        ORDER BY c.name ASC
    ''', (user_id, month))

    budgets = cursor.fetchall()
    close_db(conn)
    return budgets


def set_budget(user_id, category_id, amount, month):
    """Define ou atualiza o orçamento de uma categoria."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO budgets (user_id, category_id, amount, month)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, category_id, month)
            DO UPDATE SET amount = excluded.amount
        ''', (user_id, category_id, amount, month))

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)


def delete_budget(budget_id, user_id):
    """Remove um orçamento."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM budgets WHERE id = ? AND user_id = ?',
                        (budget_id, user_id))
        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)
