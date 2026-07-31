from django.urls import path
from . import views

app_name = 'crops'

urlpatterns = [
    path('', views.crop_list, name='my_crops'),
    path('add/', views.crop_create, name='crop_add'),
    path('analytics/', views.crop_analytics, name='crop_analytics'),
    path('disease-prediction/', views.disease_prediction_view, name='disease_prediction'),
    path('disease-prediction/<int:pk>/pdf/', views.disease_prediction_pdf, name='disease_prediction_pdf'),
    path('<int:pk>/', views.crop_detail, name='crop_detail'),
    path('<int:pk>/edit/', views.crop_update, name='crop_update'),
    path('<int:pk>/delete/', views.crop_delete, name='crop_delete'),
]
