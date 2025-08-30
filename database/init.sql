-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurar zona horaria
SET timezone = 'America/Bogota';

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS tienda_db;
