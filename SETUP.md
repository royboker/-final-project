# Setup Instructions

## Prerequisites
- Python 3.8+
- Git

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/username/repository-name.git
cd repository-name
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Ensure datasets are available:**
   - Make sure the following directories exist with image files:
     - `datasets/idnet/GRC/` - Greek passport images
     - `datasets/idnet/RUS/` - Russian ID card images  
     - `datasets/idnet/WV/` - West Virginia driver license images

## Project Structure
```
final-project/
├── src/                    # Source code
├── notebooks/              # Jupyter notebooks
├── datasets/               # Dataset files (local)
│   └── idnet/
│       ├── GRC/            # Greek passports
│       ├── RUS/            # Russian ID cards
│       ├── WV/             # West Virginia driver licenses
│       └── document_type_classification/
├── models/                 # Model files
├── results/                # Results and outputs
└── requirements.txt        # Python dependencies
```

## Usage
1. **Start Jupyter:** `jupyter lab`
2. **Open notebooks** in `notebooks/` directory
3. **Run data exploration** and preprocessing notebooks
4. **Train models** using the provided scripts

## Dataset Information
- **Total images:** ~130,000 identity documents
- **Document types:** Passports, ID Cards, Driver Licenses
- **Image formats:** PNG, JPG
- **Local storage:** All images stored locally in `datasets/` directory
