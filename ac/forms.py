from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

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