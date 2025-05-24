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
    list_display = ('user', 'farm_name', 'location', 'profile_photo')
    search_fields = ('farm_name', 'location', 'user__email')
    raw_id_fields = ('user',)  # Better for performance
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(user_type='FARMER')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    readonly_fields = ('seller',)  # Prevent seller changes after creation
    list_display = ('name', 'seller', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('name', 'seller__email', 'category')

    def save_model(self, request, obj, form, change):
        """Auto-set seller to current user in admin"""
        if not change:  # Only on creation
            obj.seller = request.user
        super().save_model(request, obj, form, change)
        
#admin.site.register(Product, ProductAdmin)
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


# ac/admin.py
from django.contrib import admin
from .models import (
    User, FarmerProfile, SupplierProfile,
    LogisticsProfile, BuyerProfile, SupportTicket
)
@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(LogisticsProfile)
class LogisticsProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ('saved_suppliers',)

from django.contrib import admin
from .models import SupportTicket, SupportAttachment

class SupportAttachmentInline(admin.TabularInline):
    model = SupportAttachment
    extra = 1

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('subject', 'message')
    inlines = [SupportAttachmentInline]
    readonly_fields = ('created_at',)

admin.site.register(SupportAttachment)

from .models import WalletTransaction

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_type', 'timestamp')
    list_filter = ('transaction_type',)
    search_fields = ('user__username', 'amount')