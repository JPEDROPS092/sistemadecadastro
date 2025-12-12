from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def login_required(f):
    """Decorator para exigir login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para exigir permissão de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_admin:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function

def gerente_required(f):
    """Decorator para exigir permissão de gerente ou superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))

        if not current_user.is_gerente:
            flash('Você não tem permissão para acessar esta página.', 'danger')
            return redirect(url_for('main.index'))

        return f(*args, **kwargs)
    return decorated_function
