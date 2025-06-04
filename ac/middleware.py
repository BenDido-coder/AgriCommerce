from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

from ac.forms import User
from .models import EscrowTransaction

# Middleware to restrict access to certain views based on user type
class TransactionAccessMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'transaction_id' in view_kwargs:
            try:
                transaction = EscrowTransaction.objects.get(pk=view_kwargs['transaction_id'])
                if request.user not in [transaction.buyer, transaction.seller]:
                    return HttpResponseForbidden("Access denied: Not transaction participant")
            except EscrowTransaction.DoesNotExist:
                pass

class ProductListingMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        protected_views = ['add_product', 'edit_product']
        if view_func.__name__ in protected_views:
            if not request.user.is_authenticated or not request.user.can_list_products():
                return HttpResponseForbidden("Product listing requires farmer/supplier account")
class RefreshUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Get fresh user with wallet balance
                request.user = User.objects.only(
                    'id', 'email', 'wallet_balance'
                ).get(pk=request.user.pk)
            except User.DoesNotExist:
                pass
        return self.get_response(request)