export interface PdfViewerState {
  currentPage: number;
  totalPages: number;
  zoom: number;
  scale: number;
  isSidebarOpen: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface PdfHighlight {
  id: string;
  pageNumber: number;
  position: {
    top: number;
    left: number;
    width: number;
    height: number;
  };
  content: string;
}

export interface DocumentBlob {
  id: string;
  blob: Blob;
  filename: string;
  url: string;
}
