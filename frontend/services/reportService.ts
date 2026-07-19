const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface ReportContent {
  id: string;
  analysis_id: string;
  report_json: Record<string, any>;
  pdf_url: string | null;
  approved: boolean;
  overall_score: number | null;
}

export const reportService = {
  async getReport(token: string, id: string): Promise<ReportContent> {
    const res = await fetch(`${API_BASE}/reports/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load report");
    }
    return data.data;
  },

  async submitFeedback(token: string, id: string, feedback: string): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/reports/${id}/feedback`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ feedback }),
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to submit feedback");
    }
    return data.data;
  },

  async approveReport(token: string, id: string): Promise<{ report_status: string; email_status: string }> {
    const res = await fetch(`${API_BASE}/reports/${id}/approve`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to approve report");
    }
    return data.data;
  },

  async getJSON(token: string, id: string): Promise<Record<string, any>> {
    const res = await fetch(`${API_BASE}/reports/${id}/json`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load report JSON");
    }
    return data.data;
  },
};
