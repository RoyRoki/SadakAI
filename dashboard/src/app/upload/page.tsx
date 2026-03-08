"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { Upload as UploadIcon, Loader2, MapPin, Camera, CameraOff, Locate, Clipboard, CheckCircle, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import type { DetectionResult } from "@/lib/types";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");
  const [gettingLocation, setGettingLocation] = useState(false);
  const [locationError, setLocationError] = useState("");
  const { showToast } = useToast();
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [stream, setStream] = useState<MediaStream | null>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith("image/")) {
      setFile(droppedFile);
      setPreview(URL.createObjectURL(droppedFile));
    }
  }, []);

  useEffect(() => {
    const handlePaste = (e: ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;
      
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith("image/")) {
          const blob = items[i].getAsFile();
          if (blob) {
            setFile(blob);
            setPreview(URL.createObjectURL(blob));
            break;
          }
        }
      }
    };
    
    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
    }
  };

  const pasteFromClipboard = async () => {
    try {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        for (const type of item.types) {
          if (type.startsWith("image/")) {
            const blob = await item.getType(type);
            const pastedFile = new File([blob], "paste.jpg", { type });
            setFile(pastedFile);
            setPreview(URL.createObjectURL(blob));
            return;
          }
        }
      }
      alert("No image found in clipboard");
    } catch (error) {
      console.error("Paste failed:", error);
      alert("Paste not supported. Please use Camera or Select Image");
    }
  };

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation not supported");
      return;
    }
    
    setGettingLocation(true);
    setLocationError("");
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLat(position.coords.latitude.toFixed(6));
        setLng(position.coords.longitude.toFixed(6));
        setGettingLocation(false);
      },
      (error) => {
        setLocationError(error.message);
        setGettingLocation(false);
      }
    );
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" } 
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setCameraActive(true);
    } catch (error) {
      console.error("Camera error:", error);
      alert("Could not access camera");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    setCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.drawImage(video, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const capturedFile = new File([blob], "capture.jpg", { type: "image/jpeg" });
          setFile(capturedFile);
          setPreview(canvas.toDataURL("image/jpeg"));
          stopCamera();
        }
      }, "image/jpeg");
    }
  };

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  const handleDetect = async () => {
    if (!file) {
      showToast("Please select an image first", "warning");
      return;
    }
    setLoading(true);
    setResult(null);

    try {
      const detection = await api.detectHazard(
        file,
        lat ? parseFloat(lat) : undefined,
        lng ? parseFloat(lng) : undefined
      );
      setResult(detection);
      if (detection.detections.length > 0) {
        showToast(`Found ${detection.detections.length} hazard(s)!`, "success");
      } else {
        showToast("No hazards detected", "info");
      }
    } catch (error) {
      console.error("Detection failed:", error);
      showToast("Detection failed. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Upload & Detect</h1>

      {!cameraActive ? (
        <div
          className="border-2 border-dashed border-border rounded-lg p-8 text-center mb-6"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          {preview ? (
            <img src={preview} alt="Preview" className="max-h-64 mx-auto rounded-lg" />
          ) : (
            <>
              <UploadIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground mb-2">
                Drag and drop an image, paste from clipboard, or use options below
              </p>
              <p className="text-xs text-muted-foreground">
                📋 Paste • 📷 Camera • 📁 Select File
              </p>
            </>
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
            id="file-input"
          />
          <label
            htmlFor="file-input"
            className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-lg cursor-pointer mr-2"
          >
            Select Image
          </label>
          <button
            onClick={startCamera}
            className="inline-block px-4 py-2 bg-secondary text-secondary-foreground rounded-lg mr-2"
          >
            <Camera className="w-4 h-4 inline mr-2" />
            Camera
          </button>
          <button
            onClick={pasteFromClipboard}
            className="inline-block px-4 py-2 bg-secondary text-secondary-foreground rounded-lg"
          >
            <Clipboard className="w-4 h-4 inline mr-2" />
            Paste
          </button>
        </div>
      ) : (
        <div className="mb-6">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full rounded-lg"
          />
          <canvas ref={canvasRef} className="hidden" />
          <div className="flex gap-2 mt-4 justify-center">
            <button
              onClick={capturePhoto}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg"
            >
              <Camera className="w-4 h-4 inline mr-2" />
              Capture
            </button>
            <button
              onClick={stopCamera}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg"
            >
              <CameraOff className="w-4 h-4 inline mr-2" />
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-2">Latitude</label>
          <div className="relative">
            <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="number"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              placeholder="26.7"
              className="w-full pl-10 px-4 py-2 bg-secondary rounded-lg border border-border"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Longitude</label>
          <input
            type="number"
            value={lng}
            onChange={(e) => setLng(e.target.value)}
            placeholder="88.4"
            className="w-full px-4 py-2 bg-secondary rounded-lg border border-border"
          />
        </div>
      </div>

      <button
        onClick={getCurrentLocation}
        disabled={gettingLocation}
        className="w-full mb-4 py-2 bg-secondary text-secondary-foreground rounded-lg flex items-center justify-center gap-2"
      >
        {gettingLocation ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Locate className="w-4 h-4" />
        )}
        {gettingLocation ? "Getting location..." : "Use Current Location"}
      </button>
      
      {locationError && (
        <p className="text-red-500 text-sm mb-4">{locationError}</p>
      )}

      <button
        onClick={handleDetect}
        disabled={!file || loading}
        className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Detecting...
          </span>
        ) : (
          "Detect Hazards"
        )}
      </button>

      {result && (
        <div className="mt-8">
          <h2 className="text-xl font-bold mb-4">Results</h2>
          <div className="grid gap-4">
            {result.detections.map((det, i) => (
              <div key={i} className="p-4 bg-secondary rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="capitalize font-medium">{det.class_name}</span>
                  <span
                    className="px-2 py-1 text-xs rounded"
                    style={{
                      backgroundColor:
                        det.severity === "critical"
                          ? "#ef4444"
                          : det.severity === "moderate"
                          ? "#f97316"
                          : "#fbbf24",
                      color: "#000",
                    }}
                  >
                    {det.severity}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  Confidence: {Math.round(det.confidence * 100)}%
                </p>
              </div>
            ))}
          </div>
          <div className="mt-4 p-4 bg-secondary rounded-lg">
            <p className="font-medium">Danger Score: {result.severity_score.toFixed(1)}/10</p>
          </div>
        </div>
      )}
    </div>
  );
}
