# 🎯 NotebookLM Replica

A pixel-perfect recreation of Google's NotebookLM interface built with **Next.js**, **React**, **Tailwind CSS**, and **Zustand**.

## 🌟 Features

### ✅ Complete UI Recreation
- **Three-panel layout**: Sources, Chat, and Studio panels
- **Dark theme**: Exact color matching with NotebookLM
- **Responsive design**: Mobile and desktop layouts
- **Smooth animations**: Framer Motion transitions
- **Modern typography**: Inter font family

### 📁 Sources Management
- **Drag & drop file upload**: Support for PDFs, DOCs, TXT, audio files
- **File processing states**: Upload, processing, ready, error indicators
- **Search functionality**: Filter sources by name
- **File metadata**: Size, upload date, file type icons

### 💬 Chat Interface
- **Real-time messaging**: User and AI conversation flow
- **Typing indicators**: Animated typing state
- **Message history**: Persistent chat storage
- **Quick actions**: Suggested prompts and conversation starters
- **Source attribution**: Messages linked to relevant sources

### 🎙️ Audio Overview
- **AI-generated conversations**: Simulated deep-dive audio content
- **Audio controls**: Play, pause, progress tracking
- **Customization options**: Host configuration and content tuning
- **Status tracking**: Generation progress and completion states

### 📝 Notes & Study Tools
- **Study guides**: AI-generated learning materials
- **FAQs**: Frequently asked questions from sources
- **Timelines**: Chronological content organization
- **Briefing docs**: Executive summaries
- **Note management**: Create, edit, and organize notes

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with custom design tokens
- **State Management**: Zustand
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **File Handling**: React Dropzone
- **Typography**: Google Fonts (Inter)

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/kenethruiz20/Elenchus.git
   cd Elenchus/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🚀 Usage

### Getting Started
1. **Upload sources**: Click "Add" in the Sources panel to upload documents
2. **Wait for processing**: Files will show processing status
3. **Start chatting**: Once sources are ready, use the chat interface
4. **Generate content**: Create study guides, FAQs, and audio overviews
5. **Manage notes**: Save and organize your learning materials

### File Types Supported
- **Documents**: PDF, DOC, DOCX, TXT
- **Audio**: MP3, WAV, M4A
- **Web**: URLs (paste website links)
- **Text**: Direct text input

## 🎨 Design Fidelity

This replica maintains 1:1 visual fidelity with the original NotebookLM:

- **Color palette**: Exact hex values matching the dark theme
- **Typography**: Inter font with proper weights and sizes
- **Spacing**: Consistent padding, margins, and component sizing
- **Interactions**: Hover states, focus indicators, and transitions
- **Layout**: Responsive grid system and panel behaviors

## 🔧 Development

### Project Structure
```
frontend/
├── app/                 # Next.js App Router pages
├── components/          # React components
├── lib/                 # Utilities and store
└── public/              # Static assets
```

### Key Components
- `Header.tsx`: Top navigation and title management
- `SourcesPanel.tsx`: File upload and source management
- `ChatPanel.tsx`: Conversation interface
- `StudioPanel.tsx`: Audio overview and notes section

### State Management
The app uses Zustand for state management with the following stores:
- Sources and file uploads
- Chat messages and conversation state
- Notes and study materials
- Audio overview generation
- UI state and panel visibility

## 🎯 Roadmap

### Current Features
- ✅ Complete UI recreation
- ✅ File upload system
- ✅ Chat interface
- ✅ Notes management
- ✅ Audio overview simulation

### Future Enhancements
- [ ] Real AI integration (OpenAI/Anthropic)
- [ ] Actual file processing and OCR
- [ ] Audio generation capabilities
- [ ] Real-time collaboration
- [ ] Database persistence
- [ ] Authentication system
- [ ] Advanced search and filtering

## 🚀 Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Connect your repository to [Vercel](https://vercel.com)
3. Deploy automatically with zero configuration

### Manual Deployment
```bash
npm run build
npm start
```

## 📄 License

This project is for educational purposes and is not affiliated with Google or NotebookLM.

## 🙏 Acknowledgments

- **Google NotebookLM**: Original inspiration and design
- **Vercel**: Next.js framework and deployment platform
- **Tailwind Labs**: Amazing CSS framework
- **Lucide**: Beautiful icon library

---

**Note**: This is a visual recreation for learning purposes. For actual AI-powered document analysis, please use the official [NotebookLM](https://notebooklm.google.com). 