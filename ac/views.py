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

