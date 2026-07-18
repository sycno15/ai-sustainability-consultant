"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Leaf, Loader2, ArrowLeft, Send, CheckCircle } from "lucide-react";
import { authService } from "@/services/authService";

const resetSchema = z.object({
  email: z.string().min(1, "Email is required").email("Invalid email address"),
});

type ResetFormValues = z.infer<typeof resetSchema>;

export default function ForgotPasswordPage() {
  const [isPending, setIsPending] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [successEmail, setSuccessEmail] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ResetFormValues>({
    resolver: zodResolver(resetSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (values: ResetFormValues) => {
    setIsPending(true);
    setSubmitError(null);
    try {
      await authService.resetPassword(values.email);
      setSuccessEmail(values.email);
    } catch (err: any) {
      setSubmitError(err.message || "Failed to request password reset. Please try again.");
    } finally {
      setIsPending(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col justify-center py-12 sm:px-6 lg:px-8 bg-gradient-to-br from-emerald-50 via-slate-50 to-teal-50">
      <div className="sm:mx-auto sm:w-full sm:max-w-md flex flex-col items-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-600 shadow-lg shadow-emerald-600/20 text-white animate-bounce-subtle">
          <Leaf className="h-6 w-6" />
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold tracking-tight text-slate-900 font-sans">
          Reset Password
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          We will send you a link to reset your account credentials
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/80 backdrop-blur-md py-8 px-4 shadow-xl border border-slate-100 rounded-2xl sm:px-10">
          
          {successEmail ? (
            /* Success State */
            <div className="text-center py-4">
              <div className="flex justify-center mb-4 text-emerald-600 animate-pulse">
                <CheckCircle className="h-16 w-16" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Email Sent</h3>
              <p className="text-sm text-slate-600 mb-6">
                A password reset link was sent to <strong className="text-slate-800">{successEmail}</strong>. 
                Please check your inbox and spam folder.
              </p>
              <Link
                href="/login"
                className="w-full flex items-center justify-center py-2.5 px-4 border border-slate-200 rounded-lg text-sm font-semibold text-slate-700 hover:bg-slate-50 transition duration-150"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Sign In
              </Link>
            </div>
          ) : (
            /* Form State */
            <>
              {submitError && (
                <div className="mb-6 rounded-lg bg-red-50 p-4 border border-red-100">
                  <div className="text-sm font-medium text-red-800">
                    {submitError}
                  </div>
                </div>
              )}

              <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                {/* Email Input */}
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-slate-700">
                    Email Address
                  </label>
                  <div className="mt-1">
                    <input
                      id="email"
                      type="email"
                      disabled={isPending}
                      {...register("email")}
                      className={`appearance-none block w-full px-3 py-2 border rounded-lg shadow-sm placeholder-slate-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition duration-150 ${
                        errors.email ? "border-red-300 text-red-900" : "border-slate-300 text-slate-900"
                      }`}
                      placeholder="name@company.com"
                    />
                    {errors.email && (
                      <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
                    )}
                  </div>
                </div>

                {/* Submit Button */}
                <div>
                  <Button
                    type="submit"
                    disabled={isPending}
                    className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition duration-150"
                  >
                    {isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Sending link...
                      </>
                    ) : (
                      <>
                        <Send className="mr-2 h-4 w-4" />
                        Send Reset Link
                      </>
                    )}
                  </Button>
                </div>
              </form>

              {/* Back to Sign In Link */}
              <div className="mt-6 text-center">
                <Link
                  href="/login"
                  className="inline-flex items-center text-sm font-semibold text-slate-600 hover:text-slate-800 transition"
                >
                  <ArrowLeft className="mr-1 h-4 w-4" />
                  Back to Sign In
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
