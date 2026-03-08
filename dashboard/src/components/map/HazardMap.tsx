"use client";

import { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { Hazard } from "@/lib/types";
import { api } from "@/lib/api";
import { Locate, Filter, X, RefreshCw, Layers, Eye, EyeOff } from "lucide-react";

const severityColors = {
  minor: "#fbbf24",
  moderate: "#f97316",
  critical: "#ef4444",
};

const hazardIcons = {
  pothole: "🕳️",
  crack: "裂",
  speed_breaker: "凸",
  waterlogging: "💧",
};

const createIcon = (severity: string, type: string) => {
  const color = severityColors[severity as keyof typeof severityColors] || "#fbbf24";
  const emoji = hazardIcons[type as keyof typeof hazardIcons] || "⚠️";
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="
      background-color: ${color};
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
    ">${emoji}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

function MyLocationButton() {
  const map = useMap();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation not supported");
      return;
    }
    setLoading(true);
    setError("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        map.flyTo([latitude, longitude], 15, { duration: 1 });
        setLoading(false);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
      }
    );
  };

  return (
    <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
      <button
        onClick={getLocation}
        disabled={loading}
        className="bg-white dark:bg-slate-800 p-3 rounded-full shadow-lg hover:shadow-xl transition-shadow disabled:opacity-50"
        title="My Location"
      >
        <Locate className={`w-5 h-5 text-slate-700 dark:text-slate-200 ${loading ? "animate-spin" : ""}`} />
      </button>
      {error && (
        <p className="bg-white dark:bg-slate-800 px-2 py-1 rounded text-xs text-red-500 shadow">{error}</p>
      )}
    </div>
  );
}

function MapEventsHandler({ onBoundsChange }: { onBoundsChange: (bounds: any) => void }) {
  const map = useMapEvents({
    moveend: () => {
      onBoundsChange(map.getBounds());
    },
  });
  return null;
}

export default function HazardMap() {
  const [hazards, setHazards] = useState<Hazard[]>([]);
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [filters, setFilters] = useState({
    severity: "" as string,
    type: "" as string,
    status: "" as string,
  });
  const [center] = useState<[number, number]>([26.7, 88.4]);

  useEffect(() => {
    loadHazards();
  }, [filters]);

  const loadHazards = async () => {
    setLoading(true);
    try {
      const data = await api.getHazards({ 
        page_size: 200,
        severity: filters.severity || undefined,
        type: filters.type || undefined,
        status: filters.status || undefined,
      });
      setHazards(data.items);
    } catch (error) {
      console.error("Failed to load hazards:", error);
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setFilters({ severity: "", type: "", status: "" });
  };

  const hasActiveFilters = filters.severity || filters.type || filters.status;

  return (
    <div className="h-full relative">
      <MapContainer
        center={center}
        zoom={13}
        className="h-full w-full"
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MyLocationButton />
        <MapEventsHandler onBoundsChange={() => {}} />

        {hazards.map((hazard) => {
          if (!hazard.location) return null;
          return (
            <Marker
              key={hazard.id}
              position={[hazard.location.lat, hazard.location.lng]}
              icon={createIcon(hazard.severity, hazard.type)}
            >
              <Popup>
                <div className="min-w-[180px]">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{hazardIcons[hazard.type as keyof hazardIcons] || "⚠️"}</span>
                    <div>
                      <p className="font-semibold capitalize">{hazard.type?.replace("_", " ")}</p>
                      <p className="text-xs text-gray-500 capitalize">{hazard.status}</p>
                    </div>
                  </div>
                  <div className="flex gap-2 mb-2">
                    <span
                      className="px-2 py-1 text-xs rounded-full font-medium"
                      style={{ 
                        backgroundColor: severityColors[hazard.severity as keyof typeof severityColors],
                        color: "#000"
                      }}
                    >
                      {hazard.severity}
                    </span>
                    <span className="px-2 py-1 text-xs rounded-full bg-gray-200">
                      {Math.round(hazard.confidence * 100)}% confidence
                    </span>
                  </div>
                  {hazard.address && (
                    <p className="text-xs text-gray-500 mb-1">📍 {hazard.address}</p>
                  )}
                  <p className="text-xs text-gray-400">
                    {new Date(hazard.created_at).toLocaleDateString()}
                  </p>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {/* Filter Button */}
      <button
        onClick={() => setShowFilters(!showFilters)}
        className="absolute top-4 left-4 z-[1000] bg-white dark:bg-slate-800 p-3 rounded-full shadow-lg hover:shadow-xl transition-shadow flex items-center gap-2"
      >
        <Filter className="w-5 h-5 text-slate-700 dark:text-slate-200" />
        {hasActiveFilters && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
            {(filters.severity ? 1 : 0) + (filters.type ? 1 : 0) + (filters.status ? 1 : 0)}
          </span>
        )}
      </button>

      {/* Refresh Button */}
      <button
        onClick={loadHazards}
        className="absolute top-4 left-16 z-[1000] bg-white dark:bg-slate-800 p-3 rounded-full shadow-lg hover:shadow-xl transition-shadow"
        title="Refresh"
      >
        <RefreshCw className={`w-5 h-5 text-slate-700 dark:text-slate-200 ${loading ? "animate-spin" : ""}`} />
      </button>

      {/* Heatmap Toggle */}
      <button
        onClick={() => setShowHeatmap(!showHeatmap)}
        className="absolute bottom-24 right-4 z-[1000] bg-white dark:bg-slate-800 p-3 rounded-full shadow-lg hover:shadow-xl transition-shadow"
        title="Toggle Heatmap"
      >
        <Layers className={`w-5 h-5 text-slate-700 dark:text-slate-200 ${showHeatmap ? "text-blue-500" : ""}`} />
      </button>

      {/* Filter Sidebar */}
      {showFilters && (
        <div className="absolute top-20 left-4 z-[1000] bg-white dark:bg-slate-800 rounded-xl shadow-xl p-4 w-64 animate-in slide-in-from-left duration-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold">Filters</h3>
            <button onClick={() => setShowFilters(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Severity</label>
              <select
                value={filters.severity}
                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
                className="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent"
              >
                <option value="">All</option>
                <option value="minor">Minor</option>
                <option value="moderate">Moderate</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Type</label>
              <select
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                className="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent"
              >
                <option value="">All</option>
                <option value="pothole">Pothole</option>
                <option value="crack">Crack</option>
                <option value="speed_breaker">Speed Breaker</option>
                <option value="waterlogging">Waterlogging</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Status</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                className="w-full p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent"
              >
                <option value="">All</option>
                <option value="active">Active</option>
                <option value="reported">Reported</option>
                <option value="fixed">Fixed</option>
              </select>
            </div>

            {hasActiveFilters && (
              <button
                onClick={clearFilters}
                className="w-full py-2 text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>
      )}

      {/* Stats Overlay */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-lg shadow-lg px-4 py-2 flex gap-4 text-sm">
        <span><strong className="text-slate-700 dark:text-slate-200">{hazards.length}</strong> hazards</span>
        <span className="text-yellow-500">● {hazards.filter(h => h.severity === "minor").length} minor</span>
        <span className="text-orange-500">● {hazards.filter(h => h.severity === "moderate").length} moderate</span>
        <span className="text-red-500">● {hazards.filter(h => h.severity === "critical").length} critical</span>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 z-[1000] bg-white/50 dark:bg-slate-800/50 flex items-center justify-center">
          <div className="bg-white dark:bg-slate-800 px-6 py-4 rounded-xl shadow-xl flex items-center gap-3">
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Loading hazards...</span>
          </div>
        </div>
      )}
    </div>
  );
}
