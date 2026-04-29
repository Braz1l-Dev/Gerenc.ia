from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Registrar blueprints
from routes.categories import categories_bp
from routes.auth import auth_bp
from routes.transactions import transactions_bp
from routes.budgets import budgets_bp

app.register_blueprint(categories_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(budgets_bp)

# Rota principal redireciona para login
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
