from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from .forms import SignupForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProductForm
from .models import Product


def home(request):
    return render(request, 'homepage.html')
def about_us(request):
    return render(request, 'about_us.html')
def my_account(request):
    return render(request, 'my account.html')
def blog(request):
    return render(request, 'blog.html')
def products(request):
    return render(request, 'products.html')
def admin(request):
    return render(request, 'admindashbor.html')
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Change to your desired redirect
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')  # or wherever you want to redirect after login
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'login.html')

@login_required
def my_account(request):
    return render(request, 'my account.html', {'user': request.user})

@login_required
def productform(request):
    if request.user.role != 'farmer':
        messages.error(request, "Only farmers can add products.")
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user  # Automatically set the logged-in user
            product.save()
            return redirect('my_account')
            # Redirect or render success
    else:
        form = ProductForm()
    return render(request, 'productform.html', {'form': form})


