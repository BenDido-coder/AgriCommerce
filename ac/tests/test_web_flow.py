from django.test import TestCase, Client
from django.urls import reverse
from ac.models import EscrowTransaction, User, Product

class WebFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.farmer = User.objects.create_user(
            email='testfarmer@agri.com',
            phone='+251911111112',
            user_type='FARMER',
            password='testpass'
        )
        self.buyer = User.objects.create_user(
            email='testbuyer@agri.com',
            phone='+251911111113',
            user_type='BUYER',
            password='testpass',
            wallet_balance=1000.00
        )
        self.product = Product.objects.create(
            name='Test Maize',
            price=200.00,
            seller=self.farmer,
            stock_quantity=50
        )

    def test_full_purchase_flow(self):
        # Login as buyer
        self.client.login(email='testbuyer@agri.com', password='testpass')
        
        # Initiate payment
        response = self.client.post(
            reverse('initiate_payment', args=[self.product.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect to transaction
        
        # Verify transaction
        transaction = EscrowTransaction.objects.first()
        self.assertEqual(transaction.status, 'held')
        
        # Confirm delivery
        self.client.post(
            reverse('confirm_delivery', args=[transaction.id])
        )
        transaction.refresh_from_db()
        self.assertEqual(transaction.status, 'completed')