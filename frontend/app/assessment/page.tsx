"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useAuthStore } from "@/store/authStore";
import { assessmentService, AssessmentPayload } from "@/services/assessmentService";
import { Button } from "@/components/ui/button";
import { 
  Leaf, 
  ChevronRight, 
  ChevronLeft, 
  Loader2, 
  Building, 
  Zap, 
  CircleDollarSign, 
  Target 
} from "lucide-react";
import Link from "next/link";

// 1. Wizard schemas per step for fine-grained validation
const step1Schema = z.object({
  business_name: z.string().min(1, "Business name is required"),
  industry: z.string().min(1, "Industry is required"),
  company_size: z.enum(["Small", "Medium", "Large"]),
  description: z.string().max(300, "Description must be less than 300 characters").optional(),
});

const step2Schema = z.object({
  electricity_usage: z.number().min(0, "Must be a positive number"),
  diesel_usage: z.number().min(0, "Must be a positive number"),
  petrol_usage: z.number().min(0, "Must be a positive number"),
  water_usage: z.number().min(0, "Must be a positive number"),
  waste_generated: z.number().min(0, "Must be a positive number"),
});

const step3Schema = z.object({
  annual_revenue: z.number().min(0, "Must be a positive number"),
  sustainability_budget: z.number().min(0, "Must be a positive number"),
});

const step4Schema = z.object({
  reduction_goal: z.number().min(0, "Goal must be positive").max(100, "Goal cannot exceed 100%").optional(),
  priority: z.string().optional(),
  timeline_months: z.number().min(1, "Timeline must be at least 1 month").optional(),
  notes: z.string().max(300).optional(),
});

// Full form model
const wizardSchema = step1Schema.merge(step2Schema).merge(step3Schema).merge(step4Schema);
type WizardFormValues = z.infer<typeof wizardSchema>;

export default function AssessmentWizardPage() {
  const router = useRouter();
  const { token } = useAuthStore();
  const [step, setStep] = useState(1);
  const [isPending, setIsPending] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    trigger,
    getValues,
    setValue,
    formState: { errors },
  } = useForm<WizardFormValues>({
    resolver: zodResolver(wizardSchema),
    defaultValues: {
      business_name: "",
      industry: "Manufacturing",
      company_size: "Medium",
      description: "",
      electricity_usage: 0,
      diesel_usage: 0,
      petrol_usage: 0,
      water_usage: 0,
      waste_generated: 0,
      annual_revenue: 0,
      sustainability_budget: 0,
      reduction_goal: 20,
      priority: "ROI",
      timeline_months: 12,
      notes: "",
    },
  });

  const handleNext = async (e?: React.MouseEvent) => {
    e?.preventDefault();
    // Validate current step fields before proceeding
    let fieldsToValidate: (keyof WizardFormValues)[] = [];
    if (step === 1) {
      fieldsToValidate = ["business_name", "industry", "company_size", "description"];
    } else if (step === 2) {
      fieldsToValidate = [
        "electricity_usage",
        "diesel_usage",
        "petrol_usage",
        "water_usage",
        "waste_generated",
      ];
    } else if (step === 3) {
      fieldsToValidate = ["annual_revenue", "sustainability_budget"];
    }

    const isValid = await trigger(fieldsToValidate);
    if (isValid) {
      setStep((s) => Math.min(s + 1, 4));
    }
  };

  const handlePrev = (e?: React.MouseEvent) => {
    e?.preventDefault();
    setStep((s) => Math.max(s - 1, 1));
  };

  const onSubmit = async (values: WizardFormValues) => {
    // Guard: only allow submit from the Goals step
    if (step !== 4) {
      await handleNext();
      return;
    }

    setIsPending(true);
    setSubmitError(null);
    try {
      const payload: AssessmentPayload = {
        business_name: values.business_name,
        industry: values.industry,
        company_size: values.company_size,
        description: values.description || "",
        electricity_usage: values.electricity_usage,
        diesel_usage: values.diesel_usage,
        petrol_usage: values.petrol_usage,
        water_usage: values.water_usage,
        waste_generated: values.waste_generated,
        annual_revenue: values.annual_revenue,
        sustainability_budget: values.sustainability_budget,
        reduction_goal: values.reduction_goal ?? 20,
        priority: values.priority || "ROI",
        timeline_months: values.timeline_months ?? 12,
        notes: values.notes || "",
      };

      const result = await assessmentService.createAssessment(token || "", payload);
      router.push(`/analysis/${result.assessment_id}`);
    } catch (err: any) {
      setSubmitError(err.message || "Failed to create assessment. Please check your connection.");
    } finally {
      setIsPending(false);
    }
  };

  const blockEnterSubmit = (e: React.KeyboardEvent<HTMLFormElement>) => {
    // Prevent Enter from skipping the Goals step / auto-submitting mid-wizard
    if (e.key === "Enter" && (e.target as HTMLElement).tagName !== "TEXTAREA") {
      e.preventDefault();
      if (step < 4) {
        void handleNext();
      }
    }
  };

  // Safe helper to convert numeric inputs
  const registerNumber = (fieldName: keyof WizardFormValues) => {
    return {
      ...register(fieldName, { valueAsNumber: true }),
      onChange: (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = parseFloat(e.target.value);
        setValue(fieldName, isNaN(val) ? 0 : val as any);
      }
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-slate-50 to-teal-50 flex flex-col justify-between py-12 px-4 sm:px-6 lg:px-8">
      {/* Header Banner */}
      <div className="sm:mx-auto sm:w-full sm:max-w-xl flex flex-col items-center">
        <Link href="/dashboard" className="flex items-center gap-2 text-emerald-700 hover:text-emerald-800 transition">
          <Leaf className="h-6 w-6" />
          <span className="font-bold text-lg">Sustainability Consultant</span>
        </Link>
        <h2 className="mt-4 text-center text-2xl font-extrabold text-slate-900 tracking-tight">
          New Sustainability Assessment
        </h2>
        <p className="mt-1.5 text-center text-sm text-slate-500 max-w-sm">
          Please complete the 4 steps to run the autonomous AI consulting workflow.
        </p>

        {/* Step Progress indicators */}
        <div className="w-full flex justify-between items-center mt-8 px-4">
          {[
            { stepNum: 1, label: "Business", icon: <Building className="h-4 w-4" /> },
            { stepNum: 2, label: "Resources", icon: <Zap className="h-4 w-4" /> },
            { stepNum: 3, label: "Financials", icon: <CircleDollarSign className="h-4 w-4" /> },
            { stepNum: 4, label: "Goals", icon: <Target className="h-4 w-4" /> },
          ].map((item) => (
            <React.Fragment key={item.stepNum}>
              <div className="flex flex-col items-center gap-1.5 relative">
                <div
                  className={`flex h-9 w-9 items-center justify-center rounded-xl border text-sm font-semibold transition shadow-sm ${
                    step >= item.stepNum
                      ? "bg-emerald-600 border-emerald-600 text-white shadow-emerald-600/10"
                      : "bg-white border-slate-200 text-slate-400"
                  }`}
                >
                  {item.icon}
                </div>
                <span className={`text-xs font-semibold ${step >= item.stepNum ? "text-emerald-800" : "text-slate-400"}`}>
                  {item.label}
                </span>
              </div>
              {item.stepNum < 4 && (
                <div
                  className={`flex-1 h-0.5 max-w-[50px] -mt-5 transition ${
                    step > item.stepNum ? "bg-emerald-600" : "bg-slate-200"
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Main Wizard Form Container */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-xl flex-1 flex flex-col justify-center">
        <div className="bg-white/80 backdrop-blur-md py-8 px-6 shadow-xl border border-slate-100 rounded-2xl sm:px-10">
          {submitError && (
            <div className="mb-6 rounded-lg bg-red-50 p-4 border border-red-100">
              <div className="text-sm font-medium text-red-800">{submitError}</div>
            </div>
          )}

          <form onSubmit={handleSubmit(onSubmit)} onKeyDown={blockEnterSubmit} className="space-y-6">
            {/* STEP 1: BUSINESS PROFILE */}
            {step === 1 && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-2">
                  Company Details
                </h3>
                
                <div>
                  <label className="block text-sm font-semibold text-slate-700">Business Name</label>
                  <input
                    type="text"
                    {...register("business_name")}
                    placeholder="e.g. ABC Manufacturing Corp"
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.business_name && (
                    <p className="mt-1 text-xs text-red-600">{errors.business_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Industry</label>
                  <select
                    {...register("industry")}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm rounded-lg shadow-sm"
                  >
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Technology">Technology</option>
                    <option value="Retail">Retail</option>
                    <option value="Hospitality">Hospitality</option>
                    <option value="Construction">Construction</option>
                    <option value="Agriculture">Agriculture</option>
                    <option value="Logistics">Logistics</option>
                    <option value="Warehousing">Warehousing</option>
                  </select>
                  {errors.industry && (
                    <p className="mt-1 text-xs text-red-600">{errors.industry.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Company Size</label>
                  <select
                    {...register("company_size")}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm rounded-lg shadow-sm"
                  >
                    <option value="Small">Small (1-50 employees)</option>
                    <option value="Medium">Medium (51-250 employees)</option>
                    <option value="Large">Large (251+ employees)</option>
                  </select>
                  {errors.company_size && (
                    <p className="mt-1 text-xs text-red-600">{errors.company_size.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Description</label>
                  <textarea
                    {...register("description")}
                    placeholder="Briefly describe what your business does..."
                    rows={3}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm resize-none"
                  />
                  {errors.description && (
                    <p className="mt-1 text-xs text-red-600">{errors.description.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* STEP 2: RESOURCE METRICS */}
            {step === 2 && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-2">
                  Annual Resource Consumption
                </h3>
                
                <div>
                  <label className="block text-sm font-semibold text-slate-700">Electricity Usage (kWh/year)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("electricity_usage")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.electricity_usage && (
                    <p className="mt-1 text-xs text-red-600">{errors.electricity_usage.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Diesel Usage (liters/year)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("diesel_usage")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.diesel_usage && (
                    <p className="mt-1 text-xs text-red-600">{errors.diesel_usage.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Petrol Usage (liters/year)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("petrol_usage")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.petrol_usage && (
                    <p className="mt-1 text-xs text-red-600">{errors.petrol_usage.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Water Usage (m³ or kL/year)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("water_usage")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.water_usage && (
                    <p className="mt-1 text-xs text-red-600">{errors.water_usage.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Waste Generated (metric tons/year)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("waste_generated")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.waste_generated && (
                    <p className="mt-1 text-xs text-red-600">{errors.waste_generated.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* STEP 3: FINANCIAL METRICS */}
            {step === 3 && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-2">
                  Company Financials
                </h3>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Annual Revenue (Rs. / INR)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("annual_revenue")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.annual_revenue && (
                    <p className="mt-1 text-xs text-red-600">{errors.annual_revenue.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Available Sustainability Budget (Rs. / INR)</label>
                  <input
                    type="number"
                    min="0"
                    {...registerNumber("sustainability_budget")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.sustainability_budget && (
                    <p className="mt-1 text-xs text-red-600">{errors.sustainability_budget.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* STEP 4: GOALS */}
            {step === 4 && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-slate-800 border-b border-slate-100 pb-2">
                  Sustainability Goals & Preferences
                </h3>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Target Carbon Reduction Goal (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    {...registerNumber("reduction_goal")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.reduction_goal && (
                    <p className="mt-1 text-xs text-red-600">{errors.reduction_goal.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Budget Priority</label>
                  <select
                    {...register("priority")}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm rounded-lg shadow-sm"
                  >
                    <option value="ROI">High ROI / Fast Payback (Recommended)</option>
                    <option value="Low Cost">Minimal Implementation Cost</option>
                    <option value="High Impact">Maximum Carbon Footprint Reduction</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Target Timeline (Months)</label>
                  <input
                    type="number"
                    min="1"
                    {...registerNumber("timeline_months")}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm"
                  />
                  {errors.timeline_months && (
                    <p className="mt-1 text-xs text-red-600">{errors.timeline_months.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700">Strategic Implementation Notes</label>
                  <textarea
                    {...register("notes")}
                    placeholder="Mention any specific constraints (e.g. rented building, no solar rooftop space)..."
                    rows={2}
                    className="mt-1 appearance-none block w-full px-3 py-2 border border-slate-300 rounded-lg shadow-sm focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm resize-none"
                  />
                  {errors.notes && (
                    <p className="mt-1 text-xs text-red-600">{errors.notes.message}</p>
                  )}
                </div>
              </div>
            )}

            {/* Navigation buttons */}
            <div className="flex justify-between items-center border-t border-slate-100 pt-6">
              {step > 1 ? (
                <button
                  type="button"
                  onClick={handlePrev}
                  disabled={isPending}
                  className="inline-flex items-center gap-1 text-sm font-semibold text-slate-600 hover:text-slate-900 transition"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Back
                </button>
              ) : (
                <Link
                  href="/dashboard"
                  className="text-sm font-semibold text-slate-500 hover:text-slate-700 transition"
                >
                  Cancel
                </Link>
              )}

              {step < 4 ? (
                <Button
                  type="button"
                  onClick={handleNext}
                  className="inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition"
                >
                  Continue
                  <ChevronRight className="ml-1.5 h-4 w-4" />
                </Button>
              ) : (
                <Button
                  type="button"
                  onClick={handleSubmit(onSubmit)}
                  disabled={isPending}
                  className="inline-flex items-center justify-center px-4 py-2 text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition"
                >
                  {isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    "Submit Assessment"
                  )}
                </Button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
