from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db, close_db, create_default_categories

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se já está logado, vai direto para categorias
    if 'user_id' in session:
        return redirect(url_for('categories.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, password)
        ).fetchone()
        close_db(db)

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('categories.index'))
        else:
            flash('E-mail ou senha inválidos!', 'danger')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Se já está logado, vai direto para categorias
    if 'user_id' in session:
        return redirect(url_for('categories.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm = request.form.get('confirm_password', '').strip()

        # Validações
        if not name or not email or not password:
            flash('Preencha todos os campos!', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('As senhas não coincidem!', 'danger')
            return render_template('register.html')

        db = get_db()

        # Verifica se email já existe
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            close_db(db)
            flash('Este e-mail já está cadastrado!', 'danger')
            return render_template('register.html')

        # Cria o usuário
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
            (name, email, password)
        )
        db.commit()
        user_id = cursor.lastrowid
        close_db(db)

        # Cria categorias padrão
        create_default_categories(user_id)

        # Já faz login automático
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email

        flash(f'Bem-vindo(a), {name}! Conta criada com sucesso!', 'success')
        return redirect(url_for('categories.index'))

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('auth.login'))
