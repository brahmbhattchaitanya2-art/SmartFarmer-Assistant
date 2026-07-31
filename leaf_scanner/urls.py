from django.urls import path
from . import views

app_name = 'leaf_scanner'

urlpatterns = [
    path('', views.scan_leaf_view, name='scan'),
]
