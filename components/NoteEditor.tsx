'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { X, Save, Maximize2 } from 'lucide-react';
import dynamic from 'next/dynamic';
import 'react-quill/dist/quill.snow.css';
import '../styles/quill-custom.css';

// Dynamically import ReactQuill to avoid SSR issues
const ReactQuill = dynamic(() => import('react-quill'), { ssr: false });

interface Note {
  id: string;
  title: string;
  content: string;
  type: 'study-guide' | 'briefing-doc' | 'faq' | 'timeline' | 'general';
  createdAt: Date;
  updatedAt: Date;
}

interface NoteEditorProps {
  isOpen: boolean;
  onClose: () => void;
  note?: Note | null;
  onSave: (title: string, content: string) => void;
}

const NoteEditor: React.FC<NoteEditorProps> = ({ isOpen, onClose, note, onSave }) => {
  const [title, setTitle] = useState(note?.title || '');
  const [content, setContent] = useState(note?.content || '');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    if (note) {
      setTitle(note.title);
      setContent(note.content);
    } else {
      setTitle('');
      setContent('');
    }
  }, [note]);

  const handleSave = () => {
    if (title.trim() || content.trim()) {
      onSave(title.trim() || 'Untitled Note', content);
      onClose();
    }
  };

  const quillModules = useMemo(() => ({
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      ['link', 'blockquote', 'code-block'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'align': [] }],
      ['clean']
    ],
  }), []);

  const quillFormats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'indent', 'link', 'blockquote',
    'code-block', 'color', 'background', 'align'
  ];

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 ${isFullscreen ? 'p-0' : ''}`}>
      <div className={`bg-gray-50 dark:bg-gray-800 rounded-lg shadow-xl flex flex-col ${
        isFullscreen ? 'w-full h-full rounded-none' : 'max-w-4xl w-full max-h-[90vh]'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            {note ? 'Edit Note' : 'New Note'}
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
            >
              <Maximize2 className="w-4 h-4" />
            </button>
            <button
              onClick={handleSave}
              className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-1"
            >
              <Save className="w-4 h-4" />
              <span>Save</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Title Input */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Note title..."
            className="w-full text-xl font-semibold bg-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none"
          />
        </div>

        {/* Content Editor */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full p-4 quill-editor-container">
            <ReactQuill
              theme="snow"
              value={content}
              onChange={setContent}
              modules={quillModules}
              formats={quillFormats}
              placeholder="Start writing your note..."
              style={{ height: isFullscreen ? 'calc(100vh - 300px)' : '400px' }}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {note && `Last edited: ${note.updatedAt.toLocaleString()}`}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-3 py-1 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Save Note
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NoteEditor;