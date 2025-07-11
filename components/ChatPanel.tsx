'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, Paperclip, Mic } from 'lucide-react';
import { useStore } from '../store/useStore';

const ChatPanel: React.FC = () => {
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
      addChatMessage(inputValue.trim(), true);
      const userMessage = inputValue.trim();
      setInputValue('');

      try {
        // Llama al backend de Chainlit (ajusta la URL si es necesario)
        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ content: userMessage }),
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        // Ajusta 'data.content' según la estructura de respuesta de tu backend
        addChatMessage(data.content || 'No response from AI assistant.', false);
      } catch (error) {
        addChatMessage('Error connecting to AI assistant.', false);
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
      <div className="h-full flex flex-col items-center justify-center bg-gray-50 dark:bg-slate-900">
        <div className="text-center max-w-md px-8">
          {/* Upload Icon */}
          <div className="w-24 h-24 mx-auto mb-8 bg-gray-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center">
            <Upload className="w-12 h-12 text-gray-400 dark:text-slate-400" />
          </div>
          
          {/* Main Text */}
          <h2 className="text-2xl font-medium text-gray-900 dark:text-gray-100 mb-4">
            Add a source to get started
          </h2>
          
          {/* Upload Button */}
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
          >
            <Upload className="w-5 h-5" />
            <span>Upload a source</span>
          </button>
          
          {/* Helper text */}
          <p className="text-sm text-gray-600 dark:text-slate-400 mt-6 leading-relaxed">
            Saved sources will appear here<br />
            Click Add source above to add PDFs, websites, text, videos, or audio files.<br />
            Or import a file directly from Google Drive.
          </p>
          
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
        
        {/* Bottom Input Area */}
        <div className="absolute bottom-0 left-0 right-0 p-4 bg-slate-900 border-t border-slate-700">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center space-x-2 text-xs text-slate-500 mb-3 justify-center">
              <span>Upload a source to get started</span>
              <span>•</span>
              <span>0 sources</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-slate-900">
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
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 dark:border-slate-700 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-slate-500 mb-3">
            <span>NotebookLM can be inaccurate, please double check its responses.</span>
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
                >
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