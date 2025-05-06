from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import Product

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.role:  # Default role for superusers
            user.role = 'ADMIN'
        if commit:
            user.save()
        return user
    

    # ac/forms.py
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock_quantity', 'harvest_date']
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }