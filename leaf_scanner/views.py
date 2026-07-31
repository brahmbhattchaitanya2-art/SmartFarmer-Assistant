import os
import json
import base64
import numpy as np
from PIL import Image

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import UploadLeafForm

_MODEL = None
_CLASS_NAMES = None

def get_model_and_classes():
    """Loads and caches the trained MobileNetV2 model and class labels."""
    global _MODEL, _CLASS_NAMES
    if _MODEL is None:
        import tensorflow as tf
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, 'leaf_disease_model.h5')
        classes_path = os.path.join(current_dir, 'class_names.json')
        
        if os.path.exists(model_path) and os.path.exists(classes_path):
            _MODEL = tf.keras.models.load_model(model_path)
            with open(classes_path, 'r') as f:
                _CLASS_NAMES = json.load(f)
        else:
            return None, None
    return _MODEL, _CLASS_NAMES

@login_required
def scan_leaf_view(request):
    form = UploadLeafForm()
    result = None
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_exists = os.path.exists(os.path.join(current_dir, 'leaf_disease_model.h5'))
    
    if request.method == 'POST':
        form = UploadLeafForm(request.POST, request.FILES)
        if form.is_valid():
            if not model_exists:
                messages.error(
                    request, 
                    "Classification model is not trained yet. Please run: 'python leaf_scanner/train_model.py' to train it first."
                )
                return render(request, 'leaf_scanner/scan.html', {'form': form, 'model_exists': model_exists})
            
            try:
                model, class_names = get_model_and_classes()
                if model is None or class_names is None:
                    raise FileNotFoundError("Model files could not be loaded.")
                
                # Retrieve uploaded file
                image_file = request.FILES['image']
                
                # 1. Convert image to base64 for stateless preview on the UI
                image_file.seek(0)
                encoded_img = base64.b64encode(image_file.read()).decode('utf-8')
                image_uri = f"data:{image_file.content_type};base64,{encoded_img}"
                
                # 2. Process image for MobileNetV2 prediction (224x224 RGB)
                image_file.seek(0)
                pil_img = Image.open(image_file).convert('RGB')
                pil_img = pil_img.resize((224, 224))
                
                # Prepare input tensor
                img_array = np.array(pil_img, dtype=np.float32)
                img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
                
                # Predict
                predictions = model.predict(img_array)
                pred_idx = np.argmax(predictions[0])
                raw_class = class_names[pred_idx]
                confidence_score = float(predictions[0][pred_idx]) * 100
                
                # Parse class name (e.g. Cotton_Alternaria_Leaf_Spot or Neem_Healthy)
                parts = raw_class.split('_')
                plant_name = parts[0]
                disease_name = " ".join(parts[1:])
                
                # Determine status
                is_healthy = "Healthy" in raw_class
                status = "Healthy" if is_healthy else "Diseased"
                
                result = {
                    'image_uri': image_uri,
                    'plant_name': plant_name,
                    'disease_name': disease_name,
                    'confidence': round(confidence_score, 2),
                    'status': status,
                    'is_healthy': is_healthy
                }
                messages.success(request, f"Diagnosis completed! Status: {status}")
                
            except Exception as e:
                messages.error(request, f"Failed to analyze leaf: {str(e)}")
                
    return render(request, 'leaf_scanner/scan.html', {
        'form': form,
        'result': result,
        'model_exists': model_exists
    })
