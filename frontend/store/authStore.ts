import { create } from "zustand";
import { authService, LoginPayload, RegisterPayload, UserProfile } from "../services/authService";

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  loadSession: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  clearError: () => set({ error: null }),

  login: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      const tokenData = await authService.login(payload);
      
      // Store token locally for session persistence
      if (typeof window !== "undefined") {
        localStorage.setItem("token", tokenData.access_token);
        // We can also set a cookie for Next.js Middleware route guards
        document.cookie = `session_token=${tokenData.access_token}; path=/; max-age=${tokenData.expires_in}; SameSite=Lax`;
      }
      
      const profile = await authService.getProfile(tokenData.access_token);
      
      set({
        token: tokenData.access_token,
        user: profile,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || "Login failed",
      });
      throw err;
    }
  },

  register: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      await authService.register(payload);
      set({ isLoading: false });
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || "Registration failed",
      });
      throw err;
    }
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      document.cookie = "session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    }
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  loadSession: async () => {
    // Check if token exists in localStorage (client-side only)
    if (typeof window === "undefined") return;
    
    const savedToken = localStorage.getItem("token");
    if (!savedToken) return;

    set({ isLoading: true, error: null });
    try {
      const profile = await authService.getProfile(savedToken);
      set({
        token: savedToken,
        user: profile,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (err) {
      // Token is likely expired or invalid, clear session
      localStorage.removeItem("token");
      document.cookie = "session_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      set({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
