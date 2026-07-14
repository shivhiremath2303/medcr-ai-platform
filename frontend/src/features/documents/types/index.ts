export interface DocumentPage {
  page_number: number;
  text: string;
}

export interface Document {
  document_id: string;
  filename: string;
  page_count: number;
  owner_id?: string;
  pages?: DocumentPage[];
  created_at?: string;
  status?: "pending" | "running" | "completed" | "failed";
}

export interface UploadResponse {
  message: string;
  filename: string;
  task_id: string;
}

export interface DocumentListResponse {
  items: Document[];
  total: number;
  limit: number;
  offset: number;
}

export interface SearchFilters {
  query?: string;
  status?: string;
  dateRange?: {
    from?: Date;
    to?: Date;
  };
}
