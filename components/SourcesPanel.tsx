'use client';

import React, { useRef } from 'react';
import { Plus, Search, FileText, Upload, X } from 'lucide-react';
import { useStore } from '../store/useStore';

const SourcesPanel: React.FC = () => {
  const { sources, addSource, removeSource } = useStore();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
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

  return (
    <div className="h-full flex flex-col bg-slate-800/50 dark:bg-slate-800/50 bg-white">
      {/* Header */}
      <div className="p-4 border-b border-slate-700 dark:border-slate-700 border-gray-200">
        <h2 className="text-lg font-medium text-gray-100 dark:text-gray-100 text-gray-900 mb-4">Sources</h2>
        
        {/* Action Buttons */}
        <div className="space-y-2">
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add</span>
          </button>
          
          <button className="w-full flex items-center justify-center space-x-2 bg-slate-700 dark:bg-slate-700 bg-gray-100 hover:bg-slate-600 dark:hover:bg-slate-600 hover:bg-gray-200 text-gray-200 dark:text-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors">
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
            <div className="w-16 h-16 mx-auto mb-4 bg-slate-700 dark:bg-slate-700 bg-gray-100 rounded-lg flex items-center justify-center">
              <FileText className="w-8 h-8 text-slate-400 dark:text-slate-400 text-gray-400" />
            </div>
            <p className="text-sm text-slate-400 dark:text-slate-400 text-gray-600 mb-2">Saved sources will appear here</p>
            <p className="text-xs text-slate-500 dark:text-slate-500 text-gray-500">Click Add source above to add PDFs, websites, text, videos, or audio files.</p>
          </div>
        ) : (
          <div className="p-4 space-y-3">
            {sources.map((source) => (
              <div key={source.id} className="group bg-slate-700/50 dark:bg-slate-700/50 bg-gray-100 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-200 rounded-lg p-3 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-slate-600 dark:bg-slate-600 bg-gray-200 rounded flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-slate-300 dark:text-slate-300 text-gray-600" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-100 dark:text-gray-100 text-gray-900 truncate">{source.name}</p>
                      <p className="text-xs text-slate-400 dark:text-slate-400 text-gray-600 mt-1">
                        {source.type.toUpperCase()}
                        {source.size && ` • ${formatFileSize(source.size)}`}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeSource(source.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 dark:text-slate-400 text-gray-500 hover:text-slate-200 dark:hover:text-slate-200 hover:text-gray-700 transition-all"
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
      <div className="p-4 border-t border-slate-700 dark:border-slate-700 border-gray-200 text-center">
        <p className="text-xs text-slate-500 dark:text-slate-500 text-gray-500">{sources.length} sources</p>
      </div>
    </div>
  );
};

export default SourcesPanel; 