from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
   
    username = None
    email = models.EmailField(unique=True)
    
    phone_number = models.CharField(max_length=15)
    role = models.CharField(max_length=20, choices=[
        ('farmer', 'Farmer/Producer'),
        ('buyer', 'Buyer/Retailer'),
        ('supplier', 'Supplier'),
        ('logistics', 'Logistics'),
        ('admin', ''),
        
    ])
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number', 'role']
    
    
    objects = CustomUserManager()

from django.db import models
from django.conf import settings

class Product(models.Model):
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=[
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains'),
        ('dairy', 'Dairy'),
        ('poultry', 'Poultry'),
        ('herbs&spices', 'Herbs & Spices')
    ])
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, choices=[
        ('kg', 'Kilogram (kg)'),
        ('g', 'Gram (g)'),
        ('lb', 'Pound (lb)'),
        ('oz', 'Ounce (oz)'),
        ('piece', 'Piece'),
        ('dozen', 'Dozen'),
        ('liter', 'Liter'),
    ])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name


