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
      content: `This is a ${noteTypeLabels[type].toLowerCase()} generated from your sources.`,
      type: type
    });
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="h-full flex flex-col bg-slate-800/50">
      {/* Header */}
      <div className="p-4 border-b border-slate-700">
        <h2 className="text-lg font-medium text-gray-100">Studio</h2>
      </div>

      {/* Audio Overview Section */}
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-100">Audio Overview</h3>
          <button className="text-slate-400 hover:text-slate-200">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
        
        {/* Audio Preview Card */}
        <div className="bg-slate-700/50 rounded-lg p-4 mb-4">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-100">Create an Audio Overview in more languages!</p>
              <p className="text-xs text-slate-400">Learn more</p>
            </div>
          </div>
          
          <div className="space-y-3">
            {/* Deep Dive Conversation */}
            <div className="bg-slate-800 rounded-lg p-3">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center">
                  <Users className="w-4 h-4 text-slate-300" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-100">Deep Dive conversation</p>
                  <p className="text-xs text-slate-400">Two hosts</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <button 
                    onClick={() => setShowCustomizeModal(true)}
                    className="px-3 py-1 text-xs bg-slate-700 hover:bg-slate-600 text-gray-200 rounded-md transition-colors"
                  >
                    Customize
                  </button>
                  <button className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors">
                    Generate
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Notes Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-100">Notes</h3>
            <button className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 text-sm">
              <Plus className="w-4 h-4" />
              <span>Add note</span>
            </button>
          </div>

          {/* Note Type Buttons */}
          <div className="grid grid-cols-2 gap-2 mb-6">
            {noteTypes.map((noteType) => {
              const Icon = noteType.icon;
              return (
                <button
                  key={noteType.id}
                  onClick={() => handleCreateNote(noteType.id)}
                  className="flex items-center space-x-2 p-3 bg-slate-700/50 hover:bg-slate-700 rounded-lg transition-colors text-left"
                >
                  <Icon className="w-4 h-4 text-slate-300" />
                  <span className="text-sm text-gray-100">{noteType.label}</span>
                </button>
              );
            })}
          </div>

          {/* Notes List */}
          {notes.length > 0 ? (
            <div className="space-y-3">
              {notes.map((note) => (
                <div key={note.id} className="bg-slate-700/50 hover:bg-slate-700 rounded-lg p-3 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-gray-100 mb-1">{note.title}</h4>
                      <p className="text-xs text-slate-400 mb-2">{note.content}</p>
                      <p className="text-xs text-slate-500">
                        {note.updatedAt.toLocaleDateString()}
                      </p>
                    </div>
                    <button
                      onClick={() => deleteNote(note.id)}
                      className="text-slate-400 hover:text-slate-200 p-1"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-slate-700 rounded-lg flex items-center justify-center">
                <FileText className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-sm text-slate-400 mb-2">No notes yet</p>
              <p className="text-xs text-slate-500">Create your first note using the buttons above</p>
            </div>
          )}
        </div>
      </div>

      {/* Customize Modal */}
      {showCustomizeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-100">Customize Audio Overview</h3>
              <button
                onClick={() => setShowCustomizeModal(false)}
                className="text-slate-400 hover:text-slate-200"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-100 mb-2">
                  Conversation Style
                </label>
                <select className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-gray-100">
                  <option>Deep Dive</option>
                  <option>Overview</option>
                  <option>Q&A</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-100 mb-2">
                  Number of Hosts
                </label>
                <select className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-gray-100">
                  <option>Two hosts</option>
                  <option>One host</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-100 mb-2">
                  Language
                </label>
                <select className="w-full bg-slate-700 border border-slate-600 rounded-md px-3 py-2 text-gray-100">
                  <option>English</option>
                  <option>Spanish</option>
                  <option>French</option>
                  <option>German</option>
                </select>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowCustomizeModal(false)}
                className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCustomizeModal(false)}
                className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-md"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StudioPanel; 