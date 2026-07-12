import { useMutation } from "@tanstack/react-query";
import { chatService } from "../services/chat-service";
import { ChatRequest, ChatResponse } from "../types";

/**
 * Hook to send a message to the AI and get a RAG response.
 */
export function useSendMessage() {
  return useMutation({
    mutationFn: (request: ChatRequest) => chatService.askQuestion(request),
  });
}

/**
 * Hook to fetch conversation history.
 * NOTE: Currently disabled as backend API is missing.
 */
export function useChatHistory() {
  // This would normally be a useQuery
  return {
    data: [],
    isLoading: false,
    error: null,
    isUnavailable: true
  };
}
