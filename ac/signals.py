# ac/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EscrowTransaction

@receiver(post_save, sender=EscrowTransaction)
def log_transaction(sender, instance, **kwargs):
    print(f"""
    [AUDIT] Transaction {instance.id}
    Status: {instance.status}
    Amount: {instance.amount}
    Buyer: {instance.buyer}
    Seller: {instance.seller}
    """)