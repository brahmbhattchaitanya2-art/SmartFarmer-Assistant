from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Crop, DiseasePrediction
from .forms import CropForm, DiseasePredictionForm
from .ml_engine import DiseaseMLEngine
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import plotly.offline as op
import plotly.graph_objects as go

def calculate_crop_progress(crop):
    """
    Calculates progress percentage from sowing_date to expected_harvest_date.
    Determines bootstrap color classes (danger, warning, info, success) and label text.
    """
    today = date.today()
    sow = crop.sowing_date
    harv = crop.expected_harvest_date
    
    # If crop is already harvested, force it to 100%
    if crop.status == 'Harvested':
        return {
            'percent': 100,
            'color': 'success',
            'label': 'Harvested (લણણી પૂર્ણ)'
        }
        
    if not sow or not harv:
        return {'percent': 0, 'color': 'danger', 'label': 'N/A'}
        
    total_days = (harv - sow).days
    elapsed_days = (today - sow).days
    
    if total_days <= 0:
        percent = 0
    else:
        percent = int((elapsed_days / total_days) * 100)
        
    # Clamp progress between 0 and 100
    percent = max(0, min(100, percent))
    
    if percent <= 25:
        color = 'danger'
        label = f'Just Sown (વાવણી થયેલ): {percent}%'
    elif percent <= 50:
        color = 'warning'
        label = f'Growing (વિકસી રહ્યું છે): {percent}%'
    elif percent <= 75:
        color = 'info'
        label = f'Near Maturity (પરિપક્વતા નજીક): {percent}%'
    else:
        color = 'success'
        label = f'Ready for Harvest (લણણી માટે તૈયાર): {percent}%'
        
    return {
        'percent': percent,
        'color': color,
        'label': label
    }

@login_required
def crop_list(request):
    """
    Displays the logged-in farmer's crops with search, status filtering, and growth progress indicators.
    """
    crops = Crop.objects.filter(farmer=request.user)
    
    # Handle Search
    query = request.GET.get('q')
    if query:
        crops = crops.filter(
            Q(name__icontains=query) | 
            Q(variety__icontains=query)
        )
        
    # Handle Status Filter
    status_filter = request.GET.get('status')
    if status_filter:
        crops = crops.filter(status=status_filter)

    # Attach dynamic progress data to each crop object
    for crop in crops:
        crop.progress_data = calculate_crop_progress(crop)

    # Calculate dynamic sums for listing summary
    total_land = sum(crop.land_size for crop in crops)
    total_investment = sum(crop.investment_cost for crop in crops)
    total_revenue = sum(crop.estimated_revenue for crop in crops)

    context = {
        'crops': crops,
        'search_query': query or '',
        'status_filter': status_filter or '',
        'status_choices': Crop.STATUS_CHOICES,
        'total_land': total_land,
        'total_investment': total_investment,
        'total_revenue': total_revenue
    }
    return render(request, 'crops/crop_list.html', context)

@login_required
def crop_create(request):
    """
    Adds a new crop entry for the logged-in farmer.
    """
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.farmer = request.user
            crop.save()
            messages.success(request, f"Crop entry for {crop.get_name_display()} ({crop.variety}) recorded successfully.")
            return redirect('crops:my_crops')
        else:
            messages.error(request, "Failed to record crop entry. Please check the details below.")
    else:
        form = CropForm()
    return render(request, 'crops/crop_form.html', {'form': form, 'title': 'Add Crop Cultivation'})

@login_required
def crop_detail(request, pk):
    """
    Shows detailed parameters of a single crop entry.
    Secures request to ensure only the owner can view.
    """
    crop = get_object_or_404(Crop, pk=pk, farmer=request.user)
    crop.progress_data = calculate_crop_progress(crop)
    return render(request, 'crops/crop_detail.html', {'crop': crop})

@login_required
def crop_update(request, pk):
    """
    Updates details of an existing crop entry.
    Secures request to ensure only the owner can modify.
    """
    crop = get_object_or_404(Crop, pk=pk, farmer=request.user)
    if request.method == 'POST':
        form = CropForm(request.POST, request.FILES, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, f"Details for {crop.get_name_display()} updated successfully.")
            return redirect('crops:crop_detail', pk=crop.pk)
        else:
            messages.error(request, "Failed to update crop details. Please check the form errors.")
    else:
        form = CropForm(instance=crop)
    return render(request, 'crops/crop_form.html', {'form': form, 'crop': crop, 'title': 'Update Crop Details'})

@login_required
def crop_delete(request, pk):
    """
    Deletes a crop entry.
    Secures request to ensure only the owner can delete.
    """
    crop = get_object_or_404(Crop, pk=pk, farmer=request.user)
    if request.method == 'POST':
        name_display = crop.get_name_display()
        crop.delete()
        messages.success(request, f"Crop entry for {name_display} deleted successfully.")
        return redirect('crops:my_crops')
    return render(request, 'crops/crop_confirm_delete.html', {'crop': crop})

@login_required
def crop_analytics(request):
    """
    Renders an interactive Crop Analytics Dashboard using Pandas and Plotly.
    Calculates summary insights and builds custom responsive charts.
    """
    user_crops = Crop.objects.filter(farmer=request.user)
    
    # If no crop records exist, render a clean empty message state
    if not user_crops.exists():
        return render(request, 'crops/analytics.html', {'empty_state': True})

    # 1. Parse Django Queryset into a Pandas DataFrame
    data_list = []
    for c in user_crops:
        data_list.append({
            'name': c.get_name_display(),
            'variety': c.variety,
            'land_size': float(c.land_size),
            'investment': float(c.investment_cost),
            'yield': float(c.expected_yield),
            'revenue': float(c.estimated_revenue),
            'status': c.get_status_display(),
            'sowing_date': c.sowing_date
        })
    df = pd.DataFrame(data_list)

    # 2. Pandas Calculations (Totals, Averages, Min, Max)
    stats_summary = {
        'total_crops': len(df),
        'total_land': df['land_size'].sum(),
        'avg_land': df['land_size'].mean(),
        'min_land': df['land_size'].min(),
        'max_land': df['land_size'].max(),
        
        'total_investment': df['investment'].sum(),
        'avg_investment': df['investment'].mean(),
        'min_investment': df['investment'].min(),
        'max_investment': df['investment'].max(),
        
        'total_yield': df['yield'].sum(),
        'avg_yield': df['yield'].mean(),
        'min_yield': df['yield'].min(),
        'max_yield': df['yield'].max(),
        
        'total_revenue': df['revenue'].sum(),
        'avg_revenue': df['revenue'].mean(),
        'min_revenue': df['revenue'].min(),
        'max_revenue': df['revenue'].max(),
    }

    # Find highest revenue crop
    idx_max_rev = df['revenue'].idxmax()
    highest_revenue = df.loc[idx_max_rev]

    # Find highest yield crop
    idx_max_yield = df['yield'].idxmax()
    highest_yield = df.loc[idx_max_yield]

    # 3. Plotly Interactive Charting (List-based to prevent Base64 binary serialization bugs)
    # Set premium palettes matching farming aesthetics
    green_palette = ['#2e7d32', '#4caf50', '#81c784', '#a5d6a7', '#c8e6c9', '#e8f5e9']
    amber_palette = ['#f57f17', '#f9a825', '#fbc02d', '#fdd835', '#ffeb3b', '#fff9c4']

    # Chart 1: Crop-wise Land Distribution (Pie)
    fig_land = px.pie(
        names=df['name'].tolist(),
        values=df['land_size'].tolist(),
        hole=0.4,
        color_discrete_sequence=green_palette
    )
    fig_land.update_layout(title_text='<b>Land Size Distribution (Acres)</b>')

    # Chart 2: Investment by Crop (Bar)
    fig_inv = go.Figure(data=[go.Bar(
        x=df['name'].tolist(),
        y=df['investment'].tolist(),
        marker_color='#2e7d32'
    )])
    fig_inv.update_layout(
        title_text='<b>Investment by Crop (₹)</b>',
        xaxis=dict(title="Crop"),
        yaxis=dict(title="Investment Sunk (₹)")
    )

    # Chart 3: Expected Revenue by Crop (Bar)
    fig_rev = go.Figure(data=[go.Bar(
        x=df['name'].tolist(),
        y=df['revenue'].tolist(),
        marker_color='#f57f17'
    )])
    fig_rev.update_layout(
        title_text='<b>Expected Revenue by Crop (₹)</b>',
        xaxis=dict(title="Crop"),
        yaxis=dict(title="Expected Revenue (₹)")
    )

    # Chart 4: Crop Status Distribution (Pie)
    status_counts = df['status'].value_counts()
    fig_status = px.pie(
        names=status_counts.index.tolist(),
        values=status_counts.values.tolist(),
        color_discrete_sequence=['#42a5f5', '#ffb74d', '#66bb6a']
    )
    fig_status.update_layout(title_text='<b>Crop Sowing Status</b>')

    # Chart 5: Sowing Timeline (Line Chart)
    df_timeline = df.sort_values(by='sowing_date')
    dates_list = df_timeline['sowing_date'].apply(lambda x: x.strftime('%d/%m/%Y')).tolist()
    investments_list = df_timeline['investment'].tolist()
    crop_names_list = df_timeline['name'].tolist()

    fig_timeline = px.line(
        x=dates_list,
        y=investments_list,
        text=crop_names_list,
        labels={'x': 'Sowing Date', 'y': 'Investment (₹)'},
        markers=True
    )
    fig_timeline.update_layout(title_text='<b>Investment Sowing Timeline (₹)</b>')
    fig_timeline.update_traces(textposition="top center", line_color='#2e7d32')

    # Apply responsive styling and fonts globally to Plotly objects
    for fig in [fig_land, fig_inv, fig_rev, fig_status, fig_timeline]:
        fig.update_layout(
            height=400,
            margin=dict(l=40, r=30, t=50, b=30),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=12),
            hovermode="closest"
        )
        fig.update_xaxes(showgrid=True, gridcolor='#e2e8f0')
        fig.update_yaxes(showgrid=True, gridcolor='#e2e8f0')

    # Convert Plotly figures to HTML DIV tags
    context = {
        'empty_state': False,
        'stats': stats_summary,
        'highest_revenue': highest_revenue,
        'highest_yield': highest_yield,
        'chart_land': op.plot(fig_land, output_type='div', include_plotlyjs=False),
        'chart_inv': op.plot(fig_inv, output_type='div', include_plotlyjs=False),
        'chart_rev': op.plot(fig_rev, output_type='div', include_plotlyjs=False),
        'chart_status': op.plot(fig_status, output_type='div', include_plotlyjs=False),
        'chart_timeline': op.plot(fig_timeline, output_type='div', include_plotlyjs=False),
    }
    return render(request, 'crops/analytics.html', context)


# Instantiate the ML engine as a singleton
ml_engine = DiseaseMLEngine()

@login_required
def disease_prediction_view(request):
    """
    Handles crop disease classification predictions.
    Saves predictions to SQLite and displays prediction logs.
    """
    form = DiseasePredictionForm(request.POST or None)
    prediction_result = None
    
    if request.method == 'POST' and form.is_valid():
        crop_name = form.cleaned_data['crop_name']
        temp = form.cleaned_data['temperature']
        humidity = form.cleaned_data['humidity']
        rainfall = form.cleaned_data['rainfall']
        soil_type = form.cleaned_data['soil_type']
        ml_model = form.cleaned_data['ml_model']
        
        # Run classification ML prediction
        disease, confidence, treatment, prevention_tips = ml_engine.predict(
            crop_name=crop_name,
            temp=temp,
            humidity=humidity,
            rainfall=rainfall,
            soil_type=soil_type,
            model_type=ml_model
        )
        
        # Save to database log
        pred_record = DiseasePrediction.objects.create(
            farmer=request.user,
            crop_name=crop_name,
            temperature=temp,
            humidity=humidity,
            rainfall=rainfall,
            soil_type=soil_type,
            ml_model=ml_model,
            disease=disease,
            confidence=confidence,
            treatment=treatment
        )
        
        prediction_result = {
            'id': pred_record.id,
            'crop_name': crop_name,
            'disease': disease,
            'confidence': round(confidence, 1),
            'treatment': treatment,
            'prevention_tips': prevention_tips,
            'ml_model': ml_model
        }
        messages.success(request, f"Disease prediction completed using {ml_model} classifier.")
        
    # Load recent 10 predictions history
    history = DiseasePrediction.objects.filter(farmer=request.user)
    
    context = {
        'form': form,
        'result': prediction_result,
        'history': history,
        'crop_display_names': dict(DiseasePredictionForm.CROP_CHOICES),
        'soil_display_names': dict(DiseasePredictionForm.SOIL_CHOICES)
    }
    return render(request, 'crops/disease_prediction.html', context)


@login_required
def disease_prediction_pdf(request, pk):
    prediction = get_object_or_404(DiseasePrediction, pk=pk, farmer=request.user)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="smartfarmer_diagnostic_{prediction.id}.pdf"'
    
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    # Setup document
    doc = SimpleDocTemplate(response, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    # Custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#2e7d32'),
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        spaceAfter=25
    )
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#1b5e20'),
        spaceBefore=15,
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        leading=14
    )
    treatment_style = ParagraphStyle(
        'TreatmentText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#1b5e20'),
        leading=14
    )
    
    # Header block
    story.append(Paragraph("SmartFarmer AI Diagnostic Report", title_style))
    story.append(Paragraph(f"Generated on {prediction.created_at.strftime('%d/%m/%Y at %H:%M')} | Farmer: {request.user.get_full_name() or request.user.username}", subtitle_style))
    
    # Section 1: Farmer & Field Details
    story.append(Paragraph("1. General Information", h2_style))
    
    # Get profile details safely
    village = "N/A"
    district = "N/A"
    primary_crop = "N/A"
    land_size = "0"
    
    if hasattr(request.user, 'profile'):
        village = request.user.profile.village or "N/A"
        district = request.user.profile.district or "N/A"
        primary_crop = request.user.profile.primary_crop or "N/A"
        land_size = str(request.user.profile.land_size or "0")
        
    info_data = [
        [Paragraph("<b>Farmer Name:</b>", body_style), Paragraph(request.user.get_full_name() or request.user.username, body_style),
         Paragraph("<b>Location:</b>", body_style), Paragraph(f"{village}, {district}", body_style)],
        [Paragraph("<b>Primary Crop:</b>", body_style), Paragraph(primary_crop, body_style),
         Paragraph("<b>Land Size:</b>", body_style), Paragraph(f"{land_size} Acres", body_style)]
    ]
    info_table = Table(info_data, colWidths=[100, 150, 100, 150])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # Section 2: Input Parameters
    story.append(Paragraph("2. Diagnostic Inputs", h2_style))
    
    # Resolve display names
    crop_display = prediction.crop_name
    for val, label in DiseasePredictionForm.CROP_CHOICES:
        if val == prediction.crop_name:
            crop_display = label
            break
            
    soil_display = prediction.soil_type
    for val, label in DiseasePredictionForm.SOIL_CHOICES:
        if val == prediction.soil_type:
            soil_display = label
            break
            
    input_data = [
        [Paragraph("<b>Crop Analyzed:</b>", body_style), Paragraph(crop_display, body_style)],
        [Paragraph("<b>Soil Type:</b>", body_style), Paragraph(soil_display, body_style)],
        [Paragraph("<b>Temperature:</b>", body_style), Paragraph(f"{prediction.temperature} &deg;C", body_style)],
        [Paragraph("<b>Relative Humidity:</b>", body_style), Paragraph(f"{prediction.humidity} %", body_style)],
        [Paragraph("<b>Rainfall Level:</b>", body_style), Paragraph(f"{prediction.rainfall} mm", body_style)],
    ]
    input_table = Table(input_data, colWidths=[150, 350])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 15))
    
    # Section 3: Diagnostic Result
    story.append(Paragraph("3. AI Diagnostic Analysis", h2_style))
    result_data = [
        [Paragraph("<b>AI ML Classifier Model:</b>", body_style), Paragraph(prediction.ml_model, body_style)],
        [Paragraph("<b>Predicted Status / Disease:</b>", body_style), Paragraph(f"<b>{prediction.disease}</b>", body_style)],
        [Paragraph("<b>Confidence Score:</b>", body_style), Paragraph(f"<b>{prediction.confidence}%</b>", body_style)],
    ]
    result_table = Table(result_data, colWidths=[150, 350])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e8f5e9') if prediction.disease == 'Healthy' else colors.HexColor('#ffebee')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#c8e6c9') if prediction.disease == 'Healthy' else colors.HexColor('#ffcdd2')),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 15))
    
    # Section 4: Recommended Treatment
    story.append(Paragraph("4. Recommended Treatment Schedule", h2_style))
    treatment_data = [[Paragraph(prediction.treatment, treatment_style)]]
    treatment_table = Table(treatment_data, colWidths=[500])
    treatment_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f1f8e9')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dcedc8')),
    ]))
    story.append(treatment_table)
    story.append(Spacer(1, 20))
    
    # Disclaimer footer
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        alignment=1 # Center
    )
    story.append(Paragraph("Disclaimer: This report is generated by an artificial intelligence model and is intended for informational assistance. Please consult a qualified agricultural expert or your local Krishi Vigyan Kendra before executing any chemical spraying.", disclaimer_style))
    
    doc.build(story)
    return response
