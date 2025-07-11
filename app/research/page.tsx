'use client';

import React, { useState } from 'react';
import Header from '@/components/Header';
import SourcesPanel from '@/components/SourcesPanel';
import ChatPanel from '@/components/ChatPanel';
import StudioPanel from '@/components/StudioPanel';

export default function Home() {
  const [sourcesPanelState, setSourcesPanelState] = useState<'normal' | 'expanded' | 'collapsed'>('normal');

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-slate-900">
      {/* Header */}
      <Header />
      
      {/* Main Content - Three Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Sources */}
        <div className={`flex-shrink-0 border-r border-gray-200 dark:border-slate-700 transition-all duration-300 ease-in-out ${
          sourcesPanelState === 'collapsed' ? 'w-0 opacity-0' : 
          sourcesPanelState === 'expanded' ? 'w-96' : 'w-80'
        }`}>
          <SourcesPanel 
            panelState={sourcesPanelState}
            onPanelStateChange={setSourcesPanelState}
          />
        </div>
        
        {/* Center Panel - Chat */}
        <div className="flex-1 flex flex-col">
          <ChatPanel 
            sourcesPanelState={sourcesPanelState}
            onExpandSources={() => setSourcesPanelState('normal')}
          />
        </div>
        
        {/* Right Panel - Studio */}
        <div className="w-80 flex-shrink-0 border-l border-gray-200 dark:border-slate-700">
          <StudioPanel />
        </div>
      </div>
    </div>
  );
} 