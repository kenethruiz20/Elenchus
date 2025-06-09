'use client';

import React from 'react';
import { Settings, Share, BarChart3, User } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="h-14 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-4">
      {/* Left side - Title */}
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-semibold text-sm">📓</span>
        </div>
        <h1 className="text-lg font-medium text-slate-100">Untitled notebook</h1>
      </div>

      {/* Right side - Controls */}
      <div className="flex items-center space-x-2">
        <button className="flex items-center space-x-2 px-3 py-1.5 text-sm text-slate-300 hover:text-slate-100 hover:bg-slate-700 rounded-md transition-colors">
          <BarChart3 className="w-4 h-4" />
          <span>Analytics</span>
        </button>
        
        <button className="flex items-center space-x-2 px-3 py-1.5 text-sm text-slate-300 hover:text-slate-100 hover:bg-slate-700 rounded-md transition-colors">
          <Share className="w-4 h-4" />
          <span>Share</span>
        </button>
        
        <button className="p-1.5 text-slate-300 hover:text-slate-100 hover:bg-slate-700 rounded-md transition-colors">
          <Settings className="w-5 h-5" />
        </button>
        
        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center ml-2">
          <User className="w-4 h-4 text-white" />
        </div>
      </div>
    </header>
  );
};

export default Header; 