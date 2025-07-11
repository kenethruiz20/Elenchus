'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
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

interface Notebook {
  id: string;
  title: string;
  date: string;
  sources: number;
  icon: string;
  type: 'case' | 'contract' | 'brief' | 'research';
}

export default function NotebookOverview() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('recent');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const notebooks: Notebook[] = [
    {
      id: '1',
      title: 'Smith v. Johnson Appeal',
      date: 'Jun 19, 2025',
      sources: 12,
      icon: '⚖️',
      type: 'case'
    },
    {
      id: '2',
      title: 'Contract Review - Tech Merger',
      date: 'Jun 27, 2025',
      sources: 8,
      icon: '📑',
      type: 'contract'
    },
    {
      id: '3',
      title: 'Employment Law Research',
      date: 'Jun 27, 2025',
      sources: 15,
      icon: '📚',
      type: 'research'
    },
    {
      id: '4',
      title: 'Motion to Dismiss Brief',
      date: 'Jun 27, 2025',
      sources: 6,
      icon: '📝',
      type: 'brief'
    },
    {
      id: '5',
      title: 'Real Estate Closing Docs',
      date: 'Jun 25, 2025',
      sources: 10,
      icon: '🏠',
      type: 'contract'
    },
    {
      id: '6',
      title: 'Criminal Defense Strategy',
      date: 'Jun 24, 2025',
      sources: 14,
      icon: '🛡️',
      type: 'case'
    }
  ];

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
                >
                  <User className="w-4 h-4 text-white" />
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg py-1 z-50">
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
                        // Handle logout logic here
                        console.log('Logout clicked');
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
            <Link 
              href="/research"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              <Plus className="h-5 w-5 mr-2" />
              Create new
            </Link>

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

          {/* Notebooks Grid */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {notebooks.map((notebook) => (
                <Link
                  key={notebook.id}
                  href={`/research?id=${notebook.id}`}
                  className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:bg-gray-50 dark:hover:bg-gray-750 transition-all hover:scale-105 transform cursor-pointer shadow-sm hover:shadow-md"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-4xl">{notebook.icon}</div>
                    <button 
                      className="p-1 hover:bg-gray-700 rounded transition"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      <MoreVertical className="h-4 w-4 text-gray-400 dark:text-gray-400 text-gray-600" />
                    </button>
                  </div>
                  <h3 className="text-gray-900 dark:text-white font-semibold mb-2 line-clamp-2">{notebook.title}</h3>
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>{notebook.date}</span>
                    <span>{notebook.sources} source{notebook.sources !== 1 ? 's' : ''}</span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg overflow-hidden">
              {notebooks.map((notebook, index) => (
                <Link
                  key={notebook.id}
                  href={`/research?id=${notebook.id}`}
                  className={`flex items-center p-4 hover:bg-gray-100 dark:hover:bg-gray-700 transition ${
                    index !== notebooks.length - 1 ? 'border-b border-gray-200 dark:border-gray-700' : ''
                  }`}
                >
                  <div className="text-2xl mr-4">{notebook.icon}</div>
                  <div className="flex-1">
                    <h3 className="text-gray-900 dark:text-white font-semibold">{notebook.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
                      <span>{notebook.date}</span>
                      <span>•</span>
                      <span>{notebook.sources} sources</span>
                      <span>•</span>
                      <div className="flex items-center">
                        {getTypeIcon(notebook.type)}
                        <span className="ml-1 capitalize">{notebook.type}</span>
                      </div>
                    </div>
                  </div>
                  <button 
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-600 rounded transition ml-4"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                  >
                    <MoreVertical className="h-4 w-4 text-gray-400" />
                  </button>
                </Link>
              ))}
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
    </div>
  );
}