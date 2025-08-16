from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# TODO: Configurar la URL de la base de datos desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://tienda_user:tienda_password@database:5432/tienda_db")

# TODO: Crear el engine de SQLAlchemy

# TODO: Crear SessionLocal para las sesiones de la base de datos

# TODO: Crear Base para los modelos

# TODO: Función para obtener la sesión de la base de datos
def get_db():
    # TODO: Implementar la función para obtener sesión de DB
    pass