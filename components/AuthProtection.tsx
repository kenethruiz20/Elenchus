'use client';

import React, { useEffect, useState } from 'react';
import { useStore } from '@/store/useStore';
import AuthModal from '@/components/AuthModal';

interface AuthProtectionProps {
  children: React.ReactNode;
}

export default function AuthProtection({ children }: AuthProtectionProps) {
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const { user, isAuthenticated, checkAuth, setAuth } = useStore();

  useEffect(() => {
    // Check for existing auth on mount
    const initAuth = async () => {
      checkAuth();
      setIsLoading(false);
    };
    
    initAuth();
  }, [checkAuth]);

  useEffect(() => {
    // After loading is done, check if we need to show auth modal
    if (!isLoading && !isAuthenticated && !user) {
      setShowAuthModal(true);
    }
  }, [isLoading, isAuthenticated, user]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  // Show auth modal if not authenticated
  if (!isAuthenticated && !user) {
    return (
      <>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
          <div className="text-center max-w-md mx-auto p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Authentication Required
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Please sign in to access Elenchus AI and start your legal research.
            </p>
            <button
              onClick={() => setShowAuthModal(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Sign In
            </button>
          </div>
        </div>
        
        <AuthModal 
          isOpen={showAuthModal} 
          onClose={() => {
            // Only allow closing if user is authenticated
            if (isAuthenticated) {
              setShowAuthModal(false);
            }
          }}
          onSuccess={(userData, token) => {
            setAuth(userData, token);
            setShowAuthModal(false);
          }}
        />
      </>
    );
  }

  // User is authenticated, show the protected content
  return <>{children}</>;
}