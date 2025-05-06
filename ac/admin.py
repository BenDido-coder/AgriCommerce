# ac/admin.py
from django.contrib import admin
from .models import User, FarmerProfile, Product, EscrowTransaction, TransactionUpdate
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm
from django.utils.html import format_html
# Unregister if already registered (safe guard)
if admin.site.is_registered(User):
    admin.site.unregister(User)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone', 'role', 'whatsapp_link')
    
    def whatsapp_link(self, obj):
        return format_html(
            '<a class="button" href="https://wa.me/{}?text=Hello%20{}%20(AgriCommerce%20Admin)" target="_blank">WhatsApp</a>',
            obj.phone, obj.username
        )
    whatsapp_link.short_description = 'Contact'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Financial', {'fields': ('wallet_balance',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'role', 'password1', 'password2'),
        }),
    )

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'location')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price', 'stock_quantity')

@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'seller', 'product', 'status', 'auto_release_date')

@admin.register(TransactionUpdate)
class TransactionUpdateAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'created_by', 'is_read', 'created_at')



