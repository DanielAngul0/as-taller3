from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product

# Crear un router para productos
router = APIRouter()

# Obtener lista de productos
@router.get("/")
async def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": str(p.price),
            "stock": p.stock,
            "image_url": p.image_url,
            "created_at": p.created_at
        }
        for p in products
    ]

# Obtener un producto por ID
@router.get("/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "image_url": product.image_url,
        "created_at": product.created_at
    }

# Crear un producto
@router.post("/")
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
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "image_url": product.image_url,
        "created_at": product.created_at
    }

# Actualizar un producto
@router.put("/{product_id}")
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
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": str(product.price),
        "stock": product.stock,
        "image_url": product.image_url,
        "created_at": product.created_at
    }

# Eliminar un producto
@router.delete("/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(product)
    db.commit()
    return {"message": f"Producto con id {product_id} eliminado correctamente"}