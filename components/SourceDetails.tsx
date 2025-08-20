'use client';

import React, { useEffect, useState } from 'react';
import { X, ChevronDown, ChevronUp, BookOpen, Calendar, FileText, User, ChevronLeft, ArrowLeft, Loader2 } from 'lucide-react';
import { ragService, RAGDocument } from '../services/ragService';

interface Source {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'txt' | 'url';
  uploadDate: Date;
  size?: number;
  ragDocumentId?: string;
  status?: 'uploading' | 'pending' | 'processing' | 'completed' | 'failed';
  aiSummary?: string;
  aiDetailedDescription?: string;
  aiTopics?: string[];
  aiMetadataGeneratedAt?: string;
}

interface SourceDetailsProps {
  source: Source;
  onClose: () => void;
  onCollapse?: () => void;
}

const SourceDetails: React.FC<SourceDetailsProps> = ({ source, onClose, onCollapse }) => {
  const [isGuideExpanded, setIsGuideExpanded] = React.useState(true);
  const [documentData, setDocumentData] = useState<RAGDocument | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch document data when component mounts or ragDocumentId changes
  useEffect(() => {
    const fetchDocumentData = async () => {
      if (!source.ragDocumentId) {
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const document = await ragService.getDocument(source.ragDocumentId);
        setDocumentData(document);
      } catch (err) {
        console.error('Failed to fetch document data:', err);
        setError(err instanceof Error ? err.message : 'Failed to load document data');
      } finally {
        setLoading(false);
      }
    };

    fetchDocumentData();
  }, [source.ragDocumentId]);

  // Prepare source data using either fetched data or source data
  const sourceData = {
    summary: documentData?.ai_summary || source.aiSummary || `AI summary for "${source.name}" is being generated...`,
    keyTopics: documentData?.ai_topics || source.aiTopics || ['Analysis in progress...'],
    metadata: {
      title: source.name.replace(/\.(pdf|docx?|txt)$/i, ''),
      subtitle: documentData?.file_type?.toUpperCase() || source.type.toUpperCase(),
      date: documentData?.created_at ? new Date(documentData.created_at).toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }) : source.uploadDate.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      }),
      context: documentData?.ai_detailed_description || source.aiDetailedDescription || 'Detailed analysis will appear here once AI processing is complete.'
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-800/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Sources</h2>
          <button 
            onClick={onClose}
            className="p-2 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            title="Back to Sources"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Source Info */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-red-100 dark:bg-red-900/20 rounded flex items-center justify-center flex-shrink-0">
            <FileText className="w-4 h-4 text-red-600 dark:text-red-400" />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 truncate">{source.name}</h3>
            <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-slate-400 mt-1">
              <span>{source.type.toUpperCase()}</span>
              {source.size && (
                <>
                  <span>•</span>
                  <span>{formatFileSize(source.size)}</span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Source Guide */}
        <div className="p-4">
          <div className="bg-gray-100 dark:bg-slate-700/50 rounded-lg">
            <button
              onClick={() => setIsGuideExpanded(!isGuideExpanded)}
              className="w-full flex items-center justify-between p-3 text-left"
            >
              <div className="flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <span className="font-medium text-gray-900 dark:text-gray-100">Source guide</span>
              </div>
              {isGuideExpanded ? (
                <ChevronUp className="w-4 h-4 text-gray-600 dark:text-slate-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-600 dark:text-slate-400" />
              )}
            </button>
            
            {isGuideExpanded && (
              <div className="px-3 pb-3">
                {loading && (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-blue-600 dark:text-blue-400" />
                    <span className="ml-2 text-sm text-gray-600 dark:text-slate-400">Loading AI analysis...</span>
                  </div>
                )}
                
                {error && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 mb-4">
                    <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
                  </div>
                )}
                
                {!loading && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {/* Summary */}
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Summary</h4>
                      <p className="text-sm text-gray-700 dark:text-slate-300 leading-relaxed">
                        {sourceData.summary}
                      </p>
                      {documentData?.ai_metadata_generated_at && (
                        <p className="text-xs text-gray-500 dark:text-slate-500 mt-2">
                          Generated {new Date(documentData.ai_metadata_generated_at).toLocaleString()}
                        </p>
                      )}
                    </div>

                    {/* Key Topics */}
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Key Topics</h4>
                      <div className="space-y-2">
                        {sourceData.keyTopics.map((topic, index) => (
                          <div
                            key={index}
                            className="block w-full text-left px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg text-sm"
                          >
                            {topic}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Document Details */}
        <div className="p-4 border-t border-gray-200 dark:border-slate-700">
          <div className="space-y-4">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">
                {sourceData.metadata.title}
              </h3>
              <p className="text-lg text-gray-700 dark:text-slate-300 mb-2">
                {sourceData.metadata.subtitle}
              </p>
              <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-slate-400">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4" />
                  <span>{sourceData.metadata.date}</span>
                </div>
                {documentData && (
                  <div className="flex items-center space-x-1">
                    <FileText className="w-4 h-4" />
                    <span>{documentData.chunks_count} chunks</span>
                  </div>
                )}
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Analysis</h4>
              <p className="text-sm text-gray-700 dark:text-slate-300 leading-relaxed">
                {sourceData.metadata.context}
              </p>
            </div>

            {/* Status indicator */}
            {source.status && (
              <div className="flex items-center space-x-2 text-sm">
                <span className="text-gray-600 dark:text-slate-400">Status:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  source.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' :
                  source.status === 'processing' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400' :
                  source.status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400' :
                  'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                }`}>
                  {source.status === 'completed' ? 'AI analysis complete' : 
                   source.status === 'processing' ? 'AI processing...' :
                   source.status === 'failed' ? 'Processing failed' :
                   'Pending processing'}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SourceDetails;