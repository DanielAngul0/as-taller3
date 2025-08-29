from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.product import Product

router = APIRouter()

# Obtener todos los usuarios
@router.get("/admin/users", tags=["admin"])
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin,
        'is_active': user.is_active,
        'created_at': user.created_at.isoformat() if user.created_at else None
    } for user in users]

# Crear producto
@router.post("/admin/products", tags=["admin"])
async def create_product(
    name: str,
    description: str = None,
    price: float = 0.0,
    stock: int = 0,
    image_url: str = None,
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
    return product

# Actualizar producto
@router.put("/admin/products/{product_id}", tags=["admin"])
async def update_product(
    product_id: int,
    name: str = None,
    description: str = None,
    price: float = None,
    stock: int = None,
    image_url: str = None,
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
    return product

# Eliminar producto
@router.delete("/admin/products/{product_id}", tags=["admin"])
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(product)
    db.commit()
    return {"message": "Producto eliminado exitosamente"}