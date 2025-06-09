import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';

export interface Source {
  id: string;
  name: string;
  type: 'pdf' | 'doc' | 'txt' | 'url';
  uploadDate: Date;
  size?: number;
}

export interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  type: 'study-guide' | 'briefing-doc' | 'faq' | 'timeline' | 'general';
  createdAt: Date;
  updatedAt: Date;
}

export interface StoreState {
  // Sources
  sources: Source[];
  addSource: (source: Omit<Source, 'id'>) => void;
  removeSource: (id: string) => void;
  
  // Chat
  chatMessages: ChatMessage[];
  addChatMessage: (content: string, isUser: boolean) => void;
  clearChat: () => void;
  
  // Notes
  notes: Note[];
  addNote: (note: Omit<Note, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateNote: (id: string, updates: Partial<Note>) => void;
  deleteNote: (id: string) => void;
  
  // UI State
  selectedNoteType: Note['type'] | null;
  setSelectedNoteType: (type: Note['type'] | null) => void;
  isChatInputFocused: boolean;
  setIsChatInputFocused: (focused: boolean) => void;
  leftPanelWidth: number;
  setLeftPanelWidth: (width: number) => void;
  rightPanelWidth: number;
  setRightPanelWidth: (width: number) => void;
}

export const useStore = create<StoreState>((set, get) => ({
  // Sources
  sources: [],
  addSource: (source) => set((state) => ({
    sources: [...state.sources, { ...source, id: uuidv4() }]
  })),
  removeSource: (id) => set((state) => ({
    sources: state.sources.filter(source => source.id !== id)
  })),
  
  // Chat
  chatMessages: [],
  addChatMessage: (content, isUser) => set((state) => ({
    chatMessages: [...state.chatMessages, {
      id: uuidv4(),
      content,
      isUser,
      timestamp: new Date()
    }]
  })),
  clearChat: () => set({ chatMessages: [] }),
  
  // Notes
  notes: [],
  addNote: (note) => set((state) => ({
    notes: [...state.notes, {
      ...note,
      id: uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date()
    }]
  })),
  updateNote: (id, updates) => set((state) => ({
    notes: state.notes.map(note => 
      note.id === id 
        ? { ...note, ...updates, updatedAt: new Date() }
        : note
    )
  })),
  deleteNote: (id) => set((state) => ({
    notes: state.notes.filter(note => note.id !== id)
  })),
  
  // UI State
  selectedNoteType: null,
  setSelectedNoteType: (type) => set({ selectedNoteType: type }),
  isChatInputFocused: false,
  setIsChatInputFocused: (focused) => set({ isChatInputFocused: focused }),
  leftPanelWidth: 320,
  setLeftPanelWidth: (width) => set({ leftPanelWidth: width }),
  rightPanelWidth: 320,
  setRightPanelWidth: (width) => set({ rightPanelWidth: width }),
})); 