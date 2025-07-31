import streamlit as st
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import PyPDF2, pdfplumber
from PyPDF2 import PdfReader
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import hashlib

# Configure page
st.set_page_config(
    page_title="CrashML - AV Accident Fault Analyzer",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.fault-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.not-fault { background-color: #d4edda; border-left: 5px solid #28a745; }
.partial-fault { background-color: #fff3cd; border-left: 5px solid #ffc107; }
.full-fault { background-color: #f8d7da; border-left: 5px solid #dc3545; }
</style>
""", unsafe_allow_html=True)

# Optional manual reset for dev/testing
with st.sidebar:
    if st.button("🔄 Clear Session Cache"):
        st.session_state.clear()
        st.rerun()

# Load pre-trained models and vectorizers
@st.cache_resource
def load_models():
    try:
        models = pickle.load(open('crashml_models.pkl', 'rb'))
        vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
        feature_names = pickle.load(open('feature_names.pkl', 'rb'))
        return models, vectorizer, feature_names
    except FileNotFoundError:
        st.error("Model files not found. Please ensure you've saved your trained models.")
        return None, None, None

def get_file_hash(uploaded_file):
    """Generate a unique hash for the uploaded file"""
    file_bytes = uploaded_file.getvalue()
    return hashlib.md5(file_bytes).hexdigest()

def extract_text_from_pdf_bytes(file_bytes):
    """Enhanced text extraction with better coverage"""
    try:
        text = ""
        
        # Method 1: Extract all text (not just bottom 35%)
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {page_num + 1} ---\n{page_text}\n"
        
        # Method 2: Also try to extract checkbox states
        try:
            reader = PdfReader(BytesIO(file_bytes))
            for page in reader.pages:
                # Try to extract annotations/form data
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        annot_obj = annotation.get_object()
                        if '/AS' in annot_obj:  # Appearance state (for checkboxes)
                            text += f" CHECKBOX_STATE: {annot_obj['/AS']} "
        except Exception as e:
            st.write(f"Note: Could not extract checkbox states: {str(e)}")
        
        return text
        
    except Exception as e:
        st.error(f"Enhanced text extraction failed: {e}")
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
        st.write(f"Note: Could not extract form fields: {str(e)}")
        return {}

def process_pdf(file_hash, file_content):
    """Process PDF and cache results based on file hash"""
    # Extract text and form fields
    extracted_text = extract_text_from_pdf_bytes(file_content)
    form_fields = extract_form_fields_from_pdf_bytes(file_content)
    return extracted_text, form_fields

def parse_dmv_report(text, form_fields):
    """Enhanced DMV report parser to extract key features with better differentiation"""
    
    st.error("🔧 USING ENHANCED PARSER - This message confirms the new parser is running!")

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
    
    # Debug: Print what we're working with
    st.write("**Debug - Parsing Information:**")
    st.write(f"Text length: {len(text)} characters")
    st.write(f"Form fields found: {len(form_fields)}")
    
    # 1. AUTONOMOUS MODE DETECTION (Enhanced)
    autonomous_indicators = [
        'autonomous mode',
        'autonomous vehicle', 
        'self-driving',
        'autopilot',
        '☑ autonomous mode',  # Checked box
        'aurora innovation',  # Aurora is autonomous
        'waymo',             # Waymo is autonomous
        'cruise',            # Cruise is autonomous
        'tesla autopilot'
    ]
    
    if any(indicator in text_lower for indicator in autonomous_indicators):
        data_point['autonomous_mode'] = 1
        st.write("✅ Autonomous mode detected")
    
    # 2. VEHICLE MOVEMENT DETECTION (Enhanced)
    # Check for "Stopped in Traffic" checkbox first
    if '☑ stopped in traffic' in text_lower or 'x stopped in traffic' in text_lower:
        data_point['vehicle_1_moving'] = 0
        st.write("✅ Vehicle 1 stopped in traffic (from checkbox)")
    # Check for "Moving" checkbox
    elif '☑ moving' in text_lower or 'x moving' in text_lower:
        data_point['vehicle_1_moving'] = 1
        st.write("✅ Vehicle 1 moving (from checkbox)")
    # Check for text indicators
    elif any(keyword in text_lower for keyword in ['proceeding straight', 'making right turn', 'making left turn', 'changing lanes', 'traveling']):
        data_point['vehicle_1_moving'] = 1
        st.write("✅ Vehicle 1 moving (from text description)")
    elif any(keyword in text_lower for keyword in ['stopped', 'parked', 'stationary']):
        data_point['vehicle_1_moving'] = 0
        st.write("✅ Vehicle 1 stationary (from text description)")
    
    # 3. DAMAGE/IMPACT DETECTION (Enhanced)
    # Check damage checkboxes
    if '☑ none' in text_lower or 'x none' in text_lower:
        st.write("✅ No damage reported")
        # No impact detected
    elif '☑ minor' in text_lower or 'x minor' in text_lower:
        st.write("✅ Minor damage reported")
        # Try to determine impact location from description
        if any(word in text_lower for word in ['rear', 'back', 'behind']):
            data_point['impact_rear'] = 1
        elif any(word in text_lower for word in ['front', 'head-on', 'forward']):
            data_point['impact_front'] = 1
        elif any(word in text_lower for word in ['side', 'sideswipe', 'lateral']):
            data_point['impact_side'] = 1
    
    # Check for collision type from the form checkboxes
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
            st.write(f"✅ {collision_text} collision detected")
    
    # 4. WEATHER CONDITIONS (Enhanced)
    weather_conditions = {
        'raining': 'weather_issue',
        'rain': 'weather_issue',
        'snowing': 'weather_issue', 
        'snow': 'weather_issue',
        'fog': 'weather_issue',
        'foggy': 'weather_issue',
        'storm': 'weather_issue',
        'wind': 'weather_issue',
        '☑ raining': 'weather_issue',
        '☑ snowing': 'weather_issue',
        '☑ fog': 'weather_issue'
    }
    
    for weather_text, field in weather_conditions.items():
        if weather_text in text_lower:
            data_point[field] = 1
            st.write(f"✅ Weather condition detected: {weather_text}")
    
    # 5. ROAD CONDITIONS (Enhanced)
    road_conditions = {
        'wet': 'road_issue',
        'slippery': 'road_issue',
        'icy': 'road_issue',
        'snowy': 'road_issue',
        'construction': 'road_issue',
        'repair zone': 'road_issue',
        'obstruction': 'road_issue',
        'flooded': 'road_issue',
        '☑ wet': 'road_issue',
        '☑ snowy': 'road_issue',
        '☑ construction': 'road_issue'
    }
    
    for road_text, field in road_conditions.items():
        if road_text in text_lower:
            data_point[field] = 1
            st.write(f"✅ Road condition detected: {road_text}")
    
    # 6. LIGHTING CONDITIONS (Enhanced)
    lighting_conditions = [
        'dark', 'night', 'dusk', 'dawn', 
        'dark – street lights', 'dark – no street lights',
        '☑ dark', '☑ dusk'
    ]
    
    if any(condition in text_lower for condition in lighting_conditions):
        # But exclude "daylight"
        if 'daylight' not in text_lower:
            data_point['dark_condition'] = 1
            st.write("✅ Dark/poor lighting condition detected")
    
    # 7. VEHICLE 2 MOVEMENT (Enhanced)
    # Look for information about the other vehicle
    vehicle2_moving_indicators = [
        'other vehicle moving',
        'other vehicle was moving',
        'second vehicle moving',
        'vehicle 2 moving'
    ]
    
    vehicle2_stopped_indicators = [
        'other vehicle stopped',
        'other vehicle was stopped', 
        'second vehicle stopped',
        'vehicle 2 stopped'
    ]
    
    if any(indicator in text_lower for indicator in vehicle2_moving_indicators):
        data_point['vehicle_2_moving'] = 1
        st.write("✅ Vehicle 2 was moving")
    elif any(indicator in text_lower for indicator in vehicle2_stopped_indicators):
        data_point['vehicle_2_moving'] = 0
        st.write("✅ Vehicle 2 was stopped")
    
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
            st.write(f"✅ {manufacturer.title()} vehicle detected - applied manufacturer rules")
    
    # 9. ENHANCED DESCRIPTION ANALYSIS
    # Look for specific phrases that indicate fault scenarios
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
            st.write(f"✅ Fault indicator detected: '{phrase}'")
    
    # 10. SUMMARY DEBUG INFO
    st.write("**Final extracted features:**")
    for key, value in data_point.items():
        if key != 'description':
            st.write(f"  • {key}: {value}")
    
    return data_point

def predict_fault(data_point, models, vectorizer, feature_names):
    """Make prediction using the trained models"""
    
    # Extract structured features
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
    
    # Extract text features
    text_features = vectorizer.transform([data_point['description']])
    text_features_array = text_features.toarray()[0]
    
    # Pad TF-IDF vector if it's smaller than expected
    expected_text_features = 216 - len(structured_features)  # = 207
    actual_text_features = text_features_array.shape[0]

    if actual_text_features < expected_text_features:
        # Pad with zeros
        padded_text_features = np.pad(text_features_array, (0, expected_text_features - actual_text_features))
    elif actual_text_features > expected_text_features:
        # Truncate if longer (shouldn't happen)
        padded_text_features = text_features_array[:expected_text_features]
    else:
        padded_text_features = text_features_array

    # Combine all features
    all_features = np.concatenate([structured_features, padded_text_features]).reshape(1, -1)
    
    # Make predictions with all models
    predictions = {}
    probabilities = {}
    
    for model_name, model in models.items():
        pred = model.predict(all_features)[0]
        prob = model.predict_proba(all_features)[0]
        
        predictions[model_name] = pred
        probabilities[model_name] = prob
    
    return predictions, probabilities, all_features

def explain_prediction(data_point, models, feature_names, all_features):
    """Provide explanation for the prediction"""
    
    explanations = []
    
    # Rule-based explanations
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
    
    # Feature importance from best model
    best_model = models['Gradient Boosting']
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        top_features = np.argsort(importances)[-5:][::-1]
        
        explanations.append("\n**Top Contributing Factors:**")
        for i, feature_idx in enumerate(top_features):
            if feature_idx < len(feature_names):
                feature_name = feature_names[feature_idx]
                importance = importances[feature_idx]
                feature_value = all_features[0][feature_idx]
                explanations.append(f"{i+1}. {feature_name}: {feature_value:.3f} (importance: {importance:.3f})")
    
    return explanations

# Main App
def main():
    st.markdown('<h1 class="main-header">🚗 CrashML: AV Accident Fault Analyzer</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Upload a California DMV Autonomous Vehicle Collision Report to analyze fault attribution using machine learning.**
    
    This system uses a trained CrashML model that combines structured data analysis with natural language processing 
    to predict fault classification and provide explanatory insights.
    """)
    
    # Load models
    models, vectorizer, feature_names = load_models()
    
    if models is None:
        st.stop()
    
    # Sidebar for model information
    with st.sidebar:
        st.header("📊 Model Information")
        st.write("**Models Available:**")
        st.write("• Random Forest")
        st.write("• Gradient Boosting")
        st.write("• Logistic Regression")
        
        st.write("**Training Data:**")
        st.write("• 563 accident reports")
        st.write("• 2019-2024 timeframe")
        st.write("• California DMV data")
        
        st.write("**Performance:**")
        st.write("• Test Accuracy: 81%")
        st.write("• Validation Accuracy: 85%")
        st.write("• Multi-class classification")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file (California DMV Collision Report)",
        type=['pdf'],
        help="Upload the PDF report from California DMV website"
    )
    
    if uploaded_file is not None:
        # Display file name as feedback
        st.caption(f"Currently analyzing: `{uploaded_file.name}`")
        
        # Generate unique hash for this file
        current_file_hash = get_file_hash(uploaded_file)
        
        # Check if we've processed this exact file before
        if 'processed_files' not in st.session_state:
            st.session_state.processed_files = {}
        
        # Only process if it's a new file or file has changed
        if current_file_hash not in st.session_state.processed_files:
            st.success("✅ File uploaded successfully!")
            
            # Get file content for processing
            file_content = uploaded_file.getvalue()
            
            # Extract text and form fields - direct extraction to avoid caching issues
            with st.spinner("Extracting text from PDF..."):
                try:
                    extracted_text = extract_text_from_pdf_bytes(file_content)
                    form_fields = extract_form_fields_from_pdf_bytes(file_content)
                except Exception as e:
                    st.error(f"Error processing PDF: {str(e)}")
                    extracted_text = ""
                    form_fields = {}
            
            if extracted_text:
                # Show extracted text (first 500 characters)
                with st.expander("📄 Extracted Text Preview"):
                    st.text_area("Text Preview", extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, height=200)
                
                # Parse the report
                with st.spinner("Parsing report data..."):
                    parsed_data = parse_dmv_report(extracted_text, form_fields)
                
                # Make prediction
                with st.spinner("Analyzing fault attribution..."):
                    predictions, probabilities, all_features = predict_fault(
                        parsed_data, models, vectorizer, feature_names
                    )
                
                # Store results in session state
                st.session_state.processed_files[current_file_hash] = {
                    'filename': uploaded_file.name,
                    'extracted_text': extracted_text,
                    'parsed_data': parsed_data,
                    'predictions': predictions,
                    'probabilities': probabilities,
                    'all_features': all_features
                }
            else:
                st.error("❌ No text extracted from the PDF. Please check the file format.")
        else:
            st.success("✅ File already processed!")
        
        # Get results (either newly processed or from cache)
        if current_file_hash in st.session_state.processed_files:
            results = st.session_state.processed_files[current_file_hash]
            
            # Display results
            st.header("🎯 Fault Analysis Results")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Fault classification results
                fault_labels = {0: "Not at Fault", 1: "Partially at Fault", 2: "Fully at Fault"}
                fault_colors = {0: "#28a745", 1: "#ffc107", 2: "#dc3545"}
                
                for model_name, prediction in results['predictions'].items():
                    fault_label = fault_labels[prediction]
                    color = fault_colors[prediction]
                    
                    st.markdown(f"""
                    <div class="fault-card" style="background-color: {color}20; border-left: 5px solid {color};">
                        <h4>{model_name}: {fault_label}</h4>
                        <p>Confidence: {results['probabilities'][model_name][prediction]:.1%}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Probability visualization
                best_model = "Gradient Boosting"
                prob_data = results['probabilities'][best_model]
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=["Not at Fault", "Partially at Fault", "Fully at Fault"],
                        y=prob_data,
                        marker_color=['#28a745', '#ffc107', '#dc3545']
                    )
                ])
                fig.update_layout(
                    title="Prediction Probabilities",
                    yaxis_title="Probability",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Explanation
            st.header("🔍 Analysis Explanation")
            explanations = explain_prediction(results['parsed_data'], models, feature_names, results['all_features'])
            
            for explanation in explanations:
                st.write(explanation)
            
            # Feature summary
            st.header("📋 Extracted Features Summary")
            parsed_data = results['parsed_data']
            feature_summary = pd.DataFrame([
                ["Vehicle 1 Moving", "Yes" if parsed_data['vehicle_1_moving'] else "No"],
                ["Vehicle 2 Moving", "Yes" if parsed_data['vehicle_2_moving'] else "No"],
                ["Autonomous Mode", "Yes" if parsed_data['autonomous_mode'] else "No"],
                ["Impact Location", "Front" if parsed_data['impact_front'] else "Rear" if parsed_data['impact_rear'] else "Side" if parsed_data['impact_side'] else "Unknown"],
                ["Weather Issues", "Yes" if parsed_data['weather_issue'] else "No"],
                ["Road Issues", "Yes" if parsed_data['road_issue'] else "No"],
                ["Dark Conditions", "Yes" if parsed_data['dark_condition'] else "No"]
            ], columns=["Feature", "Value"])
            
            st.table(feature_summary)
            
            # Show processed files in sidebar
            with st.sidebar:
                st.header("📁 Processed Files")
                for file_hash, file_data in st.session_state.processed_files.items():
                    if file_hash == current_file_hash:
                        st.write(f"🔄 **{file_data['filename']}** (current)")
                    else:
                        st.write(f"✅ {file_data['filename']}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **CrashML Fault Analyzer** | Developed by Florida Perfect Rwejuna | 
    Advisors: Dr. Alae Loukilli, Dr. Nishat Majid, Mithun Goutham
    """)

if __name__ == "__main__":
    main()