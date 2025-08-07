'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useStore } from '@/store/useStore';
import { ResearchSession } from '@/store/useStore';
import AuthProtection from '@/components/AuthProtection';
import { 
  Plus,
  MoreVertical,
  Grid3X3,
  List,
  Search,
  ChevronDown,
  Settings,
  FileText,
  Briefcase,
  Scale,
  Gavel,
  FileCheck,
  BookOpen,
  User,
  LogOut,
  MessageSquare,
  LayoutDashboard,
  Moon,
  Sun
} from 'lucide-react';
import { useTheme } from '@/app/context/ThemeContext';
import Footer from '@/components/Footer';

interface CreateSessionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreateSession: (title: string, type: ResearchSession['type']) => void;
}

function CreateSessionModal({ isOpen, onClose, onCreateSession }: CreateSessionModalProps) {
  const [title, setTitle] = useState('');
  const [selectedType, setSelectedType] = useState<ResearchSession['type']>('research');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (title.trim()) {
      onCreateSession(title.trim(), selectedType);
      setTitle('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Create New Research Session
        </h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Session Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter session title..."
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              autoFocus
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Session Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              {[
                { type: 'research' as const, icon: '📚', label: 'Research' },
                { type: 'case' as const, icon: '⚖️', label: 'Case Analysis' },
                { type: 'contract' as const, icon: '📑', label: 'Contract Review' },
                { type: 'brief' as const, icon: '📝', label: 'Brief Writing' }
              ].map(({ type, icon, label }) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSelectedType(type)}
                  className={`p-3 border rounded-lg text-left transition ${
                    selectedType === type
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30'
                      : 'border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <div className="text-xl mb-1">{icon}</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">{label}</div>
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
            >
              Create Session
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function NotebookOverviewContent() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('recent');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { theme, toggleTheme } = useTheme();
  const { user, logout, researchSessions, createSession, setCurrentSession } = useStore();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Sort and filter research sessions
  const sortedSessions = [...researchSessions].sort((a, b) => {
    switch (sortBy) {
      case 'recent':
        return new Date(b.lastAccessed).getTime() - new Date(a.lastAccessed).getTime();
      case 'name':
        return a.title.localeCompare(b.title);
      case 'created':
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      default:
        return 0;
    }
  });

  const handleCreateSession = (title: string, type: ResearchSession['type']) => {
    const sessionId = createSession(title, type);
    // Redirect to research page with the new session
    window.location.href = `/research?id=${sessionId}`;
  };

  const handleSessionClick = (sessionId: string) => {
    setCurrentSession(sessionId);
    window.location.href = `/research?id=${sessionId}`;
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTypeIcon = (type: string) => {
    switch(type) {
      case 'case': return <Gavel className="h-5 w-5" />;
      case 'contract': return <FileCheck className="h-5 w-5" />;
      case 'brief': return <FileText className="h-5 w-5" />;
      case 'research': return <BookOpen className="h-5 w-5" />;
      default: return <FileText className="h-5 w-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center">
              <Scale className="h-8 w-8 text-blue-500" />
              <span className="ml-2 text-xl font-semibold text-gray-900 dark:text-white">Elenchus AI</span>
            </Link>
            <div className="flex items-center space-x-4">
              <button className="p-2 hover:bg-gray-700 rounded-lg transition">
                <Settings className="h-5 w-5 text-gray-300" />
              </button>
              <button className="p-2 hover:bg-gray-700 rounded-lg transition">
                <Grid3X3 className="h-5 w-5 text-gray-300" />
              </button>
              
              <div className="relative" ref={dropdownRef}>
                <button 
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center hover:ring-2 hover:ring-blue-400 transition-all"
                  title={user?.email}
                >
                  {user?.first_name ? user.first_name[0].toUpperCase() : user?.email[0].toUpperCase()}
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && user && (
                  <div className="absolute right-0 mt-2 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-lg py-1 z-50">
                    <div className="px-4 py-3 border-b border-gray-700">
                      <p className="text-sm font-medium text-white">{user.full_name}</p>
                      <p className="text-xs text-gray-400 truncate">{user.email}</p>
                    </div>
                    
                    <Link 
                      href="/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-gray-100 transition-colors"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      <Settings className="w-4 h-4 mr-3" />
                      Settings
                    </Link>
                    
                    <Link 
                      href="/dashboard"
                      className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-gray-100 transition-colors"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      <LayoutDashboard className="w-4 h-4 mr-3" />
                      Dashboard
                    </Link>
                    
                    <button 
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-gray-100 transition-colors text-left"
                      onClick={toggleTheme}
                    >
                      {theme === 'dark' ? <Sun className="w-4 h-4 mr-3" /> : <Moon className="w-4 h-4 mr-3" />}
                      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                    </button>
                    
                    <div className="border-t border-gray-700 my-1"></div>
                    
                    <button 
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-gray-100 transition-colors text-left"
                      onClick={() => {
                        setIsDropdownOpen(false);
                        logout();
                      }}
                    >
                      <LogOut className="w-4 h-4 mr-3" />
                      Log Out
                    </button>
                    
                    <Link 
                      href="/feedback"
                      className="flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-gray-100 transition-colors"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      <MessageSquare className="w-4 h-4 mr-3" />
                      Feedback
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-8">
        <div className="max-w-7xl mx-auto">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Welcome to Elenchus AI</h1>
            <p className="text-gray-600 dark:text-gray-400">Your AI-powered legal research assistant</p>
          </div>

          {/* Actions Bar */}
          <div className="flex items-center justify-between mb-6">
            <button 
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Plus className="h-5 w-5 mr-2" />
              Create new
            </button>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded ${viewMode === 'grid' ? 'bg-gray-50 shadow-sm dark:bg-gray-700' : 'hover:bg-gray-200 dark:hover:bg-gray-700'} transition`}
                >
                  <Grid3X3 className="h-4 w-4 text-gray-700 dark:text-gray-300" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-gray-700 dark:bg-gray-700 bg-gray-200' : 'hover:bg-gray-700 dark:hover:bg-gray-700 hover:bg-gray-200'} transition`}
                >
                  <List className="h-4 w-4 text-gray-700 dark:text-gray-300" />
                </button>
              </div>

              <button className="inline-flex items-center px-3 py-2 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition">
                Most recent
                <ChevronDown className="h-4 w-4 ml-2" />
              </button>
            </div>
          </div>

          {/* Research Sessions Grid */}
          {sortedSessions.length > 0 ? (
            viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {sortedSessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => handleSessionClick(session.id)}
                    className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:bg-gray-50 dark:hover:bg-gray-750 transition-all hover:scale-105 transform cursor-pointer shadow-sm hover:shadow-md"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="text-4xl">{session.icon}</div>
                      <button 
                        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          // TODO: Add context menu for session options
                        }}
                      >
                        <MoreVertical className="h-4 w-4 text-gray-400" />
                      </button>
                    </div>
                    <h3 className="text-gray-900 dark:text-white font-semibold mb-2 line-clamp-2">{session.title}</h3>
                    <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                      <span>{formatDate(session.lastAccessed)}</span>
                      <span>{session.sources.length} source{session.sources.length !== 1 ? 's' : ''}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                {sortedSessions.map((session, index) => (
                  <div
                    key={session.id}
                    onClick={() => handleSessionClick(session.id)}
                    className={`flex items-center p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition cursor-pointer ${
                      index !== sortedSessions.length - 1 ? 'border-b border-gray-200 dark:border-gray-700' : ''
                    }`}
                  >
                    <div className="text-2xl mr-4">{session.icon}</div>
                    <div className="flex-1">
                      <h3 className="text-gray-900 dark:text-white font-semibold">{session.title}</h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
                        <span>{formatDate(session.lastAccessed)}</span>
                        <span>•</span>
                        <span>{session.sources.length} sources</span>
                        <span>•</span>
                        <div className="flex items-center">
                          {getTypeIcon(session.type)}
                          <span className="ml-1 capitalize">{session.type}</span>
                        </div>
                      </div>
                    </div>
                    <button 
                      className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded transition ml-4"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        // TODO: Add context menu for session options
                      }}
                    >
                      <MoreVertical className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                ))}
              </div>
            )
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 dark:text-gray-500 mb-4">
                <FileText className="h-16 w-16 mx-auto mb-4" />
                <h3 className="text-xl font-medium text-gray-900 dark:text-white mb-2">No research sessions yet</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Create your first research session to get started with legal document analysis.
                </p>
              </div>
              <button 
                onClick={() => setIsModalOpen(true)}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition mt-4"
              >
                <Plus className="h-5 w-5 mr-2" />
                Create your first session
              </button>
            </div>
          )}

          {/* Quick Start Guide */}
          <div className="mt-12 bg-gray-100 dark:bg-gray-800 rounded-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Quick Start Guide</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-3">
                  <FileText className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-gray-900 dark:text-white font-semibold mb-2">Upload Documents</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Start by uploading case files, contracts, briefs, or any legal documents you need to analyze.
                </p>
              </div>
              <div>
                <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-3">
                  <Search className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-gray-900 dark:text-white font-semibold mb-2">Ask Questions</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Query your documents naturally. Get summaries, find precedents, or explore legal concepts.
                </p>
              </div>
              <div>
                <div className="bg-blue-600 w-12 h-12 rounded-lg flex items-center justify-center mb-3">
                  <Briefcase className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-gray-900 dark:text-white font-semibold mb-2">Build Your Case</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Generate briefs, create timelines, and organize your research into compelling legal arguments.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <Footer />
      
      {/* Create Session Modal */}
      <CreateSessionModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onCreateSession={handleCreateSession}
      />
    </div>
  );
}

export default function NotebookOverview() {
  return (
    <AuthProtection>
      <NotebookOverviewContent />
    </AuthProtection>
  );
}