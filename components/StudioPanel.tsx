'use client';

import React from 'react';
import { 
  Plus, 
  FileText,
  Clock,
  HelpCircle,
  BookOpen,
  MoreHorizontal,
  Mail,
  Briefcase,
  Scale,
  Shield,
  CheckCircle,
  MessageSquare,
  Search,
  Users,
  Folder,
  PenTool,
  ChevronRight,
  Settings
} from 'lucide-react';
import { useStore } from '../store/useStore';

interface StudioPanelProps {
  panelState: 'normal' | 'collapsed';
  onPanelStateChange: (state: 'normal' | 'collapsed') => void;
}

const StudioPanel: React.FC<StudioPanelProps> = ({ panelState, onPanelStateChange }) => {
  const { 
    notes, 
    addNote, 
    deleteNote, 
    selectedNoteType, 
    setSelectedNoteType 
  } = useStore();
  

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
      content: ''
    });
  };

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-800/50">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">Research Studio</h2>
      </div>

      {/* Workflows Section */}
      <div className="p-4 border-b border-gray-200 dark:border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">Workflows</h3>
          <button className="text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200">
            <MoreHorizontal className="w-4 h-4" />
          </button>
        </div>
        
        <div className="grid grid-cols-1 gap-3">
          {workflows.map((workflow) => {
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

    </div>
  );
};

export default StudioPanel;