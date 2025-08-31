from functools import wraps
from flask import redirect, url_for, flash, session


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar si el usuario está autenticado y es administrador
        if not session.get('username'):
            flash('Por favor inicia sesión para acceder a esta página.', 'danger')
            return redirect(url_for('login'))
       
        if not session.get('is_admin', False):
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('index'))
           
        return f(*args, **kwargs)
    return decorated_function