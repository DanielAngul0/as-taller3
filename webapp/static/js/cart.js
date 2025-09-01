// static/js/cart.js
document.addEventListener('DOMContentLoaded', function() {
    initializeCartFunctionality();
});

function initializeCartFunctionality() {
    // Variables globales para el carrito
    let itemIdToRemove = null;
    let pendingChanges = {};

    // Inicializar eventos del carrito
    initializeCartEvents();
    
    // Función para inicializar todos los eventos del carrito
    function initializeCartEvents() {
        // Evento para el botón de vaciar carrito
        const clearCartBtn = document.getElementById('clear-cart-btn');
        if (clearCartBtn) {
            clearCartBtn.addEventListener('click', function() {
                $('#clearCartModal').modal('show');
            });
        }
        
        // Confirmar vaciar carrito
        const confirmClearCart = document.getElementById('confirm-clear-cart');
        if (confirmClearCart) {
            confirmClearCart.addEventListener('click', function() {
                clearCart();
            });
        }
        
        // Evento para botones de eliminar item
        document.querySelectorAll('.remove-item-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                itemIdToRemove = this.getAttribute('data-item-id');
                $('#removeItemModal').modal('show');
            });
        });
        
        // Confirmar eliminar item
        const confirmRemoveItem = document.getElementById('confirm-remove-item');
        if (confirmRemoveItem) {
            confirmRemoveItem.addEventListener('click', function() {
                if (itemIdToRemove) {
                    removeCartItem(itemIdToRemove);
                }
            });
        }
        
        // Eventos para aumentar/disminuir cantidad
        document.querySelectorAll('.increase-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
                const newValue = parseInt(input.value) + 1;
                input.value = newValue;
                showQuantityActions(itemId, newValue);
            });
        });
        
        document.querySelectorAll('.decrease-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
                if (parseInt(input.value) > 1) {
                    const newValue = parseInt(input.value) - 1;
                    input.value = newValue;
                    showQuantityActions(itemId, newValue);
                }
            });
        });
        
        // Evento para cambio directo en input
        document.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', function() {
                const itemId = this.getAttribute('data-item-id');
                if (parseInt(this.value) < 1) this.value = 1;
                showQuantityActions(itemId, parseInt(this.value));
            });
        });
        
        // Eventos para botones de confirmar/cancelar cambios de cantidad
        document.querySelectorAll('.confirm-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
                confirmQuantityChange(itemId, parseInt(input.value));
            });
        });
        
        document.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const itemId = this.getAttribute('data-item-id');
                cancelQuantityChange(itemId);
            });
        });
    }

    // Función para mostrar botones de confirmación de cantidad
    function showQuantityActions(itemId, newQuantity) {
        const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
        if (!input) return;
        
        const originalValue = input.getAttribute('data-original-value');
        const actionsDiv = document.querySelector(`.quantity-actions[data-item-id="${itemId}"]`);
        
        if (!actionsDiv) {
            console.error('No se encontraron botones de acción para el item:', itemId);
            return;
        }
        
        if (parseInt(originalValue) !== newQuantity) {
            // Mostrar botones de confirmación
            actionsDiv.style.display = 'flex';
            // Guardar cambio pendiente
            pendingChanges[itemId] = newQuantity;
        } else {
            // Ocultar botones de confirmación si el valor es el original
            actionsDiv.style.display = 'none';
            delete pendingChanges[itemId];
        }
    }

    // Función para confirmar cambio de cantidad
    function confirmQuantityChange(itemId, quantity) {
        updateCartItemQuantity(itemId, quantity)
            .then(() => {
                // Actualizar el valor original
                const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
                if (input) {
                    input.setAttribute('data-original-value', quantity);
                }
                
                // Ocultar botones de confirmación
                const actionsDiv = document.querySelector(`.quantity-actions[data-item-id="${itemId}"]`);
                if (actionsDiv) {
                    actionsDiv.style.display = 'none';
                }
                
                // Eliminar de cambios pendientes
                delete pendingChanges[itemId];
            })
            .catch(error => {
                console.error('Error al confirmar cambio:', error);
                showFlashMessage('Error al actualizar la cantidad', 'danger');
            });
    }

    // Función para cancelar cambio de cantidad
    function cancelQuantityChange(itemId) {
        const input = document.querySelector(`.quantity-input[data-item-id="${itemId}"]`);
        const actionsDiv = document.querySelector(`.quantity-actions[data-item-id="${itemId}"]`);
        
        if (!input || !actionsDiv) return;
        
        const originalValue = input.getAttribute('data-original-value');
        // Restaurar valor original
        input.value = originalValue;
        // Ocultar botones de confirmación
        actionsDiv.style.display = 'none';
        // Eliminar de cambios pendientes
        delete pendingChanges[itemId];
    }

    // Función para actualizar cantidad en el carrito
    function updateCartItemQuantity(itemId, quantity) {
        return fetch(`/update-cart-item/${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ quantity: parseInt(quantity) })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Actualizar el total del item
                const priceElement = document.querySelector(`#item-${itemId} .cart-item-price`);
                const totalElement = document.querySelector(`#item-${itemId} .item-total`);
                
                if (priceElement && totalElement) {
                    const price = parseFloat(priceElement.textContent.replace('$', '').replace(' c/u', ''));
                    const newItemTotal = price * parseInt(quantity);
                    totalElement.textContent = '$' + newItemTotal.toFixed(2);
                    
                    // Actualizar el total general del carrito
                    recalculateTotal();
                    
                    // Mostrar mensaje de éxito
                    showFlashMessage('Cantidad actualizada correctamente', 'success');
                    return data;
                }
            } else {
                showFlashMessage('Error: ' + data.message, 'danger');
                throw new Error(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('Error al actualizar la cantidad', 'danger');
            throw error;
        });
    }

    // Función para eliminar item del carrito
    function removeCartItem(itemId) {
        fetch(`/remove-from-cart/${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Eliminar la fila de la tabla sin recargar la página
                const itemRow = document.getElementById('item-' + itemId);
                if (itemRow) {
                    itemRow.remove();
                }
                
                // Recalcular el total
                recalculateTotal();
                
                // Cerrar el modal
                $('#removeItemModal').modal('hide');
                
                // Actualizar contador de items
                updateCartItemsCount();
                
                // Mostrar mensaje de éxito
                showFlashMessage('Producto eliminado del carrito', 'success');
                
                // Si no hay items, mostrar el estado de carrito vacío
                if (document.querySelectorAll('.cart-item').length === 0) {
                    showEmptyCartState();
                }
            } else {
                showFlashMessage('Error: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('Error al eliminar producto', 'danger');
        });
    }

    // Función para vaciar el carrito
    function clearCart() {
        fetch('/clear-cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Eliminar todas las filas de la tabla
                document.querySelectorAll('.cart-item').forEach(row => {
                    row.remove();
                });
                
                // Recalcular el total (será 0)
                recalculateTotal();
                
                // Cerrar el modal
                $('#clearCartModal').modal('hide');
                
                // Actualizar contador de items
                updateCartItemsCount();
                
                // Mostrar el estado de carrito vacío
                showEmptyCartState();
                
                // Mostrar mensaje de éxito
                showFlashMessage('Carrito vaciado correctamente', 'success');
            } else {
                showFlashMessage('Error: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showFlashMessage('Error al vaciar el carrito', 'danger');
        });
    }

    // Función para recalcular el total del carrito
    function recalculateTotal() {
        let total = 0;
        document.querySelectorAll('.item-total').forEach(element => {
            total += parseFloat(element.textContent.replace('$', ''));
        });
        
        // Actualizar el elemento que muestra el total general
        const totalElement = document.getElementById('cart-total');
        if (totalElement) {
            totalElement.textContent = '$' + total.toFixed(2);
        }
    }

    // Función para actualizar el contador de items
    function updateCartItemsCount() {
        const itemsCount = document.querySelectorAll('.cart-item').length;
        const cartItemsCount = document.getElementById('cart-items-count');
        if (cartItemsCount) {
            cartItemsCount.textContent = itemsCount + ' items';
        }
    }

    // Función para mostrar estado de carrito vacío
    function showEmptyCartState() {
        const cartContainer = document.querySelector('.cart-container');
        if (cartContainer) {
            cartContainer.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-shopping-cart fa-4x text-muted mb-3"></i>
                    <h3 class="text-muted">Tu carrito está vacío</h3>
                    <p class="text-muted">Agrega algunos productos para continuar con tu compra.</p>
                    <a href="/products" class="btn btn-primary mt-3">
                        <i class="fas fa-store me-2"></i> Explorar Productos
                    </a>
                </div>
            `;
        }
    }

    // Función para mostrar mensajes flash
    function showFlashMessage(message, type) {
    // Eliminar mensajes anteriores del mismo tipo para evitar duplicados
    const existingAlerts = document.querySelectorAll('.flash-toast-message');
    existingAlerts.forEach(alert => alert.remove());
    
    // Crear elemento de alerta con estilos de toast
    const alertDiv = document.createElement('div');
    alertDiv.className = `flash-toast-message alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.role = 'alert';
    alertDiv.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border-radius: 8px;
        animation: toastSlideIn 0.3s ease-out;
    `;
    
    // Iconos según el tipo de mensaje
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'danger') icon = 'fa-exclamation-circle';
    if (type === 'warning') icon = 'fa-exclamation-triangle';
    
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${icon} me-2"></i>
            <span class="flex-grow-1">${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Agregar al body
    document.body.appendChild(alertDiv);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            // Animación de salida
            alertDiv.style.animation = 'toastSlideOut 0.3s ease-in';
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 300);
        }
    }, 5000);
    
    // Configurar evento de cierre
    const closeButton = alertDiv.querySelector('.btn-close');
    if (closeButton) {
        closeButton.addEventListener('click', function() {
            alertDiv.style.animation = 'toastSlideOut 0.3s ease-in';
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 300);
        });
    }
}

    // Advertencia al salir de la página si hay cambios pendientes
    window.addEventListener('beforeunload', function (e) {
        if (Object.keys(pendingChanges).length > 0) {
            e.preventDefault();
            e.returnValue = 'Tienes cambios pendientes en tu carrito. ¿Estás seguro de que quieres salir?';
        }
    });
}