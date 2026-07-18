"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/button";
import { Leaf, Eye, EyeOff, Loader2, Mail, CheckCircle } from "lucide-react";

// Form validation schema using Zod
const registerSchema = z.object({
  full_name: z.string().min(1, "Full name is required").max(100, "Name is too long"),
  email: z.string().min(1, "Email is required").email("Invalid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser, error: authError, clearError } = useAuthStore();
  const [isPending, setIsPending] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [registeredEmail, setRegisteredEmail] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
    },
  });

  const onSubmit = async (values: RegisterFormValues) => {
    setIsPending(true);
    setSubmitError(null);
    clearError();
    try {
      await registerUser({
        full_name: values.full_name,
        email: values.email,
        password: values.password,
      });
      setRegisteredEmail(values.email);
    } catch (err: any) {
      setSubmitError(err.message || "Registration failed. Please try again.");
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
          Create Your Account
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Get started with your SME sustainability consultant
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/80 backdrop-blur-md py-8 px-4 shadow-xl border border-slate-100 rounded-2xl sm:px-10">
          
          {registeredEmail ? (
            /* Success Verification Card */
            <div className="text-center py-4">
              <div className="flex justify-center mb-4 text-emerald-600">
                <CheckCircle className="h-16 w-16" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Check Your Email</h3>
              <p className="text-sm text-slate-600 mb-6">
                We sent a verification link to <strong className="text-slate-800">{registeredEmail}</strong>. 
                Please verify your email address to activate your account.
              </p>
              <div className="space-y-4">
                <Button
                  onClick={() => router.push("/login")}
                  className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 rounded-lg shadow-sm"
                >
                  Return to Sign In
                </Button>
              </div>
            </div>
          ) : (
            /* Registration Form */
            <>
              {(submitError || authError) && (
                <div className="mb-6 rounded-lg bg-red-50 p-4 border border-red-100">
                  <div className="text-sm font-medium text-red-800">
                    {submitError || authError}
                  </div>
                </div>
              )}

              <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
                {/* Full Name Field */}
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-slate-700">
                    Full Name
                  </label>
                  <div className="mt-1">
                    <input
                      id="full_name"
                      type="text"
                      disabled={isPending}
                      {...register("full_name")}
                      className={`appearance-none block w-full px-3 py-2 border rounded-lg shadow-sm placeholder-slate-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition duration-150 ${
                        errors.full_name ? "border-red-300 text-red-900" : "border-slate-300 text-slate-900"
                      }`}
                      placeholder="John Doe"
                    />
                    {errors.full_name && (
                      <p className="mt-1 text-xs text-red-600">{errors.full_name.message}</p>
                    )}
                  </div>
                </div>

                {/* Email Field */}
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

                {/* Password Field */}
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-slate-700">
                    Password
                  </label>
                  <div className="mt-1 relative">
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      disabled={isPending}
                      {...register("password")}
                      className={`appearance-none block w-full pl-3 pr-10 py-2 border rounded-lg shadow-sm placeholder-slate-400 focus:outline-none focus:ring-emerald-500 focus:border-emerald-500 sm:text-sm transition duration-150 ${
                        errors.password ? "border-red-300 text-red-900" : "border-slate-300 text-slate-900"
                      }`}
                      placeholder="Min. 8 characters"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                    {errors.password && (
                      <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
                    )}
                  </div>
                </div>

                {/* Submit Button */}
                <div>
                  <Button
                    type="submit"
                    disabled={isPending}
                    className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition duration-150"
                  >
                    {isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating account...
                      </>
                    ) : (
                      "Create Account"
                    )}
                  </Button>
                </div>
              </form>

              {/* Login Redirect */}
              <div className="mt-6 text-center">
                <p className="text-sm text-slate-600">
                  Already have an account?{" "}
                  <Link
                    href="/login"
                    className="font-semibold text-emerald-600 hover:text-emerald-700 transition"
                  >
                    Sign in
                  </Link>
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
