'use client';

import React, { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { Settings, Share, BarChart3, User, ArrowLeft, LogOut, MessageSquare, LayoutDashboard, Moon, Sun } from 'lucide-react';
import { useTheme } from '@/app/context/ThemeContext';

const Header: React.FC = () => {
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

  return (
    <header className="h-14 bg-gray-50 dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between px-4">
      {/* Left side - Back button and Title */}
      <div className="flex items-center space-x-3">
        <Link 
          href="/app" 
          className="p-1.5 text-slate-300 dark:text-slate-300 text-gray-600 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 rounded-md transition-colors"
          title="Back to notebooks"
        >
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <Link href="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-semibold text-sm">⚖️</span>
          </div>
          <h1 className="text-lg font-medium text-slate-100 dark:text-slate-100 text-gray-900">Elenchus AI</h1>
        </Link>
      </div>

      {/* Right side - Controls */}
      <div className="flex items-center space-x-2">
        <button className="flex items-center space-x-2 px-3 py-1.5 text-sm text-slate-300 dark:text-slate-300 text-gray-600 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 rounded-md transition-colors">
          <BarChart3 className="w-4 h-4" />
          <span>Analytics</span>
        </button>
        
        <button className="flex items-center space-x-2 px-3 py-1.5 text-sm text-slate-300 dark:text-slate-300 text-gray-600 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 rounded-md transition-colors">
          <Share className="w-4 h-4" />
          <span>Share</span>
        </button>
        
        <button className="p-1.5 text-slate-300 dark:text-slate-300 text-gray-600 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 rounded-md transition-colors">
          <Settings className="w-5 h-5" />
        </button>
        
        <div className="relative" ref={dropdownRef}>
          <button 
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center ml-2 hover:ring-2 hover:ring-blue-400 transition-all"
          >
            <User className="w-4 h-4 text-white" />
          </button>

          {/* Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-slate-800 dark:bg-slate-800 bg-white border border-slate-700 dark:border-slate-700 border-gray-200 rounded-lg shadow-lg py-1 z-50">
              <Link 
                href="/settings"
                className="flex items-center px-4 py-2 text-sm text-slate-300 dark:text-slate-300 text-gray-700 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 transition-colors"
                onClick={() => setIsDropdownOpen(false)}
              >
                <Settings className="w-4 h-4 mr-3" />
                Settings
              </Link>
              
              <Link 
                href="/dashboard"
                className="flex items-center px-4 py-2 text-sm text-slate-300 dark:text-slate-300 text-gray-700 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 transition-colors"
                onClick={() => setIsDropdownOpen(false)}
              >
                <LayoutDashboard className="w-4 h-4 mr-3" />
                Dashboard
              </Link>
              
              <button 
                className="flex items-center w-full px-4 py-2 text-sm text-slate-300 dark:text-slate-300 text-gray-700 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 transition-colors text-left"
                onClick={toggleTheme}
              >
                {theme === 'dark' ? <Sun className="w-4 h-4 mr-3" /> : <Moon className="w-4 h-4 mr-3" />}
                {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
              </button>
              
              <div className="border-t border-slate-700 dark:border-slate-700 border-gray-200 my-1"></div>
              
              <button 
                className="flex items-center w-full px-4 py-2 text-sm text-slate-300 dark:text-slate-300 text-gray-700 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 transition-colors text-left"
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
                className="flex items-center px-4 py-2 text-sm text-slate-300 dark:text-slate-300 text-gray-700 hover:bg-slate-700 dark:hover:bg-slate-700 hover:bg-gray-100 hover:text-slate-100 dark:hover:text-slate-100 hover:text-gray-900 transition-colors"
                onClick={() => setIsDropdownOpen(false)}
              >
                <MessageSquare className="w-4 h-4 mr-3" />
                Feedback
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 