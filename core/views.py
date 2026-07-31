from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import FarmerRegistrationForm, UserForm, UserProfileForm, FertilizerForm
from .models import UserProfile, WeatherHistory, MandiPrice
from .weather_service import WeatherService
from crops.models import Crop, DiseasePrediction
from crops.views import calculate_crop_progress
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.offline as op
import plotly.graph_objects as go
import math

def home(request):
    """
    Renders the Home page of the Smart Farmer Assistant.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')

def about(request):
    """
    Renders the About page with information about the assistant's features and mission.
    """
    return render(request, 'core/about.html')

def contact(request):
    """
    Renders the Contact page with a message form and info details.
    """
    return render(request, 'core/contact.html')

def register(request):
    """
    Handles new farmer user registration and automatic login.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Namaste {user.first_name}! Your registration was successful.")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = FarmerRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    """
    Handles farmer user login authentication.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name}! Logged in successfully.")
                return redirect('dashboard')
        messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """
    Logs out the user and redirects to the home page.
    """
    logout(request)
    messages.info(request, "Logged out successfully. Dhanyawad!")
    return redirect('home')

@login_required
def dashboard(request):
    """
    Renders the protected farmer dashboard.
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=request.user,
            phone_number="9876543210",
            village="Chadasna",
            district="Sabarkantha",
            state="GJ",
            primary_crop="Cotton",
            land_size=5.5
        )

    today_date = datetime.now().strftime('%d/%m/%Y')
    
    # Retrieve only the logged-in user's crops
    user_crops = Crop.objects.filter(farmer=request.user)
    
    # Calculate statistics dynamically from database
    total_land = sum(crop.land_size for crop in user_crops)
    total_investment = sum(crop.investment_cost for crop in user_crops)
    expected_revenue = sum(crop.estimated_revenue for crop in user_crops)
    
    recent_crops = user_crops[:5]  # Retrieve recent 5 crop records
    for crop in recent_crops:
        crop.progress_data = calculate_crop_progress(crop)

    # Fetch recent predictions from sqlite
    recent_predictions = DiseasePrediction.objects.filter(farmer=request.user)[:5]

    context = {
        'profile': profile,
        'today_date': today_date,
        'user_crops': user_crops,
        'recent_crops': recent_crops,
        'recent_predictions': recent_predictions,
        'total_land': total_land,
        'total_investment': total_investment,
        'expected_revenue': expected_revenue,
        'soil_health': {
            'last_tested': '10/04/2026',
            'status': 'Good',
            'ph': '6.8',
        }
    }
    return render(request, 'core/dashboard.html', context)



@login_required
def crops_view(request):
    """
    Displays the Crop Library detailing Indian crops.
    """
    indian_crops = [
        {
            'name': 'Rice (Kharif)',
            'sowing_season': 'June - July',
            'harvest_season': 'November - December',
            'ideal_temp': '22°C - 32°C',
            'ideal_rainfall': '150 - 300 cm',
            'soil_type': 'Clayey or Loamy',
            'msp_price': '₹ 2,183 per Quintal',
            'market_rate': '₹ 2,400 - ₹ 3,100 per Quintal',
            'status': 'In Season'
        },
        {
            'name': 'Wheat (Rabi)',
            'sowing_season': 'October - December',
            'harvest_season': 'March - April',
            'ideal_temp': '10°C - 25°C',
            'ideal_rainfall': '50 - 75 cm',
            'soil_type': 'Well-drained Loamy',
            'msp_price': '₹ 2,275 per Quintal',
            'market_rate': '₹ 2,350 - ₹ 2,600 per Quintal',
            'status': 'Off Season'
        },
        {
            'name': 'Cotton (Kharif)',
            'sowing_season': 'May - June',
            'harvest_season': 'October - December',
            'ideal_temp': '21°C - 30°C',
            'ideal_rainfall': '50 - 100 cm',
            'soil_type': 'Black Cotton Soil',
            'msp_price': '₹ 6,620 per Quintal',
            'market_rate': '₹ 6,800 - ₹ 7,400 per Quintal',
            'status': 'In Season'
        },
        {
            'name': 'Sugarcane (Annual)',
            'sowing_season': 'Jan - March or Oct - Nov',
            'harvest_season': '10 - 18 months later',
            'ideal_temp': '21°C - 27°C',
            'ideal_rainfall': '75 - 150 cm',
            'soil_type': 'Alluvial / Loamy',
            'frp_price': '₹ 315 per Quintal',
            'market_rate': '₹ 320 - ₹ 350 per Quintal',
            'status': 'Growing'
        }
    ]
    return render(request, 'core/crops.html', {'crops': indian_crops})

@login_required
def profile_view(request):
    """
    Handles viewing and updating the farmer's personal details.
    """
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(
            user=request.user,
            phone_number="9876543210",
            village="Rampur",
            district="Patiala",
            state="PB",
            primary_crop="Rice",
            land_size=5.5
        )

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Failed to update profile. Please verify your entries.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    }
    return render(request, 'core/profile.html', context)

@login_required
def weather_updates_view(request):
    """
    Renders Weather Updates dashboard for the logged-in farmer.
    Fetches forecasts, crop advice, logs search history in SQLite.
    """
    query = request.GET.get('q')
    
    # Resolve default query using profile location
    if not query:
        try:
            profile = request.user.profile
            query = f"{profile.village}, {profile.district}"
        except UserProfile.DoesNotExist:
            query = "Chadasna, Sabarkantha"

    # Get meteorological forecasts and alerts
    weather_data = WeatherService.get_weather_data(query)
    
    # Save search result log to SQLite WeatherHistory
    WeatherHistory.objects.create(
        user=request.user,
        query_location=weather_data['location'],
        temperature=weather_data['temperature'],
        humidity=weather_data['humidity'],
        rainfall=weather_data['rainfall'],
        wind_speed=weather_data['wind_speed'],
        condition=weather_data['condition']
    )
    
    # Load past 10 search logs
    history = WeatherHistory.objects.filter(user=request.user)[:10]
    
    context = {
        'weather': weather_data,
        'search_query': query,
        'history': history
    }
    return render(request, 'core/weather_updates.html', context)

def fetch_and_store_live_mandi_data():
    import urllib.request
    import json
    import urllib.parse
    from datetime import datetime
    from core.models import MandiPrice

    api_key = '579b464db66ec23bdd000001bae12aebc26e43314a57f18d89417856'
    resource_id = '9ef84268-d588-465a-a308-a864a43d0070'
    base_url = f'https://api.data.gov.in/resource/{resource_id}'

    API_COMMODITY_MAPPING = {
        'cotton': 'Cotton',
        'groundnut': 'Groundnut',
        'ground nut seed': 'Groundnut',
        'maize': 'Maize',
        'bajra(pearl millet/cumbu)': 'Bajra',
        'bajra': 'Bajra',
        'wheat': 'Wheat',
        'castor seed': 'Castor',
        'castor': 'Castor',
        'cummin seed(jeera)': 'Cumin',
        'cumin': 'Cumin',
        'mustard': 'Mustard'
    }

    params = {
        'api-key': api_key,
        'format': 'json',
        'limit': '5000',
        'filters[state]': 'Gujarat'
    }
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        response_data = json.loads(response.read().decode('utf-8'))
        records = response_data.get('records', [])
        
        seen_keys = set()
        
        for record in records:
            commodity_raw = record.get('commodity', '').lower().strip()
            crop_name = API_COMMODITY_MAPPING.get(commodity_raw)
            if not crop_name:
                continue
                
            mandi_name = record.get('market', '').strip()
            if 'apmc' not in mandi_name.lower():
                mandi_name = f"{mandi_name} APMC"
            
            arrival_date_str = record.get('arrival_date', '').strip()
            try:
                price_date = datetime.strptime(arrival_date_str, '%d/%m/%Y').date()
            except ValueError:
                continue
                
            try:
                today_price = float(record.get('modal_price', 0))
                min_price = float(record.get('min_price', 0))
                max_price = float(record.get('max_price', 0))
            except (TypeError, ValueError):
                continue

            record_key = (crop_name, mandi_name, price_date)
            if record_key in seen_keys:
                continue
            seen_keys.add(record_key)

            # Check if this record already exists in database
            mandi_price_obj = MandiPrice.objects.filter(
                crop_name=crop_name,
                mandi_name=mandi_name,
                price_date=price_date
            ).first()

            if mandi_price_obj:
                mandi_price_obj.today_price = today_price
                mandi_price_obj.min_price = min_price
                mandi_price_obj.max_price = max_price
                mandi_price_obj.save()
            else:
                prev_record = MandiPrice.objects.filter(
                    crop_name=crop_name,
                    mandi_name=mandi_name,
                    price_date__lt=price_date
                ).order_by('-price_date').first()
                
                yesterday_price = prev_record.today_price if prev_record else today_price
                
                MandiPrice.objects.create(
                    crop_name=crop_name,
                    mandi_name=mandi_name,
                    today_price=today_price,
                    yesterday_price=yesterday_price,
                    min_price=min_price,
                    max_price=max_price,
                    price_date=price_date
                )


@login_required
def market_prices_view(request):
    """
    Renders the APMC Mandi Prices cockpit for the user.
    Shows daily rates, searches mandis, filters crops, and generates Plotly trend lines.
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models import MandiPrice

    # 1. Clear out mock records (mock records have min_price is null)
    MandiPrice.objects.filter(min_price__isnull=True).delete()

    # 2. Check if we need to fetch live data
    latest_record = MandiPrice.objects.order_by('-last_updated').first()
    
    # Try fetching live data if DB is empty or if cached data is older than 15 minutes
    api_failed = False
    if not latest_record or (timezone.now() - latest_record.last_updated) > timedelta(minutes=15):
        try:
            fetch_and_store_live_mandi_data()
        except Exception as e:
            api_failed = True

    # 3. Retrieve database records to check if we have any data to display
    latest_date_record = MandiPrice.objects.order_by('-price_date').first()
    
    if not latest_date_record:
        # If DB is empty, render the empty state
        context = {
            'empty_state': True,
            'error_message': 'No live market data available',
            'crop_choices': MandiPrice.CROP_CHOICES,
            'selected_crop': request.GET.get('crop', 'Cumin'),
            'search_query': request.GET.get('q', '')
        }
        return render(request, 'core/market_prices.html', context)

    latest_date = latest_date_record.price_date
    query = request.GET.get('q', '')
    selected_crop = request.GET.get('crop', 'Cumin')
    
    # 4. Retrieve latest prices for card decks
    card_prices = MandiPrice.objects.filter(price_date=latest_date)
    if query:
        card_prices = card_prices.filter(mandi_name__icontains=query)
    else:
        card_prices = card_prices.filter(crop_name=selected_crop)

    crop_icon_mapping = {
        'Cotton': 'bi-clouds-fill text-success',
        'Groundnut': 'bi-nut-fill text-warning',
        'Maize': 'bi-corn text-warning',
        'Bajra': 'bi-grain text-success',
        'Wheat': 'bi-crop text-warning',
        'Castor': 'bi-tree-fill text-success',
        'Cumin': 'bi-flower1 text-success',
        'Mustard': 'bi-flower3 text-warning',
    }
    
    for item in card_prices:
        item.icon = crop_icon_mapping.get(item.crop_name, 'bi-flower1')
        item.diff = item.today_price - item.yesterday_price
        if item.diff > 0:
            item.trend_arrow = '▲'
            item.trend_color = 'success'
        elif item.diff < 0:
            item.trend_arrow = '▼'
            item.trend_color = 'danger'
        else:
            item.trend_arrow = '▬'
            item.trend_color = 'secondary'

    # 5. Build Mandi-wise Price Comparison Chart dynamically from current card records
    if query:
        chart_records = card_prices.filter(crop_name=selected_crop).order_by('mandi_name')
    else:
        chart_records = card_prices.order_by('mandi_name')
    
    chart_div = None
    if chart_records.exists():
        data_list = []
        for r in chart_records:
            data_list.append({
                'mandi': r.mandi_name,
                'price': float(r.today_price)
            })
        df = pd.DataFrame(data_list)
        df = df.sort_values('mandi', ascending=True)
        
        mandi_list = df['mandi'].tolist()
        prices_list = df['price'].tolist()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=mandi_list,
            y=prices_list,
            mode='lines+markers',
            name=selected_crop,
            line=dict(color='#2e7d32', width=3),
            marker=dict(size=8, color='#f57f17')
        ))
        
        fig.update_layout(
            title=f"Mandi-wise Price Comparison: {selected_crop} (₹/Quintal)",
            margin=dict(l=65, r=30, t=50, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12),
            hovermode="closest",
            xaxis=dict(
                title="APMC Mandi Market",
                showgrid=True,
                gridcolor='#e2e8f0'
            ),
            yaxis=dict(
                title="Price (₹/Quintal)",
                showgrid=True,
                gridcolor='#e2e8f0',
                tickprefix="₹"
            )
        )
        chart_div = op.plot(fig, output_type='div', include_plotlyjs=False)

    mandi_history = MandiPrice.objects.all().order_by('-price_date', 'crop_name')[:30]
    
    context = {
        'empty_state': False,
        'latest_date': latest_date,
        'card_prices': card_prices,
        'selected_crop': selected_crop,
        'search_query': query,
        'chart_div': chart_div,
        'mandi_history': mandi_history,
        'crop_choices': MandiPrice.CROP_CHOICES
    }
    return render(request, 'core/market_prices.html', context)

@login_required
def fertilizer_guide_view(request):
    """
    Guides the farmer with tailored N-P-K fertilizer recommendations.
    Saves predictions to SQLite and maintains search log history.
    """
    from crops.models import FertilizerRecommendation
    
    # Recommendation logic database mapping
    recommendations_db = {
        'Cotton': {
            'Sowing/Basal': {
                'fertilizer_name': 'NPK (10:26:26) + Castor Cake',
                'npk_ratio': '10% N, 26% P2O5, 26% K2O',
                'quantity_per_acre': '50 kg NPK + 100 kg Castor Cake',
                'application_method': 'Soil Broadcast & Incorporation',
                'best_time': 'At the time of sowing/tillage',
                'safety_precautions': 'Use gloves while handling chemical fertilizers. Keep pets away from Castor Cake as it is toxic if consumed.'
            },
            'Vegetative': {
                'fertilizer_name': 'Urea (46% N) + Zinc Sulphate',
                'npk_ratio': '46:0:0 + Micronutrients',
                'quantity_per_acre': '45 kg Urea + 10 kg Zinc Sulphate',
                'application_method': 'Top Dressing / Band Placement',
                'best_time': '30-45 days after sowing (squaring stage)',
                'safety_precautions': 'Apply to moist soil. Do not apply during peak noon heat to avoid nitrogen loss and leaf burn.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'Muriate of Potash (MOP) + Urea',
                'npk_ratio': '46:0:60 (mixed)',
                'quantity_per_acre': '25 kg MOP + 20 kg Urea',
                'application_method': 'Top Dressing (split dose)',
                'best_time': '60-75 days after sowing (flowering onset)',
                'safety_precautions': 'Wash hands and face with soap immediately after application. Avoid skin contact with MOP.'
            }
        },
        'Wheat': {
            'Sowing/Basal': {
                'fertilizer_name': 'DAP (Diammonium Phosphate) + Urea',
                'npk_ratio': '18% N, 46% P2O5',
                'quantity_per_acre': '50 kg DAP + 20 kg Urea',
                'application_method': 'Band Placement (below seeds)',
                'best_time': 'During sowing',
                'safety_precautions': 'Ensure fertilizer is placed 5cm below and to the side of the seed to prevent seed damage.'
            },
            'Vegetative': {
                'fertilizer_name': 'Urea (46% N)',
                'npk_ratio': '46:0:0',
                'quantity_per_acre': '40 kg Urea',
                'application_method': 'Top Dressing / Broadcast',
                'best_time': 'Right after first irrigation (21-25 days, CRI stage)',
                'safety_precautions': 'Avoid application under strong winds to prevent uneven broadcasting.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'NPK (19:19:19) Foliar Spray',
                'npk_ratio': '19:19:19 (Water Soluble)',
                'quantity_per_acre': '2 kg dissolved in 200L water',
                'application_method': 'Foliar Spray',
                'best_time': 'Jointing to flowering stage',
                'safety_precautions': 'Spray during early morning or late evening. Ensure standard nozzle for uniform mist.'
            }
        },
        'Groundnut': {
            'Sowing/Basal': {
                'fertilizer_name': 'Single Super Phosphate (SSP) + Gypsum',
                'npk_ratio': '0% N, 16% P2O5, 11% S, 19% Ca',
                'quantity_per_acre': '100 kg SSP + 100 kg Gypsum',
                'application_method': 'Soil Broadcast & Mix',
                'best_time': 'Before or during sowing',
                'safety_precautions': 'SSP and Gypsum provide critical Calcium and Sulphur for pegging. Wear a protective dust mask.'
            },
            'Vegetative': {
                'fertilizer_name': 'Gypsum (Soil Application)',
                'npk_ratio': '19% Ca, 15% S',
                'quantity_per_acre': '150 kg Gypsum',
                'application_method': 'Soil Incorporation (around pegging zone)',
                'best_time': '40-45 days after sowing (early pegging stage)',
                'safety_precautions': 'Incorporate gently to avoid damaging the pegging shoots. Ensure soil is moist.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'Borax Foliar Spray + SSP',
                'npk_ratio': '0:16:0 + Boron',
                'quantity_per_acre': '5 kg Borax',
                'application_method': 'Foliar Spray / Side Dressing',
                'best_time': 'Flowering stage',
                'safety_precautions': 'Do not exceed boron dosage as it can lead to phytotoxicity.'
            }
        },
        'Maize': {
            'Sowing/Basal': {
                'fertilizer_name': 'NPK (15:15:15) + Zinc Sulphate',
                'npk_ratio': '15% N, 15% P2O5, 15% K2O',
                'quantity_per_acre': '60 kg NPK + 10 kg Zinc Sulphate',
                'application_method': 'Band placement',
                'best_time': 'At sowing time',
                'safety_precautions': 'Keep bag sealed until application. Wear boots and protective clothing.'
            },
            'Vegetative': {
                'fertilizer_name': 'Urea (46% N)',
                'npk_ratio': '46:0:0',
                'quantity_per_acre': '50 kg Urea',
                'application_method': 'Top Dressing / Side Placement',
                'best_time': 'Knee-high growth stage (30-35 days)',
                'safety_precautions': 'Place fertilizer 5-8 cm away from the stem to avoid root burn.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'Urea + Muriate of Potash (MOP)',
                'npk_ratio': '46% N, 60% K2O',
                'quantity_per_acre': '25 kg Urea + 15 kg MOP',
                'application_method': 'Side Dressing',
                'best_time': 'Tasseling to silking stage',
                'safety_precautions': 'Apply when weather is clear. Do not apply if heavy rain is expected within 24 hours.'
            }
        },
        'Bajra': {
            'Sowing/Basal': {
                'fertilizer_name': 'NPK (12:32:16) + Compost',
                'npk_ratio': '12% N, 32% P2O5, 16% K2O',
                'quantity_per_acre': '40 kg NPK + 1 ton Organic Compost',
                'application_method': 'Soil Broadcast',
                'best_time': 'Before sowing',
                'safety_precautions': 'Use well-decomposed farmyard manure to prevent pest/weed seeds introduction.'
            },
            'Vegetative': {
                'fertilizer_name': 'Urea (46% N)',
                'npk_ratio': '46:0:0',
                'quantity_per_acre': '35 kg Urea',
                'application_method': 'Top Dressing',
                'best_time': 'Tillering stage (25-30 days)',
                'safety_precautions': 'Avoid application under direct afternoon sun to minimize ammonia volatilization.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'NPK (19:19:19) Spray',
                'npk_ratio': '19:19:19 (Water Soluble)',
                'quantity_per_acre': '1.5 kg in 200L water',
                'application_method': 'Foliar Spray',
                'best_time': 'Boot stage to panicle emergence',
                'safety_precautions': 'Ensure clean water is used for foliar dilution to prevent leaf scorch.'
            }
        },
        'Castor': {
            'Sowing/Basal': {
                'fertilizer_name': 'DAP + Neem Cake',
                'npk_ratio': '18% N, 46% P2O5',
                'quantity_per_acre': '40 kg DAP + 80 kg Neem Cake',
                'application_method': 'Soil Band Placement',
                'best_time': 'Sowing time',
                'safety_precautions': 'Neem Cake helps act as a natural pesticide against soil grubs. Wear gloves.'
            },
            'Vegetative': {
                'fertilizer_name': 'Urea (46% N)',
                'npk_ratio': '46:0:0',
                'quantity_per_acre': '30 kg Urea',
                'application_method': 'Top Dressing (Inter-row)',
                'best_time': '35-40 days after sowing',
                'safety_precautions': 'Keep chemical fertilizer out of touch from children and livestock.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'Urea + Muriate of Potash (MOP)',
                'npk_ratio': '46% N, 60% K2O',
                'quantity_per_acre': '25 kg Urea + 10 kg MOP',
                'application_method': 'Top Dressing',
                'best_time': 'Spike development stage (multiple splits)',
                'safety_precautions': 'Wash thoroughly with soap if contact with eyes occurs.'
            }
        },
        'Cumin': {
            'Sowing/Basal': {
                'fertilizer_name': 'Single Super Phosphate (SSP) + Neem Cake',
                'npk_ratio': '16% P2O5, 11% S',
                'quantity_per_acre': '80 kg SSP + 100 kg Neem Cake',
                'application_method': 'Soil Broadcast',
                'best_time': 'During tillage / sowing',
                'safety_precautions': 'Neem Cake helps protect cumin seedlings from initial soil wilts. Wear a dust mask.'
            },
            'Vegetative': {
                'fertilizer_name': 'NPK (19:19:19) Foliar Spray',
                'npk_ratio': '19:19:19',
                'quantity_per_acre': '2 kg in 200L water',
                'application_method': 'Foliar Spray',
                'best_time': '30-35 days after sowing',
                'safety_precautions': 'Do not overwater cumin fields; cumin requires dry weather conditions.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'Potassium Nitrate (13:0:45) Spray',
                'npk_ratio': '13% N, 45% K2O',
                'quantity_per_acre': '1.5 kg in 150L water',
                'application_method': 'Foliar Spray',
                'best_time': 'Flowering onset',
                'safety_precautions': 'Spray only on calm days to avoid wind drift onto non-target boundary zones.'
            }
        },
        'Mustard': {
            'Sowing/Basal': {
                'fertilizer_name': 'Single Super Phosphate (SSP) + Urea',
                'npk_ratio': '46% N + 16% P2O5 + 11% S',
                'quantity_per_acre': '75 kg SSP + 30 kg Urea',
                'application_method': 'Soil Broadcast & Mix',
                'best_time': 'Before or during sowing',
                'safety_precautions': 'Mustard is highly sulfur-loving. SSP provides crucial sulfur; handle with dry gloves.'
            },
            'Vegetative': {
                'fertilizer_name': 'Urea (46% N)',
                'npk_ratio': '46:0:0',
                'quantity_per_acre': '35 kg Urea',
                'application_method': 'Top Dressing',
                'best_time': 'After first weeding / thinning (25-30 days)',
                'safety_precautions': 'Do not apply to leaves when dew is present to prevent leaf burning.'
            },
            'Flowering/Fruiting': {
                'fertilizer_name': 'NPK (19:19:19) Foliar Spray',
                'npk_ratio': '19:19:19',
                'quantity_per_acre': '2 kg in 200L water',
                'application_method': 'Foliar Spray',
                'best_time': 'Siliqua/Flowering stage',
                'safety_precautions': 'Keep the spray nozzle at a safe distance. Wash boots post application.'
            }
        }
    }

    form = FertilizerForm(request.POST or None)
    result = None

    if request.method == 'POST' and form.is_valid():
        crop_name = form.cleaned_data['crop_name']
        soil_type = form.cleaned_data['soil_type']
        crop_stage = form.cleaned_data['crop_stage']

        # Get base recommendation template
        crop_stage_key = 'Sowing/Basal'
        if 'Vegetative' in crop_stage:
            crop_stage_key = 'Vegetative'
        elif 'Flowering' in crop_stage:
            crop_stage_key = 'Flowering/Fruiting'

        base_rec = recommendations_db.get(crop_name, {}).get(crop_stage_key, {}).copy()

        if base_rec:
            # Parse quantity out for adjustment
            # Match quantity (e.g. "50 kg NPK") and apply soil adjustment multiplier
            qty_str = base_rec['quantity_per_acre']
            
            # Apply adjustments based on soil type
            multiplier = 1.0
            adjustment_note = ""
            if soil_type == 'Sandy Soil':
                multiplier = 1.2
                adjustment_note = " (Increased by 20% due to sandy soil leaching rates)"
            elif soil_type == 'Red Soil':
                multiplier = 1.1
                adjustment_note = " (Increased by 10% due to red soil nutrient deficiency)"
            elif soil_type == 'Alluvial Soil':
                multiplier = 0.95
                adjustment_note = " (Decreased by 5% due to high native alluvial fertility)"
            
            # Simple text parser to scale numerical quantities inside the string
            import re
            def scale_match(m):
                val = float(m.group(1))
                return f"{round(val * multiplier, 1)}"
            
            adjusted_qty = re.sub(r'(\d+(?:\.\d+)?)', scale_match, qty_str) + adjustment_note

            # Save recommendation to DB
            rec_obj = FertilizerRecommendation.objects.create(
                farmer=request.user,
                crop_name=crop_name,
                soil_type=soil_type,
                crop_stage=crop_stage,
                fertilizer_name=base_rec['fertilizer_name'],
                npk_ratio=base_rec['npk_ratio'],
                quantity_per_acre=adjusted_qty,
                application_method=base_rec['application_method'],
                best_time=base_rec['best_time'],
                safety_precautions=base_rec['safety_precautions']
            )

            result = {
                'crop_name': crop_name,
                'soil_type': soil_type,
                'crop_stage': crop_stage,
                'fertilizer_name': rec_obj.fertilizer_name,
                'npk_ratio': rec_obj.npk_ratio,
                'quantity_per_acre': rec_obj.quantity_per_acre,
                'application_method': rec_obj.application_method,
                'best_time': rec_obj.best_time,
                'safety_precautions': rec_obj.safety_precautions
            }
            messages.success(request, f"Fertilizer recommendation calculated successfully for {crop_name}.")

    # Load recent 10 recommendation history
    history = FertilizerRecommendation.objects.filter(farmer=request.user)[:10]

    context = {
        'form': form,
        'result': result,
        'history': history,
        'crop_choices': FertilizerRecommendation.CROP_CHOICES
    }
    return render(request, 'core/fertilizer_guide.html', context)

def fetch_and_store_news():
    import requests
    from bs4 import BeautifulSoup
    from crops.models import FarmingNews
    
    url = 'https://krishijagran.com/feeds/rss'
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch news feed. Status code: {response.status_code}")
        
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('item')
    
    new_count = 0
    for item in items[:15]:  # Fetch up to 15 news articles at a time
        title_tag = item.find('title')
        link_tag = item.find('link')
        pubdate_tag = item.find('pubdate')
        description_tag = item.find('description')
        
        if not title_tag or not link_tag:
            continue
            
        title = title_tag.text.strip()
        
        # Link resolution
        if link_tag.next_sibling and link_tag.next_sibling.strip():
            link = link_tag.next_sibling.strip()
        else:
            link = link_tag.text.strip()
            
        if not link:
            continue
            
        # Avoid duplicate news entries
        if FarmingNews.objects.filter(Q(link=link) | Q(title=title)).exists():
            continue
            
        pub_date = pubdate_tag.text.strip() if pubdate_tag else 'Recently'
        
        desc_text = description_tag.text.strip() if description_tag else 'Read the full story on Krishi Jagran.'
        desc_soup = BeautifulSoup(desc_text, 'html.parser')
        summary = desc_soup.text.strip()
        if len(summary) > 280:
            summary = summary[:277] + '...'
            
        # Image URL resolution
        media_content = item.find('media:content')
        enclosure = item.find('enclosure')
        image_url = None
        if media_content:
            image_url = media_content.get('url')
        elif enclosure:
            image_url = enclosure.get('url')
            
        FarmingNews.objects.create(
            title=title,
            link=link,
            image_url=image_url,
            summary=summary,
            pub_date=pub_date,
            source_name='Krishi Jagran'
        )
        new_count += 1
    return new_count

@login_required
def farming_news_view(request):
    """
    Scrapes and displays the latest agricultural news and scheme notifications.
    """
    from crops.models import FarmingNews
    error_message = None
    
    # Check if a refresh was explicitly requested or if database is empty
    should_fetch = (request.GET.get('refresh') == 'true') or (FarmingNews.objects.count() == 0)
    
    if should_fetch:
        try:
            new_count = fetch_and_store_news()
            if request.GET.get('refresh') == 'true':
                if new_count > 0:
                    messages.success(request, f"Successfully fetched {new_count} new news articles.")
                else:
                    messages.info(request, "You are already up to date with the latest agriculture news.")
                return redirect('farming_news')
        except Exception as e:
            error_message = "Unable to fetch the latest agriculture news. Please check your network connection and try again later."
            if request.GET.get('refresh') == 'true':
                messages.error(request, error_message)
                return redirect('farming_news')
                
    news_list = FarmingNews.objects.all().order_by('-id')
    
    context = {
        'news_list': news_list,
        'error_message': error_message
    }
    return render(request, 'core/farming_news.html', context)

def auto_seed_crop_library():
    from crops.models import CropLibrary
    cotton = CropLibrary.objects.filter(name='Cotton').first()
    if cotton and cotton.rainfall_requirement == '30 - 220 mm':
        return
    CropLibrary.objects.all().delete()

    crops_data = [
        {
            'name': 'Cotton',
            'gujarati_name': 'કપાસ (Bt Cotton)',
            'season': 'Kharif',
            'soil_type': 'Black Soil',
            'temperature_range': '26°C - 36°C',
            'rainfall_requirement': '30 - 220 mm',
            'sowing_time': 'June - July (Monsoon onset)',
            'harvest_time': 'November - February',
            'expected_yield': '15 - 25 Quintals/Acre',
            'common_diseases': 'Bacterial Blight, Leaf Spot, Wilt',
            'suitable_fertilizers': 'Urea, NPK (20:20:20), Neem Cake',
            'image_path': 'images/crops/cotton.png'
        },
        {
            'name': 'Groundnut',
            'gujarati_name': 'મગફળી (Groundnut)',
            'season': 'Kharif',
            'soil_type': 'Sandy Soil, Loamy Soil',
            'temperature_range': '24°C - 35°C',
            'rainfall_requirement': '20 - 140 mm',
            'sowing_time': 'June - July',
            'harvest_time': 'October - November',
            'expected_yield': '10 - 18 Quintals/Acre',
            'common_diseases': 'Tikka Leaf Spot, Leaf Spot, Collar Rot',
            'suitable_fertilizers': 'Single Super Phosphate (SSP), Gypsum, Ammonium Sulphate',
            'image_path': 'images/crops/groundnut.png'
        },
        {
            'name': 'Maize',
            'gujarati_name': 'મકાઈ (Maize)',
            'season': 'Kharif',
            'soil_type': 'Alluvial Soil, Loamy Soil',
            'temperature_range': '26°C - 30°C',
            'rainfall_requirement': '80 - 140 mm',
            'sowing_time': 'June - July',
            'harvest_time': 'September - October',
            'expected_yield': '20 - 30 Quintals/Acre',
            'common_diseases': 'Downy Mildew',
            'suitable_fertilizers': 'DAP, Urea, MOP (Muriate of Potash)',
            'image_path': 'images/crops/maize.png'
        },
        {
            'name': 'Bajra',
            'gujarati_name': 'બાજરી (Pearl Millet)',
            'season': 'Kharif',
            'soil_type': 'Sandy Soil',
            'temperature_range': '32°C - 35°C',
            'rainfall_requirement': '70 - 150 mm',
            'sowing_time': 'June - July',
            'harvest_time': 'September - October',
            'expected_yield': '8 - 15 Quintals/Acre',
            'common_diseases': 'Downy Mildew',
            'suitable_fertilizers': 'Urea, NPK (12:32:16)',
            'image_path': 'images/crops/bajra.png'
        },
        {
            'name': 'Wheat',
            'gujarati_name': 'ઘઉં (Wheat)',
            'season': 'Rabi',
            'soil_type': 'Alluvial Soil, Loamy Soil',
            'temperature_range': '15°C - 22°C',
            'rainfall_requirement': '20 - 60 mm',
            'sowing_time': 'October - November',
            'harvest_time': 'March - April',
            'expected_yield': '18 - 25 Quintals/Acre',
            'common_diseases': 'Yellow Rust, Wilt',
            'suitable_fertilizers': 'NPK (19:19:19), Urea, DAP',
            'image_path': 'images/crops/wheat.png'
        },
        {
            'name': 'Castor',
            'gujarati_name': 'દિવેલા (Castor)',
            'season': 'Kharif',
            'soil_type': 'Black Soil, Loamy Soil',
            'temperature_range': '28°C - 30°C',
            'rainfall_requirement': '80 - 110 mm',
            'sowing_time': 'July - August',
            'harvest_time': 'December - March (multiple pickings)',
            'expected_yield': '12 - 20 Quintals/Acre',
            'common_diseases': 'Wilt',
            'suitable_fertilizers': 'Urea, Ammonium Phosphate, MOP',
            'image_path': 'images/crops/castor.png'
        },
        {
            'name': 'Cumin',
            'gujarati_name': 'જીરું (Cumin)',
            'season': 'Rabi',
            'soil_type': 'Loamy Soil',
            'temperature_range': '20°C - 29°C',
            'rainfall_requirement': '5 - 45 mm',
            'sowing_time': 'October - November',
            'harvest_time': 'February - March',
            'expected_yield': '3 - 6 Quintals/Acre',
            'common_diseases': 'Powdery Mildew, Wilt',
            'suitable_fertilizers': 'Castor Cake, SSP, NPK (12:32:16)',
            'image_path': 'images/crops/cumin.png'
        },
        {
            'name': 'Mustard',
            'gujarati_name': 'રાઈ (Mustard)',
            'season': 'Rabi',
            'soil_type': 'Alluvial Soil, Loamy Soil',
            'temperature_range': '14°C - 20°C',
            'rainfall_requirement': '25 - 55 mm',
            'sowing_time': 'September - October',
            'harvest_time': 'February - March',
            'expected_yield': '6 - 12 Quintals/Acre',
            'common_diseases': 'White Rust',
            'suitable_fertilizers': 'Single Super Phosphate (SSP), Urea, MOP',
            'image_path': 'images/crops/mustard.png'
        }
    ]

    for c in crops_data:
        CropLibrary.objects.create(**c)


@login_required
def crop_library_view(request):
    """
    Fully functional Crop Reference Library view with search and filters.
    """
    auto_seed_crop_library()
    from crops.models import CropLibrary

    query = request.GET.get('q', '').strip()
    selected_season = request.GET.get('season', 'All').strip()

    crops = CropLibrary.objects.all()

    if selected_season != 'All':
        crops = crops.filter(season=selected_season)

    if query:
        crops = crops.filter(
            Q(name__icontains=query) |
            Q(gujarati_name__icontains=query) |
            Q(soil_type__icontains=query) |
            Q(common_diseases__icontains=query)
        )

    context = {
        'crops': crops,
        'search_query': query,
        'selected_season': selected_season,
        'seasons': ['All', 'Kharif', 'Rabi', 'Zaid']
    }
    return render(request, 'core/crop_library.html', context)

