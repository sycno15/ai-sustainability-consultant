"use client";

import React, { useState } from "react";
import { ReportItem } from "@/services/dashboardService";
import { FileText, Download, ArrowRight, Calendar, Award, Mail } from "lucide-react";
import Link from "next/link";

interface ReportsTableProps {
  reports: ReportItem[];
}

export default function ReportsTable({ reports }: ReportsTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  // Pagination logic
  const totalPages = Math.ceil(reports.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedReports = reports.slice(startIndex, startIndex + itemsPerPage);

  if (reports.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-2xl border border-slate-100 shadow-sm">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 mb-4">
          <FileText className="h-6 w-6" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900">No reports generated yet</h3>
        <p className="text-sm text-slate-500 mt-1 max-w-sm">
          Run your first sustainability assessment to calculate emissions and generate AI recommendations.
        </p>
        <Link
          href="/assessment"
          className="mt-5 inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition"
        >
          Start Assessment
          <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden flex flex-col justify-between h-full">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50/50">
              <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-500">Report Details</th>
              <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-500">Industry</th>
              <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-500">Date Generated</th>
              <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-500">Score</th>
              <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-500">Status</th>
              <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-500 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-50">
            {paginatedReports.map((report) => (
              <tr key={report.id} className="hover:bg-slate-50/40 transition">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="font-semibold text-slate-900">{report.business_name}</div>
                      <div className="text-xs text-slate-400">ID: {report.id.substring(0, 8)}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 text-sm text-slate-600">{report.industry}</td>
                <td className="px-6 py-4 text-sm text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-4 w-4 text-slate-400" />
                    {new Date(report.created_at).toLocaleDateString()}
                  </div>
                </td>
                <td className="px-6 py-4">
                  {report.overall_score !== null ? (
                    <div className="flex items-center gap-1">
                      <Award className="h-4 w-4 text-emerald-500" />
                      <span className="font-semibold text-emerald-600">{report.overall_score}/100</span>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400">N/A</span>
                  )}
                </td>
                <td className="px-6 py-4">
                  {report.approved ? (
                    <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700 border border-emerald-100">
                      Approved
                    </span>
                  ) : (
                    <span className="inline-flex items-center rounded-full bg-blue-50 px-2 py-1 text-xs font-semibold text-blue-700 border border-blue-100 animate-pulse">
                      Draft Review
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    {report.approved ? (
                      <>
                        <Link
                          href={`/report/${report.id}`}
                          className="inline-flex items-center justify-center px-3 py-1.5 text-xs font-semibold text-slate-700 hover:text-emerald-700 bg-slate-100 hover:bg-emerald-50 rounded-lg transition"
                        >
                          View
                        </Link>
                        {report.pdf_url && (
                          <a
                            href={report.pdf_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:text-emerald-600 hover:border-emerald-200 transition"
                            title="Download PDF"
                          >
                            <Download className="h-4 w-4" />
                          </a>
                        )}
                      </>
                    ) : (
                      <Link
                        href={`/draft/${report.id}`}
                        className="inline-flex items-center justify-center px-3 py-1.5 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition"
                      >
                        Continue
                        <ArrowRight className="ml-1 h-3.5 w-3.5" />
                      </Link>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-slate-100 px-6 py-4 bg-slate-50/30">
          <div className="text-xs text-slate-500">
            Showing <span className="font-semibold text-slate-900">{startIndex + 1}</span> to{" "}
            <span className="font-semibold text-slate-900">
              {Math.min(startIndex + itemsPerPage, reports.length)}
            </span>{" "}
            of <span className="font-semibold text-slate-900">{reports.length}</span> reports
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 text-xs font-semibold border rounded-lg border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50 transition"
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-1 text-xs font-semibold border rounded-lg border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-50 transition"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
