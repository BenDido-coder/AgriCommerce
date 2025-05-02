from django.http import HttpResponseForbidden
from .models import EscrowTransaction

class TransactionAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'transaction_id' in view_kwargs:
            try:
                transaction = EscrowTransaction.objects.get(pk=view_kwargs['transaction_id'])
                if request.user not in [transaction.buyer, transaction.seller]:
                    return HttpResponseForbidden()
            except EscrowTransaction.DoesNotExist:
                pass
        return None