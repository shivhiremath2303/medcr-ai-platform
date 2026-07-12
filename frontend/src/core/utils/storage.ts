/**
 * Safe wrapper for localStorage to handle SSR and potential errors.
 */
export const storage = {
  getToken: () => {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("auth_token");
  },
  setToken: (token: string) => {
    localStorage.setItem("auth_token", token);
  },
  removeToken: () => {
    localStorage.removeItem("auth_token");
  },
};
