import os
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

def load_basic_metadata(metadata_file: str) -> Dict:
    """Load basic metadata from JSON file"""
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata {metadata_file}: {e}")
        return {}

def get_fraud_details(fraud_type: str, original_id: str, detailed_metadata_dir: str) -> str:
    """Get fraud details from detailed metadata (simplified for speed)"""
    # For now, return empty string to speed up processing
    # Can be enhanced later to load specific fraud details
    return ""

def extract_person_info_rus(metadata: Dict) -> Dict:
    """Extract person information from RUS (Russian ID card) JSON"""
    person_info = {
        'person_name': '',
        'person_name_greek': '',  # Will be empty for RUS
        'birth_date': '',
        'document_number': '',
        'issue_date': '',
        'expire_date': '',
        'gender': '',
        'height': '',  # Not available in RUS
        'place_of_birth': '',
        'place_of_birth_greek': '',  # Will be empty for RUS
        'document_type': 'id_card',
        'country_code': '',
        'country_name': '',
        'issue_authority': ''  # Not available in RUS
    }
    
    # Russian ID card format - based on actual JSON structure
    if 'surname' in metadata and 'given_name' in metadata:
        person_info['person_name'] = f"{metadata['given_name']} {metadata['surname']}"
        person_info['person_name_greek'] = metadata.get('patronymic_name', '')  # Using patronymic for Greek name equivalent
    
    person_info['birth_date'] = metadata.get('birthday', '')
    person_info['document_number'] = metadata.get('card_num', '')
    person_info['issue_date'] = metadata.get('issue_date', '')
    person_info['expire_date'] = metadata.get('expire_date', '')
    person_info['gender'] = metadata.get('gender', '')
    person_info['place_of_birth'] = metadata.get('place_of_birth', '')
    person_info['document_type'] = 'id_card'
    person_info['country_code'] = metadata.get('country_code', '')
    
    return person_info

def create_unified_rus_dataset(base_path: str = "../../datasets/idnet") -> pd.DataFrame:
    """
    Create unified dataset for RUS (Russian ID Cards)
    """
    print("🚀 Creating Unified RUS Dataset...")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    base_path = (script_dir / base_path).resolve()
    country_path = base_path / "RUS" / "RUS"
    
    if not country_path.exists():
        raise FileNotFoundError(f"RUS dataset not found at {country_path}")
    
    # Define fraud categories and their corresponding directories
    fraud_categories = {
        'positive': 'real',
        'fraud1_copy_and_move': 'copy_and_move',
        'fraud2_face_morphing': 'face_morphing',
        'fraud3_face_replacement': 'face_replacement',
        'fraud4_combined': 'combined',
        'fraud5_inpaint_and_rewrite': 'inpaint_and_rewrite',
        'fraud6_crop_and_replace': 'crop_and_replace'
    }
    
    all_data = []
    basic_metadata_dir = country_path / "meta" / "basic"
    detailed_metadata_dir = country_path / "meta" / "detailed_with_fraud_info"
    
    print(f"📁 Processing RUS dataset from: {country_path}")
    print(f"📁 Basic metadata from: {basic_metadata_dir}")
    print(f"📁 Detailed metadata from: {detailed_metadata_dir}")
    
    for category_dir, fraud_type in fraud_categories.items():
        category_path = country_path / category_dir
        
        if not category_path.exists():
            print(f"⚠️  Category directory not found: {category_path}")
            continue
        
        print(f"\n📂 Processing {category_dir} ({fraud_type})...")
        
        image_files = list(category_path.glob("*.png")) + list(category_path.glob("*.jpg"))
        print(f"   Found {len(image_files)} images")
        
        for img_path in image_files:
            filename = img_path.name
            # Handle different naming patterns
            if 'generated.photos_v3_' in filename:
                # Pattern: generated.photos_v3_XXXXXXX_fake_1_XXX.jpg
                original_id = filename.split('_fake')[0]
                # Remove file extension for JSON lookup
                original_id = Path(original_id).stem
            elif 'generated_fake_2_' in filename:
                # Pattern: generated_fake_2_XXX.jpg - these are synthetic, no original
                original_id = 'synthetic'
            else:
                # Fallback
                original_id = Path(filename).stem.split('_fake')[0]
            
            # Load basic metadata
            if original_id == 'synthetic':
                # For synthetic images, create empty metadata
                basic_metadata = {}
            else:
                metadata_file = basic_metadata_dir / f"{original_id}.json"
                basic_metadata = load_basic_metadata(str(metadata_file))
            
            # Extract person information
            person_info = extract_person_info_rus(basic_metadata)
            
            # Get fraud details
            fraud_details = get_fraud_details(fraud_type, original_id, str(detailed_metadata_dir))
            
            # Create record
            record = {
                'image_path': str(img_path),
                'filename': filename,
                'country': 'RUS',
                'document_type': 'id_card',
                'is_real': 1 if fraud_type == 'real' else 0,
                'fraud_type': fraud_type,
                'original_image_id': original_id,
                'fraud_details': fraud_details,
                'bounding_boxes': '[]',  # Will be extracted from fraud_details if needed
                **person_info
            }
            
            all_data.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    print(f"\n\n📊 Total dataset statistics for RUS:")
    print(f"   Total images: {len(df)}")
    print(f"   Real images: {df['is_real'].sum()} ({df['is_real'].sum()/len(df)*100:.1f}%)")
    print(f"   Fake images: {(~df['is_real'].astype(bool)).sum()} ({(~df['is_real'].astype(bool)).sum()/len(df)*100:.1f}%)")
    
    print(f"\n   Fraud type distribution:")
    print(df['fraud_type'].value_counts().to_string())
    
    print(f"\n   Unique original images: {df['original_image_id'].nunique()}")
    
    # Save to CSV
    output_file = base_path / "RUS_Unified_Dataset.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved unified RUS dataset to: {output_file}")
    
    return df

if __name__ == "__main__":
    df = create_unified_rus_dataset()
    print(f"\n✨ RUS Unified Dataset Creation Completed!")
    print(f"\nDataset columns:")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"\nSample records:")
    print(df[['filename', 'fraud_type', 'is_real', 'person_name', 'original_image_id']].head(5).to_string())
