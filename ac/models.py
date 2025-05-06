from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError

class User(AbstractUser):
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('SUPPLIER', 'Supplier/Distributor'),
        ('BUYER', 'Buyer'),
        ('LOGISTICS', 'Logistics'),
        ('ADMIN', 'Admin'),
    ]
    
    # Fixed role field with proper choices reference
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='BUYER'
    )

    # Phone field with validation
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be in international format. E.g.: +251912345678"
        )],
        unique=True,
        blank=True,
        null=True
    )

    # Wallet balance
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )

    # Remove duplicate role field and fix commented sections
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name="ac_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name="ac_user_permissions",
        related_query_name="user",
    )

    # Wallet methods
    def deduct_wallet(self, amount):
        if isinstance(amount, float):
            amount = Decimal(str(amount))
        if self.wallet_balance >= amount:
            self.wallet_balance -= amount
            self.save(update_fields=['wallet_balance'])
            return True
        return False

    def add_wallet(self, amount):
        if isinstance(amount, float):
            amount = Decimal(str(amount))
        if amount > Decimal('0'):
            self.wallet_balance += amount
            self.save(update_fields=['wallet_balance'])
            return True
        return False

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def is_admin_user(self):
        return self.role == 'ADMIN' or self.is_superuser

class FarmerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='farmer_profile',
        limit_choices_to={'role': 'FARMER'}
    )
    farm_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    certification = models.FileField(upload_to='certifications/', null=True, blank=True)
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.farm_name} ({self.location})"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('CROP', 'Crops'),
        ('LIVESTOCK', 'Livestock'),
        ('EQUIPMENT', 'Equipment'),
        ('SEEDS', 'Seeds'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'role__in': ['FARMER', 'SUPPLIER']}
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='CROP')
    stock_quantity = models.PositiveIntegerField(default=0)
    harvest_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

def default_auto_release_date():
    return timezone.now() + timezone.timedelta(days=7)

class EscrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('held', 'Funds Held'),
        ('shipped', 'Product Shipped'),
        ('completed', 'Transaction Completed'),
        ('disputed', 'Dispute Raised'),
        ('cancelled', 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(
        User,
        related_name='purchases',
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['BUYER', 'LOGISTICS']}
    )
    seller = models.ForeignKey(
        User,
        related_name='sales',
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['FARMER', 'SUPPLIER']}
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='held')
    telebirr_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    auto_release_date = models.DateTimeField(default=default_auto_release_date)

    def total_amount(self):
        return self.amount * self.quantity
    
    class Meta:
        ordering = ['-created_at']
        
    def clean(self):
        if self.buyer == self.seller:
            raise ValidationError("Buyer and seller cannot be the same")
        if self.amount <= 0:
            raise ValidationError("Amount must be positive")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class TransactionUpdate(models.Model):
    transaction = models.ForeignKey(EscrowTransaction, on_delete=models.CASCADE, related_name='updates')
    message = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['ADMIN', 'LOGISTICS']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']