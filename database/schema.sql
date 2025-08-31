\c tienda_db;

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
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin') THEN
        INSERT INTO users (username, email, password_hash, is_active, is_admin)
        VALUES
            -- Contraseñas hasheadas generadas con bcrypt
            -- admin: admin123
            -- juan: juanUser123
            -- maria: marioUser123
            -- pedro: pedroUser123
            ('admin', 'admin@example.com', '$2b$12$THljvHVYeRZMYIt6srfRme4gn.Cr7.ab3vvYOHSS3zcN/DypDwPsK', TRUE, TRUE),
            ('juan', 'juan@example.com', '$2b$12$g2.0x1t8ivKO7uV86WHFnuvi2MpZdFKX4Du5p2bnEGNURWKM0/h6q', TRUE, FALSE),
            ('maria', 'maria@example.com', '$2b$12$GBsUB7g9IY1IEPxF93ZaAOksRDdoi64il9O1N6xZ95R1O.6GJz8OO', TRUE, FALSE),
            ('pedro', 'pedro@example.com', '$2b$12$eBbFJFpZYcAktRZ6psFB2.YtCz5J0PC0N/9Y8zKcy/Ufm.rg9r9FC', TRUE, FALSE);
    END IF;
END $$;

-- Productos
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM products WHERE name = 'Laptop') THEN
        INSERT INTO products (name, description, price, stock, image_url) VALUES
        ('Laptop', 'Laptop potente para trabajo y juegos', 1200.00, 10, 'https://www.professionalwireless.com.co/wp-content/uploads/2024/09/ENVY-16-H1053DX_40GB-300x300.png'),
        ('Mouse', 'Mouse inalámbrico ergonómico', 25.50, 50, 'https://corporativo.tecnoplaza.com.co/wp-content/uploads/2019/01/MOUSE-LOGITECH-M185-NEGRO-300x300.jpg'),
        ('Teclado', 'Teclado mecánico retroiluminado', 75.00, 30, 'https://tecnomarketink.co/wp-content/uploads/2025/02/combo-inalambrico-mouse-con-teclado-pop-icon-rosado-y-blanco-logitech-tecnomarketink-300x300.png'),
        ('NVIDIA BATTLEBOX ULTIMATE', 'PC Oficial de NVIDIA con GeForce RTX™ 4080 SUPER', 897.00, 4, 'https://gtech.systems/wp-content/uploads/2019/05/Ult-430x430.png'),
        ('Parlante Logitech WonderBoom 4 Rosa', 'El WonderBoom 4 de Logitech es el compañero de audio perfecto para tus aventuras.', 319.90, 46, 'https://www.artefacta.com/media/catalog/product/2/6/2604791_02_fm888mkohxcbs9tp_1.jpg?optimize=medium&bg-color=255,255,255&fit=bounds&height=400&width=400&canvas=400:400'),
        ('Auriculares Gamer Profesionales Con Micrófono', 'Mejora cancelacion de ruido, equipados con los nuevos controladores Razer™ TriForce de 50 mm y sonido envolvente 7.1, que brindan una experiencia de audio de juego inmersiva.', 230.90, 10, 'https://png.pngtree.com/png-vector/20250321/ourmid/pngtree-wireless-headphone-png-image_15830312.png'),
        ('Silla Gamer CIR-1039F Lilac con reposapiés y ruedas en silicona', 'La silla gamer CIR-1039F Lilac ofrece una experiencia de juego superior con su diseño elegante y ergonómico.', 579.90, 86, 'https://static.vecteezy.com/system/resources/thumbnails/034/867/032/small/blue-gaming-chair-png.png'),
        ('USB KINGSTON 128 GB Metal 3.2', 'DataTraveler Kyson de KINGSTON es una unidad de memoria USB Flash Tipo A con velocidades de transferencia extremadamente rápidas lo cual permite transferencias de archivos rápidas.', 699.19, 13, 'https://cdn.cs.1worldsync.com/syndication/feeds/sandisk/inline-content/6F/3F422FE6703537130572BEF4043EA9D6F5A9B444_IXPANDFLASHDRIVEANGLE_hero.png'),
        ('Monitor Gaming 27" 144Hz', 'Monitor gaming de 27 pulgadas con tasa de refresco de 144Hz y resolución QHD', 299.99, 15, 'https://http2.mlstatic.com/D_NQ_NP_2X_810287-CBT81631593648_012025-T.webp'),
        ('SSD NVMe 1TB', 'Unidad de estado sólido NVMe de 1TB con velocidades de lectura de hasta 3500MB/s', 89.99, 25, 'https://es.accessoires-asus.com/images/articles/67600/mini/902717672516.webp'),
        ('Tarjeta Gráfica RTX 4060', 'Tarjeta gráfica NVIDIA GeForce RTX 4060 con 8GB GDDR6 para gaming de última generación', 349.99, 8, 'https://static.gigabyte.com/StaticFile/Image/Global/4e04c9ae6035b1e528c613ebc58ab516/Product/36310/png/300'),
        ('Router WiFi 6 AX3000', 'Router inalámbrico WiFi 6 con velocidades hasta 3000Mbps y cobertura para toda la casa', 129.99, 12, 'https://m.media-amazon.com/images/I/31tt0KwhF4L._SY200_.jpg');
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