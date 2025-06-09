'use client'

import React from 'react'

export default function Home() {
  return (
    <div className="h-screen flex flex-col bg-nb-bg">
      {/* Header */}
      <header className="h-16 bg-nb-bg border-b border-nb-border flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-nb-accent rounded-lg flex items-center justify-center">
            <div className="w-4 h-4 bg-white rounded-sm opacity-90"></div>
          </div>
          <h1 className="text-lg font-medium text-nb-text">NotebookLM Replica</h1>
        </div>
        <div className="flex items-center space-x-2">
          <button className="bg-nb-accent hover:bg-nb-accent-hover text-white px-4 py-2 rounded-lg font-medium transition-colors">
            Share
          </button>
          <div className="w-8 h-8 bg-nb-accent rounded-full flex items-center justify-center">
            <span className="text-white text-sm font-medium">U</span>
          </div>
        </div>
      </header>
      
      {/* Main Content - Three Panel Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sources Panel - Left */}
        <div className="w-80 bg-nb-bg border-r border-nb-border flex flex-col">
          <div className="p-4 border-b border-nb-border">
            <h2 className="text-lg font-semibold text-nb-text mb-4">Sources</h2>
            <button className="w-full bg-nb-bg-secondary hover:bg-nb-hover text-nb-text px-4 py-3 rounded-lg font-medium transition-colors border border-nb-border">
              + Add source
            </button>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-nb-bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-nb-text-muted text-2xl">📄</span>
              </div>
              <p className="text-nb-text-muted mb-2">No sources added yet</p>
              <p className="text-sm text-nb-text-muted">Upload PDFs, websites, text, or audio files</p>
            </div>
          </div>
        </div>
        
        {/* Chat Panel - Center */}
        <div className="flex-1 flex flex-col bg-nb-bg">
          <div className="p-4 border-b border-nb-border">
            <h2 className="text-lg font-semibold text-nb-text">Chat</h2>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-nb-accent rounded-full flex items-center justify-center mx-auto mb-6">
                <div className="w-6 h-6 bg-white rounded opacity-90"></div>
              </div>
              <h3 className="text-xl font-medium text-nb-text mb-2">
                What would you like to know?
              </h3>
              <p className="text-nb-text-muted mb-6">
                Ask me anything about your sources. I can help summarize, analyze, or answer questions.
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                <button className="bg-nb-bg-secondary hover:bg-nb-hover text-nb-text px-3 py-2 rounded-lg text-sm transition-colors border border-nb-border">
                  Summarize key points
                </button>
                <button className="bg-nb-bg-secondary hover:bg-nb-hover text-nb-text px-3 py-2 rounded-lg text-sm transition-colors border border-nb-border">
                  Create outline
                </button>
              </div>
            </div>
          </div>
        </div>
        
        {/* Studio Panel - Right */}
        <div className="w-80 bg-nb-bg border-l border-nb-border flex flex-col">
          <div className="p-4 border-b border-nb-border">
            <h2 className="text-lg font-semibold text-nb-text mb-4">Studio</h2>
            <div className="flex space-x-1 bg-nb-bg-secondary rounded-lg p-1">
              <button className="flex-1 px-3 py-2 rounded-md text-sm font-medium bg-nb-accent text-white">
                Audio Overview
              </button>
              <button className="flex-1 px-3 py-2 rounded-md text-sm font-medium text-nb-text-muted hover:text-nb-text">
                Notes
              </button>
            </div>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-nb-bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-nb-text-muted text-2xl">🎙️</span>
              </div>
              <h3 className="font-medium text-nb-text mb-2">Audio Overview</h3>
              <p className="text-sm text-nb-text-muted mb-4">
                Create an Audio Overview in more languages!
              </p>
              <div className="space-y-2">
                <div className="text-sm text-nb-text-muted">Deep Dive conversation</div>
                <div className="text-sm text-nb-text-muted">Two hosts</div>
              </div>
              <div className="mt-6 space-y-2">
                <button className="w-full bg-nb-bg-secondary hover:bg-nb-hover text-nb-text px-4 py-2 rounded-lg transition-colors border border-nb-border">
                  Customize
                </button>
                <button className="w-full bg-nb-accent hover:bg-nb-accent-hover text-white px-4 py-2 rounded-lg transition-colors">
                  Generate
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 