# NotebookLM Replica

A faithful recreation of Google's NotebookLM interface using modern web technologies. This project replicates the exact UI/UX, three-panel layout, and core functionality of NotebookLM.

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

- **Frontend**: Next.js 14 + React 18 + TypeScript
- **Styling**: Tailwind CSS with custom dark theme
- **State Management**: Zustand
- **Icons**: Lucide React
- **UI Components**: Headless UI (for accessibility)
- **Development**: ESLint + TypeScript strict mode

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd notebooklm-replica
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

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