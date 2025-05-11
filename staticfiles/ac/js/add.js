document.addEventListener('DOMContentLoaded', function() {
    const addProductBtn = document.getElementById('add-product-btn');
    const productModal = document.getElementById('product-modal');
    const productForm = document.getElementById('product-form');
    const productList = document.getElementById('product-list');
    const closeButtons = document.querySelectorAll('.close-btn');

    // Open modal
    addProductBtn.addEventListener('click', function() {
        productForm.reset();
        productModal.style.display = 'block';
    });

    // Close modal
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.closest('.modal').id === 'product-modal') {
                productModal.style.display = 'none';
            }
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === productModal) {
            productModal.style.display = 'none';
        }
    });

    // Form submission
    productForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const productData = {
            name: document.getElementById('product-name').value,
            price: document.getElementById('product-price').value,
            description: document.getElementById('product-description').value,
            category: document.getElementById('product-category').value,
            unit: document.getElementById('product-unit').value,
            image: document.getElementById('product-image').files[0]
        };
        
        // Validate inputs
        if (!validateProductInputs(productData)) return;

        // Create product card
        createProductCard(productData);

        // Update products count
        updateProductsCount();

        // Close modal
        productModal.style.display = 'none';
        
        // Show success message
        alert('Product added successfully!');
    });

    // Validate product inputs
    function validateProductInputs(product) {
        if (!product.name || !product.price || !product.description || !product.category || !product.unit) {
            alert('Please fill in all required fields');
            return false;
        }
        return true;
    }

    // Create product card
    function createProductCard(product) {
        // Remove empty state if it exists
        const emptyState = productList.querySelector('.empty-state');
        if (emptyState) productList.removeChild(emptyState);

        // Create card element
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        productCard.innerHTML = `
            <div class="product-image-container">
                <img src="${product.image ? URL.createObjectURL(product.image) : 'https://via.placeholder.com/150'}" 
                     alt="${product.name}" class="product-image">
            </div>
            <div class="product-details">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price">$${product.price} per ${product.unit}</p>
                <p class="product-category">${formatCategory(product.category)}</p>
                <p class="product-description">${product.description}</p>
                <div class="product-actions">
                    <button class="btn edit-product-btn"><i class="fas fa-edit"></i> Edit</button>
                    <button class="btn btn-secondary delete-product-btn"><i class="fas fa-trash"></i> Delete</button>
                </div>
            </div>
        `;

        // Add to product list
        productList.appendChild(productCard);

        // Add event listeners
        addProductCardEventListeners(productCard);
    }

    // Add event listeners to product card buttons
    function addProductCardEventListeners(card) {
        card.querySelector('.edit-product-btn').addEventListener('click', function() {
            alert('Edit functionality would go here');
        });

        card.querySelector('.delete-product-btn').addEventListener('click', function() {
            if (confirm('Are you sure you want to delete this product?')) {
                productList.removeChild(card);
                updateProductsCount();
                if (productList.children.length === 0) showEmptyState();
            }
        });
    }

    // Format category for display
    function formatCategory(category) {
        const categories = {
            'grains': 'Grains & Cereals',
            'vegetables': 'Vegetables',
            'fruits': 'Fruits',
            'dairy': 'Dairy Products',
            'meat': 'Meat & Poultry',
            'processed': 'Processed Foods',
            'other': 'Other Farm Products'
        };
        return categories[category] || category;
    }

    // Update products count in stats
    function updateProductsCount() {
        const count = document.querySelectorAll('.product-card').length;
        document.getElementById('products-count').textContent = count;
    }

    // Show empty state
    function showEmptyState() {
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        emptyState.innerHTML = `
            <i class="fas fa-seedling"></i>
            <h3>No Products Listed Yet</h3>
            <p>You haven't listed any farm products yet. Click "Add Product" to get started!</p>
        `;
        productList.appendChild(emptyState);
    }
});