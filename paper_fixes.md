# DocuGuard Paper — Fixes to Apply

Each fix below shows exactly what to **DELETE** from the current paper and what to **REPLACE** it with.

---

## Fix 1 — Forgery Detection Subsection

**Location:** Section "Methodological Pipeline" → subsection "Forgery Detection"

### ❌ DELETE this paragraph:
> Following classification, the image is forwarded to a specialized forgery detection module tailored to the identified document type. This module analyzes both visual and structural features of the document to detect anomalies and potential manipulations. These include face replacement, texture inconsistencies, font irregularities, and other graphical alterations that are indicative of forgery. The use of specialized models for each document type enhances detection performance and allows the system to capture document-specific characteristics.

### ✅ REPLACE with:
> Following classification, the image is forwarded to a specialized forgery detection module tailored to the identified document type. For each document type, we train two complementary models: (1) a **binary classifier** that determines whether the document is authentic or forged (Real vs Fake), and (2) a **fraud type classifier** that identifies the specific forgery technique used. The forgery techniques addressed in this work are **face morphing** (blending two facial identities into one image) and **face replacement** (substituting the original face with a different one), which are the two dominant forgery categories present in the IDNet dataset. The use of specialized models per document type enhances detection performance and allows the system to capture document-specific characteristics.

---

## Fix 2 — Input Validation and Preprocessing Subsection

**Location:** Section "Methodological Pipeline" → subsection "Input Validation and Preprocessing"

### ❌ DELETE this paragraph:
> In the initial stage, the system validates the input to ensure that it is a valid image file and within acceptable size limits. The image then undergoes preprocessing, which includes resizing to a fixed resolution, normalization of pixel values, and noise reduction. Additionally, the document region is detected, aligned, and cropped in order to remove irrelevant background and improve the quality of the input for subsequent stages.

### ✅ REPLACE with:
> In the initial stage, the system validates the input to ensure that it is a valid image file and within acceptable size limits. The image is then preprocessed using standard computer vision operations: resizing to 224×224 pixels and normalization using ImageNet statistics (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]). During training, we apply data augmentation via the Albumentations library, including random horizontal flipping, brightness and contrast adjustment, and color jittering, to improve model generalization to varying capture conditions.

---

## Fix 3 — Document Type Classification Subsection

**Location:** Section "Methodological Pipeline" → subsection "Document Type Classification"

### ❌ DELETE this paragraph:
> After preprocessing, the image is passed to a document classification module. This component is responsible for identifying the type of document, such as a passport, national ID card, or driver's license. In this work, we utilize deep learning architectures including Convolutional Neural Networks (ResNet-18) and Vision Transformers (ViT), which enable the extraction of both local features (e.g., text regions and edges) and global structural patterns (e.g., layout and document design).

### ✅ REPLACE with:
> After preprocessing, the image is passed to a document classification module. This component is responsible for identifying the type of document: passport, national ID card, or driver's license. We evaluate two architectures: **ResNet-18** (11.7M parameters) and **ViT-Small/16** (22M parameters), both pretrained on ImageNet-1K. ViT-Small was ultimately selected as the primary classifier due to its superior performance. All models are fine-tuned using a **three-stage progressive unfreezing protocol**: (1) training only the classification head with the backbone frozen, (2) unfreezing the last four transformer blocks, and (3) full fine-tuning of all layers. This staged approach stabilizes training and preserves pretrained features while adapting the model to the target task.

---

## Fix 4 — Add New Subsection "Dataset"

**Location:** Insert **immediately after** this line in the paper:
> \section{Methodological Pipeline}

And **immediately before** this line:
> The proposed DocuGuard system is designed as a hierarchical multi-stage pipeline for detecting forged identity documents.

### ✅ ADD this new subsection at that location:
> \subsection{Dataset}
>
> All experiments were conducted on the **IDNet** dataset, a large-scale benchmark for identity document forgery detection containing over 290,000 images across multiple countries and document types. For each document type, we selected three country subsets to ensure diversity:
> \begin{itemize}
>     \item \textbf{Driver's License}: DC, AZ, WV (United States)
>     \item \textbf{ID Card}: RUS, SVK, NV
>     \item \textbf{Passport}: ALB, GRC, LVA
> \end{itemize}
> The dataset includes both authentic (real) and forged (fake) samples, with forgeries produced via face morphing and face replacement techniques. Data was split 80/10/10 into train, validation, and test sets. Document type classification was trained on 9,000 images (3,000 per class). Forgery detection models were trained on 15,000 images for driver's license and 20,000 images for ID card and passport.

---

## Fix 5 — Add New Subsection "Alternative Backbone: DiT-Base"

**Location:** Insert **immediately after** the end of the "Forgery Detection" subsection. Specifically, insert after this sentence in the paper:
> The use of specialized models for each document type enhances detection performance and allows the system to capture document-specific characteristics.

And **immediately before** this line:
> \subsection{Output Generation}

### ✅ ADD this new subsection at that location:
> \subsection{Alternative Backbone: DiT-Base}
>
> In addition to ViT-Small, we evaluated **DiT-Base** (Document Image Transformer), a model pretrained on 42 million scanned documents from the IIT-CDIP collection. Our hypothesis was that document-specific pretraining would improve forgery detection compared to ImageNet-pretrained ViT. However, results showed the opposite: DiT-Base consistently underperformed ViT-Small on all tasks (e.g., 85.7\% vs 93.1\% on driver's license binary classification, 77.3\% vs 93.6\% on ID card binary classification). We attribute this to the mismatch between DiT's pretraining objective (document layout and text structure understanding) and the visual cues required for face forgery detection (pixel-level blending artifacts, skin texture inconsistencies). ImageNet pretraining, while generic, provides features that transfer better to natural image analysis of facial regions.

---

## Fix 6 — Add New Subsection "Out-of-Dataset Evaluation"

**Location:** Insert **immediately after** the end of the "Output Generation" subsection. Specifically, insert after this sentence (which is the last sentence of the Methodological Pipeline section in the current paper):
> Optionally, the system logs the result for future analysis and system improvement.

This should be the **last subsection** of the Methodological Pipeline section.

### ✅ ADD this new subsection at that location:
> \subsection{Out-of-Dataset Evaluation}
>
> Beyond the standard held-out test set, we evaluate each forgery detection model on an **out-of-dataset (OOD)** evaluation set containing 999 unseen samples per document type (333 real, 333 face morphing, 333 face replacement). These samples were excluded from all training and validation stages, providing a stronger measure of generalization to unseen data.

---

## Summary

| # | Action | Location |
|---|--------|----------|
| 1 | Replace paragraph | Forgery Detection subsection |
| 2 | Replace paragraph | Input Validation and Preprocessing subsection |
| 3 | Replace paragraph | Document Type Classification subsection |
| 4 | Add new subsection | Beginning of Methodological Pipeline (before System Overview) |
| 5 | Add new subsection | After Forgery Detection subsection |
| 6 | Add new subsection | After Output Generation subsection |
