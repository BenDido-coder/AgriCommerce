from django.db.models.signals import post_save
from django.dispatch import receiver
from ac.forms import User
from .models import EscrowTransaction, FarmerProfile, Notification

@receiver(post_save, sender=EscrowTransaction)
def handle_transaction_update(sender, instance, created, **kwargs):
    print(f"""
    [AUDIT] Transaction {instance.id}
    Status: {instance.status}
    Amount: {instance.amount}
    Buyer: {instance.buyer}
    Seller: {instance.seller}
    """)

    # Add notification creation
    Notification.objects.create(
        user=instance.buyer,
        message=f"Transaction #{instance.id} updated to {instance.status}"
    )
    Notification.objects.create(
        user=instance.seller,
        message=f"Transaction #{instance.id} updated to {instance.status}"
    )
@receiver(post_save, sender=User)
def create_farmer_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'FARMER':
        FarmerProfile.objects.create(user=instance)