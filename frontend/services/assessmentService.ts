const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface AssessmentPayload {
  business_name: string;
  industry: string;
  company_size: "Small" | "Medium" | "Large";
  description?: string;
  
  electricity_usage: number;
  diesel_usage: number;
  petrol_usage: number;
  water_usage: number;
  waste_generated: number;
  
  annual_revenue: number;
  sustainability_budget: number;
}

export interface AssessmentResponse {
  assessment_id: string;
  workflow_status: string;
}

export interface AssessmentMetricDetail {
  electricity_usage: number;
  diesel_usage: number;
  petrol_usage: number;
  water_usage: number;
  waste_generated: number;
  annual_revenue: number;
  sustainability_budget: number;
}

export interface AssessmentDetail {
  id: string;
  business_name: string;
  industry: string;
  company_size: string;
  description: string | null;
  metrics: AssessmentMetricDetail | null;
}

export const assessmentService = {
  async createAssessment(token: string, payload: AssessmentPayload): Promise<AssessmentResponse> {
    const res = await fetch(`${API_BASE}/assessments`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to submit assessment");
    }
    return data.data;
  },

  async getAssessment(token: string, id: string): Promise<AssessmentDetail> {
    const res = await fetch(`${API_BASE}/assessments/${id}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load assessment details");
    }
    return data.data;
  },

  async deleteAssessment(token: string, id: string): Promise<boolean> {
    const res = await fetch(`${API_BASE}/assessments/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) {
      // Decode error if possible
      try {
        const data = await res.json();
        throw new Error(data.error?.message || "Failed to delete assessment");
      } catch (e: any) {
        throw new Error(e.message || "Failed to delete assessment");
      }
    }
    return true;
  },
};
