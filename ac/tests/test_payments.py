from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..models import Product, EscrowTransaction

User = get_user_model()

class PaymentTests(TestCase):
    def setUp(self):
        self.farmer = User.objects.create_user(
            email='farmer@test.com',
            phone='+251911111111',
            user_type='FARMER',
            password='testpass',
            wallet_balance=Decimal('1000.00')
        )
        
        self.buyer = User.objects.create_user(
            email='buyer@test.com',
            phone='+251922222222',
            user_type='BUYER',
            password='testpass',
            wallet_balance=Decimal('500.00')
        )
        
        self.product = Product.objects.create(
            name='Test Coffee',
            price=Decimal('150.00'),
            seller=self.farmer,
            stock_quantity=10
        )

    def test_payment_flow(self):
        # Test initial balances
        self.assertEqual(self.buyer.wallet_balance, Decimal('500.00'))
        
        # Deduct wallet
        self.buyer.deduct_wallet(self.product.price)
        self.buyer.refresh_from_db()
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
        
        # Verify final state
        self.assertEqual(self.farmer.wallet_balance, Decimal('1150.00'))
        self.assertEqual(transaction.status, 'completed')
        
def test_product_listing_flow(self):
    # Farmer adds product
    self.client.force_login(self.farmer)
    response = self.client.post('/farmer/add-product/', {
        'name': 'Test Maize',
        'price': '200.00',
        'category': 'CROP',
        'stock_quantity': '50'
    })
    self.assertEqual(response.status_code, 302)
    
    # Buyer views products
    self.client.force_login(self.buyer)
    response = self.client.get('/products/')
    self.assertContains(response, 'Test Maize')
    self.assertContains(response, 'Buy Now')