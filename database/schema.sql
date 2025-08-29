-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos  
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de carritos
CREATE TABLE IF NOT EXISTS carts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de items del carrito
CREATE TABLE IF NOT EXISTS cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Agregar índices para mejorar el rendimiento de las búsquedas
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_carts_user_id ON carts(user_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id);

-- Las restricciones de clave foránea ya están definidas en las tablas carts


-- ==========================
-- Insertar datos de prueba SOLO si no existen
-- ==========================

-- Usuarios
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'juan') THEN
        INSERT INTO users (username, email, password_hash, is_active, is_admin)
        VALUES
            ('admin', 'admin@example.com', 'hash_admin', TRUE, TRUE),
            ('juan', 'juan@example.com', 'hash1', TRUE, FALSE),
            ('maria', 'maria@example.com', 'hash2', TRUE, FALSE),
            ('pedro', 'pedro@example.com', 'hash3', TRUE, FALSE);
    END IF;
END $$;

-- Productos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM products WHERE name = 'Laptop') THEN
        INSERT INTO products (name, description, price, stock, image_url) VALUES
        ('Laptop', 'Laptop potente para trabajo y juegos', 1200.00, 10, 'https://example.com/laptop.jpg'),
        ('Mouse', 'Mouse inalámbrico ergonómico', 25.50, 50, 'https://example.com/mouse.jpg'),
        ('Teclado', 'Teclado mecánico retroiluminado', 75.00, 30, 'https://example.com/teclado.jpg');
    END IF;
END $$;

-- Carritos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM carts WHERE user_id = 1) THEN
        INSERT INTO carts (user_id) VALUES (1), (2);
    END IF;
END $$;

-- Items del carrito
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM cart_items WHERE cart_id = 1 AND product_id = 1) THEN
        INSERT INTO cart_items (cart_id, product_id, quantity) VALUES
        (1, 1, 1), -- Juan tiene 1 Laptop
        (1, 2, 2), -- Juan tiene 2 Mouse
        (2, 3, 1); -- Maria tiene 1 Teclado
    END IF;
END $$;