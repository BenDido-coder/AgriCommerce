from datetime import timezone
from django.shortcuts import render

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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, EscrowTransaction, TransactionUpdate

# Add these to existing views
@login_required
def initiate_payment(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        # Simulate wallet deduction
        request.user.deduct_wallet(product.price)
        
        transaction = EscrowTransaction.objects.create(
            buyer=request.user,
            seller=product.seller,
            product=product,
            amount=product.price,
            telebirr_reference=f"SIM-{timezone.now().timestamp()}"
        )
        
        TransactionUpdate.objects.create(
            transaction=transaction,
            message=f"Payment initiated for {product.name} - ₦{product.price} held in escrow"
        )
        
        return redirect('payment_success', transaction_id=transaction.id)
    
    return render(request, 'payments/payment_form.html', {'product': product})

@login_required
def payment_success(request, transaction_id):
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    return render(request, 'payments/payment_success.html', {'transaction': transaction})

@login_required
def confirm_delivery(request, transaction_id):
    transaction = get_object_or_404(EscrowTransaction, id=transaction_id)
    
    if request.user != transaction.buyer:
        return redirect('permission_denied')
    
    transaction.seller.add_wallet(transaction.amount)
    transaction.status = 'completed'
    transaction.save()
    
    TransactionUpdate.objects.create(
        transaction=transaction,
        message="Payment released to seller - transaction completed"
    )
    
    return redirect('transaction_completed')
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
from .models import User, FarmerProfile

def user_profile(request, username):
    user = User.objects.get(username=username)
    context = {
        'user': user,
        'farmer_profile': FarmerProfile.objects.filter(user=user).first()
    }
    return render(request, 'profile.html', context)