// Funcionalidad JavaScript para la tienda

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes cuando cargue la página
    initializeCartActions();
    initializeQuantityInputs();
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

    // Agregar evento a los botones de "Eliminar" en el carrito
    const removeFromCartButtons = document.querySelectorAll('.remove-from-cart-btn');
    removeFromCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            removeFromCart(itemId);
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
            // Recargar la página para actualizar el carrito
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else if (data && !data.success) {
            showFlashMessage('Error: ' + data.message, 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showFlashMessage('Error al agregar producto al carrito', 'danger');
    });
}

// Función para actualizar cantidad en el carrito
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

// Función para remover items del carrito
function removeFromCart(itemId) {
    if (confirm('¿Estás seguro de que quieres eliminar este producto del carrito?')) {
        fetch(`/remove-from-cart/${itemId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage('Producto eliminado del carrito', 'success');
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
            showFlashMessage('Error al eliminar producto', 'danger');
        });
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