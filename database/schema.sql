-- TODO: Definir las tablas del sistema

-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos  
CREATE TABLE products (
    -- TODO: Agregar campos para id, name, description, price, stock, image_url, created_at
);

-- Tabla de carritos
CREATE TABLE carts (
    -- TODO: Agregar campos para id, user_id, created_at, updated_at
);

-- Tabla de items del carrito
CREATE TABLE cart_items (
    -- TODO: Agregar campos para id, cart_id, product_id, quantity, added_at
);

-- TODO: Agregar índices y restricciones de clave foránea

-- TODO: Insertar datos de prueba (si o si)