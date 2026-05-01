from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from database import get_db, close_db
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    return render_template('dashboard.html',
        active_page='dashboard',
        user_name=session.get('user_name', 'Usuário'),
        user_email=session.get('user_email', '')
    )


@dashboard_bp.route('/api/dashboard/resumo')
def resumo():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401

    user_id = session['user_id']
    ano_atual = datetime.now().year
    mes_atual = datetime.now().month
    mes_atual_str = f"{ano_atual}-{mes_atual:02d}"

    conn = get_db()
    cursor = conn.cursor()

    # =============================
    # Entradas e saídas por mês
    # =============================
    meses = []
    entradas = []
    saidas = []

    for mes in range(1, 13):
        mes_str = f"{ano_atual}-{mes:02d}"

        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions
            WHERE user_id = ? AND type = 'receita'
            AND strftime('%Y-%m', date) = ?
        ''', (user_id, mes_str))
        total_entrada = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COALESCE(SUM(amount), 0) FROM transactions
            WHERE user_id = ? AND type = 'despesa'
            AND strftime('%Y-%m', date) = ?
        ''', (user_id, mes_str))
        total_saida = cursor.fetchone()[0]

        meses.append(f"{mes:02d}/{ano_atual}")
        entradas.append(float(total_entrada))
        saidas.append(float(total_saida))

    # =============================
    # Gastos por categoria (pizza)
    # =============================
    cursor.execute('''
        SELECT c.name, c.icon, c.color, COALESCE(SUM(t.amount), 0) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = ? AND t.type = 'despesa'
        GROUP BY c.name, c.icon, c.color
        ORDER BY total DESC
    ''', (user_id,))
    gastos_categoria = cursor.fetchall()

    categorias = [f"{g['icon']} {g['name']}" for g in gastos_categoria]
    valores_categoria = [float(g['total']) for g in gastos_categoria]
    cores_categoria = [g['color'] for g in gastos_categoria]

    # =============================
    # Orçamentos: planejado vs gasto
    # =============================
    cursor.execute('''
        SELECT b.id, b.amount, c.name, c.icon, c.color
        FROM budgets b
        JOIN categories c ON b.category_id = c.id
        WHERE b.user_id = ? AND b.month = ?
    ''', (user_id, mes_atual_str))
    orcamentos = cursor.fetchall()

    orc_labels = []
    orc_planejado = []
    orc_gasto = []
    orc_cores = []

    for orc in orcamentos:
        cursor.execute('''
            SELECT COALESCE(SUM(t.amount), 0) FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.type = 'despesa'
            AND c.name = ?
            AND strftime('%Y-%m', t.date) = ?
        ''', (user_id, orc['name'], mes_atual_str))
        total_gasto = cursor.fetchone()[0]

        orc_labels.append(f"{orc['icon']} {orc['name']}")
        orc_planejado.append(float(orc['amount']))
        orc_gasto.append(float(total_gasto))
        orc_cores.append(orc['color'])

    close_db(conn)

    return jsonify({
        'meses': meses,
        'entradas': entradas,
        'saidas': saidas,
        'categorias': categorias,
        'valores_categoria': valores_categoria,
        'cores_categoria': cores_categoria,
        'orc_labels': orc_labels,
        'orc_planejado': orc_planejado,
        'orc_gasto': orc_gasto,
        'orc_cores': orc_cores,
        'mes_atual': mes_atual_str
    })
