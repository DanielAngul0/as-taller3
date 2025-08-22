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
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de carritos
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de items del carrito
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agregar índices para mejorar el rendimiento de las búsquedas
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_name ON products(name);
CREATE INDEX idx_carts_user_id ON carts(user_id);
CREATE INDEX idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);

-- Las restricciones de clave foránea ya están definidas en las tablas carts


-- Implementando datos de prueba de las tablas
-- Usuarios
INSERT INTO users (username, email, password_hash) VALUES
('juan', 'juan@example.com', 'hash1'),
('maria', 'maria@example.com', 'hash2'),
('pedro', 'pedro@example.com', 'hash3');

-- Productos
INSERT INTO products (name, description, price, stock, image_url) VALUES
('Laptop', 'Laptop potente para trabajo y juegos', 1200.00, 10, 'https://example.com/laptop.jpg'),
('Mouse', 'Mouse inalámbrico ergonómico', 25.50, 50, 'https://example.com/mouse.jpg'),
('Teclado', 'Teclado mecánico retroiluminado', 75.00, 30, 'https://example.com/teclado.jpg');

-- Carritos
INSERT INTO carts (user_id) VALUES
(1),
(2);

-- Items del carrito
INSERT INTO cart_items (cart_id, product_id, quantity) VALUES
(1, 1, 1), -- Juan tiene 1 Laptop
(1, 2, 2), -- Juan tiene 2 Mouse
(2, 3, 1); -- Maria tiene 1 Teclado