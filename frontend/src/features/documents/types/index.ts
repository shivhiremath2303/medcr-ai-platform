export interface DocumentPage {
  page_number: number;
  text: string;
}

export interface Document {
  document_id: string;
  filename: string;
  page_count: number;
  pages?: DocumentPage[];
  created_at?: string;
  status?: "processing" | "completed" | "failed";
}

export interface UploadResponse {
  message: string;
  filename: string;
  chunks: number;
  document_id?: string;
}

export interface DocumentListResponse {
  documents: Document[];
  total: number;
}

export interface SearchFilters {
  query?: string;
  status?: string;
  dateRange?: {
    from?: Date;
    to?: Date;
  };
}
