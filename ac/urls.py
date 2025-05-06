from django.contrib import admin
from django.urls import path
from . import views
from .views import login



urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('about_us/', views.about_us, name='about us'),
    path('my_account/', views.my_account, name='my_account'),
    path('blog/', views.blog, name='blog'),
    path('products/', views.products, name='products'),
    path('admindash/', views.admin, name='admindash'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('productform/', views.productform, name='productform'),
    ]
