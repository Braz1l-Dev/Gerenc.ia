from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash


def create_user(name, email, password):
    """Cria um novo usuário no banco de dados."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        ''', (name, email, hashed_password))

        conn.commit()
        user_id = cursor.lastrowid
        return user_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        close_db(conn)


def get_user_by_email(email):
    """Busca um usuário pelo e-mail."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    close_db(conn)
    return user


def get_user_by_id(user_id):
    """Busca um usuário pelo ID."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()

    close_db(conn)
    return user


def verify_password(stored_password, provided_password):
    """Verifica se a senha fornecida corresponde à senha armazenada."""
    return check_password_hash(stored_password, provided_password)


def update_user(user_id, name=None, email=None, currency=None, theme=None):
    """Atualiza dados do usuário."""
    conn = get_db()
    cursor = conn.cursor()

    fields = []
    values = []

    if name:
        fields.append('name = ?')
        values.append(name)
    if email:
        fields.append('email = ?')
        values.append(email)
    if currency:
        fields.append('currency = ?')
        values.append(currency)
    if theme:
        fields.append('theme = ?')
        values.append(theme)

    if not fields:
        close_db(conn)
        return False

    values.append(user_id)
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"

    try:
        cursor.execute(query, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)


def update_password(user_id, new_password):
    """Atualiza a senha do usuário."""
    conn = get_db()
    cursor = conn.cursor()

    hashed = generate_password_hash(new_password)

    try:
        cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed, user_id))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        close_db(conn)
