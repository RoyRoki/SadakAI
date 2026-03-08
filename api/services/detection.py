import io
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# List of supported hazard classes for the YOLO model
CLASSES = ["pothole", "crack", "speed_breaker", "waterlogging"]


def run_inference(image_bytes: bytes, conf: float = 0.25, iou: float = 0.45) -> Dict[str, Any]:
    """
    Run YOLOv8 inference on an image to detect road hazards.
    
    This function currently simulates inference for testing purposes,
    returning random detections. In production, this would call the 
    actual model loaded in memory.
    
    Args:
        image_bytes: Raw image data
        conf: Confidence threshold for detections
        iou: Intersection-over-Union threshold for non-maximum suppression
        
    Returns:
        Dict containing success flag, list of detections, and overall danger score.
    """
    import random
    
    # Simulate a random number of detected hazards
    num_detections = random.randint(0, 3)
    detections = []
    
    for _ in range(num_detections):
        class_name = random.choice(CLASSES)
        
        detections.append({
            "class_name": class_name,
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "bbox": {
                "x1": random.randint(50, 200),
                "y1": random.randint(50, 200),
                "x2": random.randint(300, 500),
                "y2": random.randint(300, 500)
            },
            "severity": random.choice(["minor", "moderate", "critical"])
        })
    
    # Calculate a mock danger score based on detection count and random factor
    danger_score = len(detections) * random.uniform(1, 5)
    
    return {
        "success": True,
        "detections": detections,
        "danger_score": round(danger_score, 1),
        "image_size": {"width": 640, "height": 640}
    }


def annotate_image(image_bytes: bytes, detections: List[Dict[str, Any]]) -> bytes:
    """
    Draw bounding boxes and labels on the image based on detections.
    
    Args:
        image_bytes: Raw original image data
        detections: List of detection dictionaries with bbox and label
        
    Returns:
        Annotated image data in bytes.
    """
    # Returns original image for now as a placeholder
    # TODO: Implement actual annotation logic using OpenCV or PIL
    return image_bytes
