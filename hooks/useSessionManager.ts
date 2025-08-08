import { useEffect, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useStore } from '@/store/useStore';

export function useSessionManager() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { 
    currentSessionId, 
    getCurrentSession, 
    setCurrentSession, 
    createSession, 
    updateSession
  } = useStore();

  // Ensure session exists and is loaded
  useEffect(() => {
    const sessionId = searchParams.get('id');
    
    if (sessionId && sessionId !== currentSessionId) {
      // Load existing session from URL
      setCurrentSession(sessionId);
    } else if (!sessionId && !currentSessionId) {
      // No session in URL or store - create a default one but don't navigate yet
      // We'll wait for user interaction to create a proper session
    }
  }, [searchParams, currentSessionId, setCurrentSession]);

  // Create a session when user performs their first action
  const ensureSession = useCallback(
    async (actionType: 'source' | 'message' | 'note', title?: string) => {
      if (!currentSessionId) {
        const sessionTitle = title || getDefaultTitle(actionType);
        const sessionType = getSessionTypeFromAction(actionType);
        
        const sessionIdOrPromise = createSession(sessionTitle, sessionType);
        // Handle both Promise and string return types
        const newSessionId = typeof sessionIdOrPromise === 'object' && sessionIdOrPromise !== null && 'then' in sessionIdOrPromise
          ? await sessionIdOrPromise 
          : sessionIdOrPromise;
        
        // Update URL to include the session ID
        const currentUrl = window.location.pathname + window.location.search;
        const newUrl = `/research?id=${newSessionId}`;
        
        if (currentUrl !== newUrl) {
          router.replace(newUrl);
        }
        
        return newSessionId;
      }
      
      return currentSessionId;
    },
    [currentSessionId, createSession, router]
  );

  // Update session title based on user action
  const updateSessionTitle = useCallback(
    (newTitle: string) => {
      if (currentSessionId) {
        updateSession(currentSessionId, { title: newTitle });
      }
    },
    [currentSessionId, updateSession]
  );

  const currentSession = getCurrentSession();

  return {
    currentSession,
    currentSessionId,
    ensureSession,
    updateSessionTitle,
    setCurrentSession
  };
}

function getDefaultTitle(actionType: 'source' | 'message' | 'note'): string {
  const timestamp = new Date().toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
  
  switch (actionType) {
    case 'source':
      return `Document Analysis - ${timestamp}`;
    case 'message':
      return `Research Session - ${timestamp}`;
    case 'note':
      return `Legal Notes - ${timestamp}`;
    default:
      return `Research Session - ${timestamp}`;
  }
}

function getSessionTypeFromAction(actionType: 'source' | 'message' | 'note') {
  // Default to 'research' for now, but could be made smarter based on content
  return 'research' as const;
}