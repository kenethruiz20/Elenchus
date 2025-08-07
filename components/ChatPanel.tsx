'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, Paperclip, Mic, ChevronRight, FileText, ChevronLeft, Settings, Lightbulb, Scale, FileCheck, Search, BookOpen, MessageCircle } from 'lucide-react';
import { useStore } from '../store/useStore';
import { getApiUrl, config } from '../lib/config';

interface ChatPanelProps {
  sourcesPanelState?: 'normal' | 'expanded' | 'collapsed';
  onExpandSources?: () => void;
  studioPanelState?: 'normal' | 'collapsed';
  onExpandStudio?: () => void;
  onEnsureSession: (actionType: 'source' | 'message' | 'note', title?: string) => string;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ sourcesPanelState, onExpandSources, studioPanelState, onExpandStudio, onEnsureSession }) => {
  const { 
    sources, 
    chatMessages, 
    addChatMessage, 
    addSource,
    isChatInputFocused,
    setIsChatInputFocused 
  } = useStore();
  
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (inputValue.trim()) {
      // Ensure session exists before sending message
      onEnsureSession('message');
      
      addChatMessage(inputValue.trim(), true);
      const userMessage = inputValue.trim();
      setInputValue('');

      try {
        setIsLoading(true);
        // Call the backend chat endpoint
        const response = await fetch(getApiUrl(config.api.endpoints.chat), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            content: userMessage,
            session_id: sessionId 
          }),
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        
        // Store session ID from response
        if (data.session_id && !sessionId) {
          setSessionId(data.session_id);
        }
        
        addChatMessage(data.content || 'No response from AI assistant.', false);
      } catch (error) {
        console.error('Chat error:', error);
        addChatMessage('Error connecting to AI assistant.', false);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      Array.from(files).forEach(file => {
        const fileType = file.type;
        let sourceType: 'pdf' | 'doc' | 'txt' | 'url' = 'txt';
        
        if (fileType.includes('pdf')) sourceType = 'pdf';
        else if (fileType.includes('document') || fileType.includes('word')) sourceType = 'doc';
        
        addSource({
          name: file.name,
          type: sourceType,
          uploadDate: new Date(),
          size: file.size
        });
      });
    }
    // Reset the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (sources.length === 0 && chatMessages.length === 0) {
    return (
      <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-900">
        {/* Main Content Area */}
        <div className="flex-1 flex flex-col items-center justify-center px-8">
          {/* Purple gradient circle */}
          <div className="w-20 h-20 mx-auto mb-8 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full shadow-lg opacity-80"></div>
          
          {/* Greeting */}
          <h1 className="text-3xl font-medium text-gray-900 dark:text-gray-100 mb-2">
            Good Afternoon, Counselor
          </h1>
          <h2 className="text-xl text-gray-600 dark:text-slate-400 mb-8">
            What's on <span className="text-purple-500">your legal mind?</span>
          </h2>
          
          {/* Research Assistant Info */}
          <div className="flex items-start space-x-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-8 max-w-md">
            <Lightbulb className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="text-blue-900 dark:text-blue-100 font-medium mb-1">Research Assistant Available</p>
              <p className="text-blue-700 dark:text-blue-300">Upload legal documents to activate advanced case analysis, precedent research, and legal writing assistance.</p>
            </div>
          </div>
        </div>
        
        {/* Input Area */}
        <div className="border-t border-gray-200 dark:border-slate-700 p-4">
          <div className="max-w-4xl mx-auto">
            {/* Quick Actions */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              <button className="flex flex-col items-center space-y-2 p-3 rounded-lg bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors text-center">
                <Scale className="w-5 h-5 text-gray-600 dark:text-slate-400" />
                <span className="text-xs text-gray-600 dark:text-slate-400">Draft legal brief</span>
              </button>
              <button className="flex flex-col items-center space-y-2 p-3 rounded-lg bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors text-center">
                <Search className="w-5 h-5 text-gray-600 dark:text-slate-400" />
                <span className="text-xs text-gray-600 dark:text-slate-400">Research case law</span>
              </button>
              <button className="flex flex-col items-center space-y-2 p-3 rounded-lg bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors text-center">
                <FileCheck className="w-5 h-5 text-gray-600 dark:text-slate-400" />
                <span className="text-xs text-gray-600 dark:text-slate-400">Review contract</span>
              </button>
              <button className="flex flex-col items-center space-y-2 p-3 rounded-lg bg-gray-50 dark:bg-slate-800 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors text-center">
                <BookOpen className="w-5 h-5 text-gray-600 dark:text-slate-400" />
                <span className="text-xs text-gray-600 dark:text-slate-400">Analyze statute</span>
              </button>
            </div>
            
            {/* Chat Input */}
            <div className="relative">
              <div className="flex items-end space-x-2">
                <div className="flex-1 relative">
                  <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    onFocus={() => setIsChatInputFocused(true)}
                    onBlur={() => setIsChatInputFocused(false)}
                    placeholder="Ask a legal question or make a request..."
                    className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-2xl px-4 py-3 pr-20 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32"
                    rows={1}
                    style={{ minHeight: '48px' }}
                  />
                  
                  {/* Attachment and Upload Buttons */}
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="p-1 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-colors"
                      title="Upload documents"
                    >
                      <Paperclip className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => fileInputRef.current?.click()}
                      className="p-1 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-colors"
                      title="Add sources"
                    >
                      <Upload className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Voice Button */}
                <button
                  onMouseDown={() => setIsListening(true)}
                  onMouseUp={() => setIsListening(false)}
                  onMouseLeave={() => setIsListening(false)}
                  className={`p-3 rounded-full transition-colors ${
                    isListening 
                      ? 'bg-red-600 text-white' 
                      : 'bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200'
                  }`}
                >
                  <Mic className="w-5 h-5" />
                </button>
                
                {/* Send Button */}
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim()}
                  className={`p-3 rounded-full transition-colors ${
                    inputValue.trim()
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 dark:bg-slate-800 text-gray-400 dark:text-slate-600 cursor-not-allowed'
                  }`}
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              
              {/* Helper text */}
              <div className="flex items-center justify-center space-x-2 text-xs text-gray-500 dark:text-slate-500 mt-3">
                <span>Elenchus Legal AI can analyze cases, draft documents, and research precedents</span>
              </div>
              
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-900 relative">
      {/* Floating Sources Expand Button */}
      {sourcesPanelState === 'collapsed' && onExpandSources && (
        <button
          onClick={onExpandSources}
          className="absolute top-4 left-4 z-10 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-2 shadow-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors group"
          title="Show Sources"
        >
          <div className="flex items-center space-x-2">
            <ChevronRight className="w-4 h-4 text-gray-600 dark:text-slate-400" />
            <FileText className="w-4 h-4 text-gray-600 dark:text-slate-400" />
            <span className="text-sm text-gray-600 dark:text-slate-400 hidden group-hover:block">
              Sources
            </span>
          </div>
        </button>
      )}

      {/* Floating Studio Expand Button */}
      {studioPanelState === 'collapsed' && onExpandStudio && (
        <button
          onClick={onExpandStudio}
          className="absolute top-4 right-4 z-10 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-2 shadow-lg hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors group"
          title="Show Studio"
        >
          <div className="flex items-center space-x-2">
            <Settings className="w-4 h-4 text-gray-600 dark:text-slate-400" />
            <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-slate-400" />
            <span className="text-sm text-gray-600 dark:text-slate-400 hidden group-hover:block">
              Studio
            </span>
          </div>
        </button>
      )}
      
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {chatMessages.map((message) => (
            <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] ${
                message.isUser 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-50 dark:bg-slate-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-slate-600'
              } rounded-2xl px-4 py-3`}>
                <p className="text-sm leading-relaxed">{message.content}</p>
              </div>
            </div>
          ))}
          
          {/* Loading Animation */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="ai-thinking-container flex items-center space-x-2 bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-2xl px-4 py-3">
                <div className="flex space-x-1">
                  <div className="ai-thinking-orb ai-thinking-orb-1"></div>
                  <div className="ai-thinking-orb ai-thinking-orb-2"></div>
                  <div className="ai-thinking-orb ai-thinking-orb-3"></div>
                </div>
                <span className="text-sm text-gray-500 dark:text-slate-400 ml-2">Elenchus is thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-slate-700 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-slate-500 mb-3">
            <span>Elenchus...</span>
            <span>•</span>
            <span>{sources.length} sources</span>
          </div>
          
          <div className="relative">
            <div className="flex items-end space-x-2">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  onFocus={() => setIsChatInputFocused(true)}
                  onBlur={() => setIsChatInputFocused(false)}
                  placeholder="Ask me anything about your sources..."
                  className="w-full bg-gray-50 dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-2xl px-4 py-3 pr-12 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent max-h-32"
                  rows={1}
                  style={{ minHeight: '48px' }}
                />
                
                {/* Attachment Button */}
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-colors">
                  <Paperclip className="w-4 h-4" />
                </button>
              </div>
              
              {/* Voice Button */}
              <button
                onMouseDown={() => setIsListening(true)}
                onMouseUp={() => setIsListening(false)}
                onMouseLeave={() => setIsListening(false)}
                className={`p-3 rounded-full transition-colors ${
                  isListening 
                    ? 'bg-red-600 text-white' 
                    : 'bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200'
                }`}
              >
                <Mic className="w-5 h-5" />
              </button>
              
              {/* Send Button */}
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim()}
                className={`p-3 rounded-full transition-colors ${
                  inputValue.trim()
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-100 dark:bg-slate-800 text-gray-400 dark:text-slate-600 cursor-not-allowed'
                }`}
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            
            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPanel; 