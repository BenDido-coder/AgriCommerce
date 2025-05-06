from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from ac.models import Product, EscrowTransaction

User = get_user_model()

class PaymentTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            username='test_farmer',
            phone='+251911111111',
            role='FARMER',
            wallet_balance=Decimal('1000.00')
        )
        
        self.buyer = User.objects.create_user(
            username='test_buyer',
            phone='+251922222222',
            role='BUYER',
            wallet_balance=Decimal('500.00')
        )
        
        self.product = Product.objects.create(
            name='Test Coffee',
            price=Decimal('150.00'),
            seller=self.farmer,
            stock_quantity=10
        )

    def test_payment_flow(self):
        # Explicitly deduct wallet first
        self.assertTrue(self.buyer.deduct_wallet(self.product.price))
        self.buyer.refresh_from_db()

        # Create transaction after deduction
        transaction = EscrowTransaction.objects.create(
            buyer=self.buyer,
            seller=self.farmer,
            product=self.product,
            amount=self.product.price,
            status='held'
        )

        # Verify balances using Decimal
        self.assertEqual(self.buyer.wallet_balance, Decimal('350.00'))  # 500 - 150
        self.assertEqual(self.farmer.wallet_balance, Decimal('1000.00'))

        # Complete transaction
        transaction.status = 'completed'
        transaction.save()
        self.farmer.add_wallet(transaction.amount)
        self.farmer.refresh_from_db()

        # Final verification
        self.assertEqual(self.farmer.wallet_balance, Decimal('1150.00'))
        self.assertEqual(transaction.status, 'completed')