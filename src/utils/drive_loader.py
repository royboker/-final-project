#!/usr/bin/env python3
"""
Google Drive image loader for the final project.
This module provides functions to load images from Google Drive URLs.
"""

import requests
from PIL import Image
from io import BytesIO
import re
import time
from typing import Union, Optional

def extract_file_id_from_drive_url(url: str) -> Optional[str]:
    """
    Extract file ID from Google Drive sharing URL.
    
    Args:
        url: Google Drive sharing URL
        
    Returns:
        File ID if found, None otherwise
    """
    patterns = [
        r'drive\.google\.com/file/d/([a-zA-Z0-9_-]+)',
        r'drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def convert_to_direct_download_url(share_url: str) -> str:
    """
    Convert Google Drive sharing URL to direct download URL.
    
    Args:
        share_url: Google Drive sharing URL
        
    Returns:
        Direct download URL
    """
    file_id = extract_file_id_from_drive_url(share_url)
    if file_id:
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return share_url

def load_image_from_drive(drive_url: str, max_retries: int = 3) -> Image.Image:
    """
    Load image from Google Drive URL.
    
    Args:
        drive_url: Google Drive sharing URL
        max_retries: Maximum number of retry attempts
        
    Returns:
        PIL Image object
        
    Raises:
        Exception: If image cannot be loaded after retries
    """
    # Convert to direct download URL
    direct_url = convert_to_direct_download_url(drive_url)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(direct_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Load image from response content
            img = Image.open(BytesIO(response.content))
            return img
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise Exception(f"Failed to load image after {max_retries} attempts: {e}")

def load_image_from_drive_with_fallback(drive_url: str, local_fallback_path: str = None) -> Image.Image:
    """
    Load image from Google Drive with local fallback.
    
    Args:
        drive_url: Google Drive sharing URL
        local_fallback_path: Local path to fallback image
        
    Returns:
        PIL Image object
    """
    try:
        return load_image_from_drive(drive_url)
    except Exception as e:
        print(f"Failed to load from Drive: {e}")
        
        if local_fallback_path and os.path.exists(local_fallback_path):
            print(f"Loading fallback image: {local_fallback_path}")
            return Image.open(local_fallback_path)
        else:
            raise Exception(f"No fallback available. Drive error: {e}")

def test_drive_connection(drive_url: str) -> bool:
    """
    Test if Google Drive URL is accessible.
    
    Args:
        drive_url: Google Drive sharing URL
        
    Returns:
        True if accessible, False otherwise
    """
    try:
        direct_url = convert_to_direct_download_url(drive_url)
        response = requests.head(direct_url, timeout=10)
        return response.status_code == 200
    except:
        return False

# Example usage
if __name__ == "__main__":
    # Test the loader
    test_url = "https://drive.google.com/file/d/YOUR_FILE_ID/view?usp=sharing"
    
    try:
        img = load_image_from_drive(test_url)
        print(f"✅ Successfully loaded image: {img.size}")
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
