'use client';

import React from 'react';
import Header from '@/components/Header';
import SourcesPanel from '@/components/SourcesPanel';
import ChatPanel from '@/components/ChatPanel';
import StudioPanel from '@/components/StudioPanel';

export default function Home() {
  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-slate-900">
      {/* Header */}
      <Header />
      
      {/* Main Content - Three Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Sources */}
        <div className="w-80 flex-shrink-0 border-r border-gray-200 dark:border-slate-700">
          <SourcesPanel />
        </div>
        
        {/* Center Panel - Chat */}
        <div className="flex-1 flex flex-col">
          <ChatPanel />
        </div>
        
        {/* Right Panel - Studio */}
        <div className="w-80 flex-shrink-0 border-l border-gray-200 dark:border-slate-700">
          <StudioPanel />
        </div>
      </div>
    </div>
  );
} 