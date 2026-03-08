import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple
import random

# Root directory for dataset storage
DATASET_ROOT = Path("model/data")

# Supported hazard classes
CLASSES = ["pothole", "crack", "speed_breaker", "waterlogging"]

# Mapping of various dataset labels to our internal class names
CLASS_MAPPING = {
    "pothole": "pothole",
    "Pothole": "pothole",
    "potholes": "pothole",
    "D00": "pothole",
    "D01": "pothole",
    "crack": "crack",
    "Crack": "crack",
    "cracks": "crack",
    "D10": "crack",
    "D11": "crack",
    "D12": "crack",
    "speed_breaker": "speed_breaker",
    "speedbreaker": "speed_breaker",
    "SpeedBreaker": "speed_breaker",
    "waterlogging": "waterlogging",
    "water_logging": "waterlogging",
    "WaterLogging": "waterlogging",
    "flooding": "waterlogging",
}


def convert_voc_to_yolo(xml_file: Path, img_width: int, img_height: int) -> List[str]:
    """
    Convert Pascal VOC XML annotation format to YOLO txt format.
    
    Args:
        xml_file: Path to the XML annotation file
        img_width: Width of the corresponding image
        img_height: Height of the corresponding image
        
    Returns:
        List of YOLO-formatted annotation lines.
    """
    import xml.etree.ElementTree as ET
    
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    yolo_lines = []
    
    for obj in root.findall("object"):
        label = obj.find("name").text
        label = CLASS_MAPPING.get(label, label)
        
        if label not in CLASSES:
            continue
        
        class_id = CLASSES.index(label)
        
        bbox = obj.find("bndbox")
        xmin = float(bbox.find("xmin").text)
        ymin = float(bbox.find("ymin").text)
        xmax = float(bbox.find("xmax").text)
        ymax = float(bbox.find("ymax").text)
        
        # Calculate YOLO center coordinates and dimensions (normalized 0-1)
        x_center = ((xmin + xmax) / 2) / img_width
        y_center = ((ymin + ymax) / 2) / img_height
        width = (xmax - xmin) / img_width
        height = (ymax - ymin) / img_height
        
        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
    
    return yolo_lines


def convert_coco_to_yolo(coco_json: Path, images_dir: Path) -> Dict[str, List[str]]:
    """
    Convert COCO JSON annotation format to YOLO txt format.
    
    Args:
        coco_json: Path to the COCO JSON file
        images_dir: Directory containing images referenced in COCO file
        
    Returns:
        Dictionary mapping filenames to lists of YOLO annotation lines.
    """
    with open(coco_json) as f:
        coco = json.load(f)
    
    yolo_annotations = {}
    img_id_to_size = {}
    
    # Map image IDs to their dimensions
    for img in coco["images"]:
        img_id_to_size[img["id"]] = (img["width"], img["height"])
    
    for ann in coco["annotations"]:
        img_id = ann["image_id"]
        category_id = ann["category_id"]
        
        cat_name = next((c["name"] for c in coco["categories"] if c["id"] == category_id), None)
        if not cat_name:
            continue
            
        label = CLASS_MAPPING.get(cat_name, cat_name)
        if label not in CLASSES:
            continue
        
        class_id = CLASSES.index(label)
        
        # COCO bbox: [x_min, y_min, width, height]
        bbox = ann["bbox"]
        x, y, w, h = bbox
        img_w, img_h = img_id_to_size[img_id]
        
        x_center = (x + w / 2) / img_w
        y_center = (y + h / 2) / img_h
        width = w / img_w
        height = h / img_h
        
        yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        
        img_filename = next((i["file_name"] for i in coco["images"] if i["id"] == img_id), None)
        if img_filename:
            if img_filename not in yolo_annotations:
                yolo_annotations[img_filename] = []
            yolo_annotations[img_filename].append(yolo_line)
    
    return yolo_annotations


def create_data_yaml():
    """
    Generate the data.yaml file required for YOLOv8 training.
    
    Defines dataset paths and class mapping for the training process.
    """
    content = f"""# SadakAI Road Hazard Dataset Configuration

path: {DATASET_ROOT.absolute()}
train: images/train
val: images/val
test: images/test

nc: {len(CLASSES)}
names:
"""
    for i, cls in enumerate(CLASSES):
        content += f"  {i}: {cls}\n"
    
    yaml_path = DATASET_ROOT / "data.yaml"
    yaml_path.write_text(content)
    print(f"Created {yaml_path}")


def create_split_directories():
    """Create the standard YOLO folder structure for dataset splits."""
    for split in ["train", "val", "test"]:
        (DATASET_ROOT / "images" / split).mkdir(parents=True, exist_ok=True)
        (DATASET_ROOT / "labels" / split).mkdir(parents=True, exist_ok=True)
    print("Created train/val/test directories")


def download_sample_datasets():
    """Print instructions for sourcing training data."""
    print("\n" + "="*60)
    print("DATASET DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print("""
1. RDD2022 Dataset:
   - Download from: https://github.com/sekilab/RoadDamageDataset
   - Contains 47k+ images from Japan, India, etc.

2. Indian Pothole Dataset:
   - Search "Indian Pothole" on Roboflow Universe
   - Specifically curated for Indian road conditions

3. Speed Breaker Dataset:
   - Search "speed breaker" on Roboflow Universe

4. After downloading:
   - Place images in model/data/images/{train,val,test}/
   - Place labels in model/data/labels/{train,val,test}/
   - Run this script with --validate to verify annotations
""")
    print("="*60)


def validate_annotations(sample_size: int = 50):
    """
    Validate a random sample of annotation files for correctness.
    
    Checks for:
    - Proper number of columns (class_id x y w h)
    - Valid class IDs
    - Normalized values (0-1 range)
    """
    print(f"\nValidating {sample_size} random annotations...")
    
    labels_dir = DATASET_ROOT / "labels"
    
    if not labels_dir.exists():
        print("No labels directory found!")
        return
    
    all_labels = list(labels_dir.rglob("*.txt"))
    if not all_labels:
        print("No label files found!")
        return
    
    random.shuffle(all_labels)
    sample_labels = all_labels[:sample_size]
    
    errors = 0
    for label_file in sample_labels:
        with open(label_file) as f:
            for i, line in enumerate(f):
                parts = line.strip().split()
                if len(parts) != 5:
                    print(f"Error in {label_file}:{i+1}: Invalid format")
                    errors += 1
                    continue
                
                try:
                    class_id, x, y, w, h = map(float, parts)
                    
                    if class_id < 0 or class_id >= len(CLASSES):
                        print(f"Error in {label_file}:{i+1}: Invalid class_id {class_id}")
                        errors += 1
                    
                    if not (0 <= x <= 1 and 0 <= y <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                        print(f"Error in {label_file}:{i+1}: Values out of range")
                        errors += 1
                except ValueError:
                    print(f"Error in {label_file}:{i+1}: Non-numeric values")
                    errors += 1
    
    print(f"Validation complete: {errors} errors found in {sample_size} files")


def count_dataset():
    """Count and display the number of images and labels in each split."""
    print("\nDataset Statistics:")
    print("-" * 40)
    
    for split in ["train", "val", "test"]:
        img_dir = DATASET_ROOT / "images" / split
        lbl_dir = DATASET_ROOT / "labels" / split
        
        img_count = len(list(img_dir.glob("*.jpg"))) + len(list(img_dir.glob("*.png")))
        lbl_count = len(list(lbl_dir.glob("*.txt")))
        
        print(f"{split:8s}: {img_count:5d} images, {lbl_count:5d} labels")


if __name__ == "__main__":
    import sys
    
    create_split_directories()
    create_data_yaml()
    download_sample_datasets()
    
    if "--validate" in sys.argv:
        validate_annotations()
    
    count_dataset()
