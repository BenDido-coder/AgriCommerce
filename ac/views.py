from datetime import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import EscrowTransaction,TransactionUpdate, Product, User, FarmerProfile


def home(request):
    return render(request, 'homepage.html')
def login(request):
    return render(request, 'login.html')
def signup(request):
    return render(request, 'signup.html')
def about_us(request):
    return render(request, 'about_us.html')
def my_account(request):
    return render(request, 'my account.html')
def blog(request):
    return render(request, 'blog.html')
def products(request):
    return render(request, 'products.html')

#################################################

# Add these to existing views
@login_required
def initiate_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user == product.seller:
        messages.error(request, "You cannot buy your own product")
        return redirect('product_detail', product_id=product.id)
    
    if request.method == 'POST':
        # Deduct from buyer's wallet
        if request.user.deduct_wallet(product.price):
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
        # Release funds to seller
        transaction.seller.add_wallet(transaction.amount)
        transaction.status = 'completed'
        transaction.save()
        messages.success(request, "Payment released to seller!")
    else:
        messages.warning(request, "Invalid transaction state")
    
    return redirect('transaction_detail', transaction_id=transaction.id)


# Add to existing views
@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(
        EscrowTransaction,
        id=transaction_id,
        buyer=request.user  # Only buyer can view
    )
    return render(request, 'payments/transaction_detail.html', {'transaction': transaction})
# ac/views.py

def user_profile(request, username):
    user = User.objects.get(username=username)
    context = {
        'user': user,
        'farmer_profile': FarmerProfile.objects.filter(user=user).first()
    }
    return render(request, 'profile.html', context)
# ac/views.py
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def payment_health(request):
    return render(request, 'admin/payment_health.html', {
        'pending': EscrowTransaction.objects.filter(status='held').count(),
        'completed': EscrowTransaction.objects.filter(status='completed').sum('amount'),
        'disputes': EscrowTransaction.objects.filter(status='disputed').count()
    })


# Add temporary view in views.py to Directly access profile page template:
from django.shortcuts import render

def test_profile(request):
    return render(request, 'profile.html', context={
        'user': {
            'username': 'Abebe',
            'get_role_display': lambda: 'Farmer',
            'phone': '+251964802311', # Replace with your real number
            'wallet_balance': 1000.00
        },
        'farmer_profile': {
            'farm_name': 'Test Farm',
            'location': 'Addis Ababa'
        }
    })

from django.shortcuts import render
from .models import User

def test_admin_dashboard(request):
    users = User.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

def test_supplier_dashboard(request):
    return render(request, 'supplier_dashboard.html', {
        'user': {
            'username': 'TestSupplier',
            'phone': '+251900000004',
            'get_role_display': lambda: 'Supplier'
        },
        'equipment_list': [
            {'name': 'Tractor', 'price': 150000},
            {'name': 'Irrigation System', 'price': 75000}
        ]
    })