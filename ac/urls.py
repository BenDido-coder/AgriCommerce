from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from . import views
from .forms import CustomAuthForm
from .views import currency_converter

# Custom Login/Logout Views
class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser:
            return reverse('admin_dashboard')
        elif user.user_type == 'FARMER':
            return reverse('farmer_dashboard')
        elif user.user_type == 'SUPPLIER':
            return reverse('supplier_dashboard')
        elif user.user_type == 'LOGISTICS':
            return reverse('logistics_dashboard')
        elif user.user_type == 'BUYER':
            return reverse('buyer_dashboard')
        return super().get_success_url()

urlpatterns = [
    # Core Routes
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(
        authentication_form=CustomAuthForm,
        template_name='registration/login.html'
    ), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # User Management
    path('my-account/', login_required(views.my_account), name='my_account'),
    path('profile/<str:email>/', views.user_profile, name='user_profile'),

    # Payment Flow
    path('pay/<int:product_id>/', login_required(views.initiate_payment), name='initiate_payment'),
    path('pay/<int:product_id>/process/', login_required(views.process_payment), name='process_payment'),
    path('payment/success/<int:transaction_id>/', login_required(views.payment_success), name='payment_success'),

    # Transactions
    path('transactions/<int:transaction_id>/', login_required(views.transaction_detail), name='transaction_detail'),
    path('transactions/<int:transaction_id>/confirm/', login_required(views.confirm_delivery), name='confirm_delivery'),

    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Farmer Routes
    path('farmer/', include([
        path('dashboard/', login_required(views.farmer_dashboard), name='farmer_dashboard'),
        path('profile/edit/', login_required(views.farmer_edit_profile), name='farmer_edit_profile'),
        path('products/add/', login_required(views.add_product), name='farmer_add_product'),
        path('products/edit/<int:pk>/', login_required(views.edit_product), name='farmer_edit_product'),
        path('orders/<int:transaction_id>/ship/', login_required(views.mark_as_shipped), name='mark_as_shipped'),
    ])),

    # Supplier Routes
    path('supplier/', include([
        path('dashboard/', login_required(views.supplier_dashboard), name='supplier_dashboard'),
        path('profile/edit/', login_required(views.supplier_edit_profile), name='supplier_edit_profile'),
        path('products/add/', login_required(views.add_product), name='supplier_add_product'),
        path('products/edit/<int:pk>/', login_required(views.edit_product), name='supplier_edit_product'),
        path('orders/<int:transaction_id>/update/', login_required(views.update_order_status), name='update_order_status'),
    ])),

    # Custom Admin Dashboard
    #path('custom-admin/dashboard/', login_required(views.admin_dashboard), name='admin_dashboard'),

    path('custom-admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('custom-admin/users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
    path('custom-admin/moderate-product/<int:product_id>/', views.moderate_product, name='moderate_product'),
    path('custom-admin/users/<int:user_id>/', views.user_detail, name='user_detail'),

    # Default Django Admin
    path('admin/', admin.site.urls),
    #logistics dashboard
    path('logistics/', include([
    path('dashboard/', login_required(views.logistics_dashboard), name='logistics_dashboard'),
    path('profile/edit/', login_required(views.logistics_edit_profile), name='logistics_edit_profile'),
    path('jobs/<int:job_id>/accept/', login_required(views.accept_job), name='accept_job'),
    path('jobs/<int:job_id>/complete/', login_required(views.complete_job), name='complete_job'),
    ])),  
    # Buyer Routes
    path('buyer/', include([
        path('dashboard/', login_required(views.buyer_dashboard), name='buyer_dashboard'),
        path('profile/edit/', login_required(views.buyer_edit_profile), name='buyer_edit_profile'),
        path('wishlist/toggle/<int:product_id>/', login_required(views.toggle_wishlist), name='toggle_wishlist'),
        path('wishlist/', views.wishlist_view, name='wishlist_view'),
        path('orders/<int:order_id>/', login_required(views.order_detail), name='order_detail'),
        path('orders/<int:order_id>/cancel/', login_required(views.cancel_order), name='cancel_order'),
        path('orders/', views.order_history, name='order_history'),
        path('orders/<int:transaction_id>/confirm-delivery/', login_required(views.confirm_delivery), name='confirm_delivery'),
        path('wallet/add-funds/', login_required(views.add_funds), name='add_funds'),
        path('addresses/', login_required(views.manage_addresses), name='manage_addresses'),
        path('support/ticket/', login_required(views.create_support_ticket), name='create_support_ticket'),
        ])),
    path('notifications/', views.get_notifications, name='get_notifications'),


    # Wallet System
    path('wallet/topup/', login_required(views.wallet_topup), name='wallet_topup'),

    # Static Pages
    path('about/', views.about_us, name='about_us'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('help/', views.help_center, name='help'),
    path('contact/', views.contact_support, name='contact'),
    path('resources/', views.farming_resources, name='resources'),
    
    # Utilities
    path("currency-converter/", currency_converter, name="currency_converter"),    
    
    # Blog
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact_us, name='contact'),
    path('export-pdf/', login_required(views.export_pdf), name='export_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)