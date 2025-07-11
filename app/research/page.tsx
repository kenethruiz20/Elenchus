'use client';

import React from 'react';
import Header from '@/components/Header';
import SourcesPanel from '@/components/SourcesPanel';
import ChatPanel from '@/components/ChatPanel';
import StudioPanel from '@/components/StudioPanel';

export default function Home() {
  return (
    <div className="h-screen flex flex-col bg-slate-900 dark:bg-slate-900 bg-gray-50">
      {/* Header */}
      <Header />
      
      {/* Main Content - Three Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Sources */}
        <div className="w-80 flex-shrink-0 border-r border-slate-700 dark:border-slate-700 border-gray-200">
          <SourcesPanel />
        </div>
        
        {/* Center Panel - Chat */}
        <div className="flex-1 flex flex-col">
          <ChatPanel />
        </div>
        
        {/* Right Panel - Studio */}
        <div className="w-80 flex-shrink-0 border-l border-slate-700 dark:border-slate-700 border-gray-200">
          <StudioPanel />
        </div>
      </div>
    </div>
  );
} 