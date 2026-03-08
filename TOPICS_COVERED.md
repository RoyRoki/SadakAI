# 📚 Technical Topics Covered: SadakAI

This document provides a detailed exploration of the engineering concepts, libraries, and architectural patterns implemented in the SadakAI project. It is designed to help you understand the "why" and "how" behind the code.

---

## 👁️ 1. Computer Vision & AI (Deep Dive)

The core of SadakAI is its ability to "see" and "understand" road conditions. This is achieved through a combination of Deep Learning (YOLOv8) and Digital Image Processing (OpenCV).

### A. YOLOv8 (You Only Look Once)
We use the **YOLOv8m (medium)** model for object detection.
- **Object Detection vs. Classification:** Unlike simple classification (which says "there is a pothole"), YOLO performs detection, providing both the **label** and the **coordinates** (Bounding Box) of multiple objects in a single frame.
- **Inference Pipeline:**
  1. **Image Resizing:** Input images are scaled to 640x640 pixels.
  2. **Feature Extraction:** The model uses a backbone (CSPDarknet) to extract visual patterns.
  3. **Non-Maximum Suppression (NMS):** Filters out overlapping boxes to ensure each hazard is only counted once.
  4. **Confidence Thresholding:** We ignore any detection with less than 25% confidence to reduce false positives.

### B. OpenCV (Open Source Computer Vision Library)
OpenCV is the "Swiss Army Knife" used to bridge the gap between raw image bytes and the AI model.

**Key OpenCV Operations in SadakAI:**
1. **Image Decoding (`cv2.imdecode`):**
   - The API receives images as raw bytes over HTTP.
   - OpenCV converts these bytes into a **NumPy array (BGR format)** that the system can manipulate.
2. **Color Space Transformation (`cv2.cvtColor`):**
   - OpenCV defaults to **BGR**, but YOLO and web browsers expect **RGB**. We use `COLOR_BGR2RGB` for consistency.
3. **Dynamic Annotation:**
   - **Bounding Boxes:** Using `cv2.rectangle` to draw borders around detected potholes.
   - **Labeling:** Using `cv2.putText` to write the hazard type and confidence score directly on the image.
   - **Severity Overlay:** Applying different colors (Yellow for Minor, Red for Critical) using BGR color tuples.
4. **Image Encoding (`cv2.imencode`):**
   - After drawing boxes, the NumPy array is converted back into a compressed format (JPEG/WebP) to be sent to the frontend or saved to Cloud Storage.

---

## ⚡ 2. Backend Engineering (FastAPI)

The backend is built with **FastAPI**, a modern, high-performance Python web framework.

- **Asynchronous Programming:** Utilizing `async/await` for non-blocking I/O, allowing the server to handle multiple image uploads simultaneously without waiting for the GPU/CPU to finish one.
- **Pydantic Data Validation:** Every request and response is strictly typed. If a client sends a latitude of "abc", Pydantic catches the error before it even reaches the logic.
- **Dependency Injection:** We use a `get_db` generator to manage database sessions efficiently, ensuring connections are opened and closed properly.
- **Lifespan Management:** The YOLO model is loaded into RAM **once** when the server starts, preventing a 2-3 second delay on every single request.

---

## 🗺️ 3. Geospatial & Data Layer

Handling "where" things are is just as important as "what" they are.

- **PostGIS (PostgreSQL Extension):** Adds support for geographic objects. We use it to store coordinates as `GEOMETRY` points.
- **Haversine Formula Approximation:** In the SQLite version, we implement manual math to calculate distances between coordinates for the "Hazards Nearby" feature.
- **Relational Modeling:** 
  - `Hazards` (The what/where)
  - `DetectionSessions` (Grouping multiple images from one trip)
  - `APIKeys` (Security and tracking)

---

## 🌐 4. Frontend & Data Visualization (Next.js 14)

The dashboard is a modern React application focusing on usability and speed.

- **App Router & Server Components:** Next.js 14 architecture for faster initial page loads and better SEO.
- **Leaflet.js Integration:** 
  - **Dynamic Markers:** Rendering 100+ hazards on a map using custom React components.
  - **Coordinate Mapping:** Translating backend `lat/lng` into interactive map points.
- **Recharts (Data Viz):**
  - **Time-Series Analysis:** Showing how many potholes are reported over a week.
  - **Distribution Charts:** Pie charts showing the ratio of Cracks vs. Potholes.
- **Responsive Design:** Using **Tailwind CSS** with a mobile-first approach, so engineers can use the dashboard on-site via mobile devices.

---

## 🐳 5. DevOps & MLOps

How the project is built and deployed.

- **Docker & Containerization:** The entire stack is containerized. The `Dockerfile` handles the installation of heavy dependencies like `libGL` (required by OpenCV) and `PyTorch`.
- **Cloudflare R2 Storage:** An S3-compatible, zero-egress storage solution used to host original and AI-annotated images.
- **Dataset Engineering:**
  - **Normalization:** Converting VOC/COCO formats to YOLO format.
  - **Data Augmentation:** Increasing dataset variety by artificially adding blur, noise, and rotations to images.

---

## 🚀 Summary of Skills Demonstrated
- **Python:** Advanced usage (FastAPI, NumPy, Ultralytics).
- **TypeScript:** Type-safe frontend architecture.
- **OpenCV:** Real-time image manipulation and drawing.
- **Machine Learning:** YOLOv8 lifecycle (Training -> Export -> Inference).
- **Geospatial:** SQL spatial queries and interactive mapping.
- **System Design:** Distributed architecture (API, DB, Storage).
