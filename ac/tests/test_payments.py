# ac/tests/test_payments.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from ac.models import Product, EscrowTransaction

User = get_user_model()

class PaymentTests(TestCase):
    def setUp(self):
        # Create test farmer
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            phone='+251911111111',
            password='testpass123',
            user_type='FARMER',
            wallet_balance=Decimal('1000.00')
        )
        
        # Create test buyer
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            phone='+251922222222',
            password='testpass123',
            user_type='BUYER',
            wallet_balance=Decimal('500.00')
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Coffee',
            price=Decimal('150.00'),
            seller=self.farmer,
            stock_quantity=10
        )

    def test_full_payment_flow(self):
        # Test initial balances
        self.assertEqual(self.buyer.wallet_balance, Decimal('500.00'))
        
        # Simulate payment initiation
        self.buyer.deduct_wallet(self.product.price)
        self.buyer.refresh_from_db()
        
        # Verify deduction
        self.assertEqual(self.buyer.wallet_balance, Decimal('350.00'))
        
        # Create transaction
        transaction = EscrowTransaction.objects.create(
            buyer=self.buyer,
            seller=self.farmer,
            product=self.product,
            amount=self.product.price,
            status='held'
        )
        
        # Complete transaction
        transaction.status = 'completed'
        transaction.save()
        self.farmer.add_wallet(transaction.amount)
        self.farmer.refresh_from_db()
        
        # Verify final balances
        self.assertEqual(self.farmer.wallet_balance, Decimal('1150.00'))
        self.assertEqual(transaction.status, 'completed')