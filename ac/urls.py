from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views
from .forms import CustomAuthForm  # Optional: Use if you're using a custom login form

urlpatterns = [
    # --- Home ---
    path('', views.home, name='home'),

    # --- Authentication ---
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(
        authentication_form=CustomAuthForm  # ✅ Use custom auth form if needed
    ), name='login'),
   # path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('accounts/profile/', lambda request: redirect('my_account'), name='profile_redirect'),

    # --- Static Info Pages ---
    path('about_us/', views.about_us, name='about_us'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('help/', views.help_center, name='help'),
    path('contact/', views.contact_support, name='contact'),
    path('resources/', views.farming_resources, name='resources'),

    # --- User Dashboards ---
    path('my_account/', views.my_account, name='my_account'),
    path('profile/<str:username>/', views.user_profile, name='user-profile'),
    path('test-profile/', views.test_profile, name='test-profile'),
    path('test-admin/', views.test_admin_dashboard),
    path('test-supplier/', views.test_supplier_dashboard),

    # --- Products & Transactions ---
    path('products/', views.products, name='products'),
    path('pay/<int:product_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/<int:transaction_id>/', views.payment_success, name='payment_success'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('confirm-delivery/<int:transaction_id>/', views.confirm_delivery, name='confirm_delivery'),

    # --- Blog & Extras ---
    path('blog/', views.blog, name='blog'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
]
