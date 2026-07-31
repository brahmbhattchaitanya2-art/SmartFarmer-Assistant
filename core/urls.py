from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from crops import views as crops_views

urlpatterns = [
    # General Pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # User Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Authenticated User Views (Sidebar & Dashboard)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/profile/', views.profile_view, name='profile'),
    
    # Standardized routes
    path('dashboard/disease-prediction/', crops_views.disease_prediction_view, name='disease_prediction'),
    path('dashboard/weather-updates/', views.weather_updates_view, name='weather_updates'),
    path('dashboard/market-prices/', views.market_prices_view, name='market_prices'),
    path('dashboard/fertilizer-guide/', views.fertilizer_guide_view, name='fertilizer_guide'),
    path('dashboard/farming-news/', views.farming_news_view, name='farming_news'),
    path('dashboard/crop-library/', views.crop_library_view, name='crop_library'),

    # Password Reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
]
