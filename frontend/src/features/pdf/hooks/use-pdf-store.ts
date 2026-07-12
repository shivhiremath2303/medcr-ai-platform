"use client";

import { create } from "zustand";
import { DocumentBlob } from "../types";

interface PdfStore {
  // Map of documentId to local blob URL for session persistence
  localBlobs: Record<string, DocumentBlob>;
  addLocalBlob: (id: string, file: File) => void;
  getBlob: (id: string) => DocumentBlob | null;
}

/**
 * Store to bridge the gap between upload and viewing.
 * Since backend doesn't support PDF retrieval yet, we store the blob
 * locally during the session so the user can verify their upload immediately.
 */
export const usePdfStore = create<PdfStore>((set, get) => ({
  localBlobs: {},
  addLocalBlob: (id, file) => {
    const url = URL.createObjectURL(file);
    set((state) => ({
      localBlobs: {
        ...state.localBlobs,
        [id]: { id, blob: file, filename: file.name, url }
      }
    }));
  },
  getBlob: (id) => get().localBlobs[id] || null,
}));
