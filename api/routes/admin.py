# api/routes/admin.py
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.product import Product

router = APIRouter()

def serialize_user(user: User) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }

def serialize_product(product: Product) -> dict:
    return {
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': float(product.price) if product.price is not None else None,
        'stock': product.stock,
        'image_url': product.image_url,
        'created_at': product.created_at.isoformat() if product.created_at else None
    }

# Obtener todos los usuarios (admins arriba, id asc)
@router.get("/users", tags=["admin"])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.is_admin.desc(), User.id.asc()).all()
    return [serialize_user(user) for user in users]

# Obtener todos los productos (orden estable por id asc)
@router.get("/products", tags=["admin"])
async def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.id.asc()).all()
    return [serialize_product(product) for product in products]

# Crear producto (aceptar JSON en el cuerpo)
@router.post("/products", tags=["admin"], status_code=201)
async def create_product(
    name: str = Body(...),
    description: str = Body(None),
    price: float = Body(...),
    stock: int = Body(...),
    image_url: str = Body(None),
    db: Session = Depends(get_db)
):
    product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    # Devolver el producto creado y la lista completa ordenada para que la UI pueda refrescar
    products = db.query(Product).order_by(Product.id.asc()).all()
    return {
        "product": serialize_product(product),
        "products": [serialize_product(p) for p in products]
    }

# Actualizar producto (aceptar JSON en el cuerpo)
@router.put("/products/{product_id}", tags=["admin"])
async def update_product(
    product_id: int,
    name: str = Body(None),
    description: str = Body(None),
    price: float = Body(None),
    stock: int = Body(None),
    image_url: str = Body(None),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if name is not None:
        product.name = name
    if description is not None:
        product.description = description
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
    if image_url is not None:
        product.image_url = image_url
    
    db.commit()
    db.refresh(product)

    # Devolver producto actualizado + lista ordenada
    products = db.query(Product).order_by(Product.id.asc()).all()
    return {
        "product": serialize_product(product),
        "products": [serialize_product(p) for p in products]
    }

# Eliminar producto
@router.delete("/products/{product_id}", tags=["admin"])
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(product)
    db.commit()

    # Devolver lista ordenada después de la eliminación
    products = db.query(Product).order_by(Product.id.asc()).all()
    return {
        "message": "Producto eliminado exitosamente",
        "products": [serialize_product(p) for p in products]
    }

# Hacer admin a un usuario
@router.put("/users/{user_id}/make-admin", tags=["admin"])
async def make_user_admin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.is_admin = True
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Usuario convertido en administrador exitosamente",
        "user": serialize_user(user)
    }
    
# Quitar privilegios de administrador a un usuario
@router.put("/users/{user_id}/remove-admin", tags=["admin"])
async def remove_user_admin(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.is_admin = False
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Privilegios de administrador removidos exitosamente",
        "user": serialize_user(user)
    }
