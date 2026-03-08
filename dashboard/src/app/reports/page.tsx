"use client";

import { useState } from "react";
import { FileDown, Calendar } from "lucide-react";
import { api } from "@/lib/api";

export default function ReportsPage() {
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [loading, setLoading] = useState(false);

  const downloadCSV = async () => {
    setLoading(true);
    try {
      const hazards = await api.getHazards({
        from_date: fromDate,
        to_date: toDate,
        page_size: 1000,
      });

      const headers = ["ID", "Type", "Severity", "Status", "Confidence", "Created At"];
      const rows = hazards.items.map((h) => [
        h.id,
        h.type,
        h.severity,
        h.status,
        h.confidence.toString(),
        h.created_at,
      ]);

      const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `sadakai-report-${fromDate}-${toDate}.csv`;
      a.click();
    } catch (error) {
      console.error("Failed to download CSV:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Generate Reports</h1>

      <div className="space-y-4 mb-8">
        <div>
          <label className="block text-sm font-medium mb-2">From Date</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="w-full pl-10 px-4 py-2 bg-secondary rounded-lg border border-border"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">To Date</label>
          <div className="relative">
            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="w-full pl-10 px-4 py-2 bg-secondary rounded-lg border border-border"
            />
          </div>
        </div>
      </div>

      <button
        onClick={downloadCSV}
        disabled={loading}
        className="w-full py-3 bg-primary text-primary-foreground rounded-lg font-medium disabled:opacity-50 flex items-center justify-center gap-2"
      >
        <FileDown className="w-5 h-5" />
        {loading ? "Generating..." : "Download CSV Report"}
      </button>

      <div className="mt-8 p-4 bg-secondary/50 rounded-lg">
        <h3 className="font-medium mb-2">Report Contents</h3>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>• All hazards within selected date range</li>
          <li>• Type, severity, and status information</li>
          <li>• Confidence scores</li>
          <li>• Timestamps</li>
        </ul>
      </div>
    </div>
  );
}
