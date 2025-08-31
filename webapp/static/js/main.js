// Funcionalidad JavaScript para la tienda

// Variables globales para el carrito
let itemIdToRemove = null;
let pendingChanges = {};

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes cuando cargue la página
    initializeCartActions();
    initializeQuantityInputs();
    initializeCartPage();
});

// Función para inicializar los eventos del carrito
function initializeCartActions() {
    // Agregar evento a los botones de "Agregar al carrito"
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const quantity = 1; // Por defecto, agregar 1 unidad
            addToCart(productId, quantity);
        });
    });
}

// Función para inicializar la página específica del carrito
function initializeCartPage() {
    // Solo ejecutar si estamos en la página del carrito
    if (!document.getElementById('clear-cart-btn')) return;
    
    // Evento para el botón de vaciar carrito
    document.getElementById('clear-cart-btn').addEventListener('click', function() {
        $('#clearCartModal').modal('show');
    });
    
    // Confirmar vaciar carrito
    document.getElementById('confirm-clear-cart').addEventListener('click', function() {
        clearCart();
    });
    
    // Evento para botones de eliminar item
    document.querySelectorAll('.remove-item-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            itemIdToRemove = this.getAttribute('data-item-id');
            $('#removeItemModal').modal('show');
        });
    });
    
    // Confirmar eliminar item
    document.getElementById('confirm-remove-item').addEventListener('click', function() {
        if (itemIdToRemove) {
            removeCartItem(itemIdToRemove);
        }
    });
    
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

// Función para inicializar los inputs de cantidad
function initializeQuantityInputs() {
    // Agregar evento a los inputs de cantidad en el carrito
    const quantityInputs = document.querySelectorAll('.cart-quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            const quantity = parseInt(this.value);
            if (quantity > 0) {
                updateCartQuantity(itemId, quantity);
            } else {
                alert('La cantidad debe ser al menos 1');
                this.value = 1;
            }
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

// Función para agregar productos al carrito
function addToCart(productId, quantity) {
    // Crear un formulario dinámico para enviar la solicitud
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    fetch(`/add-to-cart/${productId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            return response.json();
        }
    })
    .then(data => {
        if (data && data.success) {
            showFlashMessage('Producto agregado al carrito', 'success');
            // Actualizar el contador del carrito en la navbar
            updateCartCounter();
        } else if (data && !data.success) {
            showFlashMessage('Error: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('Error al agregar producto al carrito', 'danger');
    });
}

// Función para actualizar cantidad en el carrito (desde la página de productos)
function updateCartQuantity(itemId, quantity) {
    fetch(`/update-cart-item/${itemId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showFlashMessage('Cantidad actualizada', 'success');
            // Recargar la página para ver los cambios
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showFlashMessage('Error: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('Error al actualizar cantidad', 'danger');
    });
}


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
            const priceElement = document.querySelector(`#item-${itemId} .item-price`);
            const totalElement = document.querySelector(`#item-${itemId} .item-total`);
            
            if (priceElement && totalElement) {
                const price = parseFloat(priceElement.textContent.replace('$', ''));
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
            
            // Mostrar mensaje de éxito
            showFlashMessage('Producto eliminado del carrito', 'success');
            
            // Si no hay items, mostrar el estado de carrito vacío
            if (document.querySelectorAll('tbody tr').length === 0) {
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
            document.querySelectorAll('tbody tr').forEach(row => {
                row.remove();
            });
            
            // Actualizar el total a 0
            document.getElementById('cart-total').innerHTML = '<strong>$0.00</strong>';
            
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
    let newTotal = 0;
    document.querySelectorAll('.item-total').forEach(el => {
        newTotal += parseFloat(el.textContent.replace('$', ''));
    });
    
    document.getElementById('cart-total').innerHTML = '<strong>$' + newTotal.toFixed(2) + '</strong>';
}

// Función para mostrar estado de carrito vacío
function showEmptyCartState() {
    const emptyCartHTML = `
        <tr>
            <td colspan="5" class="text-center">
                <div class="alert alert-info">
                    <h4><i class="fas fa-shopping-cart me-2"></i> Tu carrito está vacío</h4>
                    <p>Agrega algunos productos para continuar con tu compra.</p>
                </div>
                <a href="/products" class="btn btn-primary">
                    <i class="fas fa-store me-2"></i> Explorar Productos
                </a>
            </td>
        </tr>
    `;
    
    document.querySelector('tbody').innerHTML = emptyCartHTML;
}

// Función para actualizar el contador del carrito en la navbar
function updateCartCounter() {
    const cartCounter = document.querySelector('.cart-counter');
    if (cartCounter) {
        const currentCount = parseInt(cartCounter.textContent) || 0;
        cartCounter.textContent = currentCount + 1;
    }
}

// Función para mostrar mensajes flash
function showFlashMessage(message, type) {
    // Crear elemento de alerta
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insertar al principio del contenido
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Advertencia al salir de la página si hay cambios pendientes
window.addEventListener('beforeunload', function (e) {
    if (Object.keys(pendingChanges).length > 0) {
        e.preventDefault();
        e.returnValue = 'Tienes cambios pendientes en tu carrito. ¿Estás seguro de que quieres salir?';
    }
});