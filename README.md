# Elenchus - Legal AI Assistant

A hybrid legal AI assistant application consisting of a modern frontend that replicates Google's NotebookLM interface and a powerful FastAPI backend with Google Gemini AI integration.

![NotebookLM Replica Screenshot](https://via.placeholder.com/800x400/1e293b/f8fafc?text=NotebookLM+Replica)

## 🚀 Features

### ✅ Fully Implemented
- **Three-Panel Layout**: Exact replica of Sources (left), Chat (center), and Studio (right) panels
- **Dark Theme**: Pixel-perfect recreation of NotebookLM's dark interface
- **File Upload System**: Upload PDFs, DOCs, and text files as sources
- **Interactive Chat Interface**: Real-time chat with AI-like responses
- **Notes Management**: Create study guides, briefing docs, FAQs, and timelines
- **Audio Overview Section**: Deep dive conversation settings with customization
- **Responsive Design**: Mobile-friendly with proper breakpoints
- **State Management**: Zustand for efficient global state handling
- **Modern UI Components**: Hover effects, transitions, and animations

### 🔄 Interactive Features
- **Source Management**: Add, view, and remove sources with file type detection
- **Chat Functionality**: Send messages, get AI responses, attach files
- **Note Creation**: Generate different types of notes with one click
- **Audio Customization**: Modal for customizing conversation style and language
- **Real-time Updates**: Live source count and chat message handling

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 + React 18 + TypeScript
- **Styling**: Tailwind CSS with custom dark theme
- **State Management**: Zustand
- **Icons**: Lucide React
- **UI Components**: Headless UI (for accessibility)
- **Development**: ESLint + TypeScript strict mode

### Backend
- **Framework**: FastAPI + Python 3.12
- **Database**: MongoDB with Beanie ODM
- **AI Integration**: Google Gemini 1.5 Flash via ModelRouter service
- **Authentication**: OAuth 2.0 (Google)
- **Deployment**: Docker + Google Cloud Run

## 📦 Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+ and pip
- MongoDB (or Docker)
- Google Gemini API key

### Frontend Setup
```bash
# Install frontend dependencies
npm install

# Run frontend development server
npm run dev
```
Frontend runs on: http://localhost:3000

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/mongodb.txt

# Set up environment variables
cp .env.minimal .env
# Edit .env and add your Google Gemini API key

# Run backend development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend runs on: http://localhost:8000

### Docker Setup (Recommended)

**Quick Start:**
```bash
# Run the setup script (handles .env and builds containers)
./backend/docker-setup.sh
```

**Manual Setup:**
```bash
# 1. Set up backend environment
cp backend/.env.minimal backend/.env
# Edit backend/.env and add your Google Gemini API key

# 2. Build and start services
docker-compose up --build
```

This starts:
- Frontend (Next.js) on port 3001
- Backend (FastAPI) on port 8001  
- MongoDB database on port 27018
- Redis cache on port 6380

## 🌐 Access Points

### Development (Local)
- **Frontend**: http://localhost:3000 - Main application interface
- **Backend API**: http://localhost:8000 - REST API endpoints
- **API Documentation**: http://localhost:8000/docs - Interactive Swagger docs
- **Health Check**: http://localhost:8000/health - Backend status

### Docker (Containerized)
- **Frontend**: http://localhost:3001 - Main application interface
- **Backend API**: http://localhost:8001 - REST API endpoints
- **API Documentation**: http://localhost:8001/docs - Interactive Swagger docs
- **Health Check**: http://localhost:8001/health - Backend status

## 📁 Project Structure

```
Elenchus/
├── frontend/                 # Next.js frontend application
│   ├── components/          # React components (ChatPanel, SourcesPanel, etc.)
│   ├── store/              # Zustand state management
│   └── app/                # Next.js 14 app router pages
├── backend/                # FastAPI backend application
│   ├── app/
│   │   ├── api/v1/         # REST API endpoints
│   │   ├── models/         # MongoDB/Beanie models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic (ModelRouter, etc.)
│   │   └── config/         # Database and settings configuration
│   ├── requirements/       # Python dependencies
│   └── docker/            # Docker configuration files
└── docker-compose.yml     # Full stack orchestration
```

## 🎯 Usage

### Getting Started
1. **Add Sources**: Click the "Add" button in the Sources panel or use the upload button in the chat
2. **Upload Files**: Support for PDF, DOC, DOCX, and TXT files
3. **Start Chatting**: Ask questions about your uploaded sources
4. **Create Notes**: Use the Studio panel to generate study guides, timelines, etc.
5. **Audio Overview**: Customize and generate audio conversations

### Key Interactions
- **File Upload**: Drag & drop or click to upload files
- **Chat**: Type messages and press Enter to send
- **Voice Input**: Hold the microphone button to record (UI only)
- **Note Generation**: Click any note type button to create a new note
- **Customization**: Click "Customize" in Audio Overview for settings

## 📁 Project Structure

```
notebooklm-replica/
├── app/
│   ├── globals.css          # Global styles with Tailwind
│   ├── layout.tsx           # Root layout component
│   └── page.tsx             # Main page with three-panel layout
├── components/
│   ├── Header.tsx           # Top navigation bar
│   ├── SourcesPanel.tsx     # Left panel - file management
│   ├── ChatPanel.tsx        # Center panel - chat interface
│   └── StudioPanel.tsx      # Right panel - notes & audio
├── store/
│   └── useStore.ts          # Zustand state management
├── package.json             # Dependencies and scripts
├── tailwind.config.js       # Tailwind configuration
├── tsconfig.json            # TypeScript configuration
├── next.config.js           # Next.js configuration
└── README.md                # This file
```

## 🎨 Design Fidelity

The replica matches the original NotebookLM interface with:
- **Exact Color Palette**: Matching dark theme colors
- **Precise Spacing**: Identical padding, margins, and component sizing
- **Typography**: Google Sans font family
- **Interactive States**: Hover effects, focus states, and transitions
- **Layout Behavior**: Responsive panel sizing and overflow handling
- **Icon Usage**: Consistent Lucide React icons throughout

## 🔧 Customization

### Adding New Note Types
```typescript
// In components/StudioPanel.tsx
const noteTypes = [
  { id: 'custom-type', label: 'Custom Note', icon: CustomIcon },
  // ... existing types
];
```

### Modifying Theme Colors
```javascript
// In tailwind.config.js
theme: {
  extend: {
    colors: {
      'custom-primary': '#your-color',
    }
  }
}
```

### State Management
```typescript
// In store/useStore.ts
export interface StoreState {
  // Add new state properties
  customFeature: boolean;
  setCustomFeature: (value: boolean) => void;
}
```

## 🚧 Future Enhancements

- **Real AI Integration**: Connect to OpenAI or similar APIs
- **Authentication**: Firebase Auth or Auth0 integration
- **Database Persistence**: MongoDB for saving notebooks
- **Real-time Collaboration**: Socket.io for multi-user editing
- **Voice Recognition**: Web Speech API for voice input
- **File Processing**: PDF text extraction and analysis
- **Export Features**: Download notes and conversations

## 📱 Responsive Design

- **Mobile**: Collapsible panels with tab navigation
- **Tablet**: Two-panel layout with floating elements
- **Desktop**: Full three-panel layout as shown

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is for educational purposes only. NotebookLM is a trademark of Google LLC.

## 🙏 Acknowledgments

- Google NotebookLM team for the original design inspiration
- Tailwind CSS for the utility-first framework
- Zustand for lightweight state management
- Lucide React for beautiful icons

---

**Note**: This is a UI/UX replica for demonstration purposes. It does not include actual AI processing capabilities or file content analysis. 