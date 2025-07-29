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

# Load pre-trained models and vectorizers
@st.cache_resource
def load_models():
    try:
        # You'll need to save these from your Google Colab training
        models = pickle.load(open('crashml_models.pkl', 'rb'))
        vectorizer = pickle.load(open('tfidf_vectorizer.pkl', 'rb'))
        feature_names = pickle.load(open('feature_names.pkl', 'rb'))
        return models, vectorizer, feature_names
    except FileNotFoundError:
        st.error("Model files not found. Please ensure you've saved your trained models.")
        return None, None, None

def extract_text_from_pdf(uploaded_file):
    """Extracts text from the bottom portion of each page"""
    try:
        text = ""
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                width, height = page.width, page.height
                # Bottom 35% of the page where most narratives are
                bbox = (0, height * 0.65, width, height)
                region = page.within_bbox(bbox)
                if region:
                    region_text = region.extract_text()
                    if region_text:
                        text += region_text + "\n"
        return text
    except Exception as e:
        st.error(f"Text extraction failed: {e}")
        return ""


def extract_form_fields_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        reader = PdfReader(uploaded_file)
        fields = reader.get_fields()
        if not fields:
            return {}

        extracted = {k: v["/V"] for k, v in fields.items() if isinstance(v, dict) and "/V" in v}
        return extracted

    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def parse_dmv_report(text, form_fields):

    """Parse DMV report text to extract key features"""
    # This function mirrors the data extraction logic; adapt this based on your actual parsing logic
    
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
    
    # Extract autonomous mode
    if any(keyword in text.lower() for keyword in ['autonomous', 'autopilot', 'self-driving']):
        data_point['autonomous_mode'] = 1
    
    # Extract vehicle movement
    if any(keyword in text.lower() for keyword in ['moving', 'traveling', 'driving']):
        data_point['vehicle_1_moving'] = 1
    
    # Extract impact points
    if any(keyword in text.lower() for keyword in ['rear end', 'rear-end', 'rear impact']):
        data_point['impact_rear'] = 1
    elif any(keyword in text.lower() for keyword in ['front end', 'front impact']):
        data_point['impact_front'] = 1
    elif any(keyword in text.lower() for keyword in ['side impact', 'side collision']):
        data_point['impact_side'] = 1
    
    # Extract weather conditions
    if any(keyword in text.lower() for keyword in ['rain', 'snow', 'fog', 'storm']):
        data_point['weather_issue'] = 1
    
    # Extract road conditions
    if any(keyword in text.lower() for keyword in ['wet', 'slippery', 'construction']):
        data_point['road_issue'] = 1
    
    # Extract lighting conditions
    if any(keyword in text.lower() for keyword in ['dark', 'night', 'dusk']):
        data_point['dark_condition'] = 1
    
    return data_point

#reverted back to original function
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
    
    # Feature importance from best model (you can customize this)
    best_model = models['Gradient Boosting']  # Assuming this was your best model
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

        # Check if this is a new file
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            st.session_state.last_uploaded_file = uploaded_file.name
            st.rerun()

        st.success("✅ File uploaded successfully!")
        
        # Extract text
        with st.spinner("Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file) #for natural language narrative
            form_fields = extract_form_fields_from_pdf(uploaded_file) #for structured fields
        
        if extracted_text:
            # Show extracted text (first 500 characters)
            with st.expander("📄 Extracted Text Preview"):
                st.text_area("Text Preview", extracted_text[:500] + "...", height=200)
            
            # Parse the report
            with st.spinner("Parsing report data..."):
                parsed_data = parse_dmv_report(extracted_text, form_fields)
            
            # Make prediction
            with st.spinner("Analyzing fault attribution..."):
                predictions, probabilities, all_features = predict_fault(
                    parsed_data, models, vectorizer, feature_names)
                
            
            # Display results
            st.header("🎯 Fault Analysis Results")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Fault classification results
                fault_labels = {0: "Not at Fault", 1: "Partially at Fault", 2: "Fully at Fault"}
                fault_colors = {0: "#28a745", 1: "#ffc107", 2: "#dc3545"}
                
                for model_name, prediction in predictions.items():
                    fault_label = fault_labels[prediction]
                    color = fault_colors[prediction]
                    
                    st.markdown(f"""
                    <div class="fault-card" style="background-color: {color}20; border-left: 5px solid {color};">
                        <h4>{model_name}: {fault_label}</h4>
                        <p>Confidence: {probabilities[model_name][prediction]:.1%}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                # Probability visualization
                best_model = "Gradient Boosting"  # You can make this dynamic
                prob_data = probabilities[best_model]
                
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
            explanations = explain_prediction(parsed_data, models, feature_names, all_features)
            
            for explanation in explanations:
                st.write(explanation)
            
            # Feature summary
            st.header("📋 Extracted Features Summary")
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
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **CrashML Fault Analyzer** | Developed by Florida Perfect Rwejuna | 
    Advisors: Dr. Alae Loukilli, Dr. Nishat Majid, Mithun Goutham
    """)

if __name__ == "__main__":
    main()