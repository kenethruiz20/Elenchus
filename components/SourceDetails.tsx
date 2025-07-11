'use client';

import React from 'react';
import { X, ChevronDown, ChevronUp, BookOpen, Calendar, FileText, User, ChevronLeft, ArrowLeft } from 'lucide-react';

interface Source {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'txt' | 'url';
  uploadDate: Date;
  size?: number;
}

interface SourceDetailsProps {
  source: Source;
  onClose: () => void;
  onCollapse?: () => void;
}

const SourceDetails: React.FC<SourceDetailsProps> = ({ source, onClose, onCollapse }) => {
  const [isGuideExpanded, setIsGuideExpanded] = React.useState(true);

  // Mock data - in real app, this would come from document analysis
  const sourceData = {
    summary: `This comprehensive report, "${source.name}" explores the unprecedented and accelerating impact of Artificial Intelligence across various sectors, emphasizing that change is happening faster than ever. The document is structured around key themes like AI user and usage growth, capital expenditure, model compute costs, monetization threats, and AI's influence on the physical world, work evolution, and knowledge distribution. It delves into the rapid adoption of AI by consumers, developers, traditional enterprises, and even governments, highlighting how AI is becoming deeply embedded in global infrastructure, similar to electricity or the internet. The report also discusses the intense competition, particularly between the USA and China, and the dual nature of AI as both a transformative opportunity and a source of risk.`,
    keyTopics: [
      'AI growth trends and market expansion',
      'AI investment patterns and capital expenditure',
      'AI competition between major powers',
      'AI applications across industries',
      'AI workforce transformation impact'
    ],
    metadata: {
      title: source.name.replace('.pdf', ''),
      subtitle: 'Trends – Artificial Intelligence (AI)',
      date: 'May 30, 2025',
      authors: ['Mary Meeker', 'Jay Simons', 'Daegwon Chae', 'Alexander Krey'],
      context: 'We set out to compile foundational trends related to AI. A starting collection of several disparate datapoints turned into this beast. As soon as we updated one chart, we often had to update another – a data game of whack-a-mole... a pattern that shows no sign of stopping...and will grow more complex as competition among tech incumbents, emerging attackers and sovereigns accelerates.'
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
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {/* Summary */}
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Summary</h4>
                    <p className="text-sm text-gray-700 dark:text-slate-300 leading-relaxed">
                      {sourceData.summary}
                    </p>
                  </div>

                  {/* Key Topics */}
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Key Topics</h4>
                    <div className="space-y-2">
                      {sourceData.keyTopics.map((topic, index) => (
                        <button
                          key={index}
                          className="block w-full text-left px-3 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded-lg text-sm hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                        >
                          {topic}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
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
                <div className="flex items-center space-x-1">
                  <User className="w-4 h-4" />
                  <span>{sourceData.metadata.authors.join(' / ')}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Context</h4>
              <p className="text-sm text-gray-700 dark:text-slate-300 leading-relaxed">
                {sourceData.metadata.context}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SourceDetails;