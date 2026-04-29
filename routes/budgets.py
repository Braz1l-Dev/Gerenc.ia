from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.budget import get_budget_with_spent, set_budget, delete_budget
from models.category import get_expense_categories
from datetime import datetime

budgets_bp = Blueprint('budgets', __name__)


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


@budgets_bp.route('/budgets')
def budgets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    current_month = request.args.get('month', datetime.now().strftime('%Y-%m'))

    # Buscar orçamentos com gastos
    raw_budgets = get_budget_with_spent(user_id, current_month)

    # Montar mês legível para cada orçamento
    month_names = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                   'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    # Processar dados dos orçamentos
    budgets_data = []
    total_budget = 0
    total_spent = 0

    for b in raw_budgets:
        amount = float(b['budget_amount'])
        spent = float(b['spent'])
        remaining = amount - spent
        percent = (spent / amount * 100) if amount > 0 else 0

        # Label do mês
        parts = b['month'].split('-')
        m_num = int(parts[1])
        month_label = f"{month_names[m_num]} {parts[0]}"

        budgets_data.append({
            'id': b['id'],
            'category_id': b['category_id'],
            'category_name': b['category_name'],
            'category_icon': b['category_icon'],
            'category_color': b['category_color'],
            'amount': amount,
            'spent': spent,
            'remaining': remaining,
            'percent': round(percent, 1),
            'month': b['month'],
            'month_label': month_label,
            'over_budget': spent > amount,
        })

        total_budget += amount
        total_spent += spent

    total_remaining = total_budget - total_spent
    total_percent = (total_spent / total_budget * 100) if total_budget > 0 else 0

    overview = {
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_remaining': total_remaining,
        'total_percent': round(total_percent, 1),
    }

    # Categorias de despesa (para o modal de novo orçamento)
    categories = get_expense_categories(user_id)

    # Lista de meses
    months_list = get_months_list()

    return render_template('budgets.html',
        active_page='budgets',
        user_name=session.get('user_name', 'Usuário'),
        user_email=session.get('user_email', ''),
        budgets=budgets_data,
        overview=overview,
        categories=categories,
        months_list=months_list,
        current_month=current_month,
    )


@budgets_bp.route('/budgets/add', methods=['POST'])
def add_budget():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        category_id = request.form.get('category_id')
        amount = float(request.form.get('amount', 0))
        month = request.form.get('month', datetime.now().strftime('%Y-%m'))

        if not category_id or amount <= 0:
            flash('Preencha todos os campos corretamente.', 'error')
            return redirect(url_for('budgets.budgets', month=month))

        set_budget(user_id, category_id, amount, month)
        flash('Orçamento criado com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao criar orçamento: {str(e)}', 'error')

    return redirect(url_for('budgets.budgets', month=month))


@budgets_bp.route('/budgets/edit/<int:budget_id>', methods=['POST'])
def edit_budget(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    try:
        category_id = request.form.get('category_id')
        amount = float(request.form.get('amount', 0))
        month = request.form.get('month', datetime.now().strftime('%Y-%m'))

        if not category_id or amount <= 0:
            flash('Preencha todos os campos corretamente.', 'error')
            return redirect(url_for('budgets.budgets', month=month))

        set_budget(user_id, category_id, amount, month)
        flash('Orçamento atualizado com sucesso!', 'success')

    except Exception as e:
        flash(f'Erro ao atualizar orçamento: {str(e)}', 'error')

    return redirect(url_for('budgets.budgets', month=month))


@budgets_bp.route('/budgets/delete/<int:budget_id>', methods=['POST'])
def delete_budget_route(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))

    try:
        deleted = delete_budget(budget_id, user_id)
        if deleted:
            flash('Orçamento excluído com sucesso!', 'success')
        else:
            flash('Orçamento não encontrado.', 'error')
    except Exception as e:
        flash(f'Erro ao excluir orçamento: {str(e)}', 'error')

    return redirect(url_for('budgets.budgets', month=month))
