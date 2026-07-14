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
   * Fetches a list of all documents with pagination support.
   */
  getDocuments: async (limit: number = 20, offset: number = 0): Promise<Document[]> => {
    const response = await apiClient.get<DocumentListResponse>(
      `/api/v1/documents?limit=${limit}&offset=${offset}`
    );
    // Flatten items for the current frontend hook compatibility
    return response.items;
  },

  /**
   * Fetches a single document by ID.
   */
  getDocumentById: async (id: string): Promise<Document> => {
    return apiClient.get<Document>(`/api/v1/documents/${id}`);
  },

  /**
   * Deletes a document by ID.
   */
  deleteDocument: async (id: string): Promise<void> => {
    return apiClient.delete(`/api/v1/documents/${id}`);
  },

  /**
   * Polls for the status of a background task.
   */
  getTaskStatus: async (taskId: string) => {
    return apiClient.get(`/api/v1/tasks/${taskId}`);
  },
};
