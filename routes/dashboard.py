from flask import Blueprint, render_template, session, redirect, url_for, request
from models.transaction import get_monthly_summary, get_expenses_by_category, get_transactions_by_user, get_daily_totals
from models.budget import get_budget_with_spent
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    # Mês atual ou selecionado
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))

    # Dados do dashboard
    summary = get_monthly_summary(user_id, month)
    expenses_by_category = get_expenses_by_category(user_id, month)
    recent_transactions = get_transactions_by_user(user_id, month=month, limit=5)
    budgets = get_budget_with_spent(user_id, month)
    daily_totals = get_daily_totals(user_id, month)

    # Preparar dados para gráficos (JSON-safe)
    chart_categories = []
    chart_amounts = []
    chart_colors = []
    chart_icons = []

    for cat in expenses_by_category:
        chart_categories.append(cat['name'])
        chart_amounts.append(float(cat['total']))
        chart_colors.append(cat['color'])
        chart_icons.append(cat['icon'])

    # Dados do gráfico de linha (diário)
    daily_labels = []
    daily_income = []
    daily_expenses = []

    for day in daily_totals:
        # Formatar data: "2026-04-15" -> "15/04"
        parts = day['date'].split('-')
        daily_labels.append(f"{parts[2]}/{parts[1]}")
        daily_income.append(float(day['income']))
        daily_expenses.append(float(day['expenses']))

    # Preparar budgets para template
    budgets_data = []
    for b in budgets:
        budget_amount = float(b['budget_amount'])
        spent = float(b['spent'])
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        budgets_data.append({
            'category_name': b['category_name'],
            'category_icon': b['category_icon'],
            'category_color': b['category_color'],
            'budget_amount': budget_amount,
            'spent': spent,
            'remaining': budget_amount - spent,
            'percentage': min(percentage, 100),
            'over_budget': spent > budget_amount
        })

    # Gerar lista de meses para o seletor (últimos 12 meses)
    months_list = []
    now = datetime.now()
    for i in range(12):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        month_str = f"{y}-{m:02d}"
        month_names = ['', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                       'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        month_label = f"{month_names[m]} {y}"
        months_list.append({'value': month_str, 'label': month_label})

    return render_template('dashboard.html',
        active_page='dashboard',
        user_name=session.get('user_name', 'Usuário'),
        user_email=session.get('user_email', ''),
        month=month,
        months_list=months_list,
        summary=summary,
        recent_transactions=recent_transactions,
        budgets_data=budgets_data,
        chart_categories=chart_categories,
        chart_amounts=chart_amounts,
        chart_colors=chart_colors,
        chart_icons=chart_icons,
        daily_labels=daily_labels,
        daily_income=daily_income,
        daily_expenses=daily_expenses,
    )
