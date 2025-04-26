from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('about_us/', views.about_us, name='about us'),
    path('my_account/', views.my_account, name='my_account'),
    path('blog/', views.blog, name='blog'),
    path('products/', views.products, name='products'),
    ]
