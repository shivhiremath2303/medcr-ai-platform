import { apiClient } from "@/core/api/client";
import { User, LoginResponse } from "../types";
import { LoginFormValues } from "../schemas/login-schema";

export const authService = {
  login: async (credentials: LoginFormValues): Promise<LoginResponse> => {
    // Backend expects form-data for OAuth2 compatibility or simple JSON
    // Checking backend/app/api/routes/auth.py, it uses OAuth2PasswordRequestForm
    // which expects form-data (username and password)

    const formData = new URLSearchParams();
    formData.append("username", credentials.username);
    formData.append("password", credentials.password);

    return apiClient.post<LoginResponse>("/api/v1/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      skipAuth: true,
      // Overriding the default JSON body since backend uses OAuth2 form
      body: formData.toString(),
    });
  },

  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>("/api/v1/auth/me");
  },

  logout: async (): Promise<void> => {
    try {
      await apiClient.post("/api/v1/auth/logout");
    } catch (error) {
      console.error("Logout request failed:", error);
    }
  },
};
