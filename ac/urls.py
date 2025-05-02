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
    ##################################
    path('pay/<int:product_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/<int:transaction_id>/', views.payment_success, name='payment_success'),
    path('transaction/confirm/<int:transaction_id>/', views.confirm_delivery, name='confirm_delivery'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('profile/<str:username>/', views.user_profile, name='user-profile'),

]
