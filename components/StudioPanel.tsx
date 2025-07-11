'use client';

import React, { useState } from 'react';
import { 
  Plus, 
  Play, 
  Pause, 
  Volume2, 
  Download, 
  Share,
  FileText,
  Clock,
  HelpCircle,
  BookOpen,
  MoreHorizontal,
  Sparkles,
  Users,
  Settings
} from 'lucide-react';
import { useStore } from '../store/useStore';

const StudioPanel: React.FC = () => {
  const { 
    notes, 
    addNote, 
    deleteNote, 
    selectedNoteType, 
    setSelectedNoteType 
  } = useStore();
  
  const [isPlaying, setIsPlaying] = useState(false);
  const [showCustomizeModal, setShowCustomizeModal] = useState(false);

  const noteTypes = [
    { id: 'study-guide', label: 'Study guide', icon: BookOpen },
    { id: 'briefing-doc', label: 'Briefing doc', icon: FileText },
    { id: 'faq', label: 'FAQ', icon: HelpCircle },
    { id: 'timeline', label: 'Timeline', icon: Clock },
  ] as const;

  const handleCreateNote = (type: typeof noteTypes[number]['id']) => {
    const noteTypeLabels = {
      'study-guide': 'Study Guide',
      'briefing-doc': 'Briefing Document', 
      'faq': 'FAQ',
      'timeline': 'Timeline'
    };
    
    addNote({
      title: `${noteTypeLabels[type]} ${notes.filter(n => n.type === type).length + 1}`,
      type,
      createdAt: new Date(),
      content: ''
    });
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-800/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Research Studio</h2>
      </div>

      {/* Audio Overview Section */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Details</h3>
          <button className="text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
        
        {/* Audio Preview Card */}
        <div className="bg-gray-100 dark:bg-slate-700/50 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Create an Audio Overview in more languages!</p>
              <p className="text-xs text-gray-600 dark:text-slate-400">Learn more</p>
            </div>
          </div>
          
          <div className="space-y-3">
            {/* Deep Dive Conversation */}
            <div className="bg-gray-50 dark:bg-slate-800/50 border border-gray-200 dark:border-slate-600 rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Deep Dive conversation</p>
                  <p className="text-xs text-gray-600 dark:text-slate-400 flex items-center mt-1">
                    <Users className="w-3 h-3 mr-1" />
                    Two hosts
                  </p>
                </div>
              </div>
              
              {/* Audio Controls */}
              <div className="flex items-center space-x-2 mt-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors">
                  <Play className="w-4 h-4" />
                  <span className="text-sm">Generate</span>
                </button>
              </div>
            </div>
            
            <button
              onClick={() => setShowCustomizeModal(true)}
              className="w-full text-center text-blue-400 hover:text-blue-300 text-sm font-medium transition-colors"
            >
              Customize
            </button>
          </div>
        </div>
      </div>

      {/* Research Tools Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Research Tools</h3>
            <button className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1">
              <Plus className="w-3 h-3" />
              <span>Add note</span>
            </button>
          </div>
          
          {/* Note Type Buttons */}
          <div className="grid grid-cols-2 gap-2 mb-4">
            {noteTypes.map((noteType) => {
              const Icon = noteType.icon;
              return (
                <button
                  key={noteType.id}
                  onClick={() => handleCreateNote(noteType.id)}
                  className="flex items-center space-x-2 p-3 bg-gray-100 dark:bg-slate-700/50 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-lg transition-colors text-left"
                >
                  <Icon className="w-4 h-4 text-gray-600 dark:text-slate-300" />
                  <span className="text-sm text-gray-900 dark:text-gray-100">{noteType.label}</span>
                </button>
              );
            })}
          </div>
          
          {/* Notes List */}
          {notes.length > 0 ? (
            <div className="space-y-3">
              <p className="text-xs text-slate-500 dark:text-slate-500 text-gray-500 mb-2">No notes yet</p>
              <p className="text-xs text-slate-400 dark:text-slate-400 text-gray-600">
                Create your first note using the buttons above.
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 dark:bg-slate-700 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <FileText className="w-8 h-8 text-gray-400 dark:text-slate-400" />
              </div>
              <p className="text-sm text-gray-600 dark:text-slate-400">No notes yet</p>
              <p className="text-xs text-gray-500 dark:text-slate-500 mt-1">
                Create your first note using the buttons above
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Customize Modal */}
      {showCustomizeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-50 dark:bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
              Customize Audio Overview
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Conversation style
                </label>
                <select className="w-full bg-gray-50 dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 text-gray-900 dark:text-gray-100">
                  <option>Casual</option>
                  <option>Professional</option>
                  <option>Academic</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
                  Language
                </label>
                <select className="w-full bg-gray-50 dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 text-gray-900 dark:text-gray-100">
                  <option>English</option>
                  <option>Spanish</option>
                  <option>French</option>
                </select>
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCustomizeModal(false)}
                className="flex-1 bg-gray-200 dark:bg-slate-700 hover:bg-gray-300 dark:hover:bg-slate-600 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCustomizeModal(false)}
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudioPanel;