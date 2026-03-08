export interface Hazard {
  id: string;
  type: "pothole" | "crack" | "speed_breaker" | "waterlogging";
  severity: "minor" | "moderate" | "critical";
  status: "active" | "reported" | "fixed";
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  location?: {
    lat: number;
    lng: number;
  };
  address?: string;
  original_image?: string;
  annotated_image?: string;
  danger_score?: number;
  created_at: string;
  updated_at: string;
}

export interface Detection {
  class_name: string;
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
  };
  severity: "minor" | "moderate" | "critical";
}

export interface DetectionResult {
  id: string;
  detections: Detection[];
  annotated_image_url?: string;
  severity_score: number;
  location?: {
    lat: number;
    lng: number;
  };
}

export interface StatsOverview {
  total_hazards: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  critical_count: number;
  fixed_count: number;
  detection_rate: number;
}

export interface HazardFilters {
  page?: number;
  page_size?: number;
  severity?: string;
  type?: string;
  status?: string;
  from_date?: string;
  to_date?: string;
}

export interface HazardListResponse {
  items: Hazard[];
  total: number;
  page: number;
  page_size: number;
}
