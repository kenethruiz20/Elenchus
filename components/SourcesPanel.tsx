'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Plus, Search, FileText, Upload, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { useStore } from '../store/useStore';
import SourceDetails from './SourceDetails';
import DiscoverModal from './DiscoverModal';

interface SourcesPanelProps {
  panelState: 'normal' | 'expanded' | 'collapsed';
  onPanelStateChange: (state: 'normal' | 'expanded' | 'collapsed') => void;
  onEnsureSession: (actionType: 'source' | 'message' | 'note', title?: string) => Promise<string> | string;
}

const SourcesPanel: React.FC<SourcesPanelProps> = ({ panelState, onPanelStateChange, onEnsureSession }) => {
  const { sources, addSource, removeSource } = useStore();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [isDiscoverModalOpen, setIsDiscoverModalOpen] = useState(false);

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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      // Ensure session exists before adding sources
      onEnsureSession('source', 'Document Analysis');
      
      Array.from(files).forEach(file => {
        const fileType = file.type;
        let sourceType: 'pdf' | 'doc' | 'txt' | 'url' = 'txt';
        
        if (fileType.includes('pdf')) sourceType = 'pdf';
        else if (fileType.includes('document') || fileType.includes('word')) sourceType = 'doc';
        
        addSource({
          name: file.name,
          type: sourceType,
          uploadDate: new Date(),
          size: file.size
        });
      });
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