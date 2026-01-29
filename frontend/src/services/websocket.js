class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.userId = null;
    this.conversationId = null;
  }

  connect(userId, conversationId) {
    this.userId = userId;
    this.conversationId = conversationId;
    
    return new Promise((resolve, reject) => {
      // Close existing connection if any
      if (this.ws) {
        try {
          this.ws.close();
        } catch (e) {
          console.log('Previous WS cleanup:', e);
        }
      }
      
      const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/${userId}/${conversationId}`;
      console.log('🔌 Connecting to WebSocket:', wsUrl);
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        resolve(this.ws);
      };

      this.ws.onerror = (error) => {
        console.warn('⚠️ WebSocket error (will retry):', error.type || 'Unknown');
        // Don't show error toast - this is just a warning, let onclose handle actual failures
      };

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        this.emit('disconnected');
        
        // Only reject on initial connection failure
        if (this.reconnectAttempts === 0 && event.code !== 1000) {
          reject(new Error('Connection failed'));
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('message', data);
          
          // Emit specific event types
          if (data.type) {
            this.emit(data.type, data);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }
}

export default new WebSocketService();
