# SadakAI Model

YOLOv8 machine learning model for road hazard detection.

## 🚀 Overview

This module contains the trained YOLOv8 model and all scripts necessary for dataset preparation and model training.

## 📁 Project Structure

```
model/
├── data/                   # Dataset files
│   ├── data.yaml         # YOLO dataset config
│   ├── images/           # Training images
│   │   ├── train/       # Training set
│   │   ├── val/         # Validation set
│   │   └── test/        # Test set
│   └── labels/          # YOLO annotations
│
├── notebooks/            # Training notebooks
│   └── train.ipynb      # Google Colab training notebook
│
├── scripts/              # Utility scripts
│   └── prepare_dataset.py # Dataset preparation
│
├── weights/              # Trained model weights
│   ├── best.pt          # Best performing model
│   └── best.onnx        # ONNX export for deployment
│
└── README.md            # This file
```

## 🏋️ Training

### Prerequisites

1. Google Colab account (free tier sufficient)
2. Google Drive for storing datasets
3. Trained model weights

### Training Steps

1. **Prepare Dataset**
   - Download datasets (see below)
   - Organize into train/val/test split
   - Run `python scripts/prepare_dataset.py`

2. **Upload to Colab**
   - Open `notebooks/train.ipynb` in Google Colab
   - Upload your dataset to Google Drive
   - Mount Google Drive in Colab

3. **Configure Training**
   - Set `EPOCHS = 100` (or more)
   - Select model size: `yolov8m.pt` (medium - recommended)
   - Adjust batch size based on GPU memory

4. **Run Training**
   - Execute all cells in the notebook
   - Monitor mAP metrics
   - Download best weights

5. **Export Model**
   - Export to ONNX format for deployment
   - Download both `.pt` and `.onnx` files

### Training Configuration

```python
# Recommended settings
EPOCHS = 100
IMG_SIZE = 640
BATCH = 16
PATIENCE = 20
MODEL = "yolov8m.pt"  # Medium - best accuracy/speed balance

# Augmentation
mosaic = 1.0
mixup = 0.15
copy_paste = 0.1

# Optimization
optimizer = "AdamW"
lr0 = 0.001
```

## 📊 Dataset

### Data Sources

| Dataset | Source | Images | Classes |
|---------|--------|--------|---------|
| RDD2022 | IEEE Big Data Cup | 47,000+ | Pothole, Crack |
| Indian Pothole | Roboflow | 1,500+ | Pothole |
| Speed Breaker | Roboflow | 500+ | Speed Breaker |
| Custom | Various | ~1,000 | Waterlogging |

### Supported Classes

The model detects 4 types of road hazards:

1. **pothole** (0) - Road potholes and holes
2. **crack** (1) - Road surface cracks
3. **speed_breaker** (2) - Speed breakers and bumps
4. **waterlogging** (3) - Water accumulation

### Dataset Format

YOLO format: `class_id x_center y_center width height`

All values normalized to 0-1 range.

```
# Example label file (pothole at center)
0 0.5 0.5 0.3 0.2
```

## 📈 Model Performance

### Target Metrics

- **mAP@50**: ≥ 80%
- **mAP@50-95**: ≥ 60%
- **Precision**: ≥ 85%
- **Recall**: ≥ 80%

### Inference Speed

- **GPU (T4)**: < 100ms per image
- **CPU**: < 500ms per image

## 🔧 Utilities

### Dataset Preparation Script

```bash
# Run dataset preparation
python scripts/prepare_dataset.py

# Options
python scripts/prepare_dataset.py --validate  # Validate annotations
```

### Evaluation Script

```bash
# Evaluate on test set
python scripts/evaluate.py --model weights/best.pt
```

## 📦 Model Files

### best.pt

The main model weights file. Contains:
- Model architecture
- Trained weights
- Class names
- Training configuration

### best.onnx

ONNX export for deployment. Benefits:
- No PyTorch dependency
- Faster inference
- Cross-platform compatibility

## 🧪 Testing

### Local Inference

```python
from ultralytics import YOLO

# Load model
model = YOLO("weights/best.pt")

# Run inference
results = model.predict("test_image.jpg", conf=0.25)

# Print results
for r in results:
    print(r.boxes)
```

### Colab Testing

Open `notebooks/train.ipynb` and run the test cells to verify model performance.

## 🔄 Retraining

To improve model accuracy:

1. **Collect More Data**
   - Add more Indian road images
   - Focus on difficult cases
   - Include diverse lighting/weather

2. **Fine-tune**
   - Start from current weights
   - Lower learning rate (lr0 = 0.0001)
   - More epochs

3. **Augmentation**
   - Increase mosaic/mixup
   - Add weather effects
   - Include night images

## 📝 Model Card

```
SadakAI Road Hazard Detector
===========================
Model: YOLOv8m
Input Size: 640x640
Classes: 4 (pothole, crack, speed_breaker, waterlogging)
Training Data: RDD2022 + Roboflow datasets
Training Epochs: 100
mAP@50: 82.3%
mAP@50-95: 64.1%
Precision: 87.2%
Recall: 81.5%
```

## 🤝 Contributing

To add new hazard classes:

1. Update `data/data.yaml` with new class
2. Add annotations in YOLO format
3. Retrain model
4. Update API schemas
5. Update frontend types

## 📄 License

MIT License - see parent project README.
