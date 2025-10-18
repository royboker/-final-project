"""
Download and load the IDNet Identity Document Analysis dataset from Kaggle
"""
import kagglehub
import os
import shutil
from pathlib import Path


def download_idnet_dataset(target_dir: str = "../../datasets/idnet"):
    """
    Download the IDNet dataset from Kaggle and organize it in the datasets folder.
    
    Args:
        target_dir: Directory to store the dataset (relative to this script)
        
    Returns:
        Path to the dataset directory
    """
    print("Downloading IDNet Identity Document Analysis dataset...")
    
    # Download latest version from Kaggle
    path = kagglehub.dataset_download("chitreshkr/idnet-identity-document-analysis")
    
    print(f"Dataset downloaded to: {path}")
    
    # Get the absolute path to the target directory
    script_dir = Path(__file__).parent
    target_path = (script_dir / target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Copy or move files to our datasets folder
    if Path(path) != target_path:
        print(f"Organizing dataset in: {target_path}")
        # Note: You may want to move or symlink instead of copy for large datasets
        # For now, we'll just return the kagglehub cache path
    
    print("Dataset ready!")
    print(f"Path to dataset files: {path}")
    
    return path


if __name__ == "__main__":
    # Download the dataset
    dataset_path = download_idnet_dataset()
    
    # List files in the dataset
    print("\nDataset contents:")
    for item in Path(dataset_path).rglob("*"):
        if item.is_file():
            print(f"  - {item.relative_to(dataset_path)}")

