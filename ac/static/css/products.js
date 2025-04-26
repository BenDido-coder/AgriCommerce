// Sample product data
const products = [
    {
        id: 1,
        name: "Organic Tomatoes",
        image: "{% static 'images/tomatoes.jpg' %}",
        price: 3.99,
        units: "per lb",
        category: "vegetables",
        description: "Fresh organic tomatoes grown without pesticides. Perfect for salads, sauces, and sandwiches.",
        rating: 4.5,
        reviews: 24,
        stock: 50,
        location: "north",
        harvestDate: "2023-06-15",
        farmer: {
            id: 101,
            name: "Green Valley Farms",
            avatar: "{% static 'images/farmer1.jpg' %}",
            bio: "Family-owned farm specializing in organic vegetables since 1995. Committed to sustainable farming practices.",
            location: "Northern Region",
            joined: "2018-03-10",
            products: 12,
            rating: 4.7,
            followers: 245
        }
    },
    {
        id: 2,
        name: "Honeycrisp Apples",
        image: "{% static 'images/apples.jpg' %}",
        price: 2.49,
        units: "per lb",
        category: "fruits",
        description: "Crisp and juicy Honeycrisp apples, perfect for eating fresh or baking.",
        rating: 4.8,
        reviews: 36,
        stock: 75,
        location: "north",
        harvestDate: "2023-06-10",
        farmer: {
            id: 102,
            name: "Orchard Fresh",
            avatar: "{% static 'images/farmer2.jpg' %}",
            bio: "Third-generation apple orchard with over 50 varieties of apples. We practice integrated pest management.",
            location: "Northern Region",
            joined: "2016-05-22",
            products: 8,
            rating: 4.9,
            followers: 312
        }
    },
    // Add more products as needed
];

// DOM elements
const productGrid = document.getElementById('productGrid');
const searchForm = document.getElementById('searchForm');
const searchInput = document.getElementById('searchInput');
const categoryFilter = document.getElementById('categoryFilter');
const priceFilter = document.getElementById('priceFilter');
const locationFilter = document.getElementById('locationFilter');
const sortFilter = document.getElementById('sortFilter');
const productModal = document.getElementById('productModal');
const closeProductModal = document.getElementById('closeProductModal');
const productDetailContainer = document.getElementById('productDetailContainer');
const farmerModal = document.getElementById('farmerModal');
const closeFarmerModal = document.getElementById('closeFarmerModal');
const farmerDashboard = document.getElementById('farmerDashboard');
const cartCount = document.getElementById('cartCount');

// Cart functionality
let cart = JSON.parse(localStorage.getItem('cart')) || [];
updateCartCount();

// Initialize with sample data
displayProducts(products);

// Search functionality
searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const searchTerm = searchInput.value.toLowerCase();
    const filteredProducts = products.filter(product => 
        product.name.toLowerCase().includes(searchTerm) || 
        product.farmer.name.toLowerCase().includes(searchTerm) ||
        product.category.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm)
    );
    displayProducts(filteredProducts);
});

// Filter functionality
[categoryFilter, priceFilter, locationFilter, sortFilter].forEach(filter => {
    filter.addEventListener('change', applyFilters);
});

function applyFilters() {
    const category = categoryFilter.value;
    const price = priceFilter.value;
    const location = locationFilter.value;
    const sort = sortFilter.value;

    let filteredProducts = [...products];

    // Apply category filter
    if (category) {
        filteredProducts = filteredProducts.filter(product => product.category === category);
    }

    // Apply price filter
    if (price === 'low') {
        filteredProducts = filteredProducts.filter(product => product.price < 5);
    } else if (price === 'medium') {
        filteredProducts = filteredProducts.filter(product => product.price >= 5 && product.price <= 15);
    } else if (price === 'high') {
        filteredProducts = filteredProducts.filter(product => product.price > 15);
    }

    // Apply location filter
    if (location) {
        filteredProducts = filteredProducts.filter(product => product.location === location);
    }

    // Apply sorting
    if (sort === 'newest') {
        filteredProducts.sort((a, b) => new Date(b.harvestDate) - new Date(a.harvestDate));
    } else if (sort === 'price-low') {
        filteredProducts.sort((a, b) => a.price - b.price);
    } else if (sort === 'price-high') {
        filteredProducts.sort((a, b) => b.price - a.price);
    } else if (sort === 'rating') {
        filteredProducts.sort((a, b) => b.rating - a.rating);
    } else {
        // Default: popular
        filteredProducts.sort((a, b) => b.reviews - a.reviews);
    }

    displayProducts(filteredProducts);
}

function displayProducts(productsToDisplay) {
    productGrid.innerHTML = '';
    
    if (productsToDisplay.length === 0) {
        productGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No products found matching your criteria.</p>';
        return;
    }

    productsToDisplay.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        
        // Add badge if product is new (harvested within last 7 days)
        const harvestDate = new Date(product.harvestDate);
        const today = new Date();
        const daysOld = Math.floor((today - harvestDate) / (1000 * 60 * 60 * 24));
        const isNew = daysOld <= 7;
        
        productCard.innerHTML = `
            ${isNew ? '<div class="product-badge">New</div>' : ''}
            <img src="${product.image}" alt="${product.name}" class="product-image">
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <div class="product-farmer">
                    <img src="${product.farmer.avatar}" alt="${product.farmer.name}" class="farmer-avatar">
                    <a href="#" class="farmer-name" data-farmer-id="${product.farmer.id}">${product.farmer.name}</a>
                </div>
                <div class="product-rating">
                    ${generateStarRating(product.rating)}
                    <span>(${product.reviews})</span>
                </div>
                <div class="product-price">$${product.price.toFixed(2)} <small>${product.units}</small></div>
                <div class="product-actions">
                    <button class="view-btn" data-product-id="${product.id}">View Details</button>
                    <button class="add-to-cart" data-product-id="${product.id}">Add to Cart</button>
                </div>
            </div>
        `;
        productGrid.appendChild(productCard);
    });

    // Add event listeners to product cards for detail view
    document.querySelectorAll('.product-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on buttons or links
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A') {
                return;
            }
            const productId = parseInt(this.querySelector('.view-btn').getAttribute('data-product-id'));
            showProductModal(productId);
        });
    });

    // Add event listeners to view buttons
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const productId = parseInt(this.getAttribute('data-product-id'));
            showProductModal(productId);
        });
    });

    // Add event listeners to add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const productId = parseInt(this.getAttribute('data-product-id'));
            addToCart(productId);
        });
    });

    // Add event listeners to farmer name links
    document.querySelectorAll('.farmer-name').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const farmerId = parseInt(this.getAttribute('data-farmer-id'));
            showFarmerModal(farmerId);
        });
    });
}

function generateStarRating(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    
    return stars;
}

function showProductModal(productId) {
    const product = products.find(p => p.id === productId);
    
    productDetailContainer.innerHTML = `
        <div class="product-detail-image-container">
            <img src="${product.image}" alt="${product.name}" class="product-detail-image">
        </div>
        <div class="product-detail-info">
            <h1 class="product-detail-name">${product.name}</h1>
            <div class="product-detail-price">$${product.price.toFixed(2)} ${product.units}</div>
            
            <div class="product-rating">
                ${generateStarRating(product.rating)}
                <span>${product.rating} (${product.reviews} reviews)</span>
            </div>
            
            <div class="product-detail-meta">
                <div><i class="fas fa-tag"></i> Category: ${product.category.charAt(0).toUpperCase() + product.category.slice(1)}</div>
                <div><i class="fas fa-box-open"></i> Available: ${product.stock} ${product.units}</div>
                <div><i class="fas fa-calendar-alt"></i> Harvested: ${new Date(product.harvestDate).toLocaleDateString()}</div>
                <div><i class="fas fa-map-marker-alt"></i> Location: ${product.farmer.location}</div>
            </div>
            
            <h3>Description</h3>
            <p class="product-detail-description">${product.description}</p>
            
            <div class="product-detail-farmer">
                <h3>Sold By</h3>
                <div class="product-farmer" style="margin-top: 10px;">
                    <img src="${product.farmer.avatar}" alt="${product.farmer.name}" class="farmer-avatar">
                    <a href="#" class="farmer-name" data-farmer-id="${product.farmer.id}">${product.farmer.name}</a>
                </div>
            </div>
            
            <div class="product-detail-actions">
                <div class="quantity-selector">
                    <button class="quantity-btn minus">-</button>
                    <input type="number" class="quantity-input" value="1" min="1" max="${product.stock}">
                    <button class="quantity-btn plus">+</button>
                </div>
                <button class="buy-now-btn">Buy Now</button>
                <button class="add-to-cart-btn" data-product-id="${product.id}">Add to Cart</button>
            </div>
        </div>
    `;
    
    // Add event listener to farmer name in modal
    document.querySelector('.product-detail-info .farmer-name').addEventListener('click', function(e) {
        e.preventDefault();
        productModal.style.display = 'none';
        const farmerId = parseInt(this.getAttribute('data-farmer-id'));
        showFarmerModal(farmerId);
    });
    
    // Add event listener to add to cart button in modal
    document.querySelector('.add-to-cart-btn').addEventListener('click', function() {
        const quantity = parseInt(document.querySelector('.quantity-input').value);
        addToCart(productId, quantity);
    });
    
    // Quantity selector functionality
    document.querySelector('.quantity-btn.minus').addEventListener('click', function() {
        const input = document.querySelector('.quantity-input');
        if (parseInt(input.value) > 1) {
            input.value = parseInt(input.value) - 1;
        }
    });
    
    document.querySelector('.quantity-btn.plus').addEventListener('click', function() {
        const input = document.querySelector('.quantity-input');
        if (parseInt(input.value) < product.stock) {
            input.value = parseInt(input.value) + 1;
        }
    });
    
    productModal.style.display = 'block';
}

function showFarmerModal(farmerId) {
    const farmer = products.find(p => p.farmer.id === farmerId).farmer;
    const farmerProds = products.filter(p => p.farmer.id === farmerId);

    farmerDashboard.innerHTML = `
        <div class="farmer-sidebar">
            <img src="${farmer.avatar}" alt="${farmer.name}" class="farmer-avatar-large">
            <h2 class="farmer-name-large">${farmer.name}</h2>
            <div class="farmer-location">
                <i class="fas fa-map-marker-alt"></i> ${farmer.location}
            </div>
            
            <div class="farmer-stats">
                <div class="stat-item">
                    <div class="stat-value">${farmer.products}</div>
                    <div class="stat-label">Products</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${farmer.rating}</div>
                    <div class="stat-label">Rating</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${farmer.followers}</div>
                    <div class="stat-label">Followers</div>
                </div>
            </div>
            
            <ul class="farmer-menu">
                <li><a href="#" class="active"><i class="fas fa-store"></i> Products</a></li>
                <li><a href="#"><i class="fas fa-info-circle"></i> About</a></li>
                <li><a href="#"><i class="fas fa-star"></i> Reviews</a></li>
                <li><a href="#"><i class="fas fa-envelope"></i> Contact</a></li>
            </ul>
        </div>
        
        <div class="farmer-content">
            <h2>About ${farmer.name}</h2>
            <p>${farmer.bio}</p>
            
            <h3 style="margin-top: 20px;">Products from ${farmer.name}</h3>
            <div class="farmer-products-grid">
                ${farmerProds.map(product => `
                    <div class="product-card" style="cursor: pointer;">
                        <img src="${product.image}" alt="${product.name}" class="product-image">
                        <div class="product-info">
                            <h3 class="product-name">${product.name}</h3>
                            <div class="product-price">$${product.price.toFixed(2)} ${product.units}</div>
                            <button class="view-btn" data-product-id="${product.id}" style="width: 100%; margin-top: 10px;">View Product</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    // Add event listeners to product cards in farmer modal
    document.querySelectorAll('.farmer-content .product-card').forEach(card => {
        card.addEventListener('click', function() {
            const productId = parseInt(this.querySelector('.view-btn').getAttribute('data-product-id'));
            farmerModal.style.display = 'none';
            showProductModal(productId);
        });
    });
    
    farmerModal.style.display = 'block';
}

function addToCart(productId, quantity = 1) {
    const product = products.find(p => p.id === productId);
    
    // Check if product already in cart
    const existingItem = cart.find(item => item.id === productId);
    
    if (existingItem) {
        existingItem.quantity += quantity;
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            image: product.image,
            units: product.units,
            farmer: product.farmer.name,
            quantity: quantity
        });
    }
    
    // Save to localStorage
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
    
    // Show notification
    alert(`${quantity} ${product.name} added to cart!`);
}

function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    cartCount.textContent = count;
}

// Close modals
closeProductModal.addEventListener('click', function() {
    productModal.style.display = 'none';
});

closeFarmerModal.addEventListener('click', function() {
    farmerModal.style.display = 'none';
});

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    if (e.target === productModal) {
        productModal.style.display = 'none';
    }
    if (e.target === farmerModal) {
        farmerModal.style.display = 'none';
    }
});