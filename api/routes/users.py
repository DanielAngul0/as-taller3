from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

# Crear el router
router = APIRouter()

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_muy_segura")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Verifica si una contraseña coincide con su hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera el hash de una contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Registro de usuario
@router.post("/register")
async def register_user(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...), 
    db: Session = Depends(get_db)
):
    # Verificar si el usuario o email ya existen
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(status_code=400, detail="Usuario o email ya registrado")
    
    # Hashear la contraseña antes de guardarla
    hashed_password = hash_password(password)

    # Crear usuario
    user = User(username=username, email=email, password_hash=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Usuario registrado exitosamente", "user_id": user.id}



# Login de usuario
@router.post("/login")
async def login_user(
    username: str = Body(...),
    password: str = Body(...),
    db: Session = Depends(get_db)
):
    
    # Buscar usuario por username
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "is_admin": user.is_admin
    }



# Obtener perfil (RESTful con path param)
@router.get("/profile/{user_id}")
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin 
    }



# Actualizar perfil
@router.put("/profile/{user_id}")
async def update_user_profile(
    user_id: int,
    username: str = Body(None),
    email: str = Body(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if username:
        user.username = username
    if email:
        user.email = email

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active
    }

# Listar todos los usuarios
@router.get("/")
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
        for user in users
    ]
    
# Obtener información de usuario por ID
@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }

# Actualizar información de usuario
@router.put("/{user_id}")
async def update_user(
    user_id: int,
    username: str = Body(None),
    email: str = Body(None),
    current_password: str = Body(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar contraseña actual si se proporciona
    if current_password:
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Actualizar campos si se proporcionan
    if username is not None:
        # Verificar si el nuevo nombre de usuario ya existe (excluyendo al usuario actual)
        existing_user = db.query(User).filter(User.username == username, User.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
        user.username = username
    
    if email is not None:
        # Verificar si el nuevo email ya existe (excluyendo al usuario actual)
        existing_email = db.query(User).filter(User.email == email, User.id != user_id).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
        user.email = email
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin
    }

# Cambiar contraseña
@router.post("/{user_id}/change-password")
async def change_password(
    user_id: int,
    current_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar contraseña actual
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    # Hashear nueva contraseña
    hashed_password = get_password_hash(new_password)
    user.password_hash = hashed_password
    db.commit()
    
    return {"message": "Contraseña cambiada exitosamente"}