import { apiClient } from "@/core/api/client";
import { ChatRequest, ChatResponse } from "../types";

export const chatService = {
  /**
   * Sends a question to the RAG pipeline.
   */
  askQuestion: async (request: ChatRequest): Promise<ChatResponse> => {
    return apiClient.post<ChatResponse>("/api/v1/rag/ask", request);
  },

  /**
   * Retrieves conversation history.
   * NOTE: Backend currently does not expose an endpoint for this.
   */
  getHistory: async (): Promise<any[]> => {
    // Placeholder for when backend adds /chat/history
    throw new Error("Conversation history API not yet available");
  },
};
