from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import requests
import os
from datetime import datetime

# --- Configuración de la aplicación Flask ---
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave-por-defecto-cambiar')

# --- URL base de la API (FastAPI) ---
API_URL = os.getenv('API_URL', 'http://api:8000')

# Prefijo común para endpoints de la API
API_PREFIX = "/api/v1"

# --- Helpers básicos ---
def api_request(endpoint, method='GET', data=None, headers=None, params=None, timeout=10):
    """
    Helper para llamar a la API: devuelve (status_code, json|texto)
    """
    # Construir URL correctamente evitando dobles barras
    base_url = API_URL.rstrip('/')
    endpoint = endpoint.lstrip('/')
    url = f"{base_url}{API_PREFIX}/{endpoint}"
    
    try:
        method = method.upper()
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=params or data, timeout=timeout)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data, params=params, timeout=timeout)
        elif method == 'PUT':
            resp = requests.put(url, headers=headers, json=data, params=params, timeout=timeout)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, params=params, timeout=timeout)
        else:
            return 0, {"error": f"Método HTTP no soportado: {method}"}

        try:
            response_data = resp.json()
            return resp.status_code, response_data
        except ValueError:
            return resp.status_code, resp.text
    except requests.RequestException as e:
        print(f"Error en API request: {e}")
        return 0, {"error": str(e)}


def is_logged_in():
    """Por ahora: sesión activa si existe 'username' en session."""
    return 'username' in session


# --- Rutas (esqueleto) ---
@app.route("/")
def index():
    try:
        # Depuración: imprimir la URL que se está llamando
        print(f"Llamando a: {API_URL}{API_PREFIX}/products", flush=True)
        
        status, data = api_request("/products")
        print(f"Status: {status}, Data: {data}, Type: {type(data)}", flush=True)
        
        # Verificamos si la respuesta es exitosa
        if status == 200:
            # Verificamos si la respuesta es una lista
            if isinstance(data, list):
                products = data
            elif isinstance(data, dict):
                # Si es un diccionario, intentamos extraer la lista de productos
                products = data.get('products', [])
                if not isinstance(products, list):
                    products = []
            else:
                products = []
        else:
            products = []
            flash('Error al obtener productos de la API', 'danger')
            
    except Exception as e:
        print("Error al consumir API:", e, flush=True)
        products = []
        flash('Error de conexión con la API', 'danger')

    # Aseguramos que products sea una lista antes de hacer el slice
    if not isinstance(products, list):
        products = []
    
    # Aquí limitamos a los primeros 3 productos destacados
    destacados = products[:3]

    return render_template("index.html", products=destacados)

@app.route('/products')
def products():
    # Llamada a la API para obtener productos
    status, data = api_request("/products")

    if status == 200:
        if isinstance(data, list):
            productos = data
        elif isinstance(data, dict):
            productos = data.get('products', [])
            if not isinstance(productos, list):
                productos = []
        else:
            productos = []
    else:
        flash(f"Error al cargar productos: {data}", "danger")
        productos = []

    return render_template('products.html', products=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Por favor ingrese usuario y contraseña', 'danger')
            return render_template('login.html')

        status, data = api_request("/users/login", method='POST', data={
            "username": username,
            "password": password
        })

        if status == 200:
            session['username'] = data.get('username', '')
            flash('Sesión iniciada con éxito', 'success')
            return redirect(url_for('index'))
        else:
            error_msg = data.get('detail', 'Error en el inicio de sesión')
            flash(f'Error: {error_msg}', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password', '')

        if not all([username, email, password]):
            flash('Por favor complete todos los campos', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('register.html')

        status, data = api_request("/users/register", method='POST', data={
            "username": username,
            "email": email,
            "password": password
        })

        if status == 200:
            flash('Registro exitoso, ahora puedes iniciar sesión', 'success')
            return redirect(url_for('login'))
        else:
            error_msg = data.get('detail', 'Error en el registro')
            flash(f'Error: {error_msg}', 'danger')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'success')
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    if not is_logged_in():
        flash('Debe iniciar sesión para ver el carrito', 'warning')
        return redirect(url_for('login'))
    
    # Obtener carrito del usuario
    status, data = api_request("/carts")
    
    if status == 200:
        cart_items = data
    else:
        cart_items = []
        flash('Error al cargar el carrito', 'danger')
    
    return render_template('cart.html', cart_items=cart_items)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not is_logged_in():
        flash('Debe iniciar sesión para agregar productos al carrito', 'warning')
        return redirect(url_for('login'))
    
    quantity = int(request.form.get('quantity', 1))
    
    status, data = api_request("/carts/items", method='POST', data={
        "product_id": product_id,
        "quantity": quantity
    })
    
    if status == 200:
        flash('Producto agregado al carrito', 'success')
    else:
        error_msg = data.get('detail', 'Error al agregar al carrito')
        flash(f'Error: {error_msg}', 'danger')
    
    return redirect(url_for('products'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)