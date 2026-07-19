"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/store/authStore";
import { dashboardService } from "@/services/dashboardService";
import ReportsTable from "@/components/dashboard/ReportsTable";
import { 
  Leaf, 
  Plus, 
  LogOut, 
  BarChart3, 
  Award, 
  Mail, 
  Sparkles, 
  CheckCircle,
  Clock,
  AlertTriangle,
  FolderKanban
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const router = useRouter();
  const { user, token, logout } = useAuthStore();

  // 1. Fetch dashboard overview metrics
  const { data: overview, isLoading: isOverviewLoading, error: overviewError } = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: () => dashboardService.getOverview(token || ""),
    enabled: !!token,
  });

  // 2. Fetch list of reports
  const { data: reports = [], isLoading: isReportsLoading } = useQuery({
    queryKey: ["dashboardReports"],
    queryFn: () => dashboardService.getReports(token || ""),
    enabled: !!token,
  });

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const getEmailStatusColor = (status: string | null | undefined) => {
    if (!status) return "text-slate-400 bg-slate-50 border-slate-100";
    switch (status.toUpperCase()) {
      case "DELIVERED":
        return "text-emerald-700 bg-emerald-50 border-emerald-100";
      case "SENDING":
      case "QUEUED":
        return "text-blue-700 bg-blue-50 border-blue-100";
      case "FAILED":
        return "text-red-700 bg-red-50 border-red-100";
      default:
        return "text-slate-700 bg-slate-50 border-slate-100";
    }
  };

  const getEmailIcon = (status: string | null | undefined) => {
    if (!status) return <Mail className="h-5 w-5 text-slate-400" />;
    switch (status.toUpperCase()) {
      case "DELIVERED":
        return <CheckCircle className="h-5 w-5 text-emerald-500" />;
      case "SENDING":
      case "QUEUED":
        return <Clock className="h-5 w-5 text-blue-500 animate-spin" />;
      case "FAILED":
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return <Mail className="h-5 w-5 text-slate-500" />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50/50">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-white border-r border-slate-100 flex flex-col justify-between p-6">
        <div className="space-y-8">
          {/* Logo */}
          <div className="flex items-center gap-2.5 text-emerald-700">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 shadow-md shadow-emerald-600/10 text-white">
              <Leaf className="h-5 w-5" />
            </div>
            <span className="font-bold text-lg leading-tight tracking-tight text-slate-900">
              Sustainability
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="space-y-1">
            <Link
              href="/dashboard"
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold bg-emerald-50 text-emerald-700 transition"
            >
              <BarChart3 className="h-4 w-4" />
              Dashboard
            </Link>
            <Link
              href="/assessment"
              className="flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition"
            >
              <Plus className="h-4 w-4" />
              New Assessment
            </Link>
          </nav>
        </div>

        {/* User profile & Logout */}
        <div className="border-t border-slate-100 pt-6 space-y-4">
          <div className="flex items-center gap-3 px-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-100 text-emerald-800 font-bold text-sm">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div className="overflow-hidden">
              <div className="font-semibold text-sm text-slate-900 truncate">{user?.full_name}</div>
              <div className="text-xs text-slate-400 truncate">{user?.email}</div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-semibold text-red-600 hover:bg-red-50 transition"
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-8 overflow-y-auto max-w-7xl mx-auto w-full">
        {/* Welcome Section */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              Welcome back, {user?.full_name || "Client"}
              <Sparkles className="h-5 w-5 text-amber-500 animate-pulse" />
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              Here is your company's sustainability posture and active carbon assessments.
            </p>
          </div>
          <Link
            href="/assessment"
            className="inline-flex items-center justify-center px-4 py-2.5 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-md shadow-emerald-600/10 hover:shadow-lg transition duration-150"
          >
            <Plus className="mr-2 h-4 w-4" />
            Start Assessment
          </Link>
        </header>

        {/* Loading Skeletons */}
        {isOverviewLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-white border border-slate-100 rounded-2xl p-6 animate-pulse">
                <div className="h-4 w-24 bg-slate-200 rounded mb-4" />
                <div className="h-8 w-16 bg-slate-200 rounded" />
              </div>
            ))}
          </div>
        ) : (
          /* Cards Grid */
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Total Reports */}
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                  Total Assessments
                </span>
                <span className="text-3xl font-extrabold text-slate-900 block">
                  {overview?.total_reports || 0}
                </span>
              </div>
              <div className="h-12 w-12 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-600">
                <FolderKanban className="h-6 w-6" />
              </div>
            </div>

            {/* Latest Score */}
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                  Latest Score
                </span>
                <span className="text-3xl font-extrabold text-slate-900 block">
                  {overview && overview.latest_score !== null ? `${overview.latest_score}/100` : "N/A"}
                </span>
              </div>
              <div className="h-12 w-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
                <Award className="h-6 w-6" />
              </div>
            </div>

            {/* Email Status */}
            <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
              <div className="space-y-1">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
                  Email Status
                </span>
                <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold border mt-2 ${getEmailStatusColor(overview?.email_status)}`}>
                  {overview?.email_status || "No Send Logs"}
                </span>
              </div>
              <div className="h-12 w-12 rounded-xl flex items-center justify-center border bg-slate-50">
                {getEmailIcon(overview?.email_status)}
              </div>
            </div>
          </div>
        )}

        {/* Reports Table Section */}
        <section className="space-y-4">
          <h2 className="text-xl font-bold text-slate-900">Recent Sustainability Reports</h2>
          {isReportsLoading ? (
            <div className="h-64 bg-white border border-slate-100 rounded-2xl animate-pulse" />
          ) : (
            <ReportsTable reports={reports} />
          )}
        </section>
      </main>
    </div>
  );
}
