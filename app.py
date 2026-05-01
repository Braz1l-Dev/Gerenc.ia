from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Registrar blueprints
from routes.categories import categories_bp
from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.budgets import budgets_bp
from routes.dashboard import dashboard_bp
from routes.settings import settings_bp

app.register_blueprint(categories_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(budgets_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(settings_bp)

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
