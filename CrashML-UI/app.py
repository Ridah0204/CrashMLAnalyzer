from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import pickle
import PyPDF2, pdfplumber
from PyPDF2 import PdfReader
from io import BytesIO
import json
import os
from werkzeug.utils import secure_filename
import hashlib
import re
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load models globally
models = None
vectorizer = None
feature_names = None

def load_models():
    global models, vectorizer, feature_names
    try:
        models = pickle.load(open('crashml_models.pkl', 'rb'))
        vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
        feature_names = pickle.load(open('feature_names.pkl', 'rb'))
        return True
    except FileNotFoundError:
        print("Model files not found")
        return False

def extract_text_from_pdf_bytes(file_bytes):
    """Enhanced text extraction with better coverage"""
    try:
        text = ""
        
        # Method 1: Extract all text using pdfplumber
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {page_num + 1} ---\n{page_text}\n"
        
        # Method 2: Try to extract checkbox states
        try:
            reader = PdfReader(BytesIO(file_bytes))
            for page in reader.pages:
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        annot_obj = annotation.get_object()
                        if '/AS' in annot_obj:
                            text += f" CHECKBOX_STATE: {annot_obj['/AS']} "
        except Exception as e:
            print(f"Could not extract checkbox states: {str(e)}")
        
        return text
        
    except Exception as e:
        print(f"Enhanced text extraction failed: {e}")
        return ""

def extract_form_fields_from_pdf_bytes(file_bytes):
    """Extract form fields from PDF bytes"""
    try:
        reader = PdfReader(BytesIO(file_bytes))
        fields = reader.get_fields()
        if not fields:
            return {}
        
        extracted = {k: v["/V"] for k, v in fields.items() if isinstance(v, dict) and "/V" in v}
        return extracted
    except Exception as e:
        print(f"Error extracting form fields: {str(e)}")
        return {}

def parse_dmv_report(text, form_fields):
    """Enhanced DMV report parser to extract key features"""
    
    # Initialize data point
    data_point = {
        'vehicle_1_moving': 0,
        'vehicle_2_moving': 0,
        'autonomous_mode': 0,
        'impact_front': 0,
        'impact_rear': 0,
        'impact_side': 0,
        'weather_issue': 0,
        'road_issue': 0,
        'dark_condition': 0,
        'description': text
    }
    
    # Convert text to lowercase for easier matching
    text_lower = text.lower()
    
    # Debug information
    debug_info = []
    debug_info.append(f"Text length: {len(text)} characters")
    debug_info.append(f"Form fields found: {len(form_fields)}")
    
    # 1. AUTONOMOUS MODE DETECTION
    autonomous_indicators = [
        'autonomous mode',
        'autonomous vehicle', 
        'self-driving',
        'autopilot',
        '☑ autonomous mode',
        'aurora innovation',
        'waymo llc',
        'waymo',
        'cruise',
        'tesla autopilot',
        'apple inc'
    ]
    
    if any(indicator in text_lower for indicator in autonomous_indicators):
        data_point['autonomous_mode'] = 1
        debug_info.append("✅ Autonomous mode detected")
    
    # 2. VEHICLE MOVEMENT DETECTION
    if '☑ stopped in traffic' in text_lower or 'x stopped in traffic' in text_lower:
        data_point['vehicle_1_moving'] = 0
        debug_info.append("✅ Vehicle 1 stopped in traffic (from checkbox)")
    elif '☑ moving' in text_lower or 'x moving' in text_lower:
        data_point['vehicle_1_moving'] = 1
        debug_info.append("✅ Vehicle 1 moving (from checkbox)")
    elif any(keyword in text_lower for keyword in ['proceeding straight', 'making right turn', 'making left turn', 'changing lanes', 'traveling']):
        data_point['vehicle_1_moving'] = 1
        debug_info.append("✅ Vehicle 1 moving (from text description)")
    elif any(keyword in text_lower for keyword in ['stopped', 'parked', 'stationary']):
        data_point['vehicle_1_moving'] = 0
        debug_info.append("✅ Vehicle 1 stationary (from text description)")
    
    # 3. DAMAGE/IMPACT DETECTION
    if '☑ none' in text_lower or 'x none' in text_lower:
        debug_info.append("✅ No damage reported")
    elif '☑ minor' in text_lower or 'x minor' in text_lower:
        debug_info.append("✅ Minor damage reported")
        # Try to determine impact location from description
        if any(word in text_lower for word in ['rear', 'back', 'behind']):
            data_point['impact_rear'] = 1
        elif any(word in text_lower for word in ['front', 'head-on', 'forward']):
            data_point['impact_front'] = 1
        elif any(word in text_lower for word in ['side', 'sideswipe', 'lateral']):
            data_point['impact_side'] = 1
        else:
            # Default to front impact for minor damage
            data_point['impact_front'] = 1
    elif '☑ major' in text_lower or 'x major' in text_lower:
        debug_info.append("✅ Major damage reported")
        data_point['impact_front'] = 1  # Assume front impact for major damage
    
    # 4. COLLISION TYPE DETECTION
    collision_types = {
        'rear end': 'impact_rear',
        'rear-end': 'impact_rear', 
        'head-on': 'impact_front',
        'broadside': 'impact_side',
        'side swipe': 'impact_side',
        'sideswipe': 'impact_side'
    }
    
    for collision_text, impact_field in collision_types.items():
        if collision_text in text_lower:
            data_point[impact_field] = 1
            debug_info.append(f"✅ {collision_text} collision detected")
    
    # 5. WEATHER CONDITIONS
    weather_conditions = [
        'raining', 'rain', 'snowing', 'snow', 'fog', 'foggy', 'storm', 'wind'
    ]
    
    for weather in weather_conditions:
        if weather in text_lower:
            data_point['weather_issue'] = 1
            debug_info.append(f"✅ Weather condition detected: {weather}")
            break
    
    # 6. ROAD CONDITIONS
    road_conditions = [
        'wet', 'slippery', 'icy', 'snowy', 'construction', 'repair zone', 'obstruction', 'flooded'
    ]
    
    for road in road_conditions:
        if road in text_lower:
            data_point['road_issue'] = 1
            debug_info.append(f"✅ Road condition detected: {road}")
            break
    
    # 7. LIGHTING CONDITIONS
    lighting_conditions = [
        'dark', 'night', 'dusk', 'dawn', 'dark – street lights', 'dark – no street lights'
    ]
    
    if any(condition in text_lower for condition in lighting_conditions):
        if 'daylight' not in text_lower:
            data_point['dark_condition'] = 1
            debug_info.append("✅ Dark/poor lighting condition detected")
    
    # 8. MANUFACTURER-SPECIFIC LOGIC
    manufacturers = {
        'waymo': {'autonomous_mode': 1},
        'aurora': {'autonomous_mode': 1},
        'cruise': {'autonomous_mode': 1},
        'tesla': {'autonomous_mode': 1},
        'apple': {'autonomous_mode': 1}
    }
    
    for manufacturer, attributes in manufacturers.items():
        if manufacturer in text_lower:
            for attr, value in attributes.items():
                data_point[attr] = value
            debug_info.append(f"✅ {manufacturer.title()} vehicle detected")
    
    # 9. ENHANCED DESCRIPTION ANALYSIS
    fault_indicators = {
        'rear ended': {'impact_rear': 1, 'vehicle_1_moving': 0},
        'struck from behind': {'impact_rear': 1, 'vehicle_1_moving': 0},
        'hit from behind': {'impact_rear': 1, 'vehicle_1_moving': 0},
        'ran into': {'impact_front': 1, 'vehicle_1_moving': 1},
        'collided with': {'vehicle_1_moving': 1},
        'lane change': {'vehicle_1_moving': 1},
        'changing lanes': {'vehicle_1_moving': 1},
        'merging': {'vehicle_1_moving': 1},
        'turning': {'vehicle_1_moving': 1}
    }
    
    for phrase, attributes in fault_indicators.items():
        if phrase in text_lower:
            for attr, value in attributes.items():
                data_point[attr] = value
            debug_info.append(f"✅ Fault indicator detected: '{phrase}'")
    
    # Add debug info to data point
    data_point['debug_info'] = debug_info
    
    return data_point

def predict_fault(data_point):
    """Make prediction using trained models"""
    structured_features = [
        data_point['vehicle_1_moving'],
        data_point['vehicle_2_moving'],
        data_point['autonomous_mode'],
        data_point['impact_front'],
        data_point['impact_rear'],
        data_point['impact_side'],
        data_point['weather_issue'],
        data_point['road_issue'],
        data_point['dark_condition']
    ]
    
    text_features = vectorizer.transform([data_point['description']])
    text_features_array = text_features.toarray()[0]
    
    # Pad TF-IDF vector if needed
    expected_text_features = 216 - len(structured_features)
    actual_text_features = text_features_array.shape[0]

    if actual_text_features < expected_text_features:
        padded_text_features = np.pad(text_features_array, (0, expected_text_features - actual_text_features))
    elif actual_text_features > expected_text_features:
        padded_text_features = text_features_array[:expected_text_features]
    else:
        padded_text_features = text_features_array

    all_features = np.concatenate([structured_features, padded_text_features])
    all_features = all_features.reshape(1, -1)
    
    predictions = {}
    probabilities = {}
    
    fault_labels = {0: "Not at Fault", 1: "Partially at Fault", 2: "Fully at Fault"}
    
    for model_name, model in models.items():
        pred = model.predict(all_features)[0]
        prob = model.predict_proba(all_features)[0]
        
        predictions[model_name] = {
            'prediction': int(pred),
            'label': fault_labels[pred],
            'confidence': float(prob[pred])
        }
        probabilities[model_name] = prob.tolist()
    
    return predictions, probabilities

def explain_prediction(data_point):
    """Provide explanation for the prediction"""
    explanations = []
    
    if data_point['vehicle_1_moving'] == 0:
        explanations.append("✓ Vehicle was stationary (typically not at fault)")
    
    if data_point['impact_rear'] == 1:
        explanations.append("✓ Rear impact detected (typically other vehicle at fault)")
    
    if data_point['autonomous_mode'] == 1:
        explanations.append("⚠ Vehicle was in autonomous mode")
    
    if data_point['weather_issue'] == 1:
        explanations.append("⚠ Adverse weather conditions present")
    
    if data_point['road_issue'] == 1:
        explanations.append("⚠ Adverse road conditions present")
    
    if data_point['dark_condition'] == 1:
        explanations.append("⚠ Dark/poor lighting conditions")
    
    return explanations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Read file content
            with open(filepath, 'rb') as f:
                file_bytes = f.read()
            
            # Extract text and form fields
            text = extract_text_from_pdf_bytes(file_bytes)
            form_fields = extract_form_fields_from_pdf_bytes(file_bytes)
            
            if not text:
                return jsonify({'error': 'Could not extract text from PDF'})
            
            # Parse and predict
            parsed_data = parse_dmv_report(text, form_fields)
            predictions, probabilities = predict_fault(parsed_data)
            explanations = explain_prediction(parsed_data)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            # Prepare extracted features for display
            feature_summary = {
                'Vehicle 1 Moving': 'Yes' if parsed_data['vehicle_1_moving'] else 'No',
                'Vehicle 2 Moving': 'Yes' if parsed_data['vehicle_2_moving'] else 'No',
                'Autonomous Mode': 'Yes' if parsed_data['autonomous_mode'] else 'No',
                'Impact Location': 'Front' if parsed_data['impact_front'] else 'Rear' if parsed_data['impact_rear'] else 'Side' if parsed_data['impact_side'] else 'Unknown',
                'Weather Issues': 'Yes' if parsed_data['weather_issue'] else 'No',
                'Road Issues': 'Yes' if parsed_data['road_issue'] else 'No',
                'Dark Conditions': 'Yes' if parsed_data['dark_condition'] else 'No'
            }
            
            return jsonify({
                'success': True,
                'filename': filename,
                'predictions': predictions,
                'probabilities': probabilities,
                'feature_summary': feature_summary,
                'explanations': explanations,
                'debug_info': parsed_data.get('debug_info', []),
                'text_preview': text[:500] + '...' if len(text) > 500 else text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
        except Exception as e:
            # Clean up file if error occurs
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error processing file: {str(e)}'})
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF file.'})

@app.route('/model_info')
def model_info():
    return jsonify({
        'models': list(models.keys()) if models else [],
        'total_features': len(feature_names) if feature_names else 0,
        'training_info': {
            'dataset_size': '563 reports',
            'timeframe': '2019-2024',
            'source': 'California DMV',
            'test_accuracy': '81%',
            'validation_accuracy': '85%'
        }
    })

if __name__ == '__main__':
    if load_models():
        print("Models loaded successfully!")
        print("Available models:", list(models.keys()))
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to load models. Please ensure model files are available.")