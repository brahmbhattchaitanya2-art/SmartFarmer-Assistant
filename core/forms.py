from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class FarmerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    
    phone_number = forms.CharField(max_length=15, required=True, label="Mobile Number (10 digits)")
    village = forms.CharField(max_length=100, required=True, label="Village Name")
    district = forms.CharField(max_length=100, required=True, label="District")
    state = forms.ChoiceField(choices=UserProfile.STATE_CHOICES, required=True, label="State")
    land_size = forms.DecimalField(max_digits=6, decimal_places=2, required=True, label="Land Size (in Acres)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Simple Indian mobile number validation (starts with 6-9, 10 digits)
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if len(clean_phone) != 10 or not clean_phone[0] in '6789':
            raise forms.ValidationError("Please enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
        return clean_phone

    def clean_land_size(self):
        land_size = self.cleaned_data.get('land_size')
        if land_size <= 0:
            raise forms.ValidationError("Land size must be a positive number of acres.")
        return land_size

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                village=self.cleaned_data['village'],
                district=self.cleaned_data['district'],
                state=self.cleaned_data['state'],
                primary_crop="Not Specified",
                land_size=self.cleaned_data['land_size']
            )
        return user


class UserForm(forms.ModelForm):
    """Form to edit basic User model fields."""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserProfileForm(forms.ModelForm):
    """Form to edit custom UserProfile fields."""
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'village', 'district', 'state', 'primary_crop', 'land_size']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        clean_phone = ''.join(filter(str.isdigit, phone_number))
        if len(clean_phone) != 10 or not clean_phone[0] in '6789':
            raise forms.ValidationError("Please enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
        return clean_phone

    def clean_land_size(self):
        land_size = self.cleaned_data.get('land_size')
        if land_size <= 0:
            raise forms.ValidationError("Land size must be a positive number of acres.")
        return land_size


class FertilizerForm(forms.Form):
    CROP_CHOICES = [
        ('Cotton', 'Cotton (કપાસ)'),
        ('Wheat', 'Wheat (ઘઉં)'),
        ('Groundnut', 'Groundnut (મગફળી)'),
        ('Maize', 'Maize (મકાઈ)'),
        ('Bajra', 'Bajra (બાજરી)'),
        ('Castor', 'Castor (દિવેલા)'),
        ('Cumin', 'Cumin (જીરું)'),
        ('Mustard', 'Mustard (રાઈ)'),
    ]

    SOIL_CHOICES = [
        ('Black Soil', 'Black Soil (કાળી જમીન)'),
        ('Sandy Soil', 'Sandy Soil (રેતાળ જમીન)'),
        ('Alluvial Soil', 'Alluvial Soil (કાંપવાળી જમીન)'),
        ('Red Soil', 'Red Soil (લાલ જમીન)'),
    ]

    STAGE_CHOICES = [
        ('Sowing/Basal', 'Sowing / Basal Stage (વાવણી / પાયાનો તબક્કો)'),
        ('Vegetative', 'Vegetative Growth (વાનસ્પતિક વૃદ્ધિ)'),
        ('Flowering/Fruiting', 'Flowering / Fruiting (ફૂલ / ફળ બેસવાનો તબક્કો)'),
    ]

    crop_name = forms.ChoiceField(choices=CROP_CHOICES, label="Crop Name")
    soil_type = forms.ChoiceField(choices=SOIL_CHOICES, label="Soil Type")
    crop_stage = forms.ChoiceField(choices=STAGE_CHOICES, label="Crop Stage")
