import { create } from 'zustand';

export const useStore = create((set, get) => ({
  // User state
  user: null,
  setUser: (user) => set({ user }),
  
  // Conversation state
  currentConversation: null,
  conversations: [],
  messages: [],
  
  setCurrentConversation: (conversation) => set({ currentConversation: conversation }),
  setConversations: (conversations) => set({ conversations }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  setMessages: (messages) => set({ messages }),
  clearMessages: () => set({ messages: [] }),
  
  // UI state
  isRecording: false,
  isSpeaking: false,
  isConnected: false,
  mode: 'free_talk',
  personality: 'teacher',
  
  setRecording: (isRecording) => set({ isRecording }),
  setSpeaking: (isSpeaking) => set({ isSpeaking }),
  setConnected: (isConnected) => set({ isConnected }),
  setMode: (mode) => set({ mode }),
  setPersonality: (personality) => set({ personality }),
  
  // WebSocket
  ws: null,
  setWs: (ws) => set({ ws }),
  
  // Speech recognition
  recognition: null,
  synthesis: window.speechSynthesis,
  
  // Progress
  progress: [],
  setProgress: (progress) => set({ progress }),
}));
