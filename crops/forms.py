from django import forms
from .models import Crop

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = [
            'name', 'variety', 'sowing_date', 'expected_harvest_date',
            'land_size', 'investment_cost', 'expected_yield',
            'estimated_revenue', 'status', 'image'
        ]
        widgets = {
            'name': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'variety': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. Bt Cotton - II / GG-20'}),
            'sowing_date': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'land_size': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Acreage (e.g. 3.5)', 'step': '0.01'}),
            'investment_cost': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '₹ Sunk Investment', 'step': '0.01'}),
            'expected_yield': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Yield in Quintals', 'step': '0.01'}),
            'estimated_revenue': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '₹ Expected Revenue', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select form-control-custom'}),
            'image': forms.FileInput(attrs={'class': 'form-control form-control-custom'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        sowing_date = cleaned_data.get('sowing_date')
        expected_harvest_date = cleaned_data.get('expected_harvest_date')
        
        if sowing_date and expected_harvest_date:
            if expected_harvest_date <= sowing_date:
                raise forms.ValidationError("Expected harvest date must be after the sowing date.")
                
        # Validate positive values
        for field in ['land_size', 'investment_cost', 'expected_yield', 'estimated_revenue']:
            val = cleaned_data.get(field)
            if val is not None and val <= 0:
                self.add_error(field, f"Value must be a positive number.")
                
        return cleaned_data


class DiseasePredictionForm(forms.Form):
    CROP_CHOICES = [
        ('Cotton', 'Cotton (કપાસ)'),
        ('Groundnut', 'Groundnut (મગફળી)'),
        ('Maize', 'Maize (મકાઈ)'),
        ('Bajra', 'Bajra (બાજરી)'),
        ('Wheat', 'Wheat (ઘઉં)'),
        ('Castor', 'Castor (દિવેલા)'),
        ('Cumin', 'Cumin (જીરું)'),
        ('Mustard', 'Mustard (રાઈ)'),
    ]

    SOIL_CHOICES = [
        ('Black', 'Black Soil (કાળી જમીન)'),
        ('Sandy', 'Sandy Soil (રેતાળ જમીન)'),
        ('Alluvial', 'Alluvial Soil (કાંપવાળી જમીન)'),
        ('Clayey', 'Clayey Soil (ચીકણી જમીન)'),
        ('Loamy', 'Loamy Soil (ગોરાડુ જમીન)'),
    ]

    MODEL_CHOICES = [
        ('Random Forest', 'Random Forest Classifier (Recommended)'),
        ('Decision Tree', 'Decision Tree Classifier'),
        ('KNN', 'K-Nearest Neighbors (KNN)'),
    ]

    crop_name = forms.ChoiceField(choices=CROP_CHOICES, label="Crop Name", widget=forms.Select(attrs={'class': 'form-select form-control-custom'}))
    temperature = forms.DecimalField(max_value=60, min_value=-10, label="Temperature (°C)", widget=forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. 32.5', 'step': '0.1'}))
    humidity = forms.DecimalField(max_value=100, min_value=0, label="Humidity (%)", widget=forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. 80', 'step': '0.1'}))
    rainfall = forms.DecimalField(max_value=1000, min_value=0, label="Rainfall (mm)", widget=forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. 150', 'step': '0.1'}))
    soil_type = forms.ChoiceField(choices=SOIL_CHOICES, label="Soil Type", widget=forms.Select(attrs={'class': 'form-select form-control-custom'}))
    ml_model = forms.ChoiceField(choices=MODEL_CHOICES, label="Select Machine Learning Model", widget=forms.Select(attrs={'class': 'form-select form-control-custom'}))

