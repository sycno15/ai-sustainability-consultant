const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface EmailStatus {
  status: string;
  recipient: string;
  sent_at: string | null;
}

export const emailService = {
  async getEmailStatus(token: string, reportId: string): Promise<EmailStatus> {
    const res = await fetch(`${API_BASE}/reports/${reportId}/email-status`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to load email status");
    }
    return data.data;
  },

  async sendEmail(token: string, reportId: string): Promise<{ delivery_status: string }> {
    const res = await fetch(`${API_BASE}/reports/${reportId}/send-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.error?.message || "Failed to send email");
    }
    return data.data;
  },
};
