from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.transaction import (
    get_transactions_by_user,
    get_monthly_summary,
    create_transaction,
    update_transaction,
    delete_transaction
)
from models.category import get_categories_by_user
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)


def get_months_list():
    """Gera lista dos últimos 12 meses para o seletor."""
    months_list = []
    now = datetime.now()
    month_names = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    for i in range(12):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        month_str = f"{y}-{m:02d}"
        month_label = f"{month_names[m]} {y}"
        months_list.append({'value': month_str, 'label': month_label})
    return months_list


@transactions_bp.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Filtros
    current_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    current_type = request.args.get('type', '')
    current_category = request.args.get('category', '')

    # Buscar transações do mês
    all_transactions = get_transactions_by_user(user_id, month=current_month)

    # Aplicar filtro de tipo
    if current_type:
        all_transactions = [t for t in all_transactions if t['type'] == current_type]

    # Aplicar filtro de categoria
    if current_category:
        all_transactions = [t for t in all_transactions if str(t['category_id']) == str(current_category)]

    # Resumo do mês
    summary = get_monthly_summary(user_id, current_month)

    # Categorias para filtro e modal
    categories = get_categories_by_user(user_id)

    # Lista de meses
    months_list = get_months_list()

    # Converter current_category para int (para comparação no template)
    current_category_int = int(current_category) if current_category else None

    return render_template('transactions.html',
        active_page='transactions',
        user_name=session.get('user_name', 'Usuário'),
        user_email=session.get('user_email', ''),
        transactions=all_transactions,
        summary=summary,
        categories=categories,
        months_list=months_list,
        current_month=current_month,
        current_type=current_type,
        current_category=current_category_int,
    )


@transactions_bp.route('/transactions/add', methods=['POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        type_ = request.form.get('type', 'despesa')
        description = request.form.get('description', '').strip()
        amount = float(request.form.get('amount', 0))
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        category_id = request.form.get('category_id') or None

        if not description or amount <= 0:
            flash('Preencha todos os campos corretamente.', 'error')
            return redirect(url_for('transactions.transactions'))

        create_transaction(user_id, category_id, type_, description, amount, date)
        flash('Transação adicionada com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao adicionar transação: {str(e)}', 'error')

    # Redirecionar para o mês da transação
    month = date[:7] if date else datetime.now().strftime('%Y-%m')
    return redirect(url_for('transactions.transactions', month=month))


@transactions_bp.route('/transactions/edit/<int:transaction_id>', methods=['POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        type_ = request.form.get('type', 'despesa')
        description = request.form.get('description', '').strip()
        amount = float(request.form.get('amount', 0))
        date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        category_id = request.form.get('category_id') or None

        if not description or amount <= 0:
            flash('Preencha todos os campos corretamente.', 'error')
            return redirect(url_for('transactions.transactions'))

        update_transaction(transaction_id, user_id, category_id, type_, description, amount, date)
        flash('Transação atualizada com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao atualizar transação: {str(e)}', 'error')

    month = date[:7] if date else datetime.now().strftime('%Y-%m')
    return redirect(url_for('transactions.transactions', month=month))


@transactions_bp.route('/transactions/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction_route(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))

    try:
        deleted = delete_transaction(transaction_id, user_id)
        if deleted:
            flash('Transação excluída com sucesso!', 'success')
        else:
            flash('Transação não encontrada.', 'error')
    except Exception as e:
        flash(f'Erro ao excluir transação: {str(e)}', 'error')

    return redirect(url_for('transactions.transactions', month=month))
