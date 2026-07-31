from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    STATE_CHOICES = [
        ('AP', 'Andhra Pradesh'),
        ('AR', 'Arunachal Pradesh'),
        ('AS', 'Assam'),
        ('BR', 'Bihar'),
        ('CG', 'Chhattisgarh'),
        ('GA', 'Goa'),
        ('GJ', 'Gujarat'),
        ('HR', 'Haryana'),
        ('HP', 'Himachal Pradesh'),
        ('JH', 'Jharkhand'),
        ('KA', 'Karnataka'),
        ('KL', 'Kerala'),
        ('MP', 'Madhya Pradesh'),
        ('MH', 'Maharashtra'),
        ('MN', 'Manipur'),
        ('ML', 'Meghalaya'),
        ('MZ', 'Mizoram'),
        ('NL', 'Nagaland'),
        ('OD', 'Odisha'),
        ('PB', 'Punjab'),
        ('RJ', 'Rajasthan'),
        ('SK', 'Sikkim'),
        ('TN', 'Tamil Nadu'),
        ('TG', 'Telangana'),
        ('TR', 'Tripura'),
        ('UP', 'Uttar Pradesh'),
        ('UK', 'Uttarakhand'),
        ('WB', 'West Bengal'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, verbose_name="Mobile Number")
    village = models.CharField(max_length=100, verbose_name="Village Name")
    district = models.CharField(max_length=100, verbose_name="District")
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default='MH', verbose_name="State")
    primary_crop = models.CharField(max_length=100, verbose_name="Primary Crop")
    land_size = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Land Size (in Acres)")

    def __str__(self):
        return f"{self.user.username}'s Profile"


class WeatherHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weather_history')
    query_location = models.CharField(max_length=200, verbose_name="Searched Location")
    temperature = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Temperature (°C)")
    humidity = models.IntegerField(verbose_name="Humidity (%)")
    rainfall = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Rainfall (mm)")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=1, verbose_name="Wind Speed (km/h)")
    condition = models.CharField(max_length=100, verbose_name="Condition")
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name="Searched Date/Time")

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.query_location} - {self.temperature}°C ({self.searched_at.strftime('%d/%m/%Y %H:%M')})"


class MandiPrice(models.Model):
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

    crop_name = models.CharField(max_length=50, choices=CROP_CHOICES, verbose_name="Crop Name")
    mandi_name = models.CharField(max_length=100, verbose_name="Mandi Name (APMC)")
    today_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Today Price (₹/Quintal)")
    yesterday_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Yesterday Price (₹/Quintal)")
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Min Price (₹/Quintal)")
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Max Price (₹/Quintal)")
    price_date = models.DateField(verbose_name="Price Date")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Last Updated")

    class Meta:
        ordering = ['-price_date', 'crop_name']

    def __str__(self):
        return f"{self.get_crop_name_display()} - {self.mandi_name} - ₹{self.today_price} ({self.price_date.strftime('%d/%m/%Y')})"

    @property
    def price_difference(self):
        return self.today_price - self.yesterday_price

    @property
    def absolute_price_difference(self):
        return abs(self.today_price - self.yesterday_price)




