import axios from "axios";

const API_BASE = "/api/v1";

export interface Prediction {
  label: string;
  confidence: number;
}

export interface AnalyzeResponse {
  id: string;
  timestamp: string;
  original_filename: string;
  group: string;
  predictions: Prediction[];
  processing_time_ms: number;
  fallback_method: string | null;
}

export interface ResultItem {
  id: string;
  timestamp: string;
  original_filename: string;
  group: string;
  predictions: Prediction[];
  processing_time_ms: number;
  fallback_method: string | null;
}

export interface PaginatedResultsResponse {
  results: ResultItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export const api = {
  analyze: async (file: File): Promise<AnalyzeResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await axios.post<AnalyzeResponse>(
      `${API_BASE}/analyze`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  },

  getResults: async (page: number = 1, pageSize: number = 20): Promise<PaginatedResultsResponse> => {
    const response = await axios.get<PaginatedResultsResponse>(
      `${API_BASE}/results`,
      { params: { page, page_size: pageSize } }
    );
    return response.data;
  },
};
