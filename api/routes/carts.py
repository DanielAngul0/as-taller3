from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.cart import Cart, CartItem
from models.product import Product 

# Crear el router para carritos
router = APIRouter()

# Añadir modelo Pydantic para la actualización
class CartItemUpdate(BaseModel):
    quantity: int

@router.get("/")
async def get_user_cart(user_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Obtener el carrito de un usuario por su user_id
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    items = [
        {
            "id": item.id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "added_at": item.added_at
        }
        for item in cart.items
    ]
    return {"cart_id": cart.id, "user_id": cart.user_id, "items": items}


@router.post("/items", status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    user_id: int = Body(...),
    product_id: int = Body(...),
    quantity: int = Body(1),
    db: Session = Depends(get_db)
):
    """
    Agregar un producto al carrito de un usuario.
    Si no existe el carrito, lo crea.
    """

    # Validar que el producto exista
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.flush()  # permite obtener el id del carrito sin commit inmediato

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if item:
        item.quantity += quantity
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "cart_id": item.cart_id,
        "product_id": item.product_id,
        "quantity": item.quantity
    }

# Actualizar la cantidad de un producto en el carrito
@router.put("/items/{item_id}")
async def update_cart_item(
    item_id: int,
    cart_item_update: CartItemUpdate,  # Cambiar a usar el modelo Pydantic
    db: Session = Depends(get_db)
):
    """
    Actualizar la cantidad de un producto en el carrito
    """
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    if cart_item_update.quantity <= 0:
        raise HTTPException(status_code=400, detail="Cantidad inválida")

    item.quantity = cart_item_update.quantity
    db.commit()
    db.refresh(item)

    return {
        "id": item.id,
        "cart_id": item.cart_id,
        "product_id": item.product_id,
        "quantity": item.quantity
    }


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_cart(item_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un item específico del carrito
    """
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    db.delete(item)
    db.commit()
    return {"detail": "Item eliminado del carrito"}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(user_id: int = Query(...), db: Session = Depends(get_db)):
    """
    Vaciar el carrito de un usuario
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()

    return {"detail": "Carrito limpiado"}
