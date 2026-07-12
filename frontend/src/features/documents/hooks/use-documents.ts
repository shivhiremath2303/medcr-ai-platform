import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentService } from "../services/document-service";
import { Document } from "../types";

export const documentKeys = {
  all: ["documents"] as const,
  lists: () => [...documentKeys.all, "list"] as const,
  details: () => [...documentKeys.all, "detail"] as const,
  detail: (id: string) => [...documentKeys.details(), id] as const,
};

/**
 * Hook to fetch all documents.
 */
export function useDocuments() {
  return useQuery({
    queryKey: documentKeys.lists(),
    queryFn: () => documentService.getDocuments(),
    // Since backend might return 404 for now, we handle it gracefully
    retry: false,
  });
}

/**
 * Hook to fetch a single document.
 */
export function useDocument(id: string) {
  return useQuery({
    queryKey: documentKeys.detail(id),
    queryFn: () => documentService.getDocumentById(id),
    enabled: !!id,
    retry: false,
  });
}

/**
 * Hook to upload a document.
 */
export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => documentService.upload(file),
    onSuccess: () => {
      // Invalidate the document list to trigger a refetch
      queryClient.invalidateQueries({ queryKey: documentKeys.lists() });
    },
  });
}

/**
 * Hook to delete a document.
 */
export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => documentService.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: documentKeys.all });
    },
  });
}
