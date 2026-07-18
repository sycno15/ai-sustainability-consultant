"use client";

import React, { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "../../store/authStore";

export default function Providers({ children }: { children: React.ReactNode }) {
  // Initialize query client
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
      },
    },
  }));

  const loadSession = useAuthStore((state) => state.loadSession);

  // Restore authenticated session from localStorage token on mount
  useEffect(() => {
    loadSession();
  }, [loadSession]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}
