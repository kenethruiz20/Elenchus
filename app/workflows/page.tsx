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
  Mail,
  FileText,
  Scale,
  Shield,
  Clock,
  BookOpen,
  User,
  LogOut,
  MessageSquare,
  LayoutDashboard,
  Moon,
  Sun,
  PenTool,
  Users,
  Folder,
  ArrowLeft
} from 'lucide-react';
import { useTheme } from '@/app/context/ThemeContext';
import Footer from '@/components/Footer';

interface Workflow {
  id: string;
  title: string;
  description: string;
  category: string;
  icon: any;
  bgColor: string;
  iconColor: string;
  usage: number;
  lastUsed: string;
  status: 'active' | 'draft' | 'archived';
}

export default function WorkflowsPage() {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState('recent');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
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

  const workflows: Workflow[] = [
    {
      id: 'send-email',
      title: 'Send email',
      description: 'Send case updates to clients',
      category: 'communication',
      icon: Mail,
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      iconColor: 'text-red-600 dark:text-red-400',
      usage: 23,
      lastUsed: 'Yesterday',
      status: 'active'
    },
    {
      id: 'create-brief',
      title: 'Create brief',
      description: 'Generate legal brief from sources',
      category: 'document',
      icon: FileText,
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      iconColor: 'text-blue-600 dark:text-blue-400',
      usage: 45,
      lastUsed: '2 hours ago',
      status: 'active'
    },
    {
      id: 'case-analysis',
      title: 'Case analysis',
      description: 'Analyze case law and precedents',
      category: 'analysis',
      icon: Scale,
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      iconColor: 'text-purple-600 dark:text-purple-400',
      usage: 31,
      lastUsed: '1 day ago',
      status: 'active'
    },
    {
      id: 'contract-review',
      title: 'Contract review',
      description: 'Review and flag contract issues',
      category: 'review',
      icon: Shield,
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      iconColor: 'text-green-600 dark:text-green-400',
      usage: 18,
      lastUsed: '3 days ago',
      status: 'active'
    },
    {
      id: 'legal-research',
      title: 'Legal research',
      description: 'Research relevant statutes and cases',
      category: 'research',
      icon: Search,
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
      iconColor: 'text-yellow-600 dark:text-yellow-400',
      usage: 67,
      lastUsed: 'Today',
      status: 'active'
    },
    {
      id: 'create-timeline',
      title: 'Create timeline',
      description: 'Build case timeline from facts',
      category: 'organization',
      icon: Clock,
      bgColor: 'bg-indigo-50 dark:bg-indigo-900/20',
      iconColor: 'text-indigo-600 dark:text-indigo-400',
      usage: 12,
      lastUsed: '1 week ago',
      status: 'active'
    },
    {
      id: 'deposition-prep',
      title: 'Deposition prep',
      description: 'Prepare questions for depositions',
      category: 'preparation',
      icon: Users,
      bgColor: 'bg-pink-50 dark:bg-pink-900/20',
      iconColor: 'text-pink-600 dark:text-pink-400',
      usage: 8,
      lastUsed: '2 weeks ago',
      status: 'draft'
    },
    {
      id: 'document-review',
      title: 'Document review',
      description: 'Review and categorize documents',
      category: 'review',
      icon: Folder,
      bgColor: 'bg-cyan-50 dark:bg-cyan-900/20',
      iconColor: 'text-cyan-600 dark:text-cyan-400',
      usage: 34,
      lastUsed: '4 days ago',
      status: 'active'
    }
  ];

  const categories = ['all', 'communication', 'document', 'analysis', 'review', 'research', 'organization', 'preparation'];

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesSearch = workflow.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         workflow.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || workflow.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'active': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'draft': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'archived': return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link 
                href="/app" 
                className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Back to notebooks"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <Link href="/" className="flex items-center">
                <Scale className="h-8 w-8 text-blue-500" />
                <span className="ml-2 text-xl font-semibold text-gray-900 dark:text-white">Elenchus AI</span>
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition">
                <Settings className="h-5 w-5 text-gray-600 dark:text-gray-400" />
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
                  <div className="absolute right-0 mt-2 w-48 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg py-1 z-50">
                    <Link 
                      href="/settings"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      <Settings className="w-4 h-4 mr-3" />
                      Settings
                    </Link>
                    
                    <Link 
                      href="/dashboard"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      <LayoutDashboard className="w-4 h-4 mr-3" />
                      Dashboard
                    </Link>
                    
                    <button 
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 transition-colors text-left"
                      onClick={toggleTheme}
                    >
                      {theme === 'dark' ? <Sun className="w-4 h-4 mr-3" /> : <Moon className="w-4 h-4 mr-3" />}
                      {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                    </button>
                    
                    <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                    
                    <button 
                      className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 transition-colors text-left"
                      onClick={() => {
                        setIsDropdownOpen(false);
                        console.log('Logout clicked');
                      }}
                    >
                      <LogOut className="w-4 h-4 mr-3" />
                      Log Out
                    </button>
                    
                    <Link 
                      href="/feedback"
                      className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
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
          {/* Header Section */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Workflows</h1>
            <p className="text-gray-600 dark:text-gray-400">Manage and execute your legal research workflows</p>
          </div>

          {/* Search and Filters */}
          <div className="mb-6 space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search workflows..."
                  className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 pr-12 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Search className="w-5 h-5 text-gray-400" />
                </div>
              </div>
              
              <button className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                <Plus className="h-5 w-5 mr-2" />
                Create workflow
              </button>
            </div>

            {/* Category Filters */}
            <div className="flex flex-wrap gap-2">
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
                  {category === 'all' ? 'All' : category.charAt(0).toUpperCase() + category.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Actions Bar */}
          <div className="flex items-center justify-between mb-6">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {filteredWorkflows.length} workflow{filteredWorkflows.length !== 1 ? 's' : ''}
            </div>

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
                  className={`p-2 rounded ${viewMode === 'list' ? 'bg-gray-50 shadow-sm dark:bg-gray-700' : 'hover:bg-gray-200 dark:hover:bg-gray-700'} transition`}
                >
                  <List className="h-4 w-4 text-gray-700 dark:text-gray-300" />
                </button>
              </div>

              <button className="inline-flex items-center px-3 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition">
                Most used
                <ChevronDown className="h-4 w-4 ml-2" />
              </button>
            </div>
          </div>

          {/* Workflows Grid/List */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredWorkflows.map((workflow) => {
                const Icon = workflow.icon;
                return (
                  <div
                    key={workflow.id}
                    className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6 hover:bg-gray-100 dark:hover:bg-gray-750 transition-all hover:scale-105 transform cursor-pointer shadow-sm hover:shadow-md"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${workflow.bgColor}`}>
                        <Icon className={`w-6 h-6 ${workflow.iconColor}`} />
                      </div>
                      <button 
                        className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                        }}
                      >
                        <MoreVertical className="h-4 w-4 text-gray-400" />
                      </button>
                    </div>
                    <h3 className="text-gray-900 dark:text-white font-semibold mb-2">{workflow.title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{workflow.description}</p>
                    <div className="flex items-center justify-between text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(workflow.status)}`}>
                        {workflow.status}
                      </span>
                      <div className="text-gray-500 dark:text-gray-400">
                        {workflow.usage} uses
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      Last used: {workflow.lastUsed}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg overflow-hidden">
              {filteredWorkflows.map((workflow, index) => {
                const Icon = workflow.icon;
                return (
                  <div
                    key={workflow.id}
                    className={`flex items-center p-4 hover:bg-gray-100 dark:hover:bg-gray-700 transition cursor-pointer ${
                      index !== filteredWorkflows.length - 1 ? 'border-b border-gray-200 dark:border-gray-700' : ''
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mr-4 ${workflow.bgColor}`}>
                      <Icon className={`w-5 h-5 ${workflow.iconColor}`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-gray-900 dark:text-white font-semibold">{workflow.title}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{workflow.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400 mt-2">
                        <span>{workflow.usage} uses</span>
                        <span>•</span>
                        <span>Last used: {workflow.lastUsed}</span>
                        <span>•</span>
                        <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(workflow.status)}`}>
                          {workflow.status}
                        </span>
                      </div>
                    </div>
                    <button 
                      className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition ml-4"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      <MoreVertical className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  );
}