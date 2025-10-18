#!/usr/bin/env python3
"""
Create unified IDNet dataset with comprehensive metadata
Focuses on GRC dataset first, then can be extended to WV and RUS
"""

import os
import json
import pandas as pd
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple

def extract_original_image_id(filename: str) -> str:
    """
    Extract original image ID from filename
    Examples:
    - generated.photos_0139935.png -> generated.photos_0139935
    - generated.photos_0139935_fake_4398.jpg -> generated.photos_0139935
    - generated_fake_2_0.jpg -> generated_fake_2_0 (no original)
    """
    # For files with _fake_ pattern, extract the base name
    if '_fake_' in filename:
        match = re.match(r'(.+?)_fake_\d+', filename)
        if match:
            return match.group(1)
    
    # For regular files, remove extension
    return os.path.splitext(filename)[0]

def load_basic_metadata(metadata_path: str) -> Dict:
    """Load basic metadata from JSON file"""
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata {metadata_path}: {e}")
        return {}

def extract_person_info(metadata: Dict, country: str) -> Dict:
    """Extract person information based on country format"""
    person_info = {
        'person_name': '',
        'person_name_greek': '',
        'birth_date': '',
        'document_number': '',
        'issue_date': '',
        'expire_date': '',
        'gender': '',
        'height': '',
        'place_of_birth': '',
        'place_of_birth_greek': '',
        'document_type': '',
        'country_code': '',
        'country_name': '',
        'issue_authority': ''
    }
    
    if country == 'GRC':
        # Greek passport format
        if 'surname' in metadata and 'given_name' in metadata:
            surname_en = metadata['surname'].get('English', '')
            given_name_en = metadata['given_name'].get('English', '')
            surname_gr = metadata['surname'].get('Greek', '')
            given_name_gr = metadata['given_name'].get('Greek', '')
            person_info['person_name'] = f"{given_name_en} {surname_en}"
            person_info['person_name_greek'] = f"{given_name_gr} {surname_gr}"
        
        person_info['birth_date'] = metadata.get('birthday', '')
        person_info['document_number'] = metadata.get('card_num', '')
        person_info['issue_date'] = metadata.get('issue_date', '')
        person_info['expire_date'] = metadata.get('expire_date', '')
        person_info['gender'] = metadata.get('gender', '')
        person_info['height'] = metadata.get('height', '')
        person_info['place_of_birth'] = metadata.get('place_of_birth', {}).get('English', '')
        person_info['place_of_birth_greek'] = metadata.get('place_of_birth', {}).get('Greek', '')
        person_info['document_type'] = metadata.get('type', '')
        person_info['country_code'] = metadata.get('country_code', '')
        person_info['country_name'] = metadata.get('country', '')
        person_info['issue_authority'] = metadata.get('issue_authority', '')
    
    elif country == 'WV':
        # West Virginia driver's license format
        person_info['person_name'] = metadata.get('name', '')
        person_info['birth_date'] = metadata.get('birthday', '')
        person_info['document_number'] = metadata.get('license_number', '')
        person_info['issue_date'] = metadata.get('issue_date', '')
        person_info['expire_date'] = metadata.get('expire_date', '')
        person_info['gender'] = metadata.get('gender', '')
        person_info['height'] = metadata.get('height', '')
        person_info['place_of_birth'] = metadata.get('address', '')
    
    elif country == 'RUS':
        # Russian ID card format
        surname = metadata.get('surname', '')
        given_name = metadata.get('given_name', '')
        patronymic = metadata.get('patronymic_name', '')
        person_info['person_name'] = f"{surname} {given_name} {patronymic}".strip()
        
        person_info['birth_date'] = metadata.get('birthday', '')
        person_info['document_number'] = metadata.get('card_num', '')
        person_info['issue_date'] = metadata.get('issue_date', '')
        person_info['expire_date'] = metadata.get('expire_date', '')
        person_info['gender'] = metadata.get('gender', '')
    
    return person_info

def get_fraud_details(fraud_type: str, original_id: str, detailed_metadata_dir: str) -> str:
    """Get detailed fraud information from detailed metadata files"""
    if fraud_type == 'real':
        return '{}'
    
    # For now, skip detailed fraud info to speed up processing
    # We can add this back later if needed
    return '{}'

def create_unified_dataset(country: str, base_path: str = "../../datasets/idnet") -> pd.DataFrame:
    """
    Create unified dataset for a specific country (GRC, RUS, or WV)
    """
    print(f"🚀 Creating Unified {country} Dataset...")
    print("=" * 60)
    
    script_dir = Path(__file__).parent
    base_path = (script_dir / base_path).resolve()
    country_path = base_path / country / country
    
    if not country_path.exists():
        raise FileNotFoundError(f"{country} dataset not found at {country_path}")
    
    # Define document types for each country
    document_types = {
        'GRC': 'passport',
        'RUS': 'id_card', 
        'WV': 'driver_license'
    }
    
    document_type = document_types.get(country, 'unknown')
    
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
    
    print(f"📁 Processing {country} dataset from: {country_path}")
    print(f"📁 Basic metadata from: {basic_metadata_dir}")
    print(f"📁 Detailed metadata from: {detailed_metadata_dir}")
    
    for category_dir, fraud_type in fraud_categories.items():
        category_path = country_path / category_dir
        
        if not category_path.exists():
            print(f"⚠️  Category directory not found: {category_path}")
            continue
        
        print(f"\n📂 Processing {category_dir} ({fraud_type})...")
        
        # Get all image files in this category
        image_files = []
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            image_files.extend(category_path.glob(ext))
        
        print(f"   Found {len(image_files)} images")
        
        for img_path in image_files:
            filename = img_path.name
            original_id = extract_original_image_id(filename)
            
            # Load basic metadata
            metadata_file = basic_metadata_dir / f"{original_id}.json"
            basic_metadata = load_basic_metadata(str(metadata_file))
            
            # Extract person information
            person_info = extract_person_info(basic_metadata, country)
            
            # Get fraud details
            fraud_details = get_fraud_details(fraud_type, original_id, str(detailed_metadata_dir))
            
            # Create record
            record = {
                'image_path': str(img_path),
                'filename': filename,
                'country': country,
                'document_type': document_type,
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
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total images: {len(df)}")
    print(f"   Real images: {df['is_real'].sum()} ({df['is_real'].sum()/len(df)*100:.1f}%)")
    print(f"   Fake images: {(~df['is_real'].astype(bool)).sum()} ({(~df['is_real'].astype(bool)).sum()/len(df)*100:.1f}%)")
    
    print(f"\n   Fraud type distribution:")
    print(df['fraud_type'].value_counts().to_string())
    
    print(f"\n   Unique original images: {df['original_image_id'].nunique()}")
    
    # Save to CSV
    output_file = base_path / f"{country}_Unified_Dataset.csv"
    df.to_csv(output_file, index=False)
    print(f"\n✅ Saved unified {country} dataset to: {output_file}")
    
    return df

def main():
    """Main function to create unified datasets for all countries"""
    countries = ['GRC', 'RUS', 'WV']
    
    for country in countries:
        try:
            print(f"\n{'='*80}")
            print(f"Processing {country} dataset...")
            print(f"{'='*80}")
            
            df = create_unified_dataset(country)
            
            print(f"\n✨ {country} Unified Dataset Creation Completed!")
            print(f"\nDataset columns:")
            for col in df.columns:
                print(f"  - {col}")
            
            print(f"\nSample records:")
            print(df[['filename', 'fraud_type', 'is_real', 'person_name', 'original_image_id']].head(5).to_string())
            
        except Exception as e:
            print(f"❌ Error creating {country} dataset: {e}")
            continue
    
    print(f"\n{'='*80}")
    print("🎉 All datasets creation completed!")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
