const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface WorkflowStatus {
  status: string;
  current_agent: string | null;
  progress: number;
  retry_count: number;
}

export interface TimelineItem {
  agent: string;
  tool: string;
  duration: number;
  status: string;
}

export const workflowService = {
  async startWorkflow(token: string, id: string): Promise<{ status: string }> {
    const res = await fetch(`${API_BASE}/analysis/${id}/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to start workflow analysis");
    }
    return data.data;
  },

  async getStatus(token: string, id: string): Promise<WorkflowStatus> {
    const res = await fetch(`${API_BASE}/analysis/${id}/status`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load workflow status");
    }
    return data.data;
  },

  async getTimeline(token: string, id: string): Promise<TimelineItem[]> {
    const res = await fetch(`${API_BASE}/analysis/${id}/timeline`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load workflow timeline");
    }
    return data.data;
  },
};
