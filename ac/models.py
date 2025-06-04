from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta


def default_auto_release_date():
    return timezone.now() + timedelta(days=7)

@property
def display_name(self):
    if self.first_name and self.last_name:
        return f"{self.first_name} {self.last_name}"
    return self.email

class UserManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not phone:
            raise ValueError('Users must have a phone number')

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        return self.create_user(email, phone, password, **extra_fields)

class User(AbstractUser):
    class Meta:
        db_table = 'ac_user'
        
    USER_TYPE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('SUPPLIER', 'Supplier/Distributor'),
        ('BUYER', 'Buyer'),
        ('LOGISTICS', 'Logistics'),
        ('ADMIN', 'Admin'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^(\+251[79]\d{8}|0[79]\d{8})$',
            message="Phone must be Ethiopian format: +2517XXXXXXXX, +2519XXXXXXXX, 07XXXXXXXX, or 09XXXXXXXX"
        )],
        unique=True
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='BUYER')
    wallet_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        db_index=True,
        help_text="Updated via F() expressions only!"
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = UserManager()
    def __str__(self):
        return f"{self.email} ({self.get_user_type_display()})"
    
    def deduct_wallet(self, amount):
        if self.wallet_balance >= Decimal(amount):
            self.wallet_balance -= Decimal(amount)
            self.save(update_fields=['wallet_balance'])
            return True
        return False
    def add_wallet(self, amount):
        from django.db.models import F
        updated = User.objects.filter(pk=self.pk).update(
        wallet_balance=F('wallet_balance') + Decimal(amount)
        )
        self.refresh_from_db()  # Force reload from database
        return updated > 0

    def can_list_products(self):
        return self.user_type in ['FARMER', 'SUPPLIER']
    @property
    def is_logistics(self):
        return self.user_type == 'LOGISTICS'
    @property
    def is_farmer(self):
        return self.user_type == 'FARMER'
    
    @property
    def is_supplier(self):
        return self.user_type == 'SUPPLIER'
    
    @property
    def is_buyer(self):
        return self.user_type == 'BUYER'
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ORDER', 'Order Update'),
        ('PAYMENT', 'Payment'),
        ('DELIVERY', 'Delivery'),
        ('SYSTEM', 'System')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    related_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_job = models.ForeignKey(
        'DeliveryJob',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    @property
    def icon(self):
        icons = {
            'ORDER': 'shopping-cart',
            'PAYMENT': 'money-bill-wave',
            'DELIVERY': 'truck',
            'SYSTEM': 'info-circle'
        }
        return icons.get(self.notification_type, 'bell')
    
    @property
    def type(self):
        types = {
            'ORDER': 'primary',
            'PAYMENT': 'success',
            'DELIVERY': 'info',
            'SYSTEM': 'warning'
        }
        return types.get(self.notification_type, 'secondary')
    
    class Meta:
        ordering = ['-created_at']

class FarmerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='farmer_profile',
        limit_choices_to={'user_type': 'FARMER'}
    )
    farm_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    certification = models.FileField(upload_to='certifications/', null=True, blank=True)
    profile_photo = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default='avatars/default_avatar.png'
    )
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def clean(self):
        if self.user.user_type != 'FARMER':
            raise ValidationError("User must be a farmer")





class SupplierProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='supplier_profile',
        limit_choices_to={'user_type': 'SUPPLIER'},
    )
    company_name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    profile_photo = models.ImageField(
        upload_to='supplier_avatars/',
        blank=True,
        null=True,
        default='avatars/default_avatar.png'
    )
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.company_name} ({self.user.email})"


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True)  # For font icons
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Category types
    FARMER = 'FARMER'
    SUPPLIER = 'SUPPLIER'
    TYPE_CHOICES = [
        (FARMER, 'Farmer Product'),
        (SUPPLIER, 'Supplier Product'),
    ]
    category_type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default=FARMER
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Product Categories"
        ordering = ['name']


class Product(models.Model):
    # Category Constants
    FARMER_CATEGORIES = ['CROP', 'VEGETABLES', 'FRUITS', 'DAIRY', 'POULTRY', 'LIVESTOCK', 'OTHER']
    SUPPLIER_CATEGORIES = ['EQUIPMENT', 'SEEDS', 'FERTILIZER', 'OTHER']  # Added OTHER for suppliers
    
    # Unified category choices
    CATEGORY_CHOICES = [
        ('CROP', 'Crops'),
        ('VEGETABLES', 'Vegetables'),
        ('FRUITS', 'Fruits'),
        ('DAIRY', 'Dairy'),
        ('POULTRY', 'Poultry'),
        ('LIVESTOCK', 'Livestock'),
        ('EQUIPMENT', 'Equipment'),
        ('SEEDS', 'Seeds'),
        ('FERTILIZER', 'Fertilizer'),
        ('OTHER', 'Other'),
    ]
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    @classmethod
    def get_category_choices(cls, user_type):
        """Returns filtered choices based on user type"""
        if user_type == 'FARMER':
            return [c for c in cls.CATEGORY_CHOICES if c[0] in cls.FARMER_CATEGORIES]
        elif user_type == 'SUPPLIER':
            return [c for c in cls.CATEGORY_CHOICES if c[0] in cls.SUPPLIER_CATEGORIES]
        return cls.CATEGORY_CHOICES

    # Fields
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
        limit_choices_to={'user_type__in': ['FARMER', 'SUPPLIER']}
    )
    image = models.ImageField(upload_to='products/', default='default_product.png')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='CROP',
        help_text="Farmers: Agricultural products | Suppliers: Equipment/Supplies"
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    harvest_date = models.DateField(
        null=True, 
        blank=True,
        help_text="For agricultural products (Farmers only)"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="For perishable items (Suppliers only)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # Add this field
    is_active = models.BooleanField(default=True)  # Add this field
    def clean(self):
        """Extended validation"""
        # Ensure seller exists and is valid
        if not hasattr(self, 'seller') or self.seller.user_type not in ['FARMER', 'SUPPLIER']:
            raise ValidationError("Invalid seller account type")

        # Category validation
        if self.seller.user_type == 'FARMER':
            if self.category not in self.FARMER_CATEGORIES:
                raise ValidationError(
                    f"Farmers can only list: {', '.join(self.FARMER_CATEGORIES)}"
                )
            if self.expiry_date:
                raise ValidationError("Farmers should use harvest date, not expiry date")
                
        elif self.seller.user_type == 'SUPPLIER':
            if self.category not in self.SUPPLIER_CATEGORIES:
                raise ValidationError(
                    f"Suppliers can only list: {', '.join(self.SUPPLIER_CATEGORIES)}"
                )
            if self.harvest_date:
                raise ValidationError("Suppliers should use expiry date, not harvest date")

        # Validate price and stock
        if self.price <= Decimal('0'):
            raise ValidationError("Price must be greater than 0")
        if self.stock_quantity < 0:
            raise ValidationError("Stock quantity cannot be negative")

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
class EscrowTransaction(models.Model):
    STATUS_CHOICES = [
        ('held', 'Funds Held'),
        ('shipped', 'Product Shipped'),
        ('completed', 'Transaction Completed'),
        ('disputed', 'Dispute Raised'),
        ('cancelled', 'Cancelled'),
    ]
    PLATFORM_FEE_PERCENT = Decimal('0.025')

    buyer = models.ForeignKey(User, related_name='purchases', on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='sales', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='held')
    telebirr_reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    auto_release_date = models.DateTimeField(default=default_auto_release_date)  # Use the function
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    buyer_confirmed = models.BooleanField(default=False)
    delivery_confirmed_at = models.DateTimeField(null=True, blank=True)
    delivery_proof = models.FileField(upload_to='delivery_proofs/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            # Calculate platform fee (2.5% of the amount)
            self.platform_fee = (self.amount * self.PLATFORM_FEE_PERCENT).quantize(Decimal('0.00'))
            
            # Calculate total charge to buyer (amount + fee)
            total_charge = self.amount + self.platform_fee

            # Verify buyer balance
            if self.buyer.wallet_balance < total_charge:
                raise ValidationError("Insufficient funds in buyer's wallet")

            # Deduct from buyer's wallet
            self.buyer.wallet_balance -= total_charge
            self.buyer.save(update_fields=['wallet_balance'])

            # Create payment notification
            Notification.objects.create(
                user=self.buyer,
                message=f"Payment processed: {total_charge} ETB deducted for {self.product.name}",
                notification_type='PAYMENT',
                related_url=f"/transactions/{self.pk}/"
            )

        super().save(*args, **kwargs)

    def clean(self):
        # Ensure buyer and seller are not the same
        if self.buyer == self.seller:
            raise ValidationError("Buyer and seller cannot be the same")

        # Ensure the amount matches the product price multiplied by quantity
        expected_amount = self.product.price * self.quantity
        if self.amount != expected_amount:
            raise ValidationError(f"Amount mismatch: Expected {expected_amount} ETB, got {self.amount} ETB")

    def __str__(self):
        return f"Transaction #{self.pk} - {self.product.name} ({self.get_status_display()})"
    
class TransactionUpdate(models.Model):
    transaction = models.ForeignKey(EscrowTransaction, on_delete=models.CASCADE, related_name='updates')
    message = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'user_type__in': ['ADMIN', 'LOGISTICS']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
#logistics provider model
ETHIOPIAN_CITIES = [
    ('ADDIS_ABABA', 'Addis Ababa'),
    ('DIRE_DAWA', 'Dire Dawa'),
    ('BAHIR_DAR', 'Bahir Dar'),
    ('MEKELLE', 'Mekelle'),
    ('AWASA', 'Awasa'),
    ('JIMMA', 'Jimma'),
    ('GONDAR', 'Gondar'),
    ('NAZRET', 'Nazret'),
    ('DEBRE_MARKOS', 'Debre Markos'),
    ('ARBA_MINCH', 'Arba Minch'),
]

class City(models.Model):
    name = models.CharField(max_length=50, choices=ETHIOPIAN_CITIES, unique=True)
    
    def __str__(self):
        return self.name
    
class LogisticsProfile(models.Model):
    VEHICLE_TYPES = [
        ('TRUCK', 'Truck'),
        ('VAN', 'Van'),
        ('BIKE', 'Motorcycle'),
        ('COLD_CHAIN', 'Refrigerated Truck'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='logisticsprofile')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='TRUCK')
    license_plate = models.CharField(max_length=20, default='N/A')
    service_areas = models.ManyToManyField('City', help_text="Select cities you service (select Nationwide for all areas)", related_name='logistics_providers')
    nationwide = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='logistics/profile/', null=True)
    completed_jobs = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)
    price_per_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        default=10.00,
        help_text="Price per kilometer in ETB"
        )

# Add to Product model (if not exists)
    pickup_location = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        default=10.00,
        help_text="Price per kilometer in ETB"
)
    def service_areas_list(self):
        if self.nationwide:
            return ["Nationwide"]
        return [area.strip() for area in self.service_areas.split(',')]

# Add to Order model (create if not exists)
class Order(models.Model):
    logistics = models.ForeignKey(
        User, 
        null=True, 
        blank=True,
        on_delete=models.SET_NULL
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1) 
    logistics = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='logistics_orders'  # Add this
    )
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class DeliveryJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('IN_TRANSIT', 'In Transit'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    
    provider = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='jobs', on_delete=models.CASCADE)
    pickup_location = models.TextField()
    dropoff_location = models.TextField()
    pickup_time = models.DateTimeField(default=timezone.now, help_text="Estimated pickup time")
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    delivery_proof = models.FileField(upload_to='delivery_proofs/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    job = models.OneToOneField(DeliveryJob, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# Buyer dashboard
class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    primary_address = models.TextField(blank=True, default='Address not specified')  # Made optional
    saved_suppliers = models.ManyToManyField(User, related_name='followers')
    newsletter_optin = models.BooleanField(default=True)
    delivery_city = models.ForeignKey(
    'City',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    verbose_name="Primary Delivery City"
   )
    def __str__(self):
        return f"Buyer Profile - {self.user.email}"

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)

class SupportAttachment(models.Model):
    file = models.FileField(upload_to='support_tickets/')
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('ESCROW_HOLD', 'Escrow Hold'),
        ('ESCROW_RELEASE', 'Escrow Release'),
        ('REFUND', 'Refund'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    related_transaction = models.ForeignKey(  # Add this field
        EscrowTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"

class WalletTopupRequest(models.Model):
    PAYMENT_METHODS = [
        ('BANK', 'Bank Transfer'),
        ('TELEBIRR', 'Telebirr'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    screenshot = models.FileField(upload_to='topup_screenshots/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.amount} ETB"
    
    def save(self, *args, **kwargs):
        """Automatically add funds on creation"""
        if not self.pk:  # Only on first save
            self.user.add_wallet(self.amount)
            WalletTransaction.objects.create(
                user=self.user,
                amount=self.amount,
                transaction_type='DEPOSIT'
            )
        super().save(*args, **kwargs)