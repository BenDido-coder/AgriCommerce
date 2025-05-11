# views.py (Refactored and cleaned-up)
from datetime import timezone
from io import BytesIO
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from reportlab.pdfgen import canvas
from ac.forms import (
    CustomUserCreationForm, CustomAuthForm, FarmerProfileForm, ProfileUpdateForm,
)
from .models import (
    EscrowTransaction, Notification, TransactionUpdate, Product, User, FarmerProfile
)

# Static pages

def logout_view(request):
    logout(request)
    return redirect('home')

def home(request):
    return render(request, 'homepage.html')

def about_us(request):
    return render(request, 'about_us.html')

def blog(request):
    return render(request, 'blog.html')

def products(request):
    return render(request, 'products.html')

def farming_resources(request):
    return render(request, 'resources.html')

def help_center(request):
    return render(request, 'help.html')

def contact_support(request):
    return render(request, 'contact.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')


# Authentication views

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('home')
        messages.error(request, "Invalid email/phone or password")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Custom signup view
def signup(request):
    if request.method == 'POST':
        if 'force_save' in request.POST:
            try:
                user = User.objects.create(
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone'),
                    first_name=request.POST.get('first_name', ''),
                    last_name=request.POST.get('last_name', ''),
                    user_type=request.POST.get('user_type', 'BUYER')
                )
                user.set_password(request.POST['password1'])
                user.save()
                messages.success(request, "Force save succeeded. You are now registered.")
                return redirect('home')
            except Exception as e:
                messages.error(request, f"Force save failed: {str(e)}")

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use CustomAuthForm to log in with email or phone
            login_form = CustomAuthForm(request, data={
                'username': user.email or user.phone,
                'password': request.POST.get('password1')
            })
            if login_form.is_valid():
                auth_login(request, login_form.get_user())
                messages.success(request, "Account created and logged in successfully!")
                return redirect('home')
            else:
                messages.warning(request, "Account created but login failed. Please log in manually.")
                return redirect('login')
        else:
            print(form.errors.as_json())  # Optional: for debugging
            messages.error(request, "Please correct the errors below.")

    else:
        form = CustomUserCreationForm()

    return render(request, 'signup.html', {'form': form})


# Account views
@login_required
def my_account(request):
    user = request.user

    # Ensure the user has a FarmerProfile
    farmer_profile, _ = FarmerProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = ProfileUpdateForm(request.POST, instance=user)
        profile_form = FarmerProfileForm(request.POST, instance=farmer_profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('my_account')
        else:
            # Debug only: print errors in development
            print("User form errors:", user_form.errors)
            print("Profile form errors:", profile_form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = ProfileUpdateForm(instance=user)
        profile_form = FarmerProfileForm(instance=farmer_profile)

    # Fetch user's products and orders
    products = Product.objects.filter(seller=user)
    orders = EscrowTransaction.objects.filter(buyer=user)


    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'products': products,
        'orders': orders,
    }
    return render(request, 'my_account.html', context)

# Escrow & Payment views

@login_required
def initiate_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user == product.seller:
        messages.error(request, "You cannot buy your own product")
        return redirect('product_detail', product_id=product.id)
    
    if request.method == 'POST':
        if product.stock_quantity < 1:
            messages.error(request, "Product out of stock")
            return redirect('products')
            
        if request.user.deduct_wallet(product.price):
            product.stock_quantity -= 1
            product.save()
            
            transaction = EscrowTransaction.objects.create(
                buyer=request.user,
                seller=product.seller,
                product=product,
                amount=product.price,
                status='held'
            )
            messages.success(request, "Payment held in escrow! Seller will ship your order")
            return redirect('transaction_detail', transaction_id=transaction.id)
        
        messages.error(request, "Insufficient wallet balance")
        return redirect('wallet_topup')
    
    return render(request, 'payments/initiate.html', {'product': product})

@login_required
def payment_success(request, transaction_id):
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    return render(request, 'payments/payment_success.html', {'transaction': transaction})

@login_required
def confirm_delivery(request, transaction_id):
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    if request.user != transaction.buyer:
        messages.error(request, "Unauthorized action")
        return redirect('home')
    if transaction.status == 'held':
        transaction.seller.add_wallet(transaction.amount)
        transaction.status = 'completed'
        transaction.save()
        messages.success(request, "Payment released to seller!")
    else:
        messages.warning(request, "Invalid transaction state")
    return redirect('transaction_detail', transaction_id=transaction.id)

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id, buyer=request.user)
    return render(request, 'payments/transaction_detail.html', {'transaction': transaction})

# Profile PDF export

@login_required
def export_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"User Profile: {request.user.email}")
    p.drawString(100, 780, f"Name: {request.user.get_full_name()}")
    p.drawString(100, 760, f"Role: {request.user.get_user_type_display()}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='profile.pdf')

# Admin-only views

@staff_member_required
def payment_health(request):
    return render(request, 'admin/payment_health.html', {
        'pending': EscrowTransaction.objects.filter(status='held').count(),
        'completed': EscrowTransaction.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
        'disputes': EscrowTransaction.objects.filter(status='disputed').count()
    })

# Debug/testing views

def test_profile(request):
    farmer_profile = FarmerProfile.objects.filter(user=request.user).first()
    return render(request, 'profile.html', {
        'user': request.user,
        'farmer_profile': farmer_profile
    })

def test_admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

def test_supplier_dashboard(request):
    return render(request, 'supplier_dashboard.html', {
        'user': {
            'username': 'TestSupplier',
            'phone': '+251900000004',
            'get_user_type_display': lambda: 'Supplier'
        },
        'equipment_list': [
            {'name': 'Tractor', 'price': 150000},
            {'name': 'Irrigation System', 'price': 75000}
        ]
    })

# Public user profile

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    farmer_profile = FarmerProfile.objects.filter(user=user).first()
    return render(request, 'profile.html', {
        'user': user,
        'farmer_profile': farmer_profile
    })
