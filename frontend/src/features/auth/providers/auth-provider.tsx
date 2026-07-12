"use client";

import { createContext, useEffect, useState, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";
import { User, LoginFormValues, AuthState } from "../types";
import { authService } from "../services/auth-service";
import { storage } from "@/core/utils/storage";

interface AuthContextType extends AuthState {
  login: (credentials: LoginFormValues) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    error: null,
  });

  const router = useRouter();
  const pathname = usePathname();

  const restoreSession = useCallback(async () => {
    const token = storage.getToken();
    if (!token) {
      setState(prev => ({ ...prev, isLoading: false }));
      return;
    }

    try {
      const user = await authService.getCurrentUser();
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });
    } catch (error) {
      storage.removeToken();
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : "Session expired",
      });
    }
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  // Handle protected route redirection
  useEffect(() => {
    if (!state.isLoading) {
      const isPublicRoute = pathname === "/login";

      if (!state.isAuthenticated && !isPublicRoute) {
        router.push("/login");
      }

      if (state.isAuthenticated && isPublicRoute) {
        router.push("/dashboard");
      }
    }
  }, [state.isAuthenticated, state.isLoading, pathname, router]);

  const login = async (credentials: LoginFormValues) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const response = await authService.login(credentials);
      storage.setToken(response.access_token);

      const user = await authService.getCurrentUser();
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
        error: null,
      });

      router.push("/dashboard");
    } catch (error) {
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: error instanceof Error ? error.message : "Login failed",
      });
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    storage.removeToken();
    setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ ...state, login, logout }}>
      {state.isLoading ? (
        <div className="flex h-screen w-full items-center justify-center bg-background">
          <div className="flex flex-col items-center gap-4">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <p className="text-sm font-medium text-muted-foreground">Initializing secure session...</p>
          </div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
}
