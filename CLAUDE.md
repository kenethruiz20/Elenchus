# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Elenchus is a hybrid legal AI assistant application consisting of:
- **Backend**: Python Chainlit application with Google Gemini AI integration
- **Frontend**: Next.js 14 NotebookLM replica UI (React + TypeScript)
- **Deployment**: Containerized for Google Cloud Run

## Common Development Commands

### Frontend (Next.js)
```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run linting
npm run lint
```

### Backend (Python/Chainlit)
```bash
# Run the Chainlit application
chainlit run app.py

# Deploy to Google Cloud Run
./deploy.sh
```

### Docker
```bash
# Build container
docker build -t legal-assistant .

# Run container locally
docker run -p 8000:8000 legal-assistant
```

## High-Level Architecture

### Frontend Structure
The frontend replicates Google NotebookLM's three-panel layout:
- **SourcesPanel** (components/SourcesPanel.tsx): Left panel for file management
- **ChatPanel** (components/ChatPanel.tsx): Center panel for AI chat interface  
- **StudioPanel** (components/StudioPanel.tsx): Right panel for notes and audio generation
- **State Management**: Zustand store (store/useStore.ts) manages global state for sources, messages, and notes

### Backend Architecture
The Chainlit backend (app.py) provides:
- Google Gemini AI integration via LangChain
- OAuth authentication (Google)
- Literal AI integration for conversation monitoring
- FastAPI endpoint at `/chat` for programmatic access
- Session management and message streaming

### Integration Points
Currently, the frontend and backend are separate applications. To integrate:
1. Frontend should call the backend's `/chat` endpoint instead of mock responses
2. Configure CORS in the backend to allow frontend requests
3. Update frontend API calls to use the deployed Cloud Run URL

## Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=          # Google Gemini API key
LITERAL_API_KEY=         # Literal AI monitoring
CHAINLIT_AUTH_SECRET=    # Session security
OAUTH_GOOGLE_CLIENT_ID=  # Google OAuth
OAUTH_GOOGLE_CLIENT_SECRET= # Google OAuth
CHAINLIT_URL=            # Public URL after deployment
```

### Frontend
No environment variables required for current implementation.

## Deployment

The application deploys to Google Cloud Run (project: legalai-462213):
1. GitHub Actions workflow triggers on push to main
2. Builds Docker image and pushes to Artifact Registry
3. Deploys to Cloud Run with environment variables from GitHub Secrets
4. See DEPLOYMENT.md for detailed setup instructions

## Key Considerations

1. **Type Safety**: The frontend uses TypeScript with strict mode. Ensure all new components have proper type definitions.

2. **State Management**: Use the Zustand store for global state. Component-level state with useState for local UI state only.

3. **Styling**: Tailwind CSS with dark theme. Follow existing color palette and spacing conventions.

4. **AI Integration**: The backend uses Google Gemini 1.5 Flash. Consider rate limits and response streaming for optimal UX.

5. **Authentication**: OAuth is configured but optional. Enable by setting CHAINLIT_AUTH_SECRET and OAuth credentials.

6. **File Handling**: Frontend accepts PDF, DOC, DOCX, and TXT files. Backend would need file parsing libraries to process content.

## Testing Approach

No test framework is currently configured. To add testing:
- Frontend: Consider Jest + React Testing Library
- Backend: Use pytest for Python testing
- Check package.json or requirements.txt before assuming test dependencies