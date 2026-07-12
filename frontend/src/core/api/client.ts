import { env } from "@/core/config/env";
import { storage } from "@/core/utils/storage";
import { AppError } from "./types";

const BASE_URL = env.NEXT_PUBLIC_API_URL;

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
  skipAuth?: boolean;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, skipAuth, ...rest } = options;

  const url = new URL(`${BASE_URL}${endpoint}`);
  if (params) {
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  }

  const token = storage.getToken();
  const authHeader = !skipAuth && token ? { "Authorization": `Bearer ${token}` } : {};

  const defaultHeaders = {
    "Content-Type": "application/json",
    ...authHeader,
  };

  try {
    const response = await fetch(url.toString(), {
      headers: { ...defaultHeaders, ...headers },
      ...rest,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status === 401 && !skipAuth) {
        // Centralized session expiration handling
        storage.removeToken();
        if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
          window.location.href = "/login?expired=true";
        }
      }

      throw new AppError(
        data.detail || data.message || "An unexpected error occurred",
        response.status,
        data.code,
        data.details
      );
    }

    return data as T;
  } catch (error) {
    if (error instanceof AppError) throw error;

    throw new AppError(
      error instanceof Error ? error.message : "Network request failed",
      500
    );
  }
}

export const apiClient = {
  get: <T>(url: string, options?: RequestOptions) =>
    request<T>(url, { ...options, method: "GET" }),

  post: <T>(url: string, body?: any, options?: RequestOptions) =>
    request<T>(url, { ...options, method: "POST", body: JSON.stringify(body) }),

  put: <T>(url: string, body?: any, options?: RequestOptions) =>
    request<T>(url, { ...options, method: "PUT", body: JSON.stringify(body) }),

  patch: <T>(url: string, body?: any, options?: RequestOptions) =>
    request<T>(url, { ...options, method: "PATCH", body: JSON.stringify(body) }),

  delete: <T>(url: string, options?: RequestOptions) =>
    request<T>(url, { ...options, method: "DELETE" }),
};
