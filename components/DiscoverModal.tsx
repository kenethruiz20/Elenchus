'use client';

import React, { useState } from 'react';
import { X, Search, Plus, Scale, Gavel, Shield, BookOpen, Globe, FileText } from 'lucide-react';

interface DiscoverModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAddSource: (source: any) => void;
}

const DiscoverModal: React.FC<DiscoverModalProps> = ({ isOpen, onClose, onAddSource }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Internal');

  const discoverSources = [
    {
      id: '1',
      title: 'Supreme Court Cases Database',
      description: 'Access to landmark Supreme Court decisions and opinions',
      category: 'Case Law',
      icon: Scale,
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      iconColor: 'text-blue-600 dark:text-blue-400'
    },
    {
      id: '2',
      title: 'Federal Statutes Collection',
      description: 'Comprehensive collection of federal statutes and codes',
      category: 'Internal',
      icon: BookOpen,
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      iconColor: 'text-green-600 dark:text-green-400'
    },
    {
      id: '3',
      title: 'SEC Regulations & Rules',
      description: 'Securities and Exchange Commission regulations and guidance',
      category: 'Regulations',
      icon: Shield,
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      iconColor: 'text-purple-600 dark:text-purple-400'
    },
    {
      id: '4',
      title: 'US Constitution',
      description: 'Complete text of the United States Constitution and amendments',
      category: 'Constitutions',
      icon: FileText,
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      iconColor: 'text-red-600 dark:text-red-400'
    },
    {
      id: '5',
      title: 'Custom Legal Documents',
      description: 'User-uploaded legal documents and custom sources',
      category: 'Custom',
      icon: FileText,
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
      iconColor: 'text-yellow-600 dark:text-yellow-400'
    }
  ];

  const categories = ['Internal', 'Custom', 'Case Law', 'Regulations', 'Constitutions'];

  const filteredSources = discoverSources.filter(source => {
    const matchesSearch = source.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         source.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = source.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleAddSource = (source: any) => {
    const newSource = {
      name: source.title,
      type: 'url' as const,
      uploadDate: new Date(),
      description: source.description,
      category: source.category
    };
    onAddSource(newSource);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-screen overflow-hidden shadow-xl">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Discover sources</h2>
            <button
              onClick={onClose}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6">

          <div className="relative mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search sources..."
              className="w-full bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 pr-12 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
          </div>

          <div className="mb-6">
            <div className="flex flex-wrap gap-2 justify-center">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-1 rounded-full text-sm transition-colors ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredSources.map((source) => {
                const Icon = source.icon;
                return (
                  <div
                    key={source.id}
                    className="bg-gray-100 dark:bg-gray-700 rounded-lg p-4 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${source.bgColor}`}>
                        <Icon className={`w-5 h-5 ${source.iconColor}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-1 truncate">
                          {source.title}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                          {source.description}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded text-xs text-gray-500 dark:text-gray-400">
                            {source.category}
                          </span>
                          <button
                            onClick={() => handleAddSource(source)}
                            className="flex items-center space-x-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 text-sm transition-colors"
                          >
                            <Plus className="w-4 h-4" />
                            <span>Add</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DiscoverModal;