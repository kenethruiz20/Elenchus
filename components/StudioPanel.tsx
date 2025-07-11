'use client';

import React, { useState } from 'react';
import { 
  Plus, 
  FileText,
  Mail,
  Scale,
  Shield,
  Search,
  ChevronRight,
  Settings,
  Maximize2,
  Edit3,
  Clock,
  Trash2
} from 'lucide-react';
import Link from 'next/link';
import { useStore } from '../store/useStore';
import type { Note } from '../store/useStore';
import NoteEditor from './NoteEditor';

interface StudioPanelProps {
  panelState: 'normal' | 'collapsed';
  onPanelStateChange: (state: 'normal' | 'collapsed') => void;
}

const StudioPanel: React.FC<StudioPanelProps> = ({ panelState, onPanelStateChange }) => {
  const { 
    notes, 
    addNote, 
    updateNote,
    deleteNote
  } = useStore();
  
  const [workflowSearch, setWorkflowSearch] = useState('');
  const [isNoteEditorOpen, setIsNoteEditorOpen] = useState(false);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  

  // Workflow definitions
  const workflows = [
    {
      id: 'send-email',
      title: 'Send email',
      description: 'Send case updates to clients',
      icon: Mail,
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      iconColor: 'text-red-600 dark:text-red-400',
      category: 'communication'
    },
    {
      id: 'create-brief',
      title: 'Create brief',
      description: 'Generate legal brief from sources',
      icon: FileText,
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      iconColor: 'text-blue-600 dark:text-blue-400',
      category: 'document'
    },
    {
      id: 'case-analysis',
      title: 'Case analysis',
      description: 'Analyze case law and precedents',
      icon: Scale,
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      iconColor: 'text-purple-600 dark:text-purple-400',
      category: 'analysis'
    },
    {
      id: 'contract-review',
      title: 'Contract review',
      description: 'Review and flag contract issues',
      icon: Shield,
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      iconColor: 'text-green-600 dark:text-green-400',
      category: 'review'
    },
    {
      id: 'legal-research',
      title: 'Legal research',
      description: 'Research relevant statutes and cases',
      icon: Search,
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      category: 'research'
    },
    {
      id: 'create-timeline',
      title: 'Create timeline',
      description: 'Build case timeline from facts',
      icon: Clock,
      bgColor: 'bg-indigo-50 dark:bg-indigo-900/20',
      iconColor: 'text-indigo-600 dark:text-indigo-400',
      category: 'organization'
    }
  ];

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.title.toLowerCase().includes(workflowSearch.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(workflowSearch.toLowerCase());
    return matchesSearch;
  });

  const togglePanel = () => {
    if (panelState === 'collapsed') {
      onPanelStateChange('normal');
    } else {
      onPanelStateChange('collapsed');
    }
  };


  const handleCreateNote = () => {
    setSelectedNote(null);
    setIsNoteEditorOpen(true);
  };

  const handleEditNote = (note: Note) => {
    setSelectedNote(note);
    setIsNoteEditorOpen(true);
  };

  const handleSaveNote = (title: string, content: string) => {
    if (selectedNote) {
      // Update existing note
      updateNote(selectedNote.id, {
        title,
        content
      });
    } else {
      // Create new note
      addNote({
        title,
        content,
        type: 'general'
      });
    }
  };

  const handleDeleteNote = (noteId: string) => {
    if (confirm('Are you sure you want to delete this note?')) {
      deleteNote(noteId);
    }
  };

  const truncateHTML = (html: string, maxLength: number = 100) => {
    const div = document.createElement('div');
    div.innerHTML = html;
    const text = div.textContent || div.innerText || '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };

  // Handle collapsed state
  if (panelState === 'collapsed') {
    return (
      <div className="h-full bg-gray-50 dark:bg-slate-800/50">
        <div className="p-2 border-b border-gray-200 dark:border-slate-700">
          <button
            onClick={togglePanel}
            className="w-full p-2 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
            title="Expand Studio"
          >
            <ChevronRight className="w-5 h-5 rotate-180" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-800/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={togglePanel}
              className="p-1 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
              title="Collapse Studio"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Research Studio</h2>
          </div>
        </div>
      </div>

      {/* Workflows Section */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Workflows</h3>
          <Link 
            href="/workflows"
            className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 flex items-center space-x-1 transition-colors"
          >
            <Settings className="w-3 h-3" />
            <span>Manage</span>
          </Link>
        </div>
        
        {/* Search Bar */}
        <div className="relative mb-4">
          <input
            type="text"
            value={workflowSearch}
            onChange={(e) => setWorkflowSearch(e.target.value)}
            placeholder="Search workflows..."
            className="w-full bg-gray-100 dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg px-3 py-2 pr-10 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <Search className="w-4 h-4 text-gray-400" />
          </div>
        </div>
        
        <div className="max-h-64 overflow-y-auto">
          <div className="grid grid-cols-1 gap-3">
            {filteredWorkflows.map((workflow) => {
            const Icon = workflow.icon;
            return (
              <button
                key={workflow.id}
                className="flex items-start space-x-3 p-3 bg-gray-100 dark:bg-slate-700/50 hover:bg-gray-200 dark:hover:bg-slate-700 rounded-lg transition-colors text-left w-full"
              >
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${workflow.bgColor}`}>
                  <Icon className={`w-5 h-5 ${workflow.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
                    {workflow.title}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-slate-400 leading-relaxed">
                    {workflow.description}
                  </p>
                </div>
              </button>
            );
          })}
          </div>
        </div>
      </div>

      {/* Research Tools Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Notes</h3>
            <button 
              onClick={handleCreateNote}
              className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200 flex items-center space-x-1 transition-colors"
            >
              <Plus className="w-3 h-3" />
              <span>Add note</span>
            </button>
          </div>
          
          {/* Notes List */}
          {notes.length > 0 ? (
            <div className="space-y-3">
              {notes.map((note) => (
                <div
                  key={note.id}
                  className="bg-gray-100 dark:bg-slate-700/50 rounded-lg p-3 group hover:bg-gray-200 dark:hover:bg-slate-700 transition-colors cursor-pointer"
                  onClick={() => handleEditNote(note)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <Edit3 className="w-4 h-4 text-gray-600 dark:text-slate-300 flex-shrink-0" />
                        <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                          {note.title}
                        </h4>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-slate-400 leading-relaxed">
                        {note.content ? truncateHTML(note.content, 80) : 'No content'}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500 dark:text-slate-500">
                          {note.updatedAt ? new Date(note.updatedAt).toLocaleDateString() : 'No date'}
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteNote(note.id);
                          }}
                          className="opacity-0 group-hover:opacity-100 p-1 text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-all"
                          title="Delete note"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEditNote(note);
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-all"
                      title="Expand note"
                    >
                      <Maximize2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 dark:bg-slate-700 rounded-lg mx-auto mb-3 flex items-center justify-center">
                <FileText className="w-8 h-8 text-gray-400 dark:text-slate-400" />
              </div>
              <p className="text-sm text-gray-600 dark:text-slate-400">No notes yet</p>
              <p className="text-xs text-gray-500 dark:text-slate-500 mt-1">
                Create your first note using the button above
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Note Editor Modal */}
      <NoteEditor
        isOpen={isNoteEditorOpen}
        onClose={() => setIsNoteEditorOpen(false)}
        note={selectedNote}
        onSave={handleSaveNote}
      />
    </div>
  );
};

export default StudioPanel;