from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag
def get_dashboard_url(user):
    if not user.is_authenticated:
        return reverse('login')  # Or any public fallback

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
    return reverse('my_account')  # Fallback
