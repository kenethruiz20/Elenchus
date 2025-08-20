'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Plus, Search, FileText, Upload, X, ChevronLeft, ChevronRight, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { useStore } from '../store/useStore';
import SourceDetails from './SourceDetails';
import DiscoverModal from './DiscoverModal';
import { ragService, UploadProgress } from '../services/ragService';

interface SourcesPanelProps {
  panelState: 'normal' | 'expanded' | 'collapsed';
  onPanelStateChange: (state: 'normal' | 'expanded' | 'collapsed') => void;
  onEnsureSession: (actionType: 'source' | 'message' | 'note', title?: string) => Promise<string> | string;
}

const SourcesPanel: React.FC<SourcesPanelProps> = ({ panelState, onPanelStateChange, onEnsureSession }) => {
  const { sources, addSource, removeSource, updateSource, isAuthenticated } = useStore();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [isDiscoverModalOpen, setIsDiscoverModalOpen] = useState(false);

  // Periodically refresh processing sources to get AI metadata updates
  useEffect(() => {
    const interval = setInterval(async () => {
      const processingSources = sources.filter(source => 
        source.ragDocumentId && 
        (source.status === 'processing' || source.status === 'pending') &&
        isAuthenticated
      );

      for (const source of processingSources) {
        try {
          const document = await ragService.getDocument(source.ragDocumentId!);
          if (document.status === 'completed' && document.ai_summary) {
            updateSource(source.id, {
              status: 'completed',
              aiSummary: document.ai_summary,
              aiDetailedDescription: document.ai_detailed_description,
              aiTopics: document.ai_topics,
              aiMetadataGeneratedAt: document.ai_metadata_generated_at
            });
          } else if (document.status === 'failed') {
            updateSource(source.id, {
              status: 'failed',
              processingError: document.processing_error || 'Processing failed'
            });
          }
        } catch (error) {
          console.error('Failed to refresh source status:', error);
        }
      }
    }, 10000); // Check every 10 seconds

    return () => clearInterval(interval);
  }, [sources, updateSource, isAuthenticated]);

  // Handle panel state changes when source is selected/deselected
  useEffect(() => {
    if (selectedSource && panelState === 'normal') {
      onPanelStateChange('expanded');
    } else if (!selectedSource && panelState === 'expanded') {
      onPanelStateChange('normal');
    }
  }, [selectedSource, panelState, onPanelStateChange]);

  const handleSourceSelect = (sourceId: string) => {
    setSelectedSource(sourceId);
  };

  const handleSourceClose = () => {
    setSelectedSource(null);
  };

  const togglePanel = () => {
    if (panelState === 'collapsed') {
      onPanelStateChange('normal');
    } else {
      onPanelStateChange('collapsed');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    // Check if user is authenticated
    if (!isAuthenticated) {
      alert('Please log in to upload files');
      return;
    }

    // Ensure session exists before adding sources
    onEnsureSession('source', 'Document Analysis');
    
    // Process each file
    for (const file of Array.from(files)) {
      // Validate file
      const validation = ragService.validateFile(file);
      if (!validation.valid) {
        alert(`Error with ${file.name}: ${validation.error}`);
        continue;
      }

      const fileType = file.type;
      let sourceType: 'pdf' | 'doc' | 'txt' | 'url' = 'txt';
      
      if (fileType.includes('pdf')) sourceType = 'pdf';
      else if (fileType.includes('document') || fileType.includes('word')) sourceType = 'doc';

      // Add source to store immediately with uploading status
      const tempSource = {
        name: file.name,
        type: sourceType,
        uploadDate: new Date(),
        size: file.size,
        status: 'uploading' as const,
        uploadProgress: 0
      };

      // Add source and get the returned ID
      const sourceId = addSource(tempSource);
      
      if (!sourceId) {
        console.error('Failed to get source ID from addSource');
        continue;
      }

      try {
        // Upload file to RAG backend
        const response = await ragService.uploadDocument(
          file,
          (progress: UploadProgress) => {
            // Update progress in store
            updateSource(sourceId, { 
              uploadProgress: progress.percentage 
            });
          }
        );

        // Update source with successful upload and AI metadata
        updateSource(sourceId, {
          status: response.status as 'uploading' | 'pending' | 'processing' | 'completed' | 'failed',
          ragDocumentId: response.id,
          uploadProgress: 100,
          aiSummary: response.ai_summary,
          aiDetailedDescription: response.ai_detailed_description,
          aiTopics: response.ai_topics,
          aiMetadataGeneratedAt: response.ai_metadata_generated_at
        });

      } catch (error) {
        console.error('File upload failed:', error);
        
        // Update source with error status
        updateSource(sourceId, {
          status: 'failed',
          processingError: error instanceof Error ? error.message : 'Upload failed'
        });
        
        alert(`Failed to upload ${file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    // Reset the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const selectedSourceData = selectedSource ? sources.find(s => s.id === selectedSource) : null;

  // Handle collapsed state
  if (panelState === 'collapsed') {
    return (
      <div className="h-full bg-gray-50 dark:bg-slate-800/50 border-r border-gray-200 dark:border-slate-700">
        <div className="p-2 border-b border-gray-200 dark:border-slate-700">
          <button
            onClick={togglePanel}
            className="w-full p-2 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            title="Expand Sources"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </div>
    );
  }

  if (selectedSourceData) {
    return (
      <SourceDetails 
        source={selectedSourceData} 
        onClose={handleSourceClose}
        onCollapse={togglePanel}
      />
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-800/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Sources</h2>
          <button
            onClick={togglePanel}
            className="p-1 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            title="Collapse Sources"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
        
        {/* Action Buttons */}
        <div className="space-y-2">
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add</span>
          </button>
          
          <button 
            onClick={() => setIsDiscoverModalOpen(true)}
            className="w-full flex items-center justify-center space-x-2 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-lg transition-colors"
          >
            <Search className="w-4 h-4" />
            <span>Discover</span>
          </button>
        </div>
        
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>

      {/* Sources List */}
      <div className="flex-1 overflow-y-auto">
        {sources.length === 0 ? (
          <div className="p-4 text-center">
            <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
              <FileText className="w-8 h-8 text-gray-400 dark:text-slate-400" />
            </div>
            <p className="text-sm text-gray-600 dark:text-slate-400 mb-2">Saved sources will appear here</p>
            <p className="text-xs text-gray-500 dark:text-slate-500">Click Add source above to add PDFs, websites, text, videos, or audio files.</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {sources.map((source) => (
              <div 
                key={source.id} 
                className="group bg-gray-100 dark:bg-slate-700/50 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-lg p-3 transition-colors cursor-pointer"
                onClick={() => handleSourceSelect(source.id)}
              >
                <div className="flex items-start justify-between min-w-0">
                  <div className="flex items-start space-x-3 min-w-0 flex-1">
                    <div className="w-8 h-8 bg-gray-200 dark:bg-slate-600 rounded flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-gray-600 dark:text-slate-300" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate" title={source.name}>
                        {source.name}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-slate-400 mt-1 truncate">
                        {source.type.toUpperCase()}
                        {source.size && ` • ${formatFileSize(source.size)}`}
                        {source.status && (
                          <span className="ml-2">
                            {source.status === 'uploading' && (
                              <span className="inline-flex items-center text-blue-600 dark:text-blue-400">
                                <Clock className="w-3 h-3 mr-1" />
                                {source.uploadProgress !== undefined && `${source.uploadProgress}%`}
                              </span>
                            )}
                            {source.status === 'pending' && (
                              <span className="inline-flex items-center text-blue-600 dark:text-blue-400">
                                <Clock className="w-3 h-3 mr-1" />
                                Uploaded
                              </span>
                            )}
                            {source.status === 'processing' && (
                              <span className="inline-flex items-center text-yellow-600 dark:text-yellow-400">
                                <Clock className="w-3 h-3 mr-1" />
                                Processing...
                              </span>
                            )}
                            {source.status === 'completed' && (
                              <span className="inline-flex items-center text-green-600 dark:text-green-400">
                                <CheckCircle className="w-3 h-3 mr-1" />
                                Ready
                              </span>
                            )}
                            {source.status === 'failed' && (
                              <span className="inline-flex items-center text-red-600 dark:text-red-400">
                                <AlertCircle className="w-3 h-3 mr-1" />
                                Failed
                              </span>
                            )}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeSource(source.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-slate-700 text-center">
        <p className="text-xs text-gray-500 dark:text-slate-500">{sources.length} sources</p>
      </div>

      {/* Discover Modal */}
      <DiscoverModal
        isOpen={isDiscoverModalOpen}
        onClose={() => setIsDiscoverModalOpen(false)}
        onAddSource={addSource}
      />
    </div>
  );
};

export default SourcesPanel; 