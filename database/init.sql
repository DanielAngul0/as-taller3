-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurar zona horaria
SET timezone = 'America/Bogota';

-- Crear la base de datos si no existe
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM pg_database WHERE datname = 'tienda_db'
    ) THEN
        CREATE DATABASE tienda_db;
    END IF;
END
$$;
-- NOTA: La conexión a la base de datos tienda_db se realiza en schema.sql
