from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.category import (
    get_categories_by_user,
    get_category_by_id,
    create_category,
    update_category,
    delete_category,
    count_transactions_by_category
)

categories_bp = Blueprint('categories', __name__)


@categories_bp.before_request
def require_login():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))


@categories_bp.route('/categories')
def index():
    user_id = session['user_id']
    filter_type = request.args.get('type', 'all')

    if filter_type in ('despesa', 'receita'):
        categories = get_categories_by_user(user_id, filter_type)
    else:
        categories = get_categories_by_user(user_id)
        filter_type = 'all'

    # Conta transações por categoria
    categories_data = []
    for cat in categories:
        cat_dict = dict(cat)
        cat_dict['transaction_count'] = count_transactions_by_category(cat['id'], user_id)
        categories_data.append(cat_dict)

    return render_template(
        'categories.html',
        categories=categories_data,
        filter_type=filter_type,
        active_page='categories',
        user_name=session.get('user_name'),
        user_email=session.get('user_email')
    )


@categories_bp.route('/categories/create', methods=['POST'])
def create():
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    cat_type = request.form.get('type', '').strip()
    icon = request.form.get('icon', '📁').strip()
    color = request.form.get('color', '#6366F1').strip()

    if not name or not cat_type:
        flash('Nome e tipo são obrigatórios.', 'error')
        return redirect(url_for('categories.index'))

    if cat_type not in ('despesa', 'receita'):
        flash('Tipo inválido.', 'error')
        return redirect(url_for('categories.index'))

    try:
        create_category(user_id, name, cat_type, icon, color)
        flash('Categoria criada com sucesso!', 'success')
    except Exception:
        flash('Erro ao criar categoria.', 'error')

    return redirect(url_for('categories.index'))


@categories_bp.route('/categories/edit/<int:category_id>', methods=['POST'])
def edit(category_id):
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    cat_type = request.form.get('type', '').strip()
    icon = request.form.get('icon', '📁').strip()
    color = request.form.get('color', '#6366F1').strip()

    if not name or not cat_type:
        flash('Nome e tipo são obrigatórios.', 'error')
        return redirect(url_for('categories.index'))

    if cat_type not in ('despesa', 'receita'):
        flash('Tipo inválido.', 'error')
        return redirect(url_for('categories.index'))

    category = get_category_by_id(category_id, user_id)
    if not category:
        flash('Categoria não encontrada.', 'error')
        return redirect(url_for('categories.index'))

    try:
        update_category(category_id, user_id, name, cat_type, icon, color)
        flash('Categoria atualizada com sucesso!', 'success')
    except Exception:
        flash('Erro ao atualizar categoria.', 'error')

    return redirect(url_for('categories.index'))


@categories_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete(category_id):
    user_id = session['user_id']

    category = get_category_by_id(category_id, user_id)
    if not category:
        flash('Categoria não encontrada.', 'error')
        return redirect(url_for('categories.index'))

    success, message = delete_category(category_id, user_id)
    flash(message, 'success' if success else 'error')

    return redirect(url_for('categories.index'))


@categories_bp.route('/categories/<int:category_id>/json')
def get_json(category_id):
    """Retorna dados da categoria em JSON (para preencher modal de edição)."""
    user_id = session['user_id']
    category = get_category_by_id(category_id, user_id)

    if not category:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    return jsonify({
        'id': category['id'],
        'name': category['name'],
        'type': category['type'],
        'icon': category['icon'],
        'color': category['color']
    })
