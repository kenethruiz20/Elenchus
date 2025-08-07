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

export interface ResearchSession {
  id: string;
  title: string;
  description?: string;
  type: 'case' | 'contract' | 'brief' | 'research';
  icon: string;
  createdAt: Date;
  updatedAt: Date;
  lastAccessed: Date;
  userId?: string;
  sources: Source[];
  chatMessages: ChatMessage[];
  notes: Note[];
  isActive: boolean;
}

export interface User {
  id: string;
  email: string;
  first_name?: string;
  last_name?: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface StoreState {
  // Authentication
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  checkAuth: () => void;
  
  // Research Sessions
  researchSessions: ResearchSession[];
  currentSessionId: string | null;
  createSession: (title: string, type: ResearchSession['type']) => string;
  updateSession: (id: string, updates: Partial<ResearchSession>) => void;
  deleteSession: (id: string) => void;
  setCurrentSession: (id: string | null) => void;
  getCurrentSession: () => ResearchSession | null;
  
  // Sources (session-scoped)
  sources: Source[];
  addSource: (source: Omit<Source, 'id'>) => void;
  removeSource: (id: string) => void;
  
  // Chat (session-scoped)
  chatMessages: ChatMessage[];
  addChatMessage: (content: string, isUser: boolean) => void;
  clearChat: () => void;
  
  // Notes (session-scoped)
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

const getTypeIcon = (type: ResearchSession['type']): string => {
  switch (type) {
    case 'case': return '⚖️';
    case 'contract': return '📑';
    case 'brief': return '📝';
    case 'research': return '📚';
    default: return '📄';
  }
};

export const useStore = create<StoreState>((set, get) => ({
  // Authentication
  user: null,
  accessToken: null,
  isAuthenticated: false,
  setAuth: (user, token) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ user, accessToken: token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('research_sessions');
    set({ 
      user: null, 
      accessToken: null, 
      isAuthenticated: false,
      researchSessions: [],
      currentSessionId: null,
      sources: [],
      chatMessages: [],
      notes: []
    });
  },
  checkAuth: () => {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ user, accessToken: token, isAuthenticated: true });
        
        // Load research sessions from localStorage
        const sessionsStr = localStorage.getItem('research_sessions');
        if (sessionsStr) {
          const sessions = JSON.parse(sessionsStr).map((session: any) => ({
            ...session,
            createdAt: new Date(session.createdAt),
            updatedAt: new Date(session.updatedAt),
            lastAccessed: new Date(session.lastAccessed),
            sources: session.sources.map((source: any) => ({
              ...source,
              uploadDate: new Date(source.uploadDate)
            })),
            chatMessages: session.chatMessages.map((msg: any) => ({
              ...msg,
              timestamp: new Date(msg.timestamp)
            })),
            notes: session.notes.map((note: any) => ({
              ...note,
              createdAt: new Date(note.createdAt),
              updatedAt: new Date(note.updatedAt)
            }))
          }));
          set({ researchSessions: sessions });
        }
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        localStorage.removeItem('research_sessions');
      }
    }
  },
  
  // Research Sessions
  researchSessions: [],
  currentSessionId: null,
  
  createSession: (title, type) => {
    const sessionId = uuidv4();
    const now = new Date();
    const newSession: ResearchSession = {
      id: sessionId,
      title,
      type,
      icon: getTypeIcon(type),
      createdAt: now,
      updatedAt: now,
      lastAccessed: now,
      userId: get().user?.id,
      sources: [],
      chatMessages: [],
      notes: [],
      isActive: true
    };
    
    set((state) => {
      const updatedSessions = [...state.researchSessions, newSession];
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      return { 
        researchSessions: updatedSessions,
        currentSessionId: sessionId,
        sources: [],
        chatMessages: [],
        notes: []
      };
    });
    
    return sessionId;
  },
  
  updateSession: (id, updates) => {
    set((state) => {
      const updatedSessions = state.researchSessions.map(session =>
        session.id === id 
          ? { ...session, ...updates, updatedAt: new Date() }
          : session
      );
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      return { researchSessions: updatedSessions };
    });
  },
  
  deleteSession: (id) => {
    set((state) => {
      const updatedSessions = state.researchSessions.filter(session => session.id !== id);
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      const newCurrentId = state.currentSessionId === id ? null : state.currentSessionId;
      return { 
        researchSessions: updatedSessions,
        currentSessionId: newCurrentId,
        ...(newCurrentId === null && { sources: [], chatMessages: [], notes: [] })
      };
    });
  },
  
  setCurrentSession: (id) => {
    const state = get();
    const session = id ? state.researchSessions.find(s => s.id === id) : null;
    
    if (session) {
      // Update last accessed time
      const updatedSessions = state.researchSessions.map(s =>
        s.id === id ? { ...s, lastAccessed: new Date() } : s
      );
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      
      set({
        researchSessions: updatedSessions,
        currentSessionId: id,
        sources: session.sources,
        chatMessages: session.chatMessages,
        notes: session.notes
      });
    } else {
      set({
        currentSessionId: null,
        sources: [],
        chatMessages: [],
        notes: []
      });
    }
  },
  
  getCurrentSession: () => {
    const state = get();
    return state.currentSessionId 
      ? state.researchSessions.find(s => s.id === state.currentSessionId) || null
      : null;
  },
  
  // Sources (session-scoped)
  sources: [],
  addSource: (source) => {
    const newSource = { ...source, id: uuidv4() };
    set((state) => {
      const updatedSources = [...state.sources, newSource];
      
      // Update current session
      if (state.currentSessionId) {
        const updatedSessions = state.researchSessions.map(session =>
          session.id === state.currentSessionId 
            ? { ...session, sources: updatedSources, updatedAt: new Date() }
            : session
        );
        localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
        return { sources: updatedSources, researchSessions: updatedSessions };
      }
      
      return { sources: updatedSources };
    });
  },
  
  removeSource: (id) => set((state) => {
    const updatedSources = state.sources.filter(source => source.id !== id);
    
    // Update current session
    if (state.currentSessionId) {
      const updatedSessions = state.researchSessions.map(session =>
        session.id === state.currentSessionId 
          ? { ...session, sources: updatedSources, updatedAt: new Date() }
          : session
      );
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      return { sources: updatedSources, researchSessions: updatedSessions };
    }
    
    return { sources: updatedSources };
  }),
  
  // Chat (session-scoped)
  chatMessages: [],
  addChatMessage: (content, isUser) => {
    const newMessage = {
      id: uuidv4(),
      content,
      isUser,
      timestamp: new Date()
    };
    
    set((state) => {
      const updatedMessages = [...state.chatMessages, newMessage];
      
      // Update current session
      if (state.currentSessionId) {
        const updatedSessions = state.researchSessions.map(session =>
          session.id === state.currentSessionId 
            ? { ...session, chatMessages: updatedMessages, updatedAt: new Date() }
            : session
        );
        localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
        return { chatMessages: updatedMessages, researchSessions: updatedSessions };
      }
      
      return { chatMessages: updatedMessages };
    });
  },
  
  clearChat: () => set((state) => {
    // Update current session
    if (state.currentSessionId) {
      const updatedSessions = state.researchSessions.map(session =>
        session.id === state.currentSessionId 
          ? { ...session, chatMessages: [], updatedAt: new Date() }
          : session
      );
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      return { chatMessages: [], researchSessions: updatedSessions };
    }
    
    return { chatMessages: [] };
  }),
  
  // Notes (session-scoped)
  notes: [],
  addNote: (note) => {
    const newNote = {
      ...note,
      id: uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date()
    };
    
    set((state) => {
      const updatedNotes = [...state.notes, newNote];
      
      // Update current session
      if (state.currentSessionId) {
        const updatedSessions = state.researchSessions.map(session =>
          session.id === state.currentSessionId 
            ? { ...session, notes: updatedNotes, updatedAt: new Date() }
            : session
        );
        localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
        return { notes: updatedNotes, researchSessions: updatedSessions };
      }
      
      return { notes: updatedNotes };
    });
  },
  
  updateNote: (id, updates) => set((state) => {
    const updatedNotes = state.notes.map(note => 
      note.id === id 
        ? { ...note, ...updates, updatedAt: new Date() }
        : note
    );
    
    // Update current session
    if (state.currentSessionId) {
      const updatedSessions = state.researchSessions.map(session =>
        session.id === state.currentSessionId 
          ? { ...session, notes: updatedNotes, updatedAt: new Date() }
          : session
      );
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      return { notes: updatedNotes, researchSessions: updatedSessions };
    }
    
    return { notes: updatedNotes };
  }),
  
  deleteNote: (id) => set((state) => {
    const updatedNotes = state.notes.filter(note => note.id !== id);
    
    // Update current session
    if (state.currentSessionId) {
      const updatedSessions = state.researchSessions.map(session =>
        session.id === state.currentSessionId 
          ? { ...session, notes: updatedNotes, updatedAt: new Date() }
          : session
      );
      localStorage.setItem('research_sessions', JSON.stringify(updatedSessions));
      return { notes: updatedNotes, researchSessions: updatedSessions };
    }
    
    return { notes: updatedNotes };
  }),
  
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