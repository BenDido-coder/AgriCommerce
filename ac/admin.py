from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, FarmerProfile, Product,
    EscrowTransaction, TransactionUpdate
)
from .forms import CustomUserCreationForm

# Unregister the default User model if already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('email', 'phone', 'first_name', 'last_name', 'user_type', 'is_staff')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Financial', {'fields': ('wallet_balance',)}),
        ('Role Info', {'fields': ('user_type',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'farm_name', 'location')
    search_fields = ('farm_name', 'location', 'user__email')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'seller__email', 'category')


@admin.register(EscrowTransaction)
class EscrowTransactionAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'seller', 'status', 'amount')
    list_filter = ('status',)
    search_fields = ('buyer__email', 'seller__email')


@admin.register(TransactionUpdate)
class TransactionUpdateAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('transaction__id', 'created_by__email')
