import axios from "axios";
import type { Hazard, HazardFilters, HazardListResponse, DetectionResult, StatsOverview } from "./types";

const baseURL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") + "/api";

const client = axios.create({
  baseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const api = {
  async getHazards(filters: HazardFilters = {}): Promise<HazardListResponse> {
    const params = new URLSearchParams();
    if (filters.page) params.append("page", filters.page.toString());
    if (filters.page_size) params.append("page_size", filters.page_size.toString());
    if (filters.severity) params.append("severity", filters.severity);
    if (filters.type) params.append("hazard_type", filters.type);
    if (filters.status) params.append("status", filters.status);
    if (filters.from_date) params.append("from_date", filters.from_date);
    if (filters.to_date) params.append("to_date", filters.to_date);

    const { data } = await client.get(`/hazards?${params}`);
    return data;
  },

  async getHazard(id: string): Promise<Hazard> {
    const { data } = await client.get(`/hazards/${id}`);
    return data;
  },

  async updateHazard(id: string, update: { status?: string; address?: string }): Promise<void> {
    await client.patch(`/hazards/${id}`, update);
  },

  async deleteHazard(id: string): Promise<void> {
    await client.delete(`/hazards/${id}`);
  },

  async getNearbyHazards(lat: number, lng: number, radiusKm: number = 5) {
    const { data } = await client.get("/hazards/nearby", {
      params: { lat, lng, radius_km: radiusKm },
    });
    return data;
  },

  async detectHazard(file: File, lat?: number, lng?: number): Promise<DetectionResult> {
    const formData = new FormData();
    formData.append("file", file);
    if (lat) formData.append("lat", lat.toString());
    if (lng) formData.append("lng", lng.toString());

    const { data } = await client.post("/detect", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  async getStatsOverview(fromDate?: string, toDate?: string): Promise<StatsOverview> {
    const params = new URLSearchParams();
    if (fromDate) params.append("from_date", fromDate);
    if (toDate) params.append("to_date", toDate);

    const { data } = await client.get(`/stats/overview?${params}`);
    return data;
  },

  async getStatsTrends(period: string = "day", fromDate?: string, toDate?: string) {
    const params = new URLSearchParams();
    params.append("period", period);
    if (fromDate) params.append("from_date", fromDate);
    if (toDate) params.append("to_date", toDate);

    const { data } = await client.get(`/stats/trends?${params}`);
    return data;
  },

  async getWorstAreas(limit: number = 10) {
    const { data } = await client.get(`/stats/worst-roads?limit=${limit}`);
    return data;
  },

  async healthCheck() {
    const { data } = await client.get("/health");
    return data;
  },
};
