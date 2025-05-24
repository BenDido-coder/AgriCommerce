# forms.py - Fixed Version
from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ( BuyerProfile, DeliveryJob, FarmerProfile, LogisticsProfile,
 SupplierProfile, Product, SupportAttachment, SupportTicket)
from django.db.models import Q
from .widgets import MultipleFileInput  # Import at the top of the file

User = get_user_model()

# --- Authentication Forms ---
class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(label='Email or Phone')

    def clean_username(self):
        identifier = self.cleaned_data['username']
        if not User.objects.filter(Q(email=identifier) | Q(phone=identifier)).exists():
            raise forms.ValidationError("Invalid credentials")
        return identifier

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^(\+251[79]\d{8}|0[79]\d{8})$',
            message="Phone must be Ethiopian format: +2517XXXXXXXX, +2519XXXXXXXX, 07XXXXXXXX, or 09XXXXXXXX"

        )]
    )
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)

    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'last_name', 'user_type', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
    def clean_phone(self):
        phone = self.cleaned_data['phone']
    # Convert local format to international
        if phone.startswith('0'):
            return '+251' + phone[1:]
        return phone
    


# --- Profile Forms ---
class UserForm(forms.ModelForm):  # ADDED MISSING FORM
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'user_type']

class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = ['farm_name', 'location', 'certification', 'profile_photo']


class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = SupplierProfile
        fields = ['company_name', 'location', 'profile_photo']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location':     forms.TextInput(attrs={'class': 'form-control'}),
        }
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'stock_quantity', 
                  'harvest_date', 'expiry_date']
        labels = {
            'harvest_date': "Harvest Date",
            'expiry_date': "Expiry Date"
        }
        widgets = {
            'harvest_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'expiry_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            )
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Set self.user explicitly
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Set category choices
            self.fields['category'].choices = Product.get_category_choices(self.user.user_type)
            
            # Handle date fields
            if self.user.user_type == 'FARMER':
                del self.fields['expiry_date']
            else:
                del self.fields['harvest_date']

    def clean(self):
        cleaned_data = super().clean()
        if self.user:  # Ensure self.user is used correctly
            self.instance.seller = self.user
        return cleaned_data
    
# --- currency converter ---
CURRENCY_CHOICES = [
    ('ETB', 'ETB - Ethiopian Birr'),
    ('USD', 'USD - US Dollar'),
    ('EUR', 'EUR - Euro'),
    ('KES', 'KES - Kenyan Shilling'),
]

class CurrencyConvertForm(forms.Form):
    amount = forms.FloatField(min_value=0, label="Amount", widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter amount'
    }))
    from_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    to_currency = forms.ChoiceField(choices=CURRENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

class LogisticsProfileForm(forms.ModelForm):
    class Meta:
        model = LogisticsProfile
        fields = ['vehicle_type', 'license_plate', 'service_areas', 'profile_photo']
        widgets = {
            'service_areas': forms.TextInput(attrs={'placeholder': 'Comma-separated regions'})
        }

class JobCompletionForm(forms.ModelForm):
    class Meta:
        model = DeliveryJob
        fields = ['delivery_proof']

class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['primary_address', 'newsletter_optin']
        widgets = {
            'primary_address': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your primary delivery address'
            })
        }

class AddFundsForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=100,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Minimum 100 ETB'
        })
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('TELEBIRR', 'Telebirr'),
            ('CBE', 'CBE Birr'),
            ('BANK', 'Bank Transfer')
        ],
        widget=forms.RadioSelect
    )
    
class DeliveryConfirmationForm(forms.Form):
    delivery_proof = forms.FileField(
        label='Upload Delivery Proof (Optional)',
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*, .pdf'})
    )
    confirm = forms.BooleanField(
        required=True,
        label="I confirm that the products have been delivered in good condition"
    )

class SupportTicketForm(forms.ModelForm):
    attachments = forms.FileField(
        widget=MultipleFileInput(attrs={'multiple': True}),  # Use MultipleFileInput here
        required=False,
        label='Attachments (max 5 files)'
    )

    class Meta:
        model = SupportTicket
        fields = ['subject', 'message']

    def clean_attachments(self):
        attachments = self.files.getlist('attachments')
        if len(attachments) > 5:
            raise forms.ValidationError("Maximum 5 files allowed")
        
        valid_types = ['image/jpeg', 'image/png', 'application/pdf']
        for f in attachments:
            if f.content_type not in valid_types:
                raise forms.ValidationError(
                    f"Invalid file type: {f.name}. Only PDF and images(png, jpeg) are allowed."
                )
        return attachments
    
    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            for f in self.files.getlist('attachments'):
                SupportAttachment.objects.create(
                    file=f,
                    ticket=instance
                )
        return instance
    


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your full name'})
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    subject = forms.CharField(
        label="Subject",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'})
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your message here...'})
    )
