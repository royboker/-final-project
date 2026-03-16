"""
Streamlit Demo App - Document Analysis Pipeline

Full flow:
1. Upload image
2. Document Type Classification (ID Card / Passport / Driver License)
3. If Driver License → Binary Forgery Detection (Real / Fake)
4. If Fake → Fraud Type Classification (Face Morphing / Face Replacement)
"""

import streamlit as st
import torch
from PIL import Image
import os
from pathlib import Path
from model_loader import (
    load_vit_model,
    load_resnet18_model,
    load_binary_model,
    load_fraud_type_model,
    predict_image,
    predict_with_tta,
    get_device
)

# Page configuration
st.set_page_config(
    page_title="Document Analysis Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #6c757d;
        margin-bottom: 2rem;
    }
    .step-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    .step-box-success {
        border-left: 4px solid #28a745;
    }
    .step-box-warning {
        border-left: 4px solid #ffc107;
    }
    .step-box-danger {
        border-left: 4px solid #dc3545;
    }
    .result-real {
        color: #28a745;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .result-fake {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.3rem;
    }
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    .pipeline-arrow {
        text-align: center;
        font-size: 1.5rem;
        color: #667eea;
        margin: 0.3rem 0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# Paths
# ============================================
_current_file = Path(__file__).resolve()
PROJECT_ROOT = _current_file.parent.parent.absolute()

MODEL_DIRS = [
    PROJECT_ROOT / "models",
    Path("/Users/roy-siftt/final-project/models"),
]

FORGERY_MODEL_DIRS = [
    PROJECT_ROOT / "notebooks" / "drivers_license_forgery" / "production",
    Path("/Users/roy-siftt/final-project/notebooks/drivers_license_forgery/production"),
]


def find_model(model_name, search_dirs):
    """Find model file in multiple possible locations."""
    for model_dir in search_dirs:
        if model_dir.exists():
            model_path = model_dir / model_name
            if model_path.exists():
                return model_path
    return None


# Document type models
VIT_DOC_PATH = find_model("vit_document_classifier_9000.pth", MODEL_DIRS)
RESNET18_DOC_PATH = find_model("resnet18_document_classifier_9000.pth", MODEL_DIRS)

# Forgery detection models
BINARY_MODEL_PATH = find_model("vit_binary_improved_15k.pth", FORGERY_MODEL_DIRS)
FRAUD_TYPE_MODEL_PATH = find_model("vit_fraud_type_15k.pth", FORGERY_MODEL_DIRS)

# Label maps
DOC_TYPE_LABELS = {0: "ID Card", 1: "Passport", 2: "Driver License"}
BINARY_LABELS = {0: "Real", 1: "Fake"}
FRAUD_TYPE_LABELS = {0: "Face Morphing", 1: "Face Replacement"}

# ============================================
# Session State
# ============================================
for key in ['vit_doc_model', 'resnet18_doc_model', 'binary_model', 'fraud_type_model']:
    if key not in st.session_state:
        st.session_state[key] = None
if 'device' not in st.session_state:
    st.session_state.device = get_device()
if 'models_loaded' not in st.session_state:
    st.session_state.models_loaded = False


# ============================================
# Model Loading
# ============================================
def load_all_models():
    """Load all pipeline models."""
    device = st.session_state.device
    loaded = []

    # Document type - ViT
    if st.session_state.vit_doc_model is None and VIT_DOC_PATH:
        try:
            st.session_state.vit_doc_model = load_vit_model(str(VIT_DOC_PATH), device=device)
            loaded.append("ViT Doc Classifier")
        except Exception as e:
            st.error(f"Failed to load ViT doc model: {e}")

    # Document type - ResNet18
    if st.session_state.resnet18_doc_model is None and RESNET18_DOC_PATH:
        try:
            st.session_state.resnet18_doc_model = load_resnet18_model(str(RESNET18_DOC_PATH), device=device)
            loaded.append("ResNet18 Doc Classifier")
        except Exception as e:
            st.error(f"Failed to load ResNet18 doc model: {e}")

    # Binary forgery detector
    if st.session_state.binary_model is None and BINARY_MODEL_PATH:
        try:
            st.session_state.binary_model = load_binary_model(str(BINARY_MODEL_PATH), device=device)
            loaded.append("Binary Forgery Detector")
        except Exception as e:
            st.error(f"Failed to load binary model: {e}")

    # Fraud type classifier
    if st.session_state.fraud_type_model is None and FRAUD_TYPE_MODEL_PATH:
        try:
            st.session_state.fraud_type_model = load_fraud_type_model(str(FRAUD_TYPE_MODEL_PATH), device=device)
            loaded.append("Fraud Type Classifier")
        except Exception as e:
            st.error(f"Failed to load fraud type model: {e}")

    if loaded:
        st.session_state.models_loaded = True
    return loaded


def get_confidence_class(confidence):
    if confidence >= 0.7:
        return "confidence-high"
    elif confidence >= 0.5:
        return "confidence-medium"
    return "confidence-low"


# ============================================
# Main App
# ============================================
def main():
    st.markdown('<h1 class="main-header">🔍 Document Analysis Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload a document image to classify its type, detect forgery, and identify fraud method</p>', unsafe_allow_html=True)

    # Auto-load models
    if not st.session_state.models_loaded:
        with st.spinner("Loading models... Please wait."):
            load_all_models()

    # ============================================
    # Sidebar
    # ============================================
    with st.sidebar:
        st.header("Settings")

        if st.button("Reload Models", type="primary", use_container_width=True):
            for key in ['vit_doc_model', 'resnet18_doc_model', 'binary_model', 'fraud_type_model']:
                st.session_state[key] = None
            st.session_state.models_loaded = False
            load_all_models()

        device_emoji = "🖥️" if st.session_state.device == "cpu" else "🚀"
        st.info(f"{device_emoji} Device: **{st.session_state.device.upper()}**")

        st.markdown("---")
        st.subheader("Model Status")

        models_status = [
            ("Doc Type (ViT)", st.session_state.vit_doc_model),
            ("Doc Type (ResNet)", st.session_state.resnet18_doc_model),
            ("Real/Fake", st.session_state.binary_model),
            ("Fraud Type", st.session_state.fraud_type_model),
        ]
        for name, model in models_status:
            if model is not None:
                st.success(f"✅ {name}")
            else:
                st.error(f"❌ {name}")

        st.markdown("---")
        st.subheader("Pipeline")
        st.markdown("""
        **Step 1:** Document Type Classification
        *(ID Card / Passport / Driver License)*

        **Step 2:** Forgery Detection
        *(Real or Fake? — only for Driver Licenses)*

        **Step 3:** Fraud Type
        *(Face Morphing or Replacement? — only if Fake)*
        """)

    # ============================================
    # Main Content
    # ============================================
    col_upload, col_results = st.columns([1, 1.2], gap="large")

    with col_upload:
        st.markdown("### Upload Document Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['jpg', 'jpeg', 'png'],
            help="Upload an image of an identity document",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption=f"{uploaded_file.name}", use_container_width=True)
            st.caption(f"Size: {image.size[0]} x {image.size[1]} pixels")

            # Model selector for document type
            doc_model_choice = st.selectbox(
                "Document type model:",
                ["ViT (Vision Transformer)", "ResNet18"],
            )

    with col_results:
        st.markdown("### Analysis Results")

        if uploaded_file is None:
            st.info("Upload an image to start the analysis pipeline")
            return

        # Select document type model
        if doc_model_choice == "ViT (Vision Transformer)":
            doc_model = st.session_state.vit_doc_model
            doc_model_name = "ViT"
        else:
            doc_model = st.session_state.resnet18_doc_model
            doc_model_name = "ResNet18"

        if doc_model is None:
            st.warning(f"{doc_model_name} document classifier not loaded. Click 'Reload Models' in sidebar.")
            return

        # Analyze button
        if not st.button("🔍 Analyze Document", type="primary", use_container_width=True):
            return

        device = st.session_state.device

        # ============================================
        # STEP 1: Document Type Classification
        # ============================================
        with st.spinner("Step 1: Classifying document type..."):
            doc_result = predict_image(doc_model, image, device=device, label_map=DOC_TYPE_LABELS)

        doc_type = doc_result['predicted']
        doc_conf = doc_result['confidence']
        doc_conf_class = get_confidence_class(doc_conf)

        st.markdown(f"""
        <div class="step-box step-box-success">
            <strong>Step 1: Document Type Classification</strong> ({doc_model_name})<br>
            <span style="font-size:1.4rem; font-weight:bold;">📄 {doc_type}</span><br>
            Confidence: <span class="{doc_conf_class}">{doc_conf*100:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        # Show probabilities
        with st.expander("Document type probabilities"):
            for label, prob in doc_result['probabilities'].items():
                marker = "→ " if label == doc_type else "  "
                st.markdown(f"{marker}**{label}:** {prob*100:.1f}%")
                st.progress(prob)

        # ============================================
        # Check if Driver License
        # ============================================
        if doc_type != "Driver License":
            st.markdown(f"""
            <div class="step-box">
                <strong>Step 2: Forgery Detection</strong><br>
                <span style="color: #6c757d;">Skipped — forgery detection is only available for Driver Licenses.</span><br>
                <span style="color: #6c757d;">Detected document type: {doc_type}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("### Pipeline Complete")
            st.info(f"Document identified as **{doc_type}** with {doc_conf*100:.1f}% confidence. Forgery analysis is only available for Driver Licenses.")
            return

        # ============================================
        # STEP 2: Binary Forgery Detection (Driver License only)
        # ============================================
        st.markdown('<div class="pipeline-arrow">⬇️</div>', unsafe_allow_html=True)

        if st.session_state.binary_model is None:
            st.warning("Binary forgery model not loaded.")
            return

        with st.spinner("Step 2: Detecting forgery (with TTA)..."):
            binary_result = predict_with_tta(
                st.session_state.binary_model, image,
                device=device, label_map=BINARY_LABELS
            )

        is_fake = binary_result['predicted_idx'] == 1
        binary_conf = binary_result['confidence']
        binary_conf_class = get_confidence_class(binary_conf)

        if is_fake:
            step2_class = "step-box-danger"
            result_class = "result-fake"
            result_icon = "🚨"
        else:
            step2_class = "step-box-success"
            result_class = "result-real"
            result_icon = "✅"

        st.markdown(f"""
        <div class="step-box {step2_class}">
            <strong>Step 2: Forgery Detection</strong> (ViT-Small + TTA)<br>
            <span class="{result_class}" style="font-size:1.4rem;">{result_icon} {binary_result['predicted']}</span><br>
            Confidence: <span class="{binary_conf_class}">{binary_conf*100:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Forgery detection probabilities"):
            for label, prob in binary_result['probabilities'].items():
                marker = "→ " if label == binary_result['predicted'] else "  "
                st.markdown(f"{marker}**{label}:** {prob*100:.1f}%")
                st.progress(prob)

        # ============================================
        # If Real → Done
        # ============================================
        if not is_fake:
            st.markdown("---")
            st.markdown("### Pipeline Complete")
            st.success(f"This Driver License appears to be **genuine** ({binary_conf*100:.1f}% confidence). No fraud detected.")
            return

        # ============================================
        # STEP 3: Fraud Type Classification (Fake only)
        # ============================================
        st.markdown('<div class="pipeline-arrow">⬇️</div>', unsafe_allow_html=True)

        if st.session_state.fraud_type_model is None:
            st.warning("Fraud type model not loaded.")
            return

        with st.spinner("Step 3: Identifying fraud type (with TTA)..."):
            fraud_result = predict_with_tta(
                st.session_state.fraud_type_model, image,
                device=device, label_map=FRAUD_TYPE_LABELS
            )

        fraud_type = fraud_result['predicted']
        fraud_conf = fraud_result['confidence']
        fraud_conf_class = get_confidence_class(fraud_conf)

        st.markdown(f"""
        <div class="step-box step-box-warning">
            <strong>Step 3: Fraud Type Identification</strong> (ViT-Small + TTA)<br>
            <span style="font-size:1.4rem; font-weight:bold;">🔎 {fraud_type}</span><br>
            Confidence: <span class="{fraud_conf_class}">{fraud_conf*100:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Fraud type probabilities"):
            for label, prob in fraud_result['probabilities'].items():
                marker = "→ " if label == fraud_type else "  "
                st.markdown(f"{marker}**{label}:** {prob*100:.1f}%")
                st.progress(prob)

        # ============================================
        # Final Summary
        # ============================================
        st.markdown("---")
        st.markdown("### Pipeline Complete")

        st.error(f"""
        **FORGERY DETECTED**

        | Step | Result | Confidence |
        |------|--------|------------|
        | Document Type | Driver License | {doc_conf*100:.1f}% |
        | Forgery Detection | **FAKE** | {binary_conf*100:.1f}% |
        | Fraud Type | **{fraud_type}** | {fraud_conf*100:.1f}% |
        """)

        if fraud_type == "Face Morphing":
            st.markdown("""
            > **Face Morphing** — The photo on this document appears to be a blend of two or more
            > faces, creating a composite image that can match multiple individuals.
            """)
        else:
            st.markdown("""
            > **Face Replacement** — The photo on this document appears to have been swapped
            > with a different person's photo, replacing the original face entirely.
            """)


if __name__ == "__main__":
    main()
