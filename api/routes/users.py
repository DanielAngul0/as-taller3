from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

# Crear el router
router = APIRouter()

# Registro de usuario
@router.post("/register")
async def register_user(
    username: str = Body(...),
    email: str = Body(...),
    password_hash: str = Body(...),
    db: Session = Depends(get_db)
):
    # Verificar si el usuario o email ya existen
    if db.query(User).filter((User.username == username) | (User.email == email)).first():
        raise HTTPException(status_code=400, detail="Usuario o email ya registrado")

    # Crear usuario
    user = User(username=username, email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "username": user.username, "email": user.email}



# Login de usuario
@router.post("/login")
async def login_user(
    username: str = Body(...),
    password_hash: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == username, 
        User.password_hash == password_hash
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"id": user.id, "username": user.username, "email": user.email}



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
        "is_active": user.is_active
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
            "is_active": user.is_active
        }
        for user in users
    ]