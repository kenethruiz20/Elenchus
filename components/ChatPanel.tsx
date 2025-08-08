'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, Paperclip, ChevronRight, FileText, ChevronLeft, Settings, Lightbulb, Scale, FileCheck, Search, BookOpen, Copy, Check, X } from 'lucide-react';
import { useStore } from '../store/useStore';
import { getApiUrl, config } from '../lib/config';

interface ChatPanelProps {
  sourcesPanelState?: 'normal' | 'expanded' | 'collapsed';
  onExpandSources?: () => void;
  studioPanelState?: 'normal' | 'collapsed';
  onExpandStudio?: () => void;
  onEnsureSession: (actionType: 'source' | 'message' | 'note', title?: string) => Promise<string> | string;
}

const ChatPanel: React.FC<ChatPanelProps> = ({ sourcesPanelState, onExpandSources, studioPanelState, onExpandStudio, onEnsureSession }) => {
  const { 
    sources, 
    chatMessages, 
    addChatMessage, 
    addSource,
    isChatInputFocused,
    setIsChatInputFocused,
    currentSessionId,
    getCurrentSession
  } = useStore();
  
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Load conversation history when session changes
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (currentSessionId) {
        const token = localStorage.getItem('access_token');
        if (token) {
          try {
            const response = await fetch(
              getApiUrl(`${config.api.endpoints.messages}/research/${currentSessionId}`),
              {
                headers: {
                  'Authorization': `Bearer ${token}`
                }
              }
            );
            
            if (response.ok) {
              const data = await response.json();
              // The messages are already loaded in the store from localStorage
              // This would be used to sync with backend if needed
              console.log('Conversation loaded from backend:', data);
            }
          } catch (error) {
            console.error('Failed to load conversation history:', error);
          }
        }
      }
    };

    loadConversationHistory();
  }, [currentSessionId]);

  const handleSendMessage = async () => {
    if (inputValue.trim() || attachedFiles.length > 0) {
      // Ensure session exists before sending message
      const sessionId = await onEnsureSession('message');
      
      // Prepare message with attachments
      const userMessage = inputValue.trim();
      const messageFiles = [...attachedFiles];
      
      // Clear input and attachments
      setInputValue('');
      setAttachedFiles([]);

      try {
        setIsLoading(true);
        
        // Add user message with files to local store immediately
        const userMessageObj = {
          content: userMessage,
          files: messageFiles.map(file => ({
            name: file.name,
            size: file.size,
            type: file.type
          }))
        };
        addChatMessage(JSON.stringify(userMessageObj), true);
        
        // Get auth token if available
        const token = localStorage.getItem('access_token');
        
        // Check if we should use the authenticated endpoint or the simple chat endpoint
        const useAuthenticatedEndpoint = token && (sessionId || currentSessionId);
        
        if (useAuthenticatedEndpoint) {
          // Use the session ID directly (it's already the backend ObjectId)
          const backendSessionId = sessionId || currentSessionId;
          
          // Create FormData for file upload
          const formData = new FormData();
          formData.append('message', userMessage);
          messageFiles.forEach((file, index) => {
            formData.append(`files`, file);
          });
          
          // Use the authenticated messages endpoint for proper context persistence
          const response = await fetch(getApiUrl(`${config.api.endpoints.messages}/research/${backendSessionId}/send`), {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
              // Don't set Content-Type for FormData - browser sets it with boundary
            },
            body: formData,
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Network response was not ok');
          }

          const data = await response.json();
          
          // Add assistant response
          addChatMessage(data.assistant_message.content || 'No response from AI assistant.', false);
        } else {
          // Fallback to simple chat endpoint (for non-authenticated or initial state)
          
          // Prepare conversation history for context
          const conversationHistory = chatMessages.map(msg => ({
            role: msg.isUser ? 'user' : 'assistant',
            content: msg.content
          }));
          
          // Add the new user message to history
          conversationHistory.push({
            role: 'user',
            content: userMessage
          });
          
          const response = await fetch(getApiUrl(config.api.endpoints.chat), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              content: userMessage,
              session_id: sessionId || currentSessionId,
              conversation_history: conversationHistory,
              context: {
                session_title: getCurrentSession()?.title,
                session_type: getCurrentSession()?.type,
                sources_count: sources.length
              }
            }),
          });

          if (!response.ok) {
            throw new Error('Network response was not ok');
          }

          const data = await response.json();
          addChatMessage(data.content || 'No response from AI assistant.', false);
        }
      } catch (error) {
        console.error('Chat error:', error);
        addChatMessage(`Error: ${error instanceof Error ? error.message : 'Failed to connect to AI assistant'}`, false);
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
      const newFiles = Array.from(files);
      setAttachedFiles(prev => [...prev, ...newFiles]);
    }
    // Reset the input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeAttachedFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const copyToClipboard = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const addFileAsSource = (file: File) => {
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
          {chatMessages.map((message) => {
            let messageContent = message.content;
            let attachedFiles = [];
            
            // Try to parse message content for files
            try {
              const parsedMessage = JSON.parse(message.content);
              if (parsedMessage.content !== undefined && parsedMessage.files) {
                messageContent = parsedMessage.content;
                attachedFiles = parsedMessage.files;
              }
            } catch {
              // Not JSON, use as is
            }
            
            return (
              <div key={message.id} className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] group relative ${
                  message.isUser 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-50 dark:bg-slate-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-slate-600'
                } rounded-2xl px-4 py-3`}>
                  
                  {/* Copy button for assistant messages */}
                  {!message.isUser && (
                    <button
                      onClick={() => copyToClipboard(messageContent, message.id)}
                      className="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-full p-1.5 shadow-sm hover:bg-gray-50 dark:hover:bg-slate-600 transition-all"
                      title="Copy message"
                    >
                      {copiedMessageId === message.id ? (
                        <Check className="w-3 h-3 text-green-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-gray-500 dark:text-slate-400" />
                      )}
                    </button>
                  )}
                  
                  {/* Attached files display */}
                  {attachedFiles.length > 0 && (
                    <div className="mb-3 space-y-2">
                      {attachedFiles.map((file: any, index: number) => (
                        <div key={index} className="flex items-center space-x-2 bg-white/10 rounded-lg p-2">
                          <FileText className="w-4 h-4 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium truncate">{file.name}</p>
                            <p className="text-xs opacity-75">{(file.size / 1024).toFixed(1)}KB</p>
                          </div>
                          {!message.isUser && (
                            <button
                              onClick={() => addFileAsSource(file)}
                              className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                            >
                              Include as Source
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Message content */}
                  {messageContent && (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{messageContent}</p>
                  )}
                </div>
              </div>
            );
          })}
          
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
          
          {/* Attached Files Preview */}
          {attachedFiles.length > 0 && (
            <div className="mb-3 space-y-2">
              <p className="text-xs text-gray-600 dark:text-slate-400">Attached files:</p>
              {attachedFiles.map((file, index) => (
                <div key={index} className="flex items-center space-x-2 bg-gray-100 dark:bg-slate-800 rounded-lg p-2">
                  <FileText className="w-4 h-4 text-gray-500 dark:text-slate-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium truncate text-gray-900 dark:text-gray-100">{file.name}</p>
                    <p className="text-xs text-gray-500 dark:text-slate-400">{(file.size / 1024).toFixed(1)}KB</p>
                  </div>
                  <button
                    onClick={() => removeAttachedFile(index)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    title="Remove file"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
          
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
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-500 dark:text-slate-400 hover:text-gray-700 dark:hover:text-slate-200 transition-colors"
                  title="Attach files"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
              </div>
              
              {/* Send Button */}
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() && attachedFiles.length === 0}
                className={`p-3 rounded-full transition-colors ${
                  (inputValue.trim() || attachedFiles.length > 0)
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