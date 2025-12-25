"""
Streamlit Demo App for Document Type Classification
"""

import streamlit as st
import torch
from PIL import Image
import os
from pathlib import Path
from model_loader import (
    load_vit_model, 
    load_resnet18_model, 
    predict_image, 
    get_device
)

# Page configuration
st.set_page_config(
    page_title="Document Type Classifier",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.3rem;
        text-align: center;
        color: #6c757d;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .prediction-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 2px solid #e0e0e0;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .upload-section {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vit_model' not in st.session_state:
    st.session_state.vit_model = None
if 'resnet18_model' not in st.session_state:
    st.session_state.resnet18_model = None
if 'device' not in st.session_state:
    st.session_state.device = get_device()
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False

# Model paths - try multiple locations
_current_file = Path(__file__).resolve()
PROJECT_ROOT = _current_file.parent.parent.absolute()

# Try multiple possible model locations
MODEL_DIRS = [
    PROJECT_ROOT / "models",
    Path("/Users/roy-siftt/final-project/models"),
    PROJECT_ROOT.parent / "models",
    _current_file.parent.parent / "models",  # Alternative path
]

def find_model(model_name):
    """Find model file in multiple possible locations."""
    for model_dir in MODEL_DIRS:
        if model_dir.exists():
            model_path = model_dir / model_name
            if model_path.exists():
                return model_path
    return None

VIT_MODEL_PATH = find_model("vit_document_classifier_9000.pth")
RESNET18_MODEL_PATH = find_model("resnet18_document_classifier_9000.pth")

# Label map
LABEL_MAP = {
    0: "ID Card",
    1: "Passport",
    2: "Driver License"
}

def load_models():
    """Load models if not already loaded."""
    device = st.session_state.device
    success_count = 0
    
    # Load ViT model
    if st.session_state.vit_model is None:
        if VIT_MODEL_PATH and VIT_MODEL_PATH.exists():
            with st.spinner("🔄 Loading ViT model... This may take a moment."):
                try:
                    st.session_state.vit_model = load_vit_model(
                        str(VIT_MODEL_PATH), 
                        device=device
                    )
                    st.success(f"✅ ViT model loaded successfully from {VIT_MODEL_PATH.name}!")
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ Error loading ViT model: {str(e)}")
                    st.exception(e)
        else:
            st.warning(f"⚠️ ViT model not found. Searched in: {[str(d) for d in MODEL_DIRS]}")
    
    # Load ResNet18 model
    if st.session_state.resnet18_model is None:
        if RESNET18_MODEL_PATH and RESNET18_MODEL_PATH.exists():
            with st.spinner("🔄 Loading ResNet18 model... This may take a moment."):
                try:
                    st.session_state.resnet18_model = load_resnet18_model(
                        str(RESNET18_MODEL_PATH), 
                        device=device
                    )
                    st.success(f"✅ ResNet18 model loaded successfully from {RESNET18_MODEL_PATH.name}!")
                    success_count += 1
                except Exception as e:
                    st.error(f"❌ Error loading ResNet18 model: {str(e)}")
                    st.exception(e)
        else:
            st.warning(f"⚠️ ResNet18 model not found. Searched in: {[str(d) for d in MODEL_DIRS]}")
    
    if success_count > 0:
        st.session_state.models_loaded = True
    return success_count

def get_confidence_color(confidence):
    """Get color class based on confidence level."""
    if confidence >= 0.7:
        return "confidence-high"
    elif confidence >= 0.5:
        return "confidence-medium"
    else:
        return "confidence-low"

def main():
    # Header
    st.markdown('<h1 class="main-header">📄 Document Type Classifier</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload an image to classify it as ID Card, Passport, or Driver License</p>', unsafe_allow_html=True)
    
    # Auto-load models on first run (only if models are found)
    if not st.session_state.models_loaded:
        if VIT_MODEL_PATH or RESNET18_MODEL_PATH:
            with st.spinner("🔄 Loading models... Please wait."):
                load_models()
        else:
            st.warning("⚠️ Model files not found. Please check the model paths.")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Load models button
        if st.button("🔄 Load/Reload Models", type="primary", use_container_width=True):
            load_models()
        
        # Device info
        device_emoji = "🖥️" if st.session_state.device == "cpu" else "🚀"
        st.info(f"{device_emoji} Device: **{st.session_state.device.upper()}**")
        
        # Model status with better styling
        st.markdown("---")
        st.subheader("📊 Model Status")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.vit_model is not None:
                st.success("✅ ViT")
            else:
                st.error("❌ ViT")
        
        with col2:
            if st.session_state.resnet18_model is not None:
                st.success("✅ ResNet18")
            else:
                st.error("❌ ResNet18")
        
        # Model file locations
        if VIT_MODEL_PATH:
            st.caption(f"ViT: `{VIT_MODEL_PATH.name}`")
        if RESNET18_MODEL_PATH:
            st.caption(f"ResNet18: `{RESNET18_MODEL_PATH.name}`")
        
        st.markdown("---")
        st.markdown("### 📖 About")
        st.markdown("""
        This demo uses deep learning models to classify identity documents:
        
        - **🆔 ID Card**
        - **📘 Passport**
        - **🚗 Driver License**
        
        Models were trained on **9,000 images** with advanced augmentation techniques.
        """)
    
    # Main content area
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            help="Upload an image of an ID card, passport, or driver license",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            # Display uploaded image with better styling
            image = Image.open(uploaded_file)
            st.image(
                image, 
                caption=f"📷 {uploaded_file.name}", 
                use_container_width=True
            )
            st.caption(f"Image size: {image.size[0]} × {image.size[1]} pixels")
    
    with col2:
        st.markdown("### 🎯 Prediction Results")
        
        if uploaded_file is not None:
            # Only show model selection after image is uploaded
            st.markdown("#### 🔧 Select Model for Classification")
            model_choice = st.selectbox(
                "Choose which model to use:",
                ["ViT (Vision Transformer)", "ResNet18"],
                help="Select the model you want to use for classification",
                label_visibility="collapsed"
            )
            
            # Determine which model to use
            if model_choice == "ViT (Vision Transformer)":
                model = st.session_state.vit_model
                model_name = "ViT"
            else:
                model = st.session_state.resnet18_model
                model_name = "ResNet18"
            
            if model is None:
                st.warning(f"⚠️ **{model_name}** model is not loaded. Please click '🔄 Load/Reload Models' in the sidebar.")
            else:
                st.success(f"✅ **{model_name}** model is ready!")
                st.markdown("---")
                
                # Make prediction button
                if st.button("🔍 Classify Image", type="primary", use_container_width=True):
                    with st.spinner(f"🔬 Analyzing image with {model_name}..."):
                        try:
                            result = predict_image(
                                model, 
                                image, 
                                device=st.session_state.device,
                                label_map=LABEL_MAP
                            )
                            
                            # Display results with enhanced styling
                            st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                            
                            # Predicted class
                            confidence_pct = result['confidence'] * 100
                            confidence_class = get_confidence_color(result['confidence'])
                            
                            # Main prediction
                            st.markdown(f"## 🎯 **{result['predicted']}**")
                            st.markdown(f"### 📈 Confidence: <span class='{confidence_class}'>{confidence_pct:.1f}%</span>", unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # All probabilities with better visualization
                            st.markdown("#### 📊 Probability Distribution:")
                            for label, prob in result['probabilities'].items():
                                prob_pct = prob * 100
                                
                                # Highlight the predicted class
                                if label == result['predicted']:
                                    st.markdown(f"**✓ {label}:** {prob_pct:.1f}%")
                                    st.progress(prob, text=f"{prob_pct:.1f}%")
                                else:
                                    st.markdown(f"  {label}: {prob_pct:.1f}%")
                                    st.progress(prob, text=f"{prob_pct:.1f}%")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Success message
                            if confidence_pct >= 70:
                                st.success(f"✅ High confidence prediction! The model is {confidence_pct:.1f}% sure this is a **{result['predicted']}**.")
                            elif confidence_pct >= 50:
                                st.warning(f"⚠️ Moderate confidence. The model is {confidence_pct:.1f}% sure this is a **{result['predicted']}**.")
                            else:
                                st.info(f"ℹ️ Low confidence. The model is {confidence_pct:.1f}% sure this is a **{result['predicted']}**. Consider trying a clearer image.")
                            
                        except Exception as e:
                            st.error(f"❌ Error during prediction: {str(e)}")
                            with st.expander("Show error details"):
                                st.exception(e)
        else:
            st.info("👆 **Please upload an image** to get started")
            st.markdown("""
            <div style='text-align: center; padding: 2rem; color: #6c757d;'>
                <p>Supported formats: JPG, JPEG, PNG</p>
                <p>Max file size: 200MB</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6c757d; padding: 1rem;'>"
        "<strong>Document Type Classification Demo</strong> | Built with Streamlit & PyTorch"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
