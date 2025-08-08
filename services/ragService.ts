/**
 * RAG Service - Handles file uploads and RAG document management
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface RAGDocument {
  id: string;
  user_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  chunks_count: number;
  embeddings_created: boolean;
  created_at: string;
  updated_at: string;
  tags: string[];
  category?: string;
  processing_progress: number;
  processing_error?: string;
}

export type UploadResponse = RAGDocument;

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

class RAGService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
    };
  }

  /**
   * Upload a file to the RAG document store
   */
  async uploadDocument(
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<UploadResponse> {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('Authentication required for file upload');
    }

    return new Promise((resolve, reject) => {
      const formData = new FormData();
      formData.append('file', file);

      const xhr = new XMLHttpRequest();

      // Track upload progress
      if (onProgress) {
        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const progress: UploadProgress = {
              loaded: event.loaded,
              total: event.total,
              percentage: Math.round((event.loaded / event.total) * 100)
            };
            onProgress(progress);
          }
        };
      }

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch (error) {
            reject(new Error('Invalid JSON response'));
          }
        } else {
          try {
            const errorResponse = JSON.parse(xhr.responseText);
            reject(new Error(errorResponse.detail || `HTTP ${xhr.status}`));
          } catch {
            reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
          }
        }
      };

      xhr.onerror = () => {
        reject(new Error('Network error occurred'));
      };

      xhr.ontimeout = () => {
        reject(new Error('Request timeout'));
      };

      // Set timeout to 5 minutes for large files
      xhr.timeout = 5 * 60 * 1000;

      // Open request and send
      xhr.open('POST', `${API_BASE_URL}/api/v1/rag/documents/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);
    });
  }

  /**
   * Get all RAG documents for the current user
   */
  async getDocuments(): Promise<RAGDocument[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/documents`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch documents: ${response.statusText}`);
    }

    const data = await response.json();
    return data.documents || [];
  }

  /**
   * Get a specific RAG document by ID
   */
  async getDocument(documentId: string): Promise<RAGDocument> {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/documents/${documentId}`, {
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch document: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete a RAG document
   */
  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/v1/rag/documents/${documentId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to delete document: ${response.statusText}`);
    }
  }

  /**
   * Check document processing status
   */
  async getDocumentStatus(documentId: string): Promise<RAGDocument['status']> {
    const document = await this.getDocument(documentId);
    return document.status;
  }

  /**
   * Get file type icon based on content type
   */
  getFileIcon(contentType: string): string {
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('word') || contentType.includes('document')) return '📝';
    if (contentType.includes('text')) return '📃';
    if (contentType.includes('image')) return '🖼️';
    return '📁';
  }

  /**
   * Format file size for display
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Validate file before upload
   */
  validateFile(file: File): { valid: boolean; error?: string } {
    // Check file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (file.size > maxSize) {
      return { valid: false, error: 'File size must be less than 50MB' };
    }

    // Check file type
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'File type not supported. Please upload PDF, DOC, DOCX, or TXT files.' };
    }

    return { valid: true };
  }
}

export const ragService = new RAGService();