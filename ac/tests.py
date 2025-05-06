from django.test import TestCase

# Create your tests here.
# ac/tests.py (legacy)

class LegacyTests(TestCase):
    # Keep existing tests here temporarily
    pass

# ac/tests/test_payments.py (new)
from django.test import TestCase

class PaymentTests(TestCase):
    # New payment-specific tests
    pass