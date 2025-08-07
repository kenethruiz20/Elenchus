# Langfuse Integration Technical Specification
## Legal Research Assistant - Elenchus

### Executive Summary
This document outlines the technical implementation plan for integrating Langfuse observability and analytics into the Elenchus legal research assistant application. Langfuse will provide comprehensive traceability for user sessions, message flows, and model consumption metrics.

---

## 1. Architecture Overview

### 1.1 Current State
- **Frontend**: Next.js 14 application with ChatPanel component handling user interactions
- **Backend**: Python Chainlit application (separate, currently at localhost:8000)
- **State Management**: Zustand store managing sources, messages, and notes
- **API Communication**: REST endpoint at `/api/chat`

### 1.2 Target State with Langfuse
```
┌─────────────────────────────────────────────────┐
│                   User Browser                   │
│  ┌─────────────────────────────────────────┐   │
│  │         Next.js Frontend                 │   │
│  │  ┌───────────────────────────────┐      │   │
│  │  │     ChatPanel.tsx             │      │   │
│  │  │  + Langfuse Client SDK        │      │   │
│  │  │  + Session Management         │      │   │
│  │  │  + Trace Instrumentation      │      │   │
│  │  └───────────────────────────────┘      │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │    API Gateway/Proxy     │
         │  + Request Correlation   │
         └──────────────────────────┘
                        │
         ┌──────────────┴───────────────┐
         ▼                              ▼
┌─────────────────┐          ┌─────────────────┐
│  Chainlit Backend│          │ Langfuse Server │
│  + LLM Gateway   │          │  (Self-Hosted)  │
│  + Session Mgmt  │          │  + PostgreSQL   │
│                  │◄─────────┤  + Analytics    │
└─────────────────┘          └─────────────────┘
```

---

## 2. Langfuse Self-Hosting Setup

### 2.1 Deployment Options

#### Option A: Docker Compose (Recommended for Development)
```yaml
# docker-compose.langfuse.yml
version: '3.8'

services:
  langfuse-postgres:
    image: postgres:15-alpine
    container_name: langfuse-postgres
    environment:
      POSTGRES_USER: langfuse
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: langfuse
    volumes:
      - langfuse-postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - langfuse-network

  langfuse-server:
    image: langfuse/langfuse:latest
    container_name: langfuse-server
    depends_on:
      - langfuse-postgres
    environment:
      DATABASE_URL: postgresql://langfuse:${POSTGRES_PASSWORD}@langfuse-postgres:5432/langfuse
      NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}
      NEXTAUTH_URL: ${LANGFUSE_PUBLIC_URL}
      TELEMETRY_ENABLED: false
      LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES: true
      # Authentication providers (optional)
      AUTH_GOOGLE_CLIENT_ID: ${AUTH_GOOGLE_CLIENT_ID}
      AUTH_GOOGLE_CLIENT_SECRET: ${AUTH_GOOGLE_CLIENT_SECRET}
    ports:
      - "3001:3000"
    networks:
      - langfuse-network
    restart: unless-stopped

networks:
  langfuse-network:
    driver: bridge

volumes:
  langfuse-postgres-data:
```

#### Option B: Google Cloud Run Deployment (Production)
```yaml
# langfuse-cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: langfuse-server
  namespace: default
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cloudsql-instances: ${PROJECT_ID}:${REGION}:langfuse-postgres
    spec:
      containers:
      - image: langfuse/langfuse:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: langfuse-db-url
              key: url
        - name: NEXTAUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: langfuse-auth
              key: secret
        - name: NEXTAUTH_URL
          value: https://langfuse.yourdomain.com
        resources:
          limits:
            memory: 2Gi
            cpu: "2"
```

### 2.2 Initial Setup Steps

1. **Environment Variables Configuration**
```bash
# .env.langfuse
POSTGRES_PASSWORD=secure_password_here
NEXTAUTH_SECRET=$(openssl rand -base64 32)
LANGFUSE_PUBLIC_URL=http://localhost:3001
AUTH_GOOGLE_CLIENT_ID=your_google_client_id
AUTH_GOOGLE_CLIENT_SECRET=your_google_client_secret
```

2. **Deploy Langfuse**
```bash
# Development
docker-compose -f docker-compose.langfuse.yml up -d

# Wait for initialization
sleep 30

# Verify deployment
curl http://localhost:3001/api/public/health
```

3. **Create API Credentials**
- Navigate to http://localhost:3001
- Sign up/Login with Google OAuth
- Go to Settings → API Keys
- Create new API key pair:
  - Public Key: `pk_lf_...`
  - Secret Key: `sk_lf_...`

---

## 3. Frontend Integration Implementation

### 3.1 Dependencies Installation
```json
{
  "dependencies": {
    "langfuse": "^3.0.0",
    "@langfuse/react": "^3.0.0"
  }
}
```

### 3.2 Langfuse Client Configuration

#### Create Langfuse Provider (`lib/langfuse.ts`)
```typescript
import { Langfuse } from 'langfuse';

export const langfuseClient = new Langfuse({
  publicKey: process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY!,
  secretKey: process.env.LANGFUSE_SECRET_KEY!, // Only for server-side
  baseUrl: process.env.NEXT_PUBLIC_LANGFUSE_URL || 'http://localhost:3001',
  release: process.env.NEXT_PUBLIC_APP_VERSION,
  flushAt: 1, // Flush immediately in development
  flushInterval: 10000, // Flush every 10 seconds
});

// Browser-safe client
export const createBrowserClient = () => {
  if (typeof window === 'undefined') return null;
  
  return new Langfuse({
    publicKey: process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY!,
    baseUrl: process.env.NEXT_PUBLIC_LANGFUSE_URL || 'http://localhost:3001',
  });
};
```

### 3.3 Enhanced ChatPanel Integration

#### Updated ChatPanel with Langfuse Tracing
```typescript
// components/ChatPanel.tsx (Enhanced sections)

import { useCallback, useEffect } from 'react';
import { createBrowserClient } from '../lib/langfuse';
import { v4 as uuidv4 } from 'uuid';

const ChatPanel: React.FC<ChatPanelProps> = ({ ... }) => {
  const langfuse = createBrowserClient();
  const [sessionId] = useState(() => uuidv4());
  const [traceId, setTraceId] = useState<string | null>(null);
  
  // Initialize session trace
  useEffect(() => {
    if (!langfuse) return;
    
    const trace = langfuse.trace({
      id: sessionId,
      name: 'legal-research-session',
      userId: getUserId(), // Implement user identification
      metadata: {
        app: 'elenchus',
        version: process.env.NEXT_PUBLIC_APP_VERSION,
        environment: process.env.NODE_ENV,
      },
      tags: ['legal-research', 'chat-interface'],
    });
    
    setTraceId(trace.id);
    
    return () => {
      langfuse.flush();
    };
  }, [sessionId]);
  
  const handleSendMessage = async () => {
    if (!inputValue.trim() || !langfuse) return;
    
    const messageId = uuidv4();
    const userMessage = inputValue.trim();
    
    // Start generation span
    const generation = langfuse.generation({
      name: 'chat-completion',
      traceId: traceId,
      startTime: new Date(),
      model: 'backend-model', // Will be updated from response
      modelParameters: {
        temperature: 0.7,
        maxTokens: 2000,
      },
      input: userMessage,
      metadata: {
        messageId,
        sourcesCount: sources.length,
        sessionDuration: Date.now() - sessionStartTime,
      },
    });
    
    addChatMessage(userMessage, true);
    setInputValue('');
    
    try {
      const startTime = Date.now();
      
      // Enhanced API call with trace headers
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Trace-Id': traceId || '',
          'X-Session-Id': sessionId,
          'X-Message-Id': messageId,
        },
        body: JSON.stringify({ 
          content: userMessage,
          sources: sources.map(s => s.id),
          context: {
            previousMessages: chatMessages.slice(-5), // Last 5 messages for context
          }
        }),
      });
      
      const data = await response.json();
      const latency = Date.now() - startTime;
      
      // Update generation with response
      generation.update({
        endTime: new Date(),
        output: data.content,
        usage: {
          promptTokens: data.usage?.prompt_tokens,
          completionTokens: data.usage?.completion_tokens,
          totalTokens: data.usage?.total_tokens,
        },
        model: data.model || 'unknown',
        metadata: {
          ...generation.metadata,
          latency,
          statusCode: response.status,
        },
      });
      
      // Score the generation based on response time
      if (latency < 1000) {
        generation.score({
          name: 'latency',
          value: 1,
          comment: 'Fast response',
        });
      } else if (latency < 3000) {
        generation.score({
          name: 'latency',
          value: 0.5,
          comment: 'Acceptable response time',
        });
      } else {
        generation.score({
          name: 'latency',
          value: 0,
          comment: 'Slow response',
        });
      }
      
      addChatMessage(data.content || 'No response from AI assistant.', false);
      
    } catch (error) {
      generation.update({
        endTime: new Date(),
        statusMessage: `Error: ${error.message}`,
        level: 'ERROR',
      });
      
      addChatMessage('Error connecting to AI assistant.', false);
    } finally {
      generation.end();
    }
  };
  
  // Track user feedback
  const handleMessageFeedback = (messageId: string, score: number) => {
    if (!langfuse) return;
    
    langfuse.score({
      traceId: traceId,
      name: 'user-feedback',
      value: score,
      dataType: 'NUMERIC',
      comment: `User rated message ${messageId}`,
    });
  };
  
  // Track file uploads
  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || !langfuse) return;
    
    Array.from(files).forEach(file => {
      // Existing file upload logic...
      
      // Track file upload event
      langfuse.event({
        traceId: traceId,
        name: 'file-upload',
        input: {
          fileName: file.name,
          fileType: file.type,
          fileSize: file.size,
        },
        metadata: {
          timestamp: new Date().toISOString(),
        },
      });
    });
  };
  
  // ... rest of component
};
```

### 3.4 Session Management Enhancement

#### Create Session Context (`contexts/SessionContext.tsx`)
```typescript
import React, { createContext, useContext, useEffect, useState } from 'react';
import { createBrowserClient } from '../lib/langfuse';

interface SessionContextType {
  sessionId: string;
  userId: string | null;
  startTime: Date;
  endSession: () => void;
  trackEvent: (name: string, data: any) => void;
}

const SessionContext = createContext<SessionContextType | null>(null);

export const SessionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sessionId] = useState(() => uuidv4());
  const [userId, setUserId] = useState<string | null>(null);
  const [startTime] = useState(new Date());
  const langfuse = createBrowserClient();
  
  useEffect(() => {
    // Initialize session
    if (langfuse) {
      langfuse.trace({
        id: sessionId,
        name: 'user-session',
        userId: userId,
        metadata: {
          startTime: startTime.toISOString(),
          userAgent: navigator.userAgent,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight,
          },
        },
      });
    }
    
    // Cleanup on unmount
    return () => {
      endSession();
    };
  }, []);
  
  const endSession = () => {
    if (langfuse) {
      const duration = Date.now() - startTime.getTime();
      
      langfuse.event({
        traceId: sessionId,
        name: 'session-end',
        metadata: {
          duration,
          endTime: new Date().toISOString(),
        },
      });
      
      langfuse.flush();
    }
  };
  
  const trackEvent = (name: string, data: any) => {
    if (langfuse) {
      langfuse.event({
        traceId: sessionId,
        name,
        input: data,
        timestamp: new Date(),
      });
    }
  };
  
  return (
    <SessionContext.Provider value={{
      sessionId,
      userId,
      startTime,
      endSession,
      trackEvent,
    }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
};
```

---

## 4. Backend Integration (Optional Enhancement)

### 4.1 Python Chainlit Integration
```python
# backend/langfuse_integration.py
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
import os
from functools import wraps

# Initialize Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://localhost:3001"),
)

def track_chainlit_message(func):
    """Decorator to track Chainlit messages with Langfuse"""
    @wraps(func)
    @observe()
    async def wrapper(*args, **kwargs):
        # Extract trace context from headers if available
        trace_id = kwargs.get('trace_id')
        session_id = kwargs.get('session_id')
        
        if trace_id:
            langfuse_context.update_current_trace(
                id=trace_id,
                session_id=session_id,
            )
        
        # Execute the original function
        result = await func(*args, **kwargs)
        
        # Track the generation
        langfuse_context.update_current_observation(
            output=result,
            metadata={
                "function": func.__name__,
                "session_id": session_id,
            }
        )
        
        return result
    
    return wrapper

# Enhanced Chainlit endpoint
@track_chainlit_message
async def handle_chat_message(content: str, **context):
    """Process chat message with Langfuse tracking"""
    # Your existing chat logic here
    pass
```

---

## 5. Metrics and Observability

### 5.1 Key Metrics to Track

#### User Engagement Metrics
- **Session Duration**: Time spent per session
- **Messages per Session**: Average message count
- **Source Upload Rate**: Files uploaded per session
- **Feature Usage**: Which features are most used

#### Performance Metrics
- **Response Latency**: Time to generate AI responses
- **Token Usage**: Prompt and completion tokens per request
- **Error Rate**: Failed API calls percentage
- **Model Performance**: Accuracy scores and user feedback

#### Business Metrics
- **User Retention**: Returning users over time
- **Query Complexity**: Average query length and type
- **Document Processing**: Types and sizes of documents analyzed
- **Peak Usage Times**: When the system is most active

### 5.2 Custom Dashboards

#### Langfuse Dashboard Configuration
```sql
-- Example custom queries for Langfuse PostgreSQL

-- Daily Active Users
SELECT 
  DATE(created_at) as date,
  COUNT(DISTINCT user_id) as daily_active_users
FROM traces
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Average Response Time by Model
SELECT 
  model,
  AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_response_time_seconds,
  COUNT(*) as request_count
FROM generations
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY model;

-- Token Usage Trends
SELECT 
  DATE(created_at) as date,
  SUM(prompt_tokens) as total_prompt_tokens,
  SUM(completion_tokens) as total_completion_tokens,
  SUM(total_tokens) as total_tokens
FROM generations
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 6. Implementation Roadmap

### Phase 1: Infrastructure Setup (Week 1)
- [ ] Deploy Langfuse server (Docker or Cloud Run)
- [ ] Configure PostgreSQL database
- [ ] Set up authentication and API keys
- [ ] Test connectivity and basic functionality

### Phase 2: Frontend Integration (Week 2)
- [ ] Install Langfuse SDK dependencies
- [ ] Implement session management
- [ ] Add trace instrumentation to ChatPanel
- [ ] Implement event tracking for user actions
- [ ] Add error handling and retry logic

### Phase 3: Enhanced Tracking (Week 3)
- [ ] Implement user feedback collection
- [ ] Add performance scoring logic
- [ ] Create custom event types for legal research
- [ ] Implement source document tracking
- [ ] Add metadata enrichment

### Phase 4: Backend Integration (Week 4)
- [ ] Integrate Langfuse with Python backend
- [ ] Implement trace context propagation
- [ ] Add model usage tracking
- [ ] Implement cost calculation logic

### Phase 5: Analytics and Optimization (Week 5)
- [ ] Create custom dashboards
- [ ] Set up alerting for anomalies
- [ ] Implement A/B testing framework
- [ ] Create performance optimization reports
- [ ] Document best practices

---

## 7. Security Considerations

### 7.1 Data Privacy
- **PII Handling**: Implement data masking for sensitive legal information
- **Data Retention**: Configure appropriate retention policies (e.g., 90 days)
- **Encryption**: Enable TLS for all Langfuse communications
- **Access Control**: Implement role-based access to Langfuse dashboard

### 7.2 API Security
```typescript
// Secure API key handling
const langfuseConfig = {
  publicKey: process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY!,
  // Never expose secret key to client
  secretKey: process.env.NODE_ENV === 'server' 
    ? process.env.LANGFUSE_SECRET_KEY 
    : undefined,
  baseUrl: process.env.NEXT_PUBLIC_LANGFUSE_URL,
};
```

### 7.3 Compliance
- **GDPR**: Implement user consent and data deletion capabilities
- **Legal Ethics**: Ensure client confidentiality in logged data
- **Audit Trail**: Maintain immutable logs for compliance

---

## 8. Testing Strategy

### 8.1 Unit Tests
```typescript
// __tests__/langfuse.test.ts
import { createBrowserClient } from '../lib/langfuse';

describe('Langfuse Integration', () => {
  it('should initialize client with correct config', () => {
    const client = createBrowserClient();
    expect(client).toBeDefined();
    expect(client.publicKey).toBe(process.env.NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY);
  });
  
  it('should track events without errors', async () => {
    const client = createBrowserClient();
    const result = await client.event({
      name: 'test-event',
      input: { test: true },
    });
    expect(result).toBeDefined();
  });
});
```

### 8.2 Integration Tests
```typescript
// __tests__/chat-integration.test.ts
describe('Chat Panel with Langfuse', () => {
  it('should create trace on message send', async () => {
    // Mock Langfuse client
    const mockTrace = jest.fn();
    
    // Render ChatPanel
    // Send message
    // Verify trace was called
    expect(mockTrace).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'chat-completion',
      })
    );
  });
});
```

---

## 9. Monitoring and Alerts

### 9.1 Key Alerts to Configure
```yaml
# alerts.yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 5%
    window: 5m
    action: notify_slack
    
  - name: slow_response_time
    condition: p95_latency > 3000ms
    window: 10m
    action: notify_pagerduty
    
  - name: token_usage_spike
    condition: token_usage > 150% of average
    window: 1h
    action: notify_email
```

### 9.2 Health Checks
```typescript
// api/health/langfuse.ts
export async function GET() {
  try {
    const client = createBrowserClient();
    await client.health();
    
    return Response.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return Response.json({
      status: 'unhealthy',
      error: error.message,
    }, { status: 503 });
  }
}
```

---

## 10. Cost Estimation

### 10.1 Self-Hosted Infrastructure Costs
| Component | Specification | Monthly Cost (Est.) |
|-----------|--------------|---------------------|
| PostgreSQL Database | 2 vCPU, 4GB RAM, 100GB SSD | $50-100 |
| Langfuse Server | 2 vCPU, 4GB RAM | $40-80 |
| Load Balancer | Standard | $20 |
| Storage (Backups) | 500GB | $10 |
| **Total** | | **$120-210/month** |

### 10.2 Token Tracking for Cost Management
```typescript
// utils/cost-calculator.ts
const MODEL_COSTS = {
  'gpt-4': { prompt: 0.03, completion: 0.06 }, // per 1K tokens
  'gpt-3.5-turbo': { prompt: 0.001, completion: 0.002 },
  'gemini-1.5-flash': { prompt: 0.00035, completion: 0.0007 },
};

export function calculateCost(usage: TokenUsage, model: string) {
  const costs = MODEL_COSTS[model] || { prompt: 0, completion: 0 };
  
  const promptCost = (usage.promptTokens / 1000) * costs.prompt;
  const completionCost = (usage.completionTokens / 1000) * costs.completion;
  
  return {
    promptCost,
    completionCost,
    totalCost: promptCost + completionCost,
  };
}
```

---

## 11. Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Traces not appearing in Langfuse dashboard
```typescript
// Debug checklist:
1. Verify API keys are correct
2. Check network connectivity to Langfuse server
3. Ensure flush() is called
4. Check browser console for errors
5. Verify CORS settings if self-hosted

// Debug code:
langfuse.debug = true; // Enable debug logging
```

#### Issue: High latency in trace submission
```typescript
// Optimize batching:
const langfuse = new Langfuse({
  // ... config
  flushAt: 20, // Batch 20 events
  flushInterval: 30000, // Flush every 30 seconds
});
```

#### Issue: Missing context between frontend and backend
```typescript
// Ensure headers are propagated:
headers: {
  'X-Trace-Id': traceId,
  'X-Session-Id': sessionId,
  'X-Parent-Span-Id': parentSpanId,
}
```

---

## 12. References and Resources

### Documentation
- [Langfuse Official Docs](https://langfuse.com/docs)
- [Langfuse JS/TS SDK](https://langfuse.com/docs/sdk/typescript)
- [Self-Hosting Guide](https://langfuse.com/docs/deployment/self-host)
- [Langfuse Tracing Concepts](https://langfuse.com/docs/tracing)

### Example Implementations
- [Next.js + Langfuse Example](https://github.com/langfuse/langfuse-js/tree/main/examples/nextjs)
- [Python Integration Examples](https://github.com/langfuse/langfuse-python/tree/main/examples)

### Community Resources
- [Langfuse Discord](https://discord.gg/langfuse)
- [GitHub Issues](https://github.com/langfuse/langfuse/issues)

---

## Appendix A: Environment Variables

### Frontend (.env.local)
```bash
# Langfuse Configuration
NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY=pk_lf_xxxxx
NEXT_PUBLIC_LANGFUSE_URL=http://localhost:3001
NEXT_PUBLIC_APP_VERSION=1.0.0

# Server-only (for API routes)
LANGFUSE_SECRET_KEY=sk_lf_xxxxx
```

### Backend (.env)
```bash
# Existing variables
GOOGLE_API_KEY=xxx
LITERAL_API_KEY=xxx
CHAINLIT_AUTH_SECRET=xxx

# Add Langfuse
LANGFUSE_PUBLIC_KEY=pk_lf_xxxxx
LANGFUSE_SECRET_KEY=sk_lf_xxxxx
LANGFUSE_HOST=http://localhost:3001
```

### Docker Compose (.env.langfuse)
```bash
# Database
POSTGRES_PASSWORD=secure_password_here
POSTGRES_USER=langfuse
POSTGRES_DB=langfuse

# Langfuse Server
NEXTAUTH_SECRET=your_32_char_secret_here
NEXTAUTH_URL=http://localhost:3001
TELEMETRY_ENABLED=false

# OAuth (Optional)
AUTH_GOOGLE_CLIENT_ID=xxx
AUTH_GOOGLE_CLIENT_SECRET=xxx
```

---

## Appendix B: Quick Start Commands

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/elenchus.git
cd elenchus

# 2. Create specs directory and this file
mkdir -p specs
# Copy this spec to specs/langfuse_implementation.md

# 3. Setup Langfuse
cd infrastructure
docker-compose -f docker-compose.langfuse.yml up -d

# 4. Install frontend dependencies
cd ../
npm install langfuse @langfuse/react

# 5. Configure environment
cp .env.example .env.local
# Add Langfuse keys to .env.local

# 6. Run development servers
npm run dev  # Frontend
docker logs -f langfuse-server  # Monitor Langfuse

# 7. Access dashboards
# Frontend: http://localhost:3000
# Langfuse: http://localhost:3001
```

---

*Document Version: 1.0.0*  
*Last Updated: 2025-08-05*  
*Status: Ready for Implementation*