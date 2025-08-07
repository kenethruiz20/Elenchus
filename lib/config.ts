/**
 * Application Configuration
 */

export const config = {
  api: {
    baseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    endpoints: {
      auth: {
        register: '/api/v1/auth/register',
        login: '/api/v1/auth/login',
        logout: '/api/v1/auth/logout',
        refresh: '/api/v1/auth/refresh',
        profile: '/api/v1/auth/profile'
      },
      research: '/api/v1/research',
      sources: '/api/v1/sources',
      notes: '/api/v1/notes',
      messages: '/api/v1/messages',
      chat: '/api/chat'
    }
  },
  app: {
    name: 'Elenchus AI',
    version: '1.0.0'
  }
};

/**
 * Get full API endpoint URL
 */
export const getApiUrl = (endpoint: string): string => {
  return `${config.api.baseUrl}${endpoint}`;
};

/**
 * Common API configuration
 */
export const apiConfig = {
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false
};