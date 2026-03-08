"use client";

import { useEffect, useState } from "react";
import { BarChart3, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { api } from "@/lib/api";
import type { StatsOverview } from "@/lib/types";

const COLORS = ["#ef4444", "#f97316", "#fbbf24", "#22c55e"];

function SkeletonCard({ className }: { className?: string }) {
  return <div className={`bg-gray-200 dark:bg-gray-700 rounded-lg ${className || ""} animate-pulse`} />;
}

function SkeletonChart() {
  return (
    <div className="p-4 bg-card rounded-lg border border-border">
      <div className="h-6 w-32 bg-gray-200 dark:bg-gray-700 rounded mb-4 animate-pulse" />
      <div className="h-[250px] bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
    </div>
  );
}

export default function StatsPage() {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [trends, setTrends] = useState<{ data: { date: string; count: number }[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [overview, trendData] = await Promise.all([
        api.getStatsOverview(),
        api.getStatsTrends("day"),
      ]);
      setStats(overview);
      setTrends(trendData);
    } catch (error) {
      console.error("Failed to load stats:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded mb-6 animate-pulse" />
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <SkeletonCard key={i} className="h-28" />
          ))}
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <SkeletonChart />
          <SkeletonChart />
          <SkeletonChart />
        </div>
      </div>
    );
  }

  const typeData = stats
    ? Object.entries(stats.by_type).map(([name, value]) => ({ name, value }))
    : [];
  const severityData = stats
    ? Object.entries(stats.by_severity).map(([name, value]) => ({ name, value }))
    : [];

  const statCards = [
    { label: "Total Hazards", value: stats?.total_hazards || 0, icon: BarChart3, color: "text-primary" },
    { label: "Critical", value: stats?.critical_count || 0, icon: AlertTriangle, color: "text-red-500" },
    { label: "Fixed", value: stats?.fixed_count || 0, icon: CheckCircle, color: "text-green-500" },
    { label: "Fix Rate", value: `${stats?.detection_rate || 0}%`, icon: TrendingUp, color: "text-blue-500" },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Statistics</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((card) => (
          <div key={card.label} className="p-4 bg-card rounded-lg border border-border">
            <div className="flex items-center gap-3 mb-2">
              <card.icon className={`w-5 h-5 ${card.color}`} />
              <span className="text-sm text-muted-foreground">{card.label}</span>
            </div>
            <p className="text-2xl font-bold">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="p-4 bg-card rounded-lg border border-border">
          <h2 className="text-lg font-semibold mb-4">Hazards by Type</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={typeData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {typeData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="p-4 bg-card rounded-lg border border-border">
          <h2 className="text-lg font-semibold mb-4">Severity Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={severityData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="p-4 bg-card rounded-lg border border-border lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Trends</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trends?.data || []}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
