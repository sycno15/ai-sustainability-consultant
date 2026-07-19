"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { reportService, ReportContent } from "@/services/reportService";
import {
  Leaf,
  ArrowLeft,
  Award,
  Download,
  Loader2,
  CheckCircle2,
  Mail,
} from "lucide-react";
import { emailService } from "@/services/emailService";

function normalizeReportBody(reportJson: Record<string, any>) {
  if (reportJson?.report && typeof reportJson.report === "object") {
    return reportJson.report;
  }
  return reportJson || {};
}

function asList(value: unknown): string[] {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.map((item) => {
      if (typeof item === "string") return item;
      if (item && typeof item === "object" && "title" in item) {
        return String((item as { title: unknown }).title);
      }
      return JSON.stringify(item);
    });
  }
  if (typeof value === "string") return [value];
  return [String(value)];
}

export default function ApprovedReportPage() {
  const params = useParams();
  const { token } = useAuthStore();
  const id = params.id as string;

  const [report, setReport] = useState<ReportContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEmailing, setIsEmailing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!token || !id) return;
      setIsLoading(true);
      setErrorMsg(null);
      try {
        const data = await reportService.getReport(token, id);
        setReport(data);
      } catch (err: any) {
        setErrorMsg(err.message || "Failed to load report");
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [token, id]);

  const body = useMemo(() => normalizeReportBody(report?.report_json || {}), [report]);

  const handleResendEmail = async () => {
    if (!token || !report) return;
    setIsEmailing(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      await emailService.sendEmail(token, report.id);
      setSuccessMsg("Report email queued successfully.");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to send email");
    } finally {
      setIsEmailing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-slate-50 px-4">
        <p className="text-slate-700">{errorMsg || "Report not found."}</p>
        <Link href="/dashboard" className="text-emerald-700 font-semibold hover:underline">
          Back to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-50 to-teal-50">
      <header className="border-b border-slate-100 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
          <Link href="/dashboard" className="inline-flex items-center gap-2 text-slate-600 hover:text-emerald-700">
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Link>
          <div className="inline-flex items-center gap-2 font-semibold text-emerald-800">
            <Leaf className="h-5 w-5" />
            Final Report
          </div>
          <div className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">
            <Award className="h-4 w-4" />
            {report.overall_score ?? "—"}/100
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 px-4 py-8">
        {errorMsg && (
          <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            {errorMsg}
          </div>
        )}
        {successMsg && (
          <div className="rounded-xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
            {successMsg}
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          {report.pdf_url ? (
            <a
              href={report.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700"
            >
              <Download className="mr-2 h-4 w-4" />
              Download PDF
            </a>
          ) : (
            <span className="inline-flex items-center rounded-lg bg-slate-100 px-4 py-2 text-sm text-slate-500">
              PDF is still generating…
            </span>
          )}
          <button
            onClick={handleResendEmail}
            disabled={isEmailing || !report.approved}
            className="inline-flex items-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
          >
            {isEmailing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Mail className="mr-2 h-4 w-4" />}
            Resend Email
          </button>
        </div>

        <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-900">Executive Summary</h1>
          <p className="mt-3 text-slate-600 leading-relaxed">
            {body.executive_summary || "No executive summary available."}
          </p>
        </section>

        <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Carbon Analysis</h2>
          <p className="mt-3 text-slate-600 leading-relaxed">
            {typeof body.carbon_analysis === "string"
              ? body.carbon_analysis
              : JSON.stringify(body.carbon_analysis || "No carbon analysis available.")}
          </p>
        </section>

        <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Recommendations</h2>
          <ul className="mt-3 space-y-2">
            {asList(body.recommendations).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-slate-600">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="grid gap-6 md:grid-cols-2">
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Financial Summary</h2>
            <p className="mt-3 text-slate-600 leading-relaxed">
              {typeof body.financial_summary === "string"
                ? body.financial_summary
                : JSON.stringify(body.financial_summary || "No financial summary available.")}
            </p>
          </div>
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Implementation Plan</h2>
            <p className="mt-3 text-slate-600 leading-relaxed">
              {typeof body.implementation_plan === "string"
                ? body.implementation_plan
                : JSON.stringify(body.implementation_plan || "No implementation plan available.")}
            </p>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-900">Next Steps</h2>
          <ul className="mt-3 list-disc space-y-1 pl-5 text-slate-600">
            {asList(body.next_steps).map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ul>
        </section>
      </main>
    </div>
  );
}
