"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { workflowService, WorkflowStatus, TimelineItem } from "@/services/workflowService";
import { 
  Leaf, 
  Settings, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  ArrowRight, 
  History,
  FileText,
  DollarSign,
  TrendingDown,
  Calendar,
  AlertOctagon,
  Eye,
  Bot
} from "lucide-react";
import Link from "next/link";

const AGENTS_SEQUENCE = [
  "Carbon Agent",
  "Recommendation Agent",
  "Financial Agent",
  "Planner Agent",
  "Critic Agent",
  "Report Agent"
];

const AGENT_INFO: Record<string, { desc: string; icon: any; color: string }> = {
  "Carbon Agent": {
    desc: "Calculates greenhouse gas footprint from resource metrics.",
    icon: Leaf,
    color: "bg-emerald-500 shadow-emerald-500/10 text-emerald-600"
  },
  "Recommendation Agent": {
    desc: "Matches carbon hotspots to carbon-reduction measures.",
    icon: TrendingDown,
    color: "bg-blue-500 shadow-blue-500/10 text-blue-600"
  },
  "Financial Agent": {
    desc: "Calculates costs, savings, ROI and payback timelines.",
    icon: DollarSign,
    color: "bg-purple-500 shadow-purple-500/10 text-purple-600"
  },
  "Planner Agent": {
    desc: "Converts measures into a phased implementation roadmap.",
    icon: Calendar,
    color: "bg-orange-500 shadow-orange-500/10 text-orange-600"
  },
  "Critic Agent": {
    desc: "Reviews logical consistency and confidence metrics.",
    icon: AlertOctagon,
    color: "bg-rose-500 shadow-rose-500/10 text-rose-600"
  },
  "Report Agent": {
    desc: "Assembles validated agent outputs into a unified report draft.",
    icon: FileText,
    color: "bg-teal-500 shadow-teal-500/10 text-teal-600"
  }
};

export default function AnalysisProgressPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const { token } = useAuthStore();
  const [statusInfo, setStatusInfo] = useState<WorkflowStatus | null>(null);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize and start workflow
  useEffect(() => {
    if (!token || !id) return;

    const startAndMonitor = async () => {
      try {
        // Trigger workflow start.
        // If it was already started (e.g. page refresh), the backend might return 400,
        // which we catch and proceed directly to monitoring.
        await workflowService.startWorkflow(token, id);
      } catch (err: any) {
        logger_local("Workflow start notice (resuming session): " + err.message);
      }
      
      // Start polling status
      fetchLatestStatus();
      pollingRef.current = setInterval(fetchLatestStatus, 2000);
    };

    startAndMonitor();

    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [token, id]);

  const fetchLatestStatus = async () => {
    if (!token || !id) return;
    try {
      const stats = await workflowService.getStatus(token, id);
      setStatusInfo(stats);
      
      // Fetch timeline logs
      const logs = await workflowService.getTimeline(token, id);
      setTimeline(logs);

      // Stop polling and redirect once completed
      if (stats.status === "COMPLETED" || stats.status === "APPROVED") {
        if (pollingRef.current) clearInterval(pollingRef.current);
        // Wait 2 seconds so the user sees the 100% completion state, then redirect to draft report review
        setTimeout(() => {
          if (stats.report_id) {
            router.push(`/draft/${stats.report_id}`);
          } else {
            setErrorMsg("Analysis completed, but the report draft is not ready yet. Open it from the dashboard.");
          }
        }, 2000);
      } else if (stats.status === "FAILED") {
        if (pollingRef.current) clearInterval(pollingRef.current);
      }
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to sync workflow progress");
    }
  };

  const getAgentCardStatus = (agentName: string) => {
    if (!statusInfo) return "Waiting";
    const globalStatus = statusInfo.status;
    
    if (globalStatus === "COMPLETED" || globalStatus === "APPROVED") {
      return "Success";
    }
    
    if (globalStatus === "FAILED" && statusInfo.current_agent === agentName) {
      return "Failed";
    }
    
    const currentIndex = AGENTS_SEQUENCE.indexOf(statusInfo.current_agent || "");
    const targetIndex = AGENTS_SEQUENCE.indexOf(agentName);
    
    if (currentIndex === -1) return "Waiting";
    if (targetIndex < currentIndex) return "Success";
    if (targetIndex === currentIndex) {
      return globalStatus === "RUNNING" ? "Running" : "Waiting";
    }
    return "Waiting";
  };

  const logger_local = (msg: string) => {
    console.log("[Client Analysis]", msg);
  };

  const getBadgeStyle = (state: string) => {
    switch (state) {
      case "Success":
        return "bg-emerald-50 text-emerald-700 border-emerald-100";
      case "Running":
        return "bg-blue-50 text-blue-700 border-blue-100 animate-pulse";
      case "Failed":
        return "bg-red-50 text-red-700 border-red-100";
      default:
        return "bg-slate-50 text-slate-400 border-slate-100";
    }
  };

  return (
    <div className="min-h-screen bg-slate-50/50 flex flex-col justify-between py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto w-full space-y-8">
        {/* Header section */}
        <div className="flex flex-col items-center text-center">
          <Link href="/dashboard" className="flex items-center gap-2 text-emerald-700 hover:text-emerald-800 transition">
            <Leaf className="h-6 w-6" />
            <span className="font-bold text-lg">Sustainability Consultant</span>
          </Link>
          <h2 className="mt-4 text-2xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
            AI Multi-Agent Analysis Running
            <Bot className="h-6 w-6 text-emerald-600 animate-bounce-subtle" />
          </h2>
          <p className="mt-1 text-sm text-slate-500 max-w-md">
            Our autonomous agents are working collaboratively in sequence to compute emissions, formulate measures, check budgets, and compile your report.
          </p>
        </div>

        {/* Global Progress Bar Card */}
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4">
          <div className="flex justify-between items-center text-sm font-semibold">
            <span className="text-slate-700">
              {statusInfo?.status === "COMPLETED" ? "Analysis Complete!" : `Agent Step: ${statusInfo?.current_agent || "Initializing..."}`}
            </span>
            <span className="text-emerald-600">{statusInfo?.progress || 0}%</span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
            <div 
              className="bg-emerald-600 h-full rounded-full transition-all duration-500 ease-out"
              style={{ width: `${statusInfo?.progress || 5}%` }}
            />
          </div>

          {statusInfo?.retry_count && statusInfo.retry_count > 0 ? (
            <div className="text-xs text-amber-600 font-medium bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-100 inline-block">
              Critic flagged revision: Replanning attempt {statusInfo.retry_count}/2
            </div>
          ) : null}
        </div>

        {/* Agent Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {AGENTS_SEQUENCE.map((agentName) => {
            const cardState = getAgentCardStatus(agentName);
            const agentMeta = AGENT_INFO[agentName];
            const IconComp = agentMeta.icon;

            return (
              <div 
                key={agentName}
                className={`bg-white p-5 rounded-2xl border transition shadow-sm flex items-start gap-4 ${
                  cardState === "Running" 
                    ? "border-blue-200 ring-2 ring-blue-50" 
                    : cardState === "Success" 
                    ? "border-emerald-100" 
                    : "border-slate-100"
                }`}
              >
                <div className={`p-3 rounded-xl text-white ${cardState !== "Waiting" ? agentMeta.color.split(" ")[0] : "bg-slate-200 text-slate-400"}`}>
                  <IconComp className="h-5 w-5" />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-slate-800">{agentName}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${getBadgeStyle(cardState)}`}>
                      {cardState}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-normal">{agentMeta.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Timeline Log History */}
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4">
          <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2 border-b border-slate-100 pb-2">
            <History className="h-4 w-4 text-slate-500" />
            Execution Timeline Log
          </h3>

          {timeline.length === 0 ? (
            <div className="text-center py-6 text-xs text-slate-400">
              Waiting for agent activity logs...
            </div>
          ) : (
            <div className="space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100">
              {timeline.map((item, idx) => (
                <div key={idx} className="flex gap-4 items-start relative pl-1.5">
                  <div className="flex h-4 w-4 items-center justify-center rounded-full bg-white border border-emerald-500 z-10">
                    <div className="h-2 w-2 rounded-full bg-emerald-500" />
                  </div>
                  <div className="flex-1 text-xs space-y-0.5">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-slate-800">
                        {item.agent} invoked tool: <code className="bg-slate-50 px-1 rounded text-emerald-800">{item.tool}</code>
                      </span>
                      <span className="text-[10px] text-slate-400">
                        {item.duration.toFixed(2)}s
                      </span>
                    </div>
                    <div className="text-slate-400">
                      Execution status: <span className={item.status === "Success" ? "text-emerald-600 font-medium" : "text-red-500 font-medium"}>{item.status}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Error view */}
        {errorMsg && (
          <div className="rounded-lg bg-red-50 p-4 border border-red-100 text-sm text-red-800 font-medium">
            {errorMsg}
          </div>
        )}

        {/* Action Bottom */}
        {statusInfo?.status === "COMPLETED" || statusInfo?.status === "APPROVED" ? (
          <div className="text-center">
            <Link
              href={`/draft/${id}`}
              className="inline-flex items-center justify-center px-5 py-3 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-xl shadow-lg shadow-emerald-600/10 transition"
            >
              Redirecting to Report...
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </div>
        ) : null}
      </div>
    </div>
  );
}
