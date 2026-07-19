const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface DashboardOverview {
  total_reports: number;
  latest_score: number | null;
  email_status: string | null;
}

export interface ReportItem {
  id: string;
  business_name: string;
  industry: string;
  overall_score: number | null;
  approved: boolean;
  created_at: string;
  pdf_url?: string | null;
}

export const dashboardService = {
  async getOverview(token: string): Promise<DashboardOverview> {
    const res = await fetch(`${API_BASE}/dashboard`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load dashboard overview");
    }
    return data.data;
  },

  async getReports(token: string): Promise<ReportItem[]> {
    const res = await fetch(`${API_BASE}/dashboard/reports`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load reports");
    }
    return data.data;
  },
};
