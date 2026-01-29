import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Users
export const createUser = (userData) => api.post('/api/users', userData);
export const getUser = (userId) => api.get(`/api/users/${userId}`);
export const listUsers = () => api.get('/api/users');

// Conversations
export const createConversation = (userId, conversationData) => 
  api.post('/api/conversations', conversationData, { params: { user_id: userId } });

export const getConversation = (conversationId) => 
  api.get(`/api/conversations/${conversationId}`);

export const getUserConversations = (userId, limit = 20) => 
  api.get(`/api/users/${userId}/conversations`, { params: { limit } });

export const getConversationMessages = (conversationId) => 
  api.get(`/api/conversations/${conversationId}/messages`);

export const endConversation = (conversationId) => 
  api.post(`/api/conversations/${conversationId}/end`);

// Progress
export const getUserProgress = (userId, days = 7) => 
  api.get(`/api/users/${userId}/progress`, { params: { days } });

// Health check
export const healthCheck = () => api.get('/health');

export default api;
