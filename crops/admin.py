from django.contrib import admin
from .models import Crop

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'variety', 'farmer', 'land_size', 'status', 'sowing_date')
    list_filter = ('status', 'name')
    search_fields = ('variety', 'farmer__username')

