# views.py - Refactored and Optimized
from datetime import datetime, timedelta, timezone
from email.headerregistry import Address
from venv import logger
from django.utils import timezone  # Ensure this import is present
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from io import BytesIO
from uuid import uuid4
from django.urls import reverse
import requests
from .forms import CurrencyConvertForm, DeliveryConfirmationForm, JobCompletionForm, LogisticsProfileForm, SupportTicketForm, WalletTopupForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.forms import ValidationError
from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from reportlab.pdfgen import canvas

from ac.forms import (
    CustomUserCreationForm, UserForm, SupplierProfileForm, FarmerProfileForm,
    ProductForm, ProfileUpdateForm, 
    BuyerProfileForm
)
from ac.models import (
    City, DeliveryJob, EscrowTransaction, LogisticsProfile, Order, 
    Product, SupportTicket, User, BuyerProfile, SupplierProfile, FarmerProfile,
    Notification, TransactionUpdate, WishlistItem,
    WalletTransaction, ProductCategory
)
# ------------------------- Utility Functions -------------------------
def create_notification(user, message, notification_type='SYSTEM', related_url=None, delivery_job=None):
    """Create notification with proper relationships"""
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        related_url=related_url,
        delivery_job=delivery_job
    )

def validate_farmer_access(user):
    """Check if user is a farmer with valid profile"""
    if not user.is_authenticated or user.user_type != 'FARMER':
        return False
    return hasattr(user, 'farmer_profile')

# ------------------------- Core Views -------------------------
def home(request):
    stats = {
        'total_farmers': User.objects.filter(user_type='FARMER').count(),
        'total_transactions': EscrowTransaction.objects.count(),
    }
    featured_products = Product.objects.filter(
        is_approved=True, 
        stock_quantity__gt=0
    ).select_related('seller')[:8]
    
    return render(request, 'homepage.html', {
        'stats': stats,
        'featured_products': featured_products
    })

def logout_view(request):
    """Custom logout with confirmation message"""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home')

# ------------------------- Authentication Views -------------------------
from django.contrib.auth import get_backends
@transaction.atomic
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Save the user object first
                user = form.save(commit=False)
                user.save()  # Save the user to the database to generate a primary key

                user_type = form.cleaned_data.get('user_type')

                # Create the appropriate profile
                if user_type == 'FARMER':
                    FarmerProfile.objects.create(user=user)
                elif user_type == 'SUPPLIER':
                    SupplierProfile.objects.create(user=user)
                elif user_type == 'LOGISTICS':
                    LogisticsProfile.objects.create(user=user)
                elif user_type == 'BUYER':
                    BuyerProfile.objects.create(user=user)

                # Log the user in with the backend specified
                backend = get_backends()[0]  # Use the first authentication backend
                auth_login(request, user, backend=backend.__class__.__name__)

                # Redirect based on user type
                if user.is_superuser:
                    return redirect('admin_dashboard')
                redirect_url = {
                    'FARMER': 'farmer_dashboard',
                    'SUPPLIER': 'supplier_dashboard',
                    'LOGISTICS': 'logistics_dashboard',
                    'BUYER': 'buyer_dashboard',
                }.get(user.user_type, 'home')

                return redirect(redirect_url)

            except IntegrityError:
                messages.error(request, "Account creation failed. Please try again.")
        else:
            print("Form errors:", form.errors)  # Debugging line
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})

class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'LOGISTICS':
            return reverse('logistics_dashboard')
        elif self.request.user.is_superuser:
            return reverse('admin_dashboard')
        elif user.user_type == 'FARMER':
            return reverse('farmer_dashboard')
        elif user.user_type == 'SUPPLIER':
            return reverse('supplier_dashboard')
        return super().get_success_url()
# ------------------------- Account Management -------------------------
from ac.models import FarmerProfile, SupplierProfile, Product, EscrowTransaction, Notification
from ac.forms import UserForm, FarmerProfileForm, SupplierProfileForm

@login_required
def my_account(request):
    user = request.user

    # --- pick or create the correct profile instance + form class ---
    profile_instance = None
    ProfileFormClass = None

    if user.user_type == 'FARMER':
        profile_instance, _ = FarmerProfile.objects.get_or_create(user=user)
        ProfileFormClass    = FarmerProfileForm

    elif user.user_type == 'SUPPLIER':
        profile_instance, _ = SupplierProfile.objects.get_or_create(user=user)
        ProfileFormClass    = SupplierProfileForm

    # else: buyers, logistics, admins have no extra profile

    # --- handle POST vs GET ---
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)

        if ProfileFormClass:
            profile_form = ProfileFormClass(
                request.POST, request.FILES,
                instance=profile_instance
            )
        else:
            profile_form = None

        if user_form.is_valid() and (not profile_form or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('my_account')
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        user_form    = UserForm(instance=user)
        profile_form = ProfileFormClass(instance=profile_instance) if ProfileFormClass else None

    # --- other tabs data ---
    products      = Product.objects.filter(seller=user)
    orders        = EscrowTransaction.objects.filter(buyer=user)
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]

    tabs = [
        ('profile',       'user'),
        ('products',      'tractor'),
        ('orders',        'clipboard-list'),
        ('notifications', 'bell'),
    ]

    context = {
        'tabs':            tabs,
        'user_form':       user_form,
        'profile_form':    profile_form,
        'products':        products,
        'orders':          orders,
        'notifications':   notifications,
        'farmer_profile':  profile_instance if user.user_type == 'FARMER' else None,
        'supplier_profile':profile_instance if user.user_type == 'SUPPLIER' else None,
        'user_type':       user.user_type,
        'is_farmer':       user.user_type == 'FARMER',
        'is_supplier':     user.user_type == 'SUPPLIER',
        'is_buyer':        user.user_type == 'BUYER',
        'is_logistics':    user.user_type == 'LOGISTICS',
        'is_admin':        user.is_superuser or user.user_type == 'ADMIN',
    }
    return render(request, 'my_account.html', context)

# ------------------------- Product Views -------------------------
def product_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    products = Product.objects.filter(stock_quantity__gt=0, is_approved=True)
    
    # Apply filters
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(seller__farmer_profile__farm_name__icontains=query)
        )
    if category:
        products = products.filter(category=category)

    # Get all available categories from the products
    available_categories = products.order_by('category').values_list(
        'category', flat=True).distinct()
    
    # Map to human-readable names
    category_choices = dict(Product.CATEGORY_CHOICES)
    categories = [(cat, category_choices[cat]) for cat in available_categories]

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'FARMER_CATEGORIES': Product.FARMER_CATEGORIES,
        'SUPPLIER_CATEGORIES': Product.SUPPLIER_CATEGORIES,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'products/includes/product_grid.html', context)
    
    return render(request, 'products/list.html', context)

@login_required
def product_detail(request, product_id):
    """Product detail view with seller info"""
    product = get_object_or_404(
        Product.objects.select_related('seller'),
        pk=product_id,
        stock_quantity__gt=0
    )
    return render(request, 'products/detail.html', {'product': product})

# ------------------------- Admin Dashboard -------------------------

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Admin access required")
    support_tickets = SupportTicket.objects.filter(status='open').order_by('-created_at')[:5]

    # Quick Stats
    stats = {
        'total_farmers': User.objects.filter(user_type='FARMER').count(),
        'total_buyers': User.objects.filter(user_type='BUYER').count(),
        'total_products': Product.objects.count(),
        'total_transactions': EscrowTransaction.objects.count(),
        'revenue_30d': EscrowTransaction.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)  # Use django.utils.timezone.now()
        ).aggregate(Sum('platform_fee'))['platform_fee__sum'] or 0,
    }
        # Get users with valid Ethiopian numbers
    valid_users = User.objects.filter(
        phone__regex=r'^\+251[79]\d{8}$'
    ).exclude(phone__isnull=True)

    # Recent Data
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_transactions = EscrowTransaction.objects.select_related(
        'buyer', 'seller'
    ).order_by('-created_at')[:5]
    open_tickets = SupportTicket.objects.filter(status='OPEN')

    return render(request, 'admin/dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_transactions': recent_transactions,
        'pending_products': Product.objects.filter(is_approved=False).select_related('seller')[:10],
        'open_tickets': open_tickets,
        'valid_users': valid_users,
        'support_tickets': support_tickets
    })

@require_POST
@login_required
def toggle_user_status(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True, 
        'is_active': user.is_active,
        'new_status': 'Active' if user.is_active else 'Suspended',
        'new_class': 'bg-success' if user.is_active else 'bg-danger'
    })

@login_required
def user_detail(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    try:
        user = User.objects.get(pk=user_id)
        return JsonResponse({
            'full_name': user.get_full_name(),
            'email': user.email,
            'phone': user.phone,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active,
            'user_type': user.get_user_type_display()
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@login_required
def moderate_product(request, product_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            product.is_approved = True
            product.is_active = True
            messages.success(request, f'Product "{product.name}" approved')
        elif action == 'reject':
            product.is_approved = False
            product.is_active = False
            messages.warning(request, f'Product "{product.name}" rejected')
        elif action == 'delete':
            product_name = product.name
            product.delete()
            messages.success(request, f'Product "{product_name}" permanently deleted')
            return redirect('admin_dashboard')
        
        product.save()
        return redirect('admin_dashboard')
    
    # GET request handling for preview
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'seller': product.seller.email,
        'price': str(product.price),
        'category': product.get_category_display(),
        'description': product.description,
        'image_url': product.image.url if product.image else '',
        'created_at': product.created_at.strftime("%b %d, %Y %H:%M")
    })
# ------------------------- common Dashboard -------------------------
def common_dashboard_setup(request):
    return {
        'notifications': Notification.objects.filter(user=request.user)
                                              .order_by('-created_at')[:10]
    }
# ------------------------- Farmer and Supplier Views -------------------------
@login_required
def farmer_dashboard(request):
    """Farmer-specific dashboard with agricultural focus"""
        # Force refresh user data from database
    request.user.refresh_from_db()
    profile, created = FarmerProfile.objects.get_or_create(user=request.user)
    if not validate_farmer_access(request.user):
        return HttpResponseForbidden("Access restricted to registered farmers")
    
    farmer = request.user
    products = Product.objects.filter(seller=farmer)
    transactions = EscrowTransaction.objects.filter(seller=farmer)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    # Dashboard metrics
    total_sales = transactions.filter(status='completed').aggregate(
        Sum('amount'))['amount__sum'] or 0
    pending_orders = transactions.filter(status='held').count()
    
    return render(request, 'farmer/dashboard.html', {
        'profile': farmer.farmer_profile,
        'products': products,
        'transactions': transactions,
        'total_sales': total_sales,
        'notifications': notifications,
        'pending_orders': pending_orders,
        **common_dashboard_setup(request),
        'SUPPORT_PHONE': '+251915451380'  # Replace with actual support number
    })

@login_required
@transaction.atomic
def mark_as_shipped(request, transaction_id):
    """Farmer marks order as shipped"""
    transaction = get_object_or_404(
        EscrowTransaction.objects.select_related('seller'),
        pk=transaction_id,
        seller=request.user
    )
    buyer_name = transaction.buyer.get_full_name()
    create_notification(
        user=request.user,
        message=f"New order for {transaction.product.name} from {buyer_name}",
        notification_type='ORDER'
    )
    if transaction.status != 'held':
        messages.error(request, "Invalid transaction state for shipping")
        return redirect('farmer_dashboard')

    try:
        transaction.status = 'shipped'
        transaction.save()
        
        # Create system update
        TransactionUpdate.objects.create(
            transaction=transaction,
            message=f"Product marked as shipped by farmer",
            created_by=request.user
        )

        messages.success(request, "Product shipping status updated!")
        
    except Exception as e:
        messages.error(request, f"Shipping update failed: {str(e)}")
        logger.error(f"Shipping error: {str(e)}")

    return redirect('farmer_dashboard')

@login_required
def farmer_edit_profile(request):
    if request.user.user_type != 'FARMER':
        return HttpResponseForbidden("Farmer access required")
    
    farmer = request.user
    profile = get_object_or_404(FarmerProfile, user=farmer)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=farmer)
        profile_form = FarmerProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('farmer_dashboard')
    else:
        user_form = UserForm(instance=farmer)
        profile_form = FarmerProfileForm(instance=profile)
    
    return render(request, 'farmer/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def supplier_dashboard(request):
    if request.user.user_type != 'SUPPLIER':
        return HttpResponseForbidden("Supplier access required")
    
    supplier = request.user
    products = Product.objects.filter(seller=supplier).order_by('-created_at')
    transactions = EscrowTransaction.objects.filter(seller=supplier)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    # Pagination
    product_paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    product_page = product_paginator.get_page(page_number)
    
    # Performance metrics
    total_sales = transactions.filter(status='completed').aggregate(
        Sum('amount'))['amount__sum'] or 0
    pending_orders = transactions.filter(status='held').count()
    
    return render(request, 'supplier/dashboard.html', {
        'profile': supplier.supplier_profile,
        'products': product_page,
        'transactions': transactions,
        'total_sales': total_sales,
        'notifications': notifications,
        **common_dashboard_setup(request),
        'pending_orders': pending_orders,
    })
@login_required
@transaction.atomic
def update_order_status(request, transaction_id):
    # Fetch the transaction with the related product
    transaction = get_object_or_404(
        EscrowTransaction.objects.select_related('product'),  # Ensure product is loaded
        pk=transaction_id,
        seller=request.user
    )
    
    # Debugging: Ensure the product instance is loaded
    product = transaction.product
    if not isinstance(product, Product):
        raise ValueError("The product field is not properly resolved to a Product instance.")
    
    # Check stock quantity
    if product.stock_quantity < 5:
        create_notification(
            user=transaction.seller,
            message=f"Low stock alert for {product.name}",  # Access product.name correctly
            notification_type='INVENTORY'
        )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['shipped', 'completed']:
            transaction.status = new_status
            transaction.save()
            messages.success(request, f"Order status updated to {new_status}")
        else:
            messages.error(request, "Invalid status update")
    
    return redirect('supplier_dashboard')
    
@login_required
def supplier_edit_profile(request):
    if request.user.user_type != 'SUPPLIER':
        return HttpResponseForbidden("Supplier access required")
    
    supplier = request.user
    profile = get_object_or_404(SupplierProfile, user=supplier)
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=supplier)
        profile_form = SupplierProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('supplier_dashboard')
    else:
        user_form = UserForm(instance=supplier)
        profile_form = SupplierProfileForm(instance=profile)
    
    return render(request, 'supplier/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
# ------------------------- Product Management Views -------------------------
@login_required
@transaction.atomic
def add_product(request):
    if request.user.user_type not in ['FARMER', 'SUPPLIER']:
        messages.error(request, "Product listing not allowed for your account type")
        return redirect('home')

    if request.method == 'POST':

        form = ProductForm(request.POST or None, request.FILES or None, user=request.user)  # Pass user to form
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.seller = request.user
                product.full_clean()  # Explicit validation
                product.save()
                messages.success(request, "Product listed successfully!")
                return redirect('farmer_dashboard' if request.user.user_type == 'FARMER'
                               else 'supplier_dashboard')
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'farmer/product_form.html', {'form': form})  # Stay on same page
            except IntegrityError:
                messages.error(request, "Product creation failed. Please try again.")
    else:
        form = ProductForm(initial={'seller': request.user})  # Pre-set seller
    context = {
        'form': form,
        'agricultural_categories': Product.FARMER_CATEGORIES,
        'equipment_categories': Product.SUPPLIER_CATEGORIES,
        'is_farmer': request.user.user_type == 'FARMER'
    }
    return render(request, 'farmer/product_form.html', context)
            
@login_required
@transaction.atomic
def edit_product(request, pk):
    """Product editing with ownership validation"""
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        # Pass user to form
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect('farmer_dashboard')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'farmer/product_form.html', {'form': form})
def clean_stock_quantity(self):
    stock = self.cleaned_data['stock_quantity']
    if stock < 0:
        raise ValidationError("Stock cannot be negative")
    return stock
# ------------------------- Payment Views -------------------------

@login_required
def initiate_payment(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cities = City.objects.all()

    if product.seller == request.user:
        messages.error(request, "You cannot purchase your own product")
        return redirect('product_detail', product_id=product_id)
    
    return render(request, 'payments/initiate.html', {
        'product': product,
        'user_balance': request.user.wallet_balance,
        'product_price': product.price,
        'cities': cities,
        'balance_sufficient': request.user.wallet_balance >= product.price
    })
@login_required
@transaction.atomic
def process_payment(request, product_id):
    if request.method != 'POST':
        return redirect('initiate_payment', product_id=product_id)

    product = get_object_or_404(Product, pk=product_id)
    user = request.user

    try:
        quantity = int(request.POST.get('quantity', 1))
        logistics_id = request.POST.get('logistics')

        if quantity < 1:
            raise ValueError("Quantity must be at least 1")

        # Calculate base amount (product price * quantity)
        base_amount = product.price * quantity

        # Calculate delivery cost if logistics is selected
        delivery_cost = Decimal('0.00')
        if logistics_id:
            logistics = get_object_or_404(User, pk=logistics_id)
            price_per_km = Decimal(str(logistics.logisticsprofile.price_per_km))
            distance_km = Decimal('10.0')  # Example distance
            delivery_cost = (price_per_km * distance_km).quantize(Decimal('0.00'))

        # Calculate platform fee (2.5% of base amount)
        platform_fee = (base_amount * Decimal('0.025')).quantize(Decimal('0.00'))

        # Total charge to buyer (base + delivery + fee)
        total_charge = base_amount + delivery_cost + platform_fee

        # Validate buyer balance
        if user.wallet_balance < total_charge:
            needed = total_charge - user.wallet_balance
            messages.error(request,
                f"Insufficient balance. You need {needed:.2f} ETB more for {quantity} items"
            )
            return redirect('initiate_payment', product_id=product_id)

        # Validate stock
        if product.stock_quantity < quantity:
            messages.error(request,
                f"Only {product.stock_quantity} items available in stock"
            )
            return redirect('initiate_payment', product_id=product_id)

        # Deduct funds from buyer
        user.wallet_balance -= total_charge
        user.save()

        # Create escrow transaction (product amount + fee)
        transaction = EscrowTransaction.objects.create(
            buyer=user,
            seller=product.seller,
            product=product,
            quantity=quantity,
            amount=base_amount,  # This is just the product amount
            platform_fee=platform_fee,
            status='held',
            telebirr_reference=f"TX-{uuid4().hex[:8].upper()}"
        )

        # Update stock
        product.stock_quantity -= quantity
        product.save()

        # Create order with logistics info
        order = Order.objects.create(
            product=product,
            quantity=quantity,
            logistics=logistics if logistics_id else None,
            delivery_cost=delivery_cost
        )

        # Handle delivery job if logistics selected
        if logistics_id:
            pickup_time = timezone.now() + timedelta(hours=2)
            pickup_location = getattr(product.seller, 'farmerprofile', getattr(product.seller, 'supplierprofile', None))
            if pickup_location:
                pickup_location = pickup_location.location
            else:
                pickup_location = "Seller Location Not Specified"
            
            job = DeliveryJob.objects.create(
                provider=logistics,
                client=user,
                pickup_location=pickup_location,
                dropoff_location=user.buyerprofile.primary_address,
                payment_amount=delivery_cost * Decimal('0.9'),  # 10% platform fee
                pickup_time=pickup_time,
                status='PENDING'
            )
            
            create_notification(
                user=logistics,
                message=f"New delivery request for {product.name} from {user.get_full_name()} - Pickup at {pickup_time.strftime('%b %d, %H:%M')}",
                notification_type='DELIVERY',
                related_url=reverse('logistics_dashboard')
            )

        return redirect('payment_success', transaction_id=transaction.id)

    except Exception as e:
        messages.error(request, f"Payment failed: {str(e)}")
        return redirect('initiate_payment', product_id=product_id)
    
@login_required
def payment_success(request, transaction_id):
    transaction = get_object_or_404(
        EscrowTransaction,
        id=transaction_id,
        buyer=request.user
    )
    return render(request, 'payments/payment_success.html', {
        'transaction': transaction
    })

@login_required
def transaction_detail(request, transaction_id):
    """Transaction detail view with updates"""
    transaction = get_object_or_404(
        EscrowTransaction.objects.select_related('buyer', 'seller'),
        Q(buyer=request.user) | Q(seller=request.user),
        pk=transaction_id
    )
    updates = TransactionUpdate.objects.filter(transaction=transaction)
    return render(request, 'payments/transaction_detail.html', {
        'transaction': transaction,
        'updates': updates
    })

# ------------------------- Wallet System -------------------------
@login_required
def wallet_topup(request):
    if request.method == 'POST':
        form = WalletTopupForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Save will automatically add funds through model's save()
                topup = form.save(commit=False)
                topup.user = request.user
                topup.save()
                
                messages.success(request, 
                    f"Successfully added {topup.amount} ETB to your wallet. "
                    f"New balance: {request.user.wallet_balance} ETB"
                )
                return redirect('wallet_topup')
            
            except Exception as e:
                messages.error(request, f"Error processing top-up: {str(e)}")
        else:
            messages.error(request, "Please correct the errors below")
    else:
        form = WalletTopupForm()

    return render(request, 'payments/wallet_topup.html', {
        'form': form,
        'current_balance': request.user.wallet_balance
    })
# ------------------------- Static Pages -------------------------
def about_us(request):
    stats = {
        'total_farmers': User.objects.filter(user_type='FARMER').count(),
        'total_buyers': User.objects.filter(user_type='BUYER').count(),
        'total_transactions': EscrowTransaction.objects.count(),
        'total_revenue': EscrowTransaction.objects.aggregate(
            Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'about_us.html', {'stats': stats})

def help_center(request):
    return render(request, 'help.html')
def farming_resources(request):
    return render(request, 'resources.html')
def blog(request):
    return render(request, 'blog.html')
def blog_post(request, post_id):
    """Blog post detail view"""
    # Assuming you have a BlogPost model
    # blog_post = get_object_or_404(BlogPost, id=post_id)
    # return render(request, 'blog_post.html', {'blog_post': blog_post})
    raise Http404("Blog post not found")  # Placeholder for actual implementation

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

# ------------------------- PDF Export -------------------------
@login_required
def export_pdf(request):
    """Generate PDF profile with error handling"""
    try:
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        
        # PDF content
        p.drawString(100, 800, f"User Profile: {request.user.email}")
        p.drawString(100, 780, f"Name: {request.user.get_full_name()}")
        p.drawString(100, 760, f"Wallet Balance: {request.user.wallet_balance} ETB")
        p.drawString(100, 740, f"Account Type: {request.user.get_user_type_display()}")
        p.drawString(100, 720, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename='profile.pdf')
    
    except Exception as e:
        messages.error(request, "Failed to generate PDF")
        return redirect('my_account')

# ------------------------- Public Profile -------------------------
def user_profile(request, username):
    """Public user profile view"""
    user = get_object_or_404(
        User.objects.prefetch_related('products'),
        username=username
    )
    return render(request, 'profile.html', {
        'profile_user': user,
        'farmer_profile': getattr(user, 'farmer_profile', None)
    })

# ------------------------- Currency Converter -------------------------
import requests
from django.shortcuts import render
from .forms import CurrencyConvertForm

def currency_converter(request):
    result = None
    error = None
    form = CurrencyConvertForm()

    if request.method == 'POST':
        form = CurrencyConvertForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            from_currency = form.cleaned_data['from_currency']
            to_currency = form.cleaned_data['to_currency']

            api_key = 'f1477878fed70eca8b5deb09'  # Replace this with your actual key
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"

            try:
                res = requests.get(url)
                data = res.json()
                print("API response:", data)

                if data['result'] == 'success':
                    result = round(data['conversion_result'], 2)
                else:
                    error = "Currency conversion failed. Try again."

            except Exception as e:
                print("API error:", str(e))
                error = "Failed to connect to the currency API. Try later."

    return render(request, "currency_converter.html", {
        'form': form,
        'result': result,
        'error': error,
    })

# ------------------------- Logistics Views -------------------------

@login_required
def logistics_dashboard(request):
    profile, created = LogisticsProfile.objects.get_or_create(user=request.user)
    if not request.user.is_logistics:
        return HttpResponseForbidden("Logistics access required")
    
    # Get all jobs for the provider
    jobs = DeliveryJob.objects.filter(provider=request.user).order_by('-created_at')
    
    # Get unread delivery notifications
    delivery_notifications = Notification.objects.filter(
        user=request.user,
        notification_type='DELIVERY',
        is_read=False
    )
    
    # Mark notifications as read when viewed
    delivery_notifications.update(is_read=True)

    # Dashboard metrics
    total_earnings = jobs.filter(status='COMPLETED').aggregate(
        Sum('payment_amount'))['payment_amount__sum'] or 0
    pending_jobs = jobs.filter(status='PENDING').count()
    
    return render(request, 'logistics/dashboard.html', {
        'profile': profile,
        'jobs': jobs,
        'total_earnings': total_earnings,
        'pending_jobs': pending_jobs,
        'upcoming_jobs': jobs.exclude(status__in=['COMPLETED', 'CANCELLED']),
        'SUPPORT_PHONE': '+251915451380',
        **common_dashboard_setup(request)
    })

@login_required
def logistics_edit_profile(request):
    if not request.user.is_logistics:
        return HttpResponseForbidden("Logistics access required")
    
    profile = request.user.logisticsprofile
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    if request.method == 'POST':
        form = LogisticsProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('logistics_dashboard')
    else:
        form = LogisticsProfileForm(instance=profile)
    
    return render(request, 'logistics/edit_profile.html', {
        'form': form,
        'notifications': notifications,
        })

@login_required
def job_details(request, job_id):
    job = get_object_or_404(DeliveryJob, id=job_id, provider=request.user)
    return render(request, 'logistics/job_details.html', {'job': job})
@login_required
def accept_job(request, job_id):
    job = get_object_or_404(DeliveryJob, id=job_id, provider=request.user, status='PENDING')
    job.status = 'ACCEPTED'
    job.save()
    
    create_notification(
        user=job.client,
        message=f"{request.user.get_full_name()} accepted your delivery request",
        notification_type='DELIVERY'
    )
    
    messages.success(request, "Job accepted successfully!")
    return redirect('job_details', job_id=job_id)

@login_required
def reject_job(request, job_id):
    job = get_object_or_404(DeliveryJob, id=job_id, provider=request.user, status='PENDING')
    job.status = 'CANCELLED'
    job.save()
    
    create_notification(
        user=job.client,
        message=f"{request.user.get_full_name()} rejected your delivery request",
        notification_type='DELIVERY'
    )
    
    messages.warning(request, "Job rejected successfully!")
    return redirect('logistics_dashboard')
@login_required
def complete_job(request, job_id):
    job = get_object_or_404(DeliveryJob, id=job_id, provider=request.user)
    if request.method == 'POST':
        form = JobCompletionForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            job.status = 'COMPLETED'
            job.save()
            
            # Update provider stats
            provider = request.user.logisticsprofile
            provider.completed_jobs += 1
            provider.save()
            
            messages.success(request, "Job marked as completed!")
            return redirect('logistics_dashboard')
    return redirect('logistics_dashboard')
@login_required
def checkout(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    cities = City.objects.all()

    if request.method == 'POST':
        # Get selected logistics provider
        logistics_id = request.POST.get('logistics')
        city_id = request.POST.get('delivery_city')
        if not city_id:
            messages.error(request, "Please select delivery city")
            return redirect('checkout', product_id=product_id)
            # Save city to buyer profile
        buyer_profile = request.user.buyerprofile
        buyer_profile.delivery_city = City.objects.get(id=city_id)
        buyer_profile.save()
        
        if logistics_id:
            logistics = get_object_or_404(User, pk=logistics_id)
            # Simple distance calculation (implement real logic)
            delivery_cost = logistics.logisticsprofile.price_per_km * 10  # 10km default
            
            # Create order
            order = Order.objects.create(
                buyer=request.user,
                product=product,
                logistics=logistics,
                delivery_cost=delivery_cost
            )
            
            # Create delivery job
            DeliveryJob.objects.create(
                provider=logistics,
                client=request.user,
                pickup_location=product.seller.farmerprofile.location,
                dropoff_location=request.user.buyerprofile.primary_address,
                payment_amount=delivery_cost * 0.9  # 10% platform fee
            )
            
            # Notifications
            create_notification(
                user=logistics,
                message=f"New delivery request from {request.user.get_full_name()}",
                notification_type='DELIVERY'
            )
            create_notification(
                user=request.user,
                message=f"Delivery request sent to {logistics.get_full_name()}",
                notification_type='DELIVERY'
            )
            
            return redirect('order_confirmation', order.id)
    
    # Get available logistics providers
    logistics_providers = User.objects.filter(
        user_type='LOGISTICS',
        logisticsprofile__service_areas__icontains=product.seller.farmerprofile.location
    )
    # Get available cities
    cities = City.objects.all()
    return render(request, 'checkout.html', {
        'product': product,
        'logistics_options': logistics_providers,
        'cities': cities
    })


def logistics_providers(request):
    city_id = request.GET.get('city')
    providers = []

    # Get nationwide providers
    nationwide_providers = User.objects.filter(
        logisticsprofile__nationwide=True,
        logisticsprofile__isnull=False
    ).distinct()

    # Get city-specific providers
    city_providers = User.objects.filter(
        logisticsprofile__service_areas__id=city_id,
        logisticsprofile__isnull=False
    ).distinct()

    # Combine both querysets
    all_providers = nationwide_providers | city_providers
    
    for provider in all_providers.distinct():
        profile = provider.logisticsprofile
        providers.append({
            'id': provider.id,
            'name': provider.get_full_name(),
            'vehicle_type': profile.get_vehicle_type_display(),
            'price_per_km': float(profile.price_per_km),
            'service_areas': "Nationwide" if profile.nationwide else ", ".join(
                [city.get_name_display() for city in profile.service_areas.all()]
            )
        })
    
    return JsonResponse(providers, safe=False)

# BUYER DASHBOARD
@login_required
def buyer_dashboard(request):
    request.user.refresh_from_db()
    if not request.user.is_buyer:
        return HttpResponseForbidden("Buyer access required")
    
    profile, created = BuyerProfile.objects.get_or_create(user=request.user)
    if created:
        profile.primary_address = "Address not specified"
        profile.save()

    # Get orders with related data to optimize queries
    orders = EscrowTransaction.objects.filter(buyer=request.user).select_related(
        'product', 'seller'
    ).order_by('-created_at')

    # Notifications (last 5 unread)
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    # Spending analytics (last 6 months)
    today = timezone.now()
    six_months_ago = today - timedelta(days=180)
    
    monthly_spending = orders.filter(
        status='completed',
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    # Prepare chart data
    chart_labels = []
    chart_data = []
    
    for month in range(6):
        date = six_months_ago + relativedelta(months=+month)
        chart_labels.append(date.strftime("%b %Y"))
        
        monthly_total = next(
            (item['total'] for item in monthly_spending 
             if item['month'].month == date.month and 
                item['month'].year == date.year),
            0
        )
        chart_data.append(float(monthly_total))

    return render(request, 'buyer/dashboard.html', {
        'profile': profile,
        'orders': orders[:5],  # Only show 5 most recent
        'wishlist': WishlistItem.objects.filter(user=request.user),
        'total_spent': orders.filter(status='completed').aggregate(
            Sum('amount'))['amount__sum'] or 0,
        'active_orders': orders.exclude(
            status__in=['completed', 'cancelled']).count(),
        'wallet_transactions': WalletTransaction.objects.filter(
            user=request.user).order_by('-timestamp')[:5],
        'categories': ProductCategory.objects.all(),
        'products': Product.objects.filter(is_active=True)[:6],  # Sample products
        'notifications': notifications,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'SUPPORT_PHONE': '+251915451380'
    })

@login_required
def toggle_wishlist(request, product_id):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        product = Product.objects.get(id=product_id)
        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user, 
            product=product
        )
        
        if not created:
            wishlist_item.delete()
        
        return JsonResponse({
            'added': created,
            'wishlist_count': request.user.wishlist_items.count()
        })
        
    except Exception as e:
        logger.error(f"Wishlist error: {str(e)}")
        return JsonResponse({
            'error': 'Failed to update wishlist',
            'detail': str(e)
        }, status=500)
    
@login_required
def buyer_edit_profile(request):
    user = request.user
    profile = user.buyerprofile
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = BuyerProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('buyer_dashboard')
    else:
        user_form = UserForm(instance=user)
        profile_form = BuyerProfileForm(instance=profile)
    
    return render(request, 'buyer/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(EscrowTransaction, id=order_id, buyer=request.user)
    if order.status == 'held':
        order.status = 'cancelled'
        order.save()
        # Refund logic
        request.user.wallet_balance += order.amount
        request.user.save()
        WalletTransaction.objects.create(
            user=request.user,
            amount=order.amount,
            transaction_type='REFUND'
        )
        messages.success(request, "Order cancelled and funds refunded")
    else:
        messages.error(request, "Cannot cancel order after shipping")
    return redirect('buyer_dashboard')

@login_required
def manage_addresses(request):
    addresses = request.user.addresses.all()
    return render(request, 'buyer/addresses.html', {'addresses': addresses})

@login_required
def create_support_ticket(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            form.save_m2m()  # Save the many-to-many data
            messages.success(request, "Support ticket submitted successfully")
            return redirect('buyer_dashboard')
    else:
        form = SupportTicketForm()
    
    return render(request, 'buyer/support_ticket.html', {
        'form': form,
        'max_files': 5,
        'allowed_types': ['image/*', 'application/pdf']
    })

@login_required
def order_history(request):
    orders = EscrowTransaction.objects.filter(
        buyer=request.user
    ).select_related('product', 'seller').order_by('-created_at')
    
    return render(request, 'buyer/order_history.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        EscrowTransaction.objects.select_related('product', 'seller', 'buyer'),
        id=order_id,
        buyer=request.user
    )
    
    updates = TransactionUpdate.objects.filter(
        transaction=order
    ).order_by('-created_at')
    
    return render(request, 'buyer/order_detail.html', {
        'order': order,
        'updates': updates,
        'can_confirm': order.status == 'shipped' and not order.buyer_confirmed
    })

@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(
        user=request.user
    ).select_related('product')
    
    return render(request, 'buyer/wishlist.html', {
        'wishlist_items': wishlist_items
    })
@login_required
@transaction.atomic
def confirm_delivery(request, transaction_id):
    transaction = get_object_or_404(
        EscrowTransaction.objects.select_related('seller'),
        pk=transaction_id,
        buyer=request.user,
        status='shipped'
    )

    if transaction.status != 'shipped':
        messages.error(request, "Product must be shipped first")
        return redirect('buyer_dashboard')
    
    if request.method == 'POST':
        form = DeliveryConfirmationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Calculate net amount after platform fee
                net_amount = transaction.amount - transaction.platform_fee
                
                # Update transaction
                transaction.status = 'completed'
                transaction.delivery_confirmed_at = timezone.now()
                transaction.buyer_confirmed = True
                
                if form.cleaned_data['delivery_proof']:
                    transaction.delivery_proof = form.cleaned_data['delivery_proof']
                
                transaction.save()

                # Release funds to seller
                transaction.seller.wallet_balance += net_amount
                transaction.seller.save()

                # Create wallet transaction record
                WalletTransaction.objects.create(
                    user=transaction.seller,
                    amount=net_amount,
                    transaction_type='ESCROW_RELEASE',
                    related_transaction=transaction
                )

                # Create system update
                TransactionUpdate.objects.create(
                    transaction=transaction,
                    message=f"Delivery confirmed by buyer. {net_amount} ETB released to seller.",
                    created_by=request.user
                )

                # Create notification for seller
                Notification.objects.create(
                    user=transaction.seller,
                    message=f"Buyer confirmed delivery for order #{transaction.id}",
                    notification_type='DELIVERY',
                    related_url=f"/seller/orders/{transaction.id}/"
                )

                messages.success(request, "Delivery confirmed! Funds released to seller.")
                return redirect('order_detail', order_id=transaction.id)

            except Exception as e:
                messages.error(request, f"Confirmation failed: {str(e)}")
                logger.error(f"Delivery confirmation error: {str(e)}")
                return redirect('transaction_detail', transaction_id=transaction_id)
    else:
        form = DeliveryConfirmationForm()

    return render(request, 'buyer/confirm_delivery.html', {
        'transaction': transaction,
        'form': form,
        'net_amount': transaction.amount - transaction.platform_fee
    })
@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5].values(
        'message', 
        'notification_type',
        'created_at',
        'related_url'
    )
    return JsonResponse(list(notifications), safe=False)


from django.core.mail import send_mail
from .forms import ContactForm

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            subject_mapping = {
                'general': 'General Inquiry',
                'support': 'Technical Support',
                'orders': 'Order Issues',
                'accounts': 'Account Help',
                'transaction': 'Transaction Issues',
                'feedback': 'Feedback',
                'complaint': 'Complaint',
                'other': 'Other',
            }

            # Get friendly subject name
            subject_display = subject_mapping.get(cd['subject'], cd['subject'])
            
            # Handle custom subject
            if cd['subject'] == 'other' and cd.get('custom_subject'):
                email_subject = f"[AgriCommerce] {cd['custom_subject']}"
            else:
                email_subject = f"[AgriCommerce] {subject_display}"

            full_message = f"From: {cd['name']} <{cd['email']}>\n\n{cd['message']}"
            
            send_mail(
                email_subject,  # Use the constructed subject
                full_message,
                cd['email'],
                ['groupo1ne@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent! We'll get back to you soon.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})