-- TODO: Definir las tablas del sistema

-- Tabla de usuarios
CREATE TABLE users (
    -- TODO: Agregar campos para id, username, email, password_hash, created_at
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

-- TODO: Insertar datos de prueba