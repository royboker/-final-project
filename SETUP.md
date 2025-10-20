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

4. **Download datasets:**
   - Download the large datasets from [dataset source]
   - Extract to `datasets/` directory
   - The following directories should be present:
     - `datasets/idnet/GRC/`
     - `datasets/idnet/RUS/`
     - `datasets/idnet/WV/`

## Project Structure
```
final-project/
├── src/                    # Source code
├── notebooks/              # Jupyter notebooks
├── datasets/               # Dataset files (download separately)
├── models/                 # Model files
├── results/                # Results and outputs
└── requirements.txt        # Python dependencies
```

## Usage
1. Start Jupyter: `jupyter lab`
2. Open notebooks in `notebooks/` directory
3. Run data exploration and preprocessing notebooks
