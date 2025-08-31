from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
import requests
import os
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from utils import admin_required


# --- Configuración de la aplicación Flask ---
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'clave-por-defecto-cambiar')


# --- Configuración de JWT ---
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-cambiar-en-produccion')
app.config['JWT_TOKEN_LOCATION'] = ['headers']  # Los tokens se envían en headers
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'


# Inicializar JWTManager
jwt = JWTManager(app)


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
    final_headers = {}
    if headers:
        final_headers.update(headers)
    if 'access_token' in session:
        final_headers['Authorization'] = f"Bearer {session['access_token']}"

    # Para endpoints que esperamos JSON por defecto (se puede mantener para compatibilidad)
    json_endpoints = ["users/login", "users/register", "admin/products", "carts/items"]
    if any(ep in endpoint for ep in json_endpoints) or endpoint.startswith(("admin/products/", "carts/items/")):
        final_headers.setdefault('Content-Type', 'application/json')

    try:
        method = method.upper()

        if method == 'GET':
            resp = requests.get(url, headers=final_headers, params=params, timeout=timeout)

        elif method == 'POST':
            # Si se indicó explícitamente JSON en headers o se pasó un dict en data -> enviar JSON
            if final_headers.get('Content-Type') == 'application/json' or isinstance(data, dict):
                resp = requests.post(url, headers=final_headers, json=data, timeout=timeout)
            else:
                # En caso contrario, enviar form-encoded o params (según se necesite)
                resp = requests.post(url, headers=final_headers, data=params or data, timeout=timeout)

        elif method == 'PUT':
            # Para todas las requests PUT, usar json=data
            resp = requests.put(url, headers=final_headers, json=data, timeout=timeout)

        elif method == 'DELETE':
            resp = requests.delete(url, headers=final_headers, params=params, timeout=timeout)

        else:
            return 0, {"error": f"Método HTTP no soportado: {method}"}

        # Manejar respuestas vacías (como 204 No Content)
        if resp.status_code == 204:
            return resp.status_code, {}

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

# Ruta para el dashboard de administración
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Obtener datos de la API para el dashboard de administración
    users_status, users_data = api_request("/admin/users")
    products_status, products_data = api_request("/admin/products")
    
    users = users_data if users_status == 200 else []
    products = products_data if products_status == 200 else []
    
    # Crear respuesta y evitar caching
    response = make_response(render_template('admin.html', users=users, products=products))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


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
            # Verificar que data es un diccionario antes de acceder a sus propiedades
            if isinstance(data, dict):
                session['username'] = data.get('username', '')
                session['user_id'] = data.get('user_id', '')
                session['access_token'] = data.get('access_token', '')
                session['is_admin'] = data.get('is_admin', False)
                flash('Sesión iniciada con éxito', 'success')
                
                # Redirigir según el , administradores van a admin_dashboard, otros a index
                if session.get('is_admin'):
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('index'))
                
            else:
                flash('Error en el formato de respuesta del servidor', 'danger')
        else:
            # Manejar diferentes tipos de respuestas de error
            if isinstance(data, dict):
                error_msg = data.get('detail', 'Error en el inicio de sesión')
            else:
                # Si data es una cadena (como HTML de error), mostrar un mensaje genérico
                error_msg = 'Error en el servidor. Por favor, intente más tarde.'
                print(f"Error detallado del servidor: {data}", flush=True)
           
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

# Ruta para ver el carrito
@app.route('/cart')
def cart():
    if not is_logged_in():
        flash('Debe iniciar sesión para ver el carrito', 'warning')
        return redirect(url_for('login'))
   
    # Obtener carrito del usuario
    status, data = api_request("/carts", params={"user_id": session['user_id']})
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

# Ruta para agregar un producto al carrito
@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not is_logged_in():
        flash('Debe iniciar sesión para agregar productos al carrito', 'warning')
        return redirect(url_for('login'))
   
    quantity = int(request.form.get('quantity', 1))
   
    # Llamar a la API para agregar al carrito
    status, data = api_request("/carts/items", method='POST', data={
        "user_id": session['user_id'],
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

# Ruta para vaciar el carrito
@app.route('/clear-cart', methods=['POST'])
def clear_cart():
    if not is_logged_in():
        return jsonify({"success": False, "message": "Debe iniciar sesión"})
   
    status, data = api_request("/carts/", method='DELETE', params={"user_id": session['user_id']})
   
    if status == 200 or status == 204:
        flash('Carrito vaciado correctamente', 'success')
        return jsonify({"success": True})
    else:
        error_msg = data.get('detail', 'Error al vaciar el carrito') if isinstance(data, dict) else str(data)
        return jsonify({"success": False, "message": error_msg})

# Ruta para eliminar un item del carrito
@app.route('/remove-from-cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if not is_logged_in():
        return jsonify({"success": False, "message": "Debe iniciar sesión"})
   
    status, data = api_request(f"/carts/items/{item_id}", method='DELETE')
   
    if status == 200:
        flash('Producto eliminado del carrito', 'success')
        return jsonify({"success": True})
    else:
        error_msg = data.get('detail', 'Error al eliminar') if isinstance(data, dict) else str(data)
        return jsonify({"success": False, "message": error_msg})

# Ruta para actualizar la cantidad de un item del carrito
@app.route('/update-cart-item/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    if not is_logged_in():
        return jsonify({"success": False, "message": "Debe iniciar sesión"})
   
    quantity = request.json.get('quantity', 1)
    
    # Llamar a la API para actualizar la cantidad
    status, data = api_request(f"/carts/items/{item_id}", method='PUT', data={
        "quantity": quantity
    })
   
    if status == 200:
        return jsonify({"success": True})
    else:
        error_msg = data.get('detail', 'Error al actualizar') if isinstance(data, dict) else str(data)
        return jsonify({"success": False, "message": error_msg})


# Perfil de usuario
@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if not is_logged_in():
        flash('Debe iniciar sesión para acceder a su perfil', 'warning')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Procesar actualización de perfil
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        
        # Llamar a la API para actualizar el perfil
        status, data = api_request(f"/users/{session['user_id']}", method='PUT', data={
            "username": username,
            "email": email,
            "current_password": current_password
        })
        
        if status == 200:
            session['username'] = username
            flash('Perfil actualizado correctamente', 'success')
        else:
            error_msg = data.get('detail', 'Error al actualizar el perfil')
            flash(f'Error: {error_msg}', 'danger')
        
        return redirect(url_for('perfil'))
    
    # Obtener información del usuario
    status, data = api_request(f"/users/{session['user_id']}")
    
    if status == 200:
        usuario = data
    else:
        usuario = {"username": session.get('username', ''), "email": ""}
        flash('Error al cargar información del perfil', 'danger')
    
    return render_template('perfil.html', usuario=usuario)

# Cambiar contraseña
@app.route('/cambiar-password', methods=['POST'])
def cambiar_password():
    if not is_logged_in():
        return jsonify({"success": False, "message": "Debe iniciar sesión"})
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('Las contraseñas no coinciden', 'danger')
        return redirect(url_for('perfil'))
    
    # Llamar a la API para cambiar la contraseña
    status, data = api_request(
        f"/users/{session['user_id']}/change-password", 
        method='POST', 
        data={
            "current_password": current_password,
            "new_password": new_password
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if status == 200:
        flash('Contraseña cambiada correctamente', 'success')
    else:
        error_msg = data.get('detail', 'Error al cambiar la contraseña')
        flash(f'Error: {error_msg}', 'danger')
    
    return redirect(url_for('perfil'))


# Crear nuevo producto
@app.route('/admin/create-product', methods=['POST'])
@admin_required
def create_product():
    try:
        # Usar data en lugar de params para enviar como JSON
        data = {
            "name": request.form.get('name'),
            "description": request.form.get('description'),
            "price": float(request.form.get('price')),
            "stock": int(request.form.get('stock')),
            "image_url": request.form.get('image_url', '')
        }
        
        status, response_data = api_request("/admin/products", method='POST', data=data)
       
        if status == 201:
            flash('Producto creado exitosamente', 'success')
        else:
            error_msg = response_data.get('detail', 'Error al crear el producto')
            flash(f'Error: {error_msg}', 'danger')
   
    except Exception as e:
        flash(f'Error al crear el producto: {str(e)}', 'danger')
   
    return redirect(url_for('admin_dashboard'))

# Actualizar producto
@app.route('/admin/update-product', methods=['POST'])
@admin_required
def update_product_admin():
    try:
        product_id = request.form.get('id')
        # Validar y convertir datos
        name = request.form.get('name')
        description = request.form.get('description')
        
        try:
            price = float(request.form.get('price'))
        except (TypeError, ValueError):
            flash('El precio debe ser un número válido', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        try:
            stock = int(request.form.get('stock'))
        except (TypeError, ValueError):
            flash('El stock debe ser un número entero válido', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        image_url = request.form.get('image_url', '')
        
        # Usar data en lugar de params para enviar como JSON
        data = {
            "name": name,
            "description": description,
            "price": price,
            "stock": stock,
            "image_url": image_url
        }
        
        print(f"DEBUG - Updating product {product_id} with data: {data}")
        
        status, response_data = api_request(f"/admin/products/{product_id}", method='PUT', data=data)
       
        if status == 200:
            flash('Producto actualizado exitosamente', 'success')
        else:
            error_msg = response_data.get('detail', 'Error al actualizar el producto')
            flash(f'Error: {error_msg}', 'danger')
   
    except Exception as e:
        print(f"Error updating product: {e}")
        flash(f'Error al actualizar el producto: {str(e)}', 'danger')
   
    return redirect(url_for('admin_dashboard'))


# Eliminar producto
@app.route('/admin/delete-product', methods=['POST'])
@admin_required
def delete_product():
    try:
        product_id = request.form.get('id')
        status, data = api_request(f"/admin/products/{product_id}", method='DELETE')
       
        if status == 200:
            flash('Producto eliminado exitosamente', 'success')
        else:
            error_msg = data.get('detail', 'Error al eliminar el producto')
            flash(f'Error: {error_msg}', 'danger')
   
    except Exception as e:
        flash('Error al eliminar el producto', 'danger')
   
    return redirect(url_for('admin_dashboard'))

# Hacer admin a un usuario
@app.route('/admin/make-admin/<int:user_id>', methods=['POST'])
@admin_required
def make_admin(user_id):
    try:
        status, data = api_request(f"/admin/users/{user_id}/make-admin", method='PUT')
       
        if status == 200:
            flash('Usuario convertido en administrador exitosamente', 'success')
        else:
            error_msg = data.get('detail', 'Error al hacer admin al usuario')
            flash(f'Error: {error_msg}', 'danger')
   
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
   
    return redirect(url_for('admin_dashboard'))

# Quitar el admin a un usuario
@app.route('/admin/remove-admin/<int:user_id>', methods=['POST'])
@admin_required
def remove_admin(user_id):
    try:
        status, data = api_request(f"/admin/users/{user_id}/remove-admin", method='PUT')
       
        if status == 200:
            flash('Privilegios de administrador removidos exitosamente', 'success')
        else:
            error_msg = data.get('detail', 'Error al remover privilegios de administrador')
            flash(f'Error: {error_msg}', 'danger')
   
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
   
    return redirect(url_for('admin_dashboard'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
    