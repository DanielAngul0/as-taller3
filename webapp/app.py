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
    
    # Preparar headers con autenticación si existe
    final_headers = headers or {}
    if 'access_token' in session:
        final_headers['Authorization'] = f"Bearer {session['access_token']}"
    
    # Si es una solicitud GET, agregar user_id a los parámetros si está disponible
    if method.upper() == 'GET' and 'user_id' in session:
        params = params or {}
        params['user_id'] = session['user_id']
    
    try:
        method = method.upper()
        if method == 'GET':
            resp = requests.get(url, headers=final_headers, params=params, timeout=timeout)
        elif method == 'POST':
            # Para POST, agregar user_id al cuerpo de la solicitud si está disponible
            if data is None:
                data = {}
            if 'user_id' in session and isinstance(data, dict):
                data['user_id'] = session['user_id']
            resp = requests.post(url, headers=final_headers, json=data, params=params, timeout=timeout)
        elif method == 'PUT':
            if data is None:
                data = {}
            if 'user_id' in session and isinstance(data, dict):
                data['user_id'] = session['user_id']
            resp = requests.put(url, headers=final_headers, json=data, params=params, timeout=timeout)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=final_headers, params=params, timeout=timeout)
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
    """Verifica si el usuario tiene una sesión activa"""
    return 'username' in session and 'user_id' in session and 'access_token' in session


# --- Rutas ---
@app.route("/")
def index():
    try:
        status, data = api_request("/products")
        print(f"DEBUG - Index API Response: Status={status}, Data type: {type(data)}", flush=True)
        
        products = []
        if status == 200:
            if isinstance(data, list):
                products = data
            elif isinstance(data, dict):
                products = data.get('products', [])
        
        # Aseguramos que products sea una lista
        if not isinstance(products, list):
            products = []
            
    except Exception as e:
        print("Error al consumir API:", e, flush=True)
        products = []
        flash('Error de conexión con la API', 'danger')

    # Limitar a los primeros 3 productos destacados
    destacados = products[:3]
    return render_template("index.html", products=destacados)

@app.route('/products')
def products():
    status, data = api_request("/products")
    print(f"DEBUG - Products API Response: Status={status}", flush=True)
    
    productos = []
    if status == 200:
        if isinstance(data, list):
            productos = data
        elif isinstance(data, dict):
            productos = data.get('products', [])
    else:
        error_msg = data.get('detail', 'Error desconocido') if isinstance(data, dict) else str(data)
        flash(f"Error al cargar productos: {error_msg}", "danger")

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

        print(f"DEBUG - Login API Response: Status={status}, Data={data}", flush=True)
        
        if status == 200:
            session['username'] = data.get('username', '')
            session['user_id'] = data.get('user_id', '')
            session['access_token'] = data.get('access_token', '')
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
    print(f"DEBUG - Cart API Response: Status={status}, Data={data}", flush=True)
    
    cart_items = []
    total = 0
    
    if status == 200:
        # Obtener los items del carrito
        if isinstance(data, dict) and 'items' in data:
            raw_items = data.get('items', [])
        elif isinstance(data, list):
            raw_items = data
        else:
            raw_items = []
        
        # Para cada item, obtener la información completa del producto
        for item in raw_items:
            product_id = item.get('product_id')
            if product_id:
                # Obtener información del producto
                product_status, product_data = api_request(f"/products/{product_id}")
                if product_status == 200:
                    # Combinar la información del item del carrito con la del producto
                    combined_item = {
                        'id': item.get('id'),
                        'product_id': product_id,
                        'product_name': product_data.get('name', 'Producto no disponible'),
                        'price': float(product_data.get('price', 0)),
                        'quantity': item.get('quantity', 0),
                        'added_at': item.get('added_at'),
                        'image_url': product_data.get('image_url', '')
                    }
                    cart_items.append(combined_item)
                    
                    # Calcular el total
                    total += combined_item['price'] * combined_item['quantity']
                else:
                    # Si no se puede obtener la información del producto, usar valores por defecto
                    cart_items.append({
                        'id': item.get('id'),
                        'product_id': product_id,
                        'product_name': 'Producto no disponible',
                        'price': 0,
                        'quantity': item.get('quantity', 0),
                        'added_at': item.get('added_at')
                    })
            else:
                # Item sin product_id
                cart_items.append({
                    'id': item.get('id'),
                    'product_name': 'Producto no disponible',
                    'price': 0,
                    'quantity': item.get('quantity', 0),
                    'added_at': item.get('added_at')
                })
    else:
        error_msg = data.get('detail', 'Error al cargar el carrito') if isinstance(data, dict) else str(data)
        flash(f'Error: {error_msg}', 'danger')
    
    print(f"DEBUG - Final cart items: {cart_items}", flush=True)
    print(f"DEBUG - Final total: {total}", flush=True)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not is_logged_in():
        flash('Debe iniciar sesión para agregar productos al carrito', 'warning')
        return redirect(url_for('login'))
    
    quantity = int(request.form.get('quantity', 1))
    
    # Llamar a la API para agregar al carrito
    status, data = api_request("/carts/items", method='POST', data={
        "product_id": product_id,
        "quantity": quantity
    })
    
    print(f"DEBUG - Add to cart API Response: Status={status}, Data={data}", flush=True)
    
    # Tanto 200 (OK) como 201 (Created) son respuestas exitosas
    if status in [200, 201]:
        flash('Producto agregado al carrito', 'success')
    else:
        error_msg = data.get('detail', 'Error al agregar al carrito') if isinstance(data, dict) else str(data)
        flash(f'Error: {error_msg}', 'danger')
    
    return redirect(url_for('products'))

@app.route('/update-cart-item/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    if not is_logged_in():
        return jsonify({"success": False, "message": "Debe iniciar sesión"})
    
    quantity = request.json.get('quantity', 1)
    
    status, data = api_request(f"/carts/items/{item_id}", method='PUT', data={"quantity": quantity})
    
    if status == 200:
        return jsonify({"success": True, "new_total": data.get('total', 0)})
    else:
        return jsonify({"success": False, "message": data.get('detail', 'Error al actualizar')})

@app.route('/remove-from-cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if not is_logged_in():
        return jsonify({"success": False, "message": "Debe iniciar sesión"})
    
    status, data = api_request(f"/carts/items/{item_id}", method='DELETE')
    
    if status == 200:
        return jsonify({"success": True, "new_total": data.get('total', 0)})
    else:
        return jsonify({"success": False, "message": data.get('detail', 'Error al eliminar')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)