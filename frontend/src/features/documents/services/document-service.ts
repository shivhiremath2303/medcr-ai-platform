import { apiClient } from "@/core/api/client";
import { Document, UploadResponse, DocumentListResponse } from "../types";

export const documentService = {
  /**
   * Uploads a document to the backend.
   * Note: This uses multipart/form-data.
   */
  upload: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    // We use a custom fetch here because apiClient default is JSON
    // but our apiClient wrapper can handle custom bodies if we don't stringify
    // However, the current apiClient stringifies body by default in POST.
    // Let's use a raw fetch or adjust apiClient to handle FormData.

    // I will use a direct fetch or better, I should have updated apiClient
    // to handle FormData in Step 2, but for now I'll do a specialized request.

    // Re-using headers and base URL logic from apiClient but with FormData
    const token = localStorage.getItem("auth_token");
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

    const response = await fetch(`${baseUrl}/api/v1/documents/upload`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Upload failed");
    }

    return response.json();
  },

  /**
   * Fetches a list of all documents.
   * NOTE: Based on Audit, this endpoint is currently NOT EXPOSED by the backend API.
   * We implement the service call anyway for future-readiness.
   */
  getDocuments: async (): Promise<Document[]> => {
    // This will currently fail with 404 until backend adds the route
    return apiClient.get<Document[]>("/api/v1/documents");
  },

  /**
   * Fetches a single document by ID.
   * NOTE: Based on Audit, this endpoint is currently NOT EXPOSED by the backend API.
   */
  getDocumentById: async (id: string): Promise<Document> => {
    return apiClient.get<Document>(`/api/v1/documents/${id}`);
  },

  /**
   * Deletes a document by ID.
   * NOTE: Based on Audit, this endpoint is currently NOT EXPOSED by the backend API.
   */
  deleteDocument: async (id: string): Promise<void> => {
    return apiClient.delete(`/api/v1/documents/${id}`);
  },
};
