from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    user_id = session['user_id']
    
    # Buscar contas do usuário
    accounts = db.execute(
        'SELECT * FROM accounts WHERE user_id = ?', (user_id,)
    ).fetchall()
    
    return render_template('settings.html', accounts=accounts)


@settings_bp.route('/settings/accounts', methods=['POST'])
def add_account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    user_id = session['user_id']
    
    name = request.form['name']
    acc_type = request.form['type']
    balance = float(request.form.get('balance', 0))
    icon = request.form.get('icon', '🏦')
    color = request.form.get('color', '#4A90D9')
    
    db.execute(
        'INSERT INTO accounts (user_id, name, type, balance, icon, color) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, name, acc_type, balance, icon, color)
    )
    db.commit()
    
    flash('Conta criada com sucesso!', 'success')
    return redirect(url_for('settings.index'))


@settings_bp.route('/settings/accounts/<int:account_id>/edit', methods=['POST'])
def edit_account(account_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    user_id = session['user_id']
    
    name = request.form['name']
    acc_type = request.form['type']
    balance = float(request.form.get('balance', 0))
    icon = request.form.get('icon', '🏦')
    color = request.form.get('color', '#4A90D9')
    
    db.execute(
        'UPDATE accounts SET name=?, type=?, balance=?, icon=?, color=? WHERE id=? AND user_id=?',
        (name, acc_type, balance, icon, color, account_id, user_id)
    )
    db.commit()
    
    flash('Conta atualizada com sucesso!', 'success')
    return redirect(url_for('settings.index'))


@settings_bp.route('/settings/accounts/<int:account_id>/delete', methods=['POST'])
def delete_account(account_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    user_id = session['user_id']
    
    db.execute('DELETE FROM accounts WHERE id = ? AND user_id = ?', (account_id, user_id))
    db.commit()
    
    flash('Conta excluída com sucesso!', 'success')
    return redirect(url_for('settings.index'))
