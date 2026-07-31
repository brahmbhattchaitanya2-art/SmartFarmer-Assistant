from django.db import models
from django.contrib.auth.models import User

class Crop(models.Model):
    CROP_NAME_CHOICES = [
        ('Cotton', 'Cotton (કપાસ)'),
        ('Groundnut', 'Groundnut (મગફળી)'),
        ('Maize', 'Maize (મકાઈ)'),
        ('Bajra', 'Bajra (બાજરી)'),
        ('Wheat', 'Wheat (ઘઉં)'),
        ('Castor', 'Castor (દિવેલા)'),
        ('Cumin', 'Cumin (જીરું)'),
        ('Mustard', 'Mustard (રાઈ)'),
    ]

    STATUS_CHOICES = [
        ('Growing', 'Growing (વિકસી રહ્યું છે)'),
        ('Ready to Harvest', 'Ready to Harvest (લણણી માટે તૈયાર)'),
        ('Harvested', 'Harvested (લણણી પૂર્ણ)'),
    ]

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops')
    name = models.CharField(max_length=50, choices=CROP_NAME_CHOICES, verbose_name="Crop Name")
    variety = models.CharField(max_length=100, verbose_name="Crop Variety")
    sowing_date = models.DateField(verbose_name="Sowing Date")
    expected_harvest_date = models.DateField(verbose_name="Expected Harvest Date")
    land_size = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Land Size (Acres)")
    investment_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Investment Cost (₹)")
    expected_yield = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Expected Yield (Quintals)")
    estimated_revenue = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Estimated Revenue (₹)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Growing', verbose_name="Crop Status")
    image = models.ImageField(upload_to='crop_images/', blank=True, null=True, verbose_name="Crop Image")

    class Meta:
        ordering = ['-sowing_date']

    def __str__(self):
        return f"{self.get_name_display()} ({self.variety}) - {self.farmer.username}"


class DiseasePrediction(models.Model):
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

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disease_predictions')
    crop_name = models.CharField(max_length=50, choices=CROP_CHOICES, verbose_name="Crop Name")
    temperature = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Temperature (°C)")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Humidity (%)")
    rainfall = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Rainfall (mm)")
    soil_type = models.CharField(max_length=50, choices=SOIL_CHOICES, verbose_name="Soil Type")
    ml_model = models.CharField(max_length=50, verbose_name="ML Model")
    disease = models.CharField(max_length=100, verbose_name="Predicted Disease")
    confidence = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Confidence Score (%)")
    treatment = models.TextField(verbose_name="Treatment Recommended")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Prediction Date")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_crop_name_display()} - {self.disease} ({self.created_at.strftime('%d/%m/%Y')})"


class CropLibrary(models.Model):
    SEASON_CHOICES = [
        ('Kharif', 'Kharif (ખરીફ)'),
        ('Rabi', 'Rabi (રવિ)'),
        ('Zaid', 'Zaid (જાયદ)'),
    ]
    name = models.CharField(max_length=50, unique=True, verbose_name="Crop Name")
    gujarati_name = models.CharField(max_length=100, verbose_name="Gujarati Name")
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, verbose_name="Season")
    soil_type = models.CharField(max_length=150, verbose_name="Soil Type")
    temperature_range = models.CharField(max_length=100, verbose_name="Temperature Range")
    rainfall_requirement = models.CharField(max_length=100, verbose_name="Rainfall Requirement")
    sowing_time = models.CharField(max_length=100, verbose_name="Sowing Time")
    harvest_time = models.CharField(max_length=100, verbose_name="Harvest Time")
    expected_yield = models.CharField(max_length=150, verbose_name="Expected Yield")
    common_diseases = models.TextField(verbose_name="Common Diseases")
    suitable_fertilizers = models.TextField(verbose_name="Suitable Fertilizers")
    image_path = models.CharField(max_length=255, blank=True, verbose_name="Static Image Path")

    def __str__(self):
        return f"{self.name} ({self.gujarati_name})"


class FertilizerRecommendation(models.Model):
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

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fertilizer_recommendations')
    crop_name = models.CharField(max_length=50, choices=CROP_CHOICES, verbose_name="Crop Name")
    soil_type = models.CharField(max_length=50, choices=SOIL_CHOICES, verbose_name="Soil Type")
    crop_stage = models.CharField(max_length=50, choices=STAGE_CHOICES, verbose_name="Crop Stage")
    
    fertilizer_name = models.CharField(max_length=150, verbose_name="Recommended Fertilizer")
    npk_ratio = models.CharField(max_length=50, verbose_name="NPK Ratio")
    quantity_per_acre = models.CharField(max_length=100, verbose_name="Quantity per Acre")
    application_method = models.CharField(max_length=100, verbose_name="Application Method")
    best_time = models.CharField(max_length=150, verbose_name="Best Application Time")
    safety_precautions = models.TextField(verbose_name="Safety Precautions")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Recommendation Date")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.farmer.username} - {self.crop_name} - {self.fertilizer_name}"


class FarmingNews(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="News Title")
    link = models.CharField(max_length=255, unique=True, verbose_name="Source URL")
    image_url = models.CharField(max_length=255, blank=True, null=True, verbose_name="News Image URL")
    summary = models.TextField(verbose_name="Short Summary")
    pub_date = models.CharField(max_length=100, verbose_name="Published Date")
    source_name = models.CharField(max_length=100, verbose_name="Source Name")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fetched Date")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


