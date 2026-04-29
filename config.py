import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pedro-finance-secret-key-2026'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pedro.db')
