import { Mic, MicOff, Volume2, X, Menu, Plus, History, LogOut, Square, Settings, MessageCircle, BookOpen, Sparkles, Briefcase, Plane, Heart, User, Pencil, Send } from 'lucide-react';
import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import wsService from '../services/websocket';
import speechService from '../services/speech';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { createConversation } from '../services/api';

export default function ChatInterface() {
  const navigate = useNavigate();
  const { 
    user, 
    currentConversation, 
    messages, 
    addMessage, 
    clearMessages,
    isRecording, 
    setRecording,
    isSpeaking,
    setSpeaking,
    mode,
    setMode,
    personality,
    setPersonality,
    setCurrentConversation
  } = useStore();

  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [showSidebar, setShowSidebar] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [learningInsights, setLearningInsights] = useState(null);
  const [showInsights, setShowInsights] = useState(false);
  const [silenceTimer, setSilenceTimer] = useState(null);
  const [isConversationActive, setIsConversationActive] = useState(false);
  const [customTopic, setCustomTopic] = useState('');
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const modes = [
    { id: 'free_talk', name: 'Free Talk', icon: MessageCircle },
    { id: 'grammar_focus', name: 'Grammar', icon: BookOpen },
    { id: 'vocabulary', name: 'Vocabulary', icon: Sparkles },
    { id: 'pronunciation', name: 'Speaking', icon: Mic },
    { id: 'business', name: 'Business', icon: Briefcase },
    { id: 'travel', name: 'Travel', icon: Plane },
  ];

  const personalities = [
    { id: 'teacher', name: 'Teacher', icon: User, desc: 'Professional tutor' },
    { id: 'girlfriend', name: 'Girlfriend', icon: Heart, desc: 'Loving partner' },
    { id: 'friend', name: 'Friend', icon: MessageCircle, desc: 'Casual buddy' },
  ];

  // Fetch user's conversation history and learning insights
  useEffect(() => {
    if (user?.id) {
      // Fetch conversations
      fetch(`/api/users/${user.id}/conversations`)
        .then(res => res.json())
        .then(data => {
          setConversations(data || []);
        })
        .catch(err => console.error('Failed to load conversations:', err));
      
      // Fetch learning insights
      fetch(`/api/users/${user.id}/insights`)
        .then(res => res.json())
        .then(data => {
          setLearningInsights(data);
        })
        .catch(err => console.error('Failed to load insights:', err));
    }
  }, [user]);

  useEffect(() => {
    if (!user || !currentConversation) return;

    wsService.connect(user.id, currentConversation.id)
      .then(() => {
        // Load conversation history
        fetch(`/api/conversations/${currentConversation.id}/messages`)
          .then(res => res.json())
          .then(history => {
            if (history && history.length > 0) {
              // EXISTING CONVERSATION - Load history but DON'T auto-start
              console.log(`📜 Loading ${history.length} previous messages`);
              history.forEach(msg => {
                addMessage({
                  role: msg.role,
                  content: msg.content,
                  timestamp: new Date(msg.timestamp || msg.created_at)
                });
              });
              toast.success(`Welcome back! Click the mic to continue your conversation.`);
              // Don't auto-start - let user click mic when ready
            } else {
              // NEW CONVERSATION - AI starts first!
              toast.success(`Hey ${user.full_name || user.username}! Let's talk!`);
              setTimeout(() => {
                setIsConversationActive(true);
                wsService.send({
                  type: 'user_message',
                  content: `START_GREETING:${user.full_name || user.username}:${mode || 'free_talk'}:${personality}`
                });
              }, 500);
            }
          })
          .catch(err => console.error('Failed to load history:', err));
      })
      .catch((error) => {
        // Only show error after multiple failed attempts
        console.error('WebSocket connection issue:', error);
        setTimeout(() => {
          if (!wsService.ws || wsService.ws.readyState !== WebSocket.OPEN) {
            toast.error('Connection failed. Please refresh the page.');
          }
        }, 3000);
      });

    wsService.on('ai_response', (data) => {
      const aiMessage = {
        role: 'assistant',
        content: data.content,
        timestamp: new Date(data.timestamp)
      };
      addMessage(aiMessage);

      // CRITICAL: Stop mic BEFORE AI speaks to prevent echo
      console.log('🛑 Stopping mic before AI speaks');
      speechService.stopRecognition();
      setIsListening(false);
      setRecording(false);
      setTranscript('');
      setInterimTranscript('');
      
      // PREVENT auto-restart while AI is speaking
      window.aiIsSpeaking = true;

      // Store FULL AI response for echo detection (lowercase, no punctuation)
      const cleanResponse = data.content.toLowerCase().replace(/[^\w\s]/g, '').trim();
      window.lastAIResponse = cleanResponse;
      window.lastAIWords = cleanResponse.split(/\s+/).filter(w => w.length > 2);
      
      console.log('💾 Stored AI response for echo detection:', window.lastAIResponse.substring(0, 60) + '...');
      
      // Clear after 15 seconds (longer to catch slow echoes)
      setTimeout(() => {
        window.lastAIResponse = null;
        window.lastAIWords = null;
      }, 15000);

      // AI speaks - with longer delay to ensure mic is fully stopped
      setTimeout(() => {
        setSpeaking(true);
        speechService.speak(data.content)
          .then(() => {
            setSpeaking(false);
            window.aiIsSpeaking = false; // Allow mic restart now
            console.log('🔊 AI finished speaking - user can click mic now');
          })
          .catch(() => {
            setSpeaking(false);
            window.aiIsSpeaking = false; // Allow mic restart on error
          });
      }, 500); // Longer delay
    });

    return () => {
      wsService.disconnect();
      stopListening();
    };
  }, [user, currentConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Check if text looks like echo of AI response - LESS aggressive but still effective
  const isEcho = (text) => {
    if (!window.lastAIResponse || !text) return false;
    
    const normalizedText = text.toLowerCase().trim().replace(/[^\w\s]/g, '');
    const textWords = normalizedText.split(/\s+/).filter(w => w.length > 2);
    
    // Skip very short responses (user saying "yes", "ok", etc.)
    if (textWords.length <= 2 && normalizedText.length < 15) return false;
    
    // Check 1: Exact substring match (first 40 chars)
    const aiStart = window.lastAIResponse.substring(0, 40);
    if (aiStart.length > 15 && normalizedText.includes(aiStart)) {
      console.log('🔊 ECHO: Exact start match');
      return true;
    }
    
    // Check 2: High word overlap (>70% of user words are in AI response)
    if (window.lastAIWords && textWords.length > 3) {
      const matchingWords = textWords.filter(w => window.lastAIWords.includes(w));
      const overlapRatio = matchingWords.length / textWords.length;
      
      if (overlapRatio > 0.7) {
        console.log(`🔊 ECHO: ${Math.round(overlapRatio * 100)}% word overlap`);
        return true;
      }
    }
    
    return false;
  };

  // Manual send - NO auto-send, user controls when to send
  const handleManualSend = () => {
    if (transcript.trim()) {
      // Check for echo
      if (isEcho(transcript)) {
        toast.error('Echo detected! Click "Clear Echo" to remove.');
        return;
      }
      sendMessage(transcript.trim());
      setTranscript('');
      setInterimTranscript('');
      stopListening();
    }
  };

  // Clear echo manually
  const clearEcho = () => {
    setTranscript('');
    setInterimTranscript('');
    window.lastAIResponse = null;
    window.lastAIWords = null;
    toast.success('Transcript cleared!');
  };

  // Switch to dual Hindi+English recognition
  const switchToDualMode = () => {
    speechService.forceRestartWithLanguage('hi-IN'); // Start with Hindi for max coverage
    recognitionRef.current = null; // Force re-init
    toast.info('Dual mode: Hindi + English recognition');
  };

  const startListening = () => {
    if (!speechService.isSupported) {
      toast.error('Use Chrome, Edge, or Safari for voice');
      return;
    }
    
    // Don't start if already listening or AI is speaking
    if (isListening || isSpeaking) {
      console.log('⏳ Cannot start - already listening or AI speaking');
      return;
    }

    console.log('🎤 Starting microphone...');

    navigator.mediaDevices?.getUserMedia({ audio: true })
      .then(() => {
        console.log('✅ Mic permission granted');
        
        if (!recognitionRef.current) {
          recognitionRef.current = speechService.initRecognition();
        }

        speechService.startRecognition(
          ({ final, interim }) => {
            // CRITICAL: Block ALL input while AI is speaking
            if (window.aiIsSpeaking || isSpeaking) {
              console.log('🚫 BLOCKED: AI is speaking, ignoring all mic input');
              return;
            }
            
            console.log('📝 Heard:', interim || final);
            
            // Real-time echo check - don't add echoed content
            const textToCheck = final || interim;
            if (textToCheck && isEcho(textToCheck)) {
              console.log('🔊 BLOCKED: Echo detected in real-time, ignoring');
              return; // Don't update transcript
            }
            
            setInterimTranscript(interim);
            if (final) {
              setTranscript(prev => (prev + ' ' + final).trim());
              setInterimTranscript('');
            }
          },
          () => {
            // Recognition ended - restart ONLY if AI not speaking
            console.log('🔄 Recognition ended');
            setTimeout(() => {
              if (!isSpeaking && !window.aiIsSpeaking && isConversationActive) {
                console.log('🔄 Safe to restart recognition - AI not speaking');
                try {
                  speechService.startRecognition(
                    ({ final, interim }) => {
                      // CRITICAL: Block ALL input while AI is speaking
                      if (window.aiIsSpeaking || isSpeaking) {
                        console.log('🚫 RESTART BLOCKED: AI is speaking');
                        return;
                      }
                      
                      // Real-time echo check
                      const textToCheck = final || interim;
                      if (textToCheck && isEcho(textToCheck)) {
                        console.log('🔊 BLOCKED: Echo in restart recognition');
                        return;
                      }
                      setInterimTranscript(interim);
                      if (final) {
                        setTranscript(prev => (prev + ' ' + final).trim());
                        setInterimTranscript('');
                      }
                    },
                    null, // Will use default end handler
                    (error) => console.log('Recognition error:', error)
                  );
                } catch (e) {
                  console.log('Restart failed:', e);
                }
              } else {
                console.log('⚠️ Skipping restart - AI still speaking or inactive');
              }
            }, 500);
          },
          (error) => {
            console.error('❌ Recognition error:', error);
            if (error === 'not-allowed') {
              toast.error('Microphone blocked. Allow microphone in browser settings.');
            }
          }
        );

        setIsListening(true);
        setRecording(true);
        setIsConversationActive(true);
        toast.success('🎤 Listening! Speak now...');
      })
      .catch((err) => {
        console.error('❌ Mic access denied:', err);
        toast.error('Please allow microphone access to speak');
      });
  };

  const stopListening = () => {
    console.log('🛑 Stopping mic');
    speechService.stopRecognition();
    setIsListening(false);
    setRecording(false);
    if (silenceTimer) clearTimeout(silenceTimer);
  };

  const toggleConversation = () => {
    if (isConversationActive && !isSpeaking) {
      // End conversation
      console.log('⏹️ Ending conversation');
      stopListening();
      speechService.stopSpeaking();
      setSpeaking(false);
      setIsConversationActive(false);
      toast.success('Conversation paused. Tap mic to continue.');
    } else if (!isConversationActive) {
      // Start/resume conversation
      console.log('▶️ Starting conversation');
      setIsConversationActive(true);
      if (messages.length === 0) {
        // First time - AI greets
        wsService.send({
          type: 'user_message',
          content: `START_GREETING:${user.full_name || user.username}:${mode || 'free_talk'}:${personality}`
        });
      } else {
        // Resume - start listening
        startListening();
      }
    }
  };

  const sendMessage = (text, isHidden = false) => {
    if (!text.trim()) return;

    // Don't show system commands in chat
    if (!isHidden && !text.startsWith('START_GREETING')) {
      const userMessage = {
        role: 'user',
        content: text,
        timestamp: new Date()
      };
      addMessage(userMessage);
    }
    
    wsService.send({
      type: 'user_message',
      content: text,
      personality: personality  // Send current personality to backend
    });
  };

  const startNewConversation = async () => {
    try {
      const res = await fetch(`/api/conversations?user_id=${user.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode || 'free_talk' })
      });
      const conv = await res.json();
      clearMessages();
      setCurrentConversation(conv);
      setShowSidebar(false);
      setIsConversationActive(false);
      toast.success('New conversation started');
    } catch (err) {
      toast.error('Failed to start new conversation');
    }
  };

  const changeTopic = async (newMode, customTopicText = '') => {
    try {
      stopListening();
      speechService.stopSpeaking();
      
      const topicName = customTopicText || modes.find(m => m.id === newMode)?.name || 'Free Talk';
      
      const res = await fetch(`/api/conversations?user_id=${user.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          mode: newMode, 
          topic: topicName,
          personality: personality 
        })
      });
      const conv = await res.json();
      
      clearMessages();
      setMode(newMode);
      setCurrentConversation(conv);
      setShowSettings(false);
      setIsConversationActive(false);
      setCustomTopic('');
      
      // Reconnect websocket with new conversation
      wsService.disconnect();
      setTimeout(() => {
        wsService.connect(user.id, conv.id).then(() => {
          toast.success(`Switched to ${topicName}!`);
        });
      }, 300);
    } catch (err) {
      toast.error('Failed to change topic');
    }
  };

  const startCustomTopic = () => {
    if (!customTopic.trim()) {
      toast.error('Enter a topic first');
      return;
    }
    changeTopic('free_talk', customTopic.trim());
  };

  const loadConversation = async (convId) => {
    try {
      clearMessages();
      setCurrentConversation({ id: convId });
      setShowSidebar(false);
      setIsConversationActive(false);
    } catch (err) {
      toast.error('Failed to load conversation');
    }
  };

  const endSession = () => {
    stopListening();
    speechService.stopSpeaking();
    wsService.disconnect();
    navigate('/');
  };

  // RESPONSIVE: Update on resize
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' && window.innerWidth < 768);
  
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    window.addEventListener('resize', handleResize);
    handleResize(); // Check on mount
    
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div style={{
      display: 'flex',
      height: '100dvh',
      width: '100vw',
      maxWidth: '100%',
      backgroundColor: '#0f0f0f',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      overflow: 'hidden',
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0
    }}>
      
      {/* Sidebar - ChatGPT style */}
      <AnimatePresence>
        {showSidebar && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowSidebar(false)}
              style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(0,0,0,0.5)',
                zIndex: 40
              }}
            />
            
            <motion.div
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: 'spring', damping: 25 }}
              style={{
                position: 'fixed',
                left: 0,
                top: 0,
                bottom: 0,
                width: isMobile ? '100%' : '280px',
                maxWidth: '320px',
                backgroundColor: '#171717',
                zIndex: 50,
                display: 'flex',
                flexDirection: 'column',
                borderRight: '1px solid #2d2d2d'
              }}
            >
              <div style={{
                padding: '16px',
                borderBottom: '1px solid #2d2d2d',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button 
                    onClick={() => setShowInsights(false)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: showInsights ? '#888' : '#fff',
                      cursor: 'pointer',
                      fontWeight: showInsights ? 400 : 600,
                      fontSize: '16px'
                    }}
                  >
                    History
                  </button>
                  <button 
                    onClick={() => setShowInsights(true)}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: showInsights ? '#fff' : '#888',
                      cursor: 'pointer',
                      fontWeight: showInsights ? 600 : 400,
                      fontSize: '16px'
                    }}
                  >
                    Insights
                  </button>
                </div>
                <button onClick={() => setShowSidebar(false)} style={{
                  background: 'none',
                  border: 'none',
                  color: '#888',
                  cursor: 'pointer',
                  padding: '8px'
                }}>
                  <X size={24} />
                </button>
              </div>

              <button
                onClick={startNewConversation}
                style={{
                  margin: '12px',
                  padding: '14px',
                  backgroundColor: '#2563eb',
                  border: 'none',
                  borderRadius: '12px',
                  color: '#fff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '16px'
                }}
              >
                <Plus size={20} /> New Chat
              </button>

              <div style={{ flex: 1, overflow: 'auto', padding: '8px' }}>
                {!showInsights ? (
                  <>
                    <p style={{ 
                      color: '#888', 
                      fontSize: '12px', 
                      padding: '8px 12px',
                      margin: 0
                    }}>
                      💡 AI learns from your past chats!
                    </p>
                    
                    {conversations.length === 0 ? (
                      <p style={{ color: '#666', textAlign: 'center', padding: '20px' }}>
                        No past conversations
                      </p>
                    ) : (
                      conversations.map((conv) => {
                    const date = new Date(conv.started_at);
                    const isToday = date.toDateString() === new Date().toDateString();
                    const isYesterday = date.toDateString() === new Date(Date.now() - 86400000).toDateString();
                    
                    // Use summary as main title, fallback to time if no summary
                    const mainTitle = conv.summary || 'Quick chat';
                    const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    const dateStr = isToday ? `Today ${timeStr}` : 
                                    isYesterday ? `Yesterday ${timeStr}` :
                                    `${date.toLocaleDateString()}`;
                    
                    // Show learning progress if available
                    const progressInfo = [];
                    if (conv.hindi_words_translated > 0) {
                      progressInfo.push(`${conv.hindi_words_translated} translations`);
                    }
                    if (conv.grammar_corrections > 0) {
                      progressInfo.push(`${conv.grammar_corrections} corrections`);
                    }
                    if (conv.message_count) {
                      progressInfo.push(`${conv.message_count} messages`);
                    }
                    
                    return (
                      <button
                        key={conv.id}
                        onClick={() => loadConversation(conv.id)}
                        style={{
                          width: '100%',
                          padding: '14px',
                          background: currentConversation?.id === conv.id ? '#2d2d2d' : 'transparent',
                          border: 'none',
                          borderRadius: '10px',
                          color: '#e5e5e5',
                          textAlign: 'left',
                          cursor: 'pointer',
                          marginBottom: '4px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px'
                        }}
                      >
                        <History size={18} style={{ color: '#888', flexShrink: 0 }} />
                        <div style={{ flex: 1, overflow: 'hidden' }}>
                          <div style={{ fontSize: '14px', color: '#fff', fontWeight: 500, marginBottom: '4px' }}>
                            {mainTitle}
                          </div>
                          <div style={{ fontSize: '11px', color: '#666', marginBottom: '2px' }}>
                            {dateStr}
                          </div>
                          {progressInfo.length > 0 && (
                            <div style={{ fontSize: '10px', color: '#888' }}>
                              {progressInfo.join(' • ')}
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })
                )}
                  </>
                ) : (
                  // Learning Insights Panel
                  <div style={{ padding: '12px' }}>
                    <h3 style={{ color: '#fff', fontSize: '16px', marginBottom: '16px', fontWeight: 600 }}>
                      🧠 Your Learning Progress
                    </h3>
                    
                    {!learningInsights ? (
                      <p style={{ color: '#888', textAlign: 'center' }}>Loading insights...</p>
                    ) : learningInsights.error ? (
                      <p style={{ color: '#f87171' }}>Need more conversation data</p>
                    ) : (
                      <>
                        {/* Stats */}
                        {learningInsights.stats && (
                          <div style={{ 
                            backgroundColor: '#2d2d2d', 
                            padding: '12px', 
                            borderRadius: '8px', 
                            marginBottom: '16px' 
                          }}>
                            <h4 style={{ color: '#fff', fontSize: '14px', margin: '0 0 8px 0' }}>📊 Stats</h4>
                            <div style={{ fontSize: '12px', color: '#ccc' }}>
                              <div>Messages: {learningInsights.stats.total_messages}</div>
                              <div>Hindi usage: {learningInsights.stats.hindi_messages}</div>
                              <div>Corrections: {learningInsights.stats.ai_corrections}</div>
                            </div>
                          </div>
                        )}
                        
                        {/* Strengths */}
                        {learningInsights.strengths && (
                          <div style={{ marginBottom: '16px' }}>
                            <h4 style={{ color: '#22c55e', fontSize: '14px', margin: '0 0 8px 0' }}>✅ Strengths</h4>
                            {learningInsights.strengths.map((strength, i) => (
                              <div key={i} style={{ 
                                fontSize: '12px', 
                                color: '#ccc', 
                                marginBottom: '4px',
                                paddingLeft: '8px',
                                borderLeft: '2px solid #22c55e'
                              }}>
                                {strength}
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {/* Improvement Areas */}
                        {learningInsights.improvement_areas && (
                          <div style={{ marginBottom: '16px' }}>
                            <h4 style={{ color: '#f59e0b', fontSize: '14px', margin: '0 0 8px 0' }}>🎯 Focus On</h4>
                            {learningInsights.improvement_areas.map((area, i) => (
                              <div key={i} style={{ 
                                fontSize: '12px', 
                                color: '#ccc', 
                                marginBottom: '4px',
                                paddingLeft: '8px',
                                borderLeft: '2px solid #f59e0b'
                              }}>
                                {area}
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {/* Common Mistakes */}
                        {learningInsights.common_mistakes && (
                          <div style={{ marginBottom: '16px' }}>
                            <h4 style={{ color: '#ef4444', fontSize: '14px', margin: '0 0 8px 0' }}>🔧 Common Mistakes</h4>
                            {learningInsights.common_mistakes.map((mistake, i) => (
                              <div key={i} style={{ 
                                fontSize: '12px', 
                                color: '#ccc', 
                                marginBottom: '4px',
                                paddingLeft: '8px',
                                borderLeft: '2px solid #ef4444'
                              }}>
                                {mistake}
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
                
              <button
                onClick={endSession}
                  style={{
                    margin: '12px',
                    padding: '14px',
                    backgroundColor: '#dc2626',
                    border: 'none',
                    borderRadius: '12px',
                    color: '#fff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '16px'
                  }}
                >
                  <LogOut size={20} /> Exit
                </button>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowSettings(false)}
              style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'rgba(0,0,0,0.7)',
                zIndex: 60
              }}
            />
            
            <motion.div
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%' }}
              transition={{ type: 'spring', damping: 25 }}
              style={{
                position: 'fixed',
                left: 0,
                right: 0,
                bottom: 0,
                maxHeight: '85vh',
                backgroundColor: '#1a1a1a',
                zIndex: 70,
                borderRadius: '20px 20px 0 0',
                overflow: 'auto'
              }}
            >
              {/* Settings Header */}
              <div style={{
                padding: '16px 20px',
                borderBottom: '1px solid #333',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                position: 'sticky',
                top: 0,
                backgroundColor: '#1a1a1a',
                zIndex: 1
              }}>
                <span style={{ color: '#fff', fontWeight: 600, fontSize: '18px' }}>Settings</span>
                <button onClick={() => setShowSettings(false)} style={{
                  background: 'none',
                  border: 'none',
                  color: '#888',
                  cursor: 'pointer',
                  padding: '8px'
                }}>
                  <X size={24} />
                </button>
              </div>

              <div style={{ padding: '16px 20px' }}>
                {/* Personality Selection */}
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ color: '#fff', fontSize: '15px', marginBottom: '12px', fontWeight: 600 }}>
                    AI Personality
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
                    {personalities.map(p => (
                      <button
                        key={p.id}
                        onClick={() => setPersonality(p.id)}
                        style={{
                          padding: '14px 10px',
                          backgroundColor: personality === p.id ? '#2563eb' : '#2d2d2d',
                          border: personality === p.id ? '2px solid #3b82f6' : '2px solid transparent',
                          borderRadius: '12px',
                          color: '#fff',
                          cursor: 'pointer',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        <p.icon size={22} />
                        <span style={{ fontSize: '13px', fontWeight: 500 }}>{p.name}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Topic Selection */}
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ color: '#fff', fontSize: '15px', marginBottom: '12px', fontWeight: 600 }}>
                    Change Topic
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                    {modes.map(m => (
                      <button
                        key={m.id}
                        onClick={() => changeTopic(m.id)}
                        style={{
                          padding: '14px',
                          backgroundColor: mode === m.id ? '#2563eb' : '#2d2d2d',
                          border: mode === m.id ? '2px solid #3b82f6' : '2px solid transparent',
                          borderRadius: '12px',
                          color: '#fff',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          textAlign: 'left'
                        }}
                      >
                        <m.icon size={20} />
                        <span style={{ fontSize: '14px', fontWeight: 500 }}>{m.name}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Custom Topic */}
                <div style={{ marginBottom: '24px' }}>
                  <h3 style={{ color: '#fff', fontSize: '15px', marginBottom: '12px', fontWeight: 600 }}>
                    Custom Topic
                  </h3>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <input
                      type="text"
                      value={customTopic}
                      onChange={(e) => setCustomTopic(e.target.value)}
                      placeholder="E.g., Job interview, Dating, Movies..."
                      style={{
                        flex: 1,
                        padding: '14px 16px',
                        backgroundColor: '#2d2d2d',
                        border: '1px solid #444',
                        borderRadius: '12px',
                        color: '#fff',
                        fontSize: '14px',
                        outline: 'none'
                      }}
                      onKeyDown={(e) => e.key === 'Enter' && startCustomTopic()}
                    />
                    <button
                      onClick={startCustomTopic}
                      style={{
                        padding: '14px 20px',
                        backgroundColor: '#2563eb',
                        border: 'none',
                        borderRadius: '12px',
                        color: '#fff',
                        cursor: 'pointer',
                        fontWeight: 600
                      }}
                    >
                      Go
                    </button>
                  </div>
                </div>

                {/* Apply Changes */}
                <button
                  onClick={() => {
                    setShowSettings(false);
                    toast.success('Settings updated!');
                  }}
                  style={{
                    width: '100%',
                    padding: '16px',
                    backgroundColor: '#16a34a',
                    border: 'none',
                    borderRadius: '12px',
                    color: '#fff',
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '16px'
                  }}
                >
                  Done
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
        
        {/* Header */}
        <div style={{
          padding: '12px 16px',
          backgroundColor: '#171717',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #2d2d2d',
          minHeight: '60px'
        }}>
          <button
            onClick={() => setShowSidebar(true)}
            style={{
              background: 'none',
              border: 'none',
              color: '#fff',
              cursor: 'pointer',
              padding: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Menu size={24} />
          </button>
          
          <div style={{ textAlign: 'center', flex: 1 }}>
            <h1 style={{ 
              color: '#fff', 
              fontSize: isMobile ? '15px' : '16px', 
              fontWeight: 600,
              margin: 0 
            }}>
              {personality === 'girlfriend' ? 'Aria 💕' : personality === 'friend' ? 'Your Buddy' : 'English Tutor'}
            </h1>
            <p style={{ 
              color: '#888', 
              fontSize: '12px',
              margin: 0,
              textTransform: 'capitalize'
            }}>
              {mode?.replace('_', ' ') || 'Free Talk'}
            </p>
          </div>
          
          {/* Settings Button */}
          <button
            onClick={() => setShowSettings(true)}
            style={{
              background: 'none',
              border: 'none',
              color: '#888',
              cursor: 'pointer',
              padding: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Settings size={22} />
          </button>
        </div>

        {/* Messages Area */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: isMobile ? '12px' : '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '12px',
          WebkitOverflowScrolling: 'touch'
        }}>
          {messages.length === 0 ? (
            <div style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#666',
              textAlign: 'center',
              padding: '20px'
            }}>
              <div style={{
                width: isMobile ? '70px' : '80px',
                height: isMobile ? '70px' : '80px',
                borderRadius: '50%',
                backgroundColor: '#1f1f1f',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '20px'
              }}>
                <Mic size={isMobile ? 30 : 36} style={{ color: '#2563eb' }} />
              </div>
              <h2 style={{ color: '#e5e5e5', marginBottom: '8px', fontSize: isMobile ? '18px' : '20px' }}>
                Hey {user?.full_name?.split(' ')[0] || 'there'}!
              </h2>
              <p style={{ maxWidth: '280px', lineHeight: 1.5, fontSize: isMobile ? '14px' : '15px', color: '#888' }}>
                Starting conversation...
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  width: '100%'
                }}
              >
                <div style={{
                  maxWidth: isMobile ? '90%' : '75%',
                  padding: isMobile ? '10px 14px' : '12px 16px',
                  borderRadius: msg.role === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
                  backgroundColor: msg.role === 'user' ? '#2563eb' : '#2d2d2d',
                  color: '#fff'
                }}>
                  <p style={{ 
                    margin: 0, 
                    lineHeight: 1.5, 
                    fontSize: isMobile ? '14px' : '15px',
                    wordBreak: 'break-word'
                  }}>
                    {msg.content}
                  </p>
                </div>
              </motion.div>
            ))
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Controls */}
        <div style={{
          padding: isMobile ? '12px' : '16px',
          paddingBottom: isMobile ? '20px' : '24px',
          backgroundColor: '#171717',
          borderTop: '1px solid #2d2d2d',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px'
        }}>
          {/* Editable Text Input - Always visible */}
          <div style={{
            display: 'flex',
            gap: '8px',
            width: '100%',
            maxWidth: '500px',
            alignItems: 'flex-end'
          }}>
            <textarea
              value={transcript + (interimTranscript ? ' ' + interimTranscript : '')}
              onChange={(e) => {
                setTranscript(e.target.value);
                setInterimTranscript('');
              }}
              placeholder={isSpeaking ? "Wait for AI to finish..." : "Type or tap mic to speak..."}
              disabled={isSpeaking}
              style={{
                flex: 1,
                minHeight: '50px',
                maxHeight: '120px',
                padding: '12px 16px',
                borderRadius: '20px',
                border: '1px solid #333',
                backgroundColor: '#1f1f1f',
                color: '#fff',
                fontSize: '15px',
                resize: 'none',
                outline: 'none',
                fontFamily: 'inherit',
                opacity: isSpeaking ? 0.5 : 1
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey && transcript.trim()) {
                  e.preventDefault();
                  handleManualSend();
                }
              }}
            />
            
            {/* Mic Button - smaller */}
            <button
              onClick={() => {
                if (isListening) {
                  stopListening();
                } else if (!isSpeaking) {
                  setTranscript(''); // Clear before starting fresh
                  startListening();
                }
              }}
              disabled={isSpeaking}
              style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                border: 'none',
                cursor: isSpeaking ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: isSpeaking ? '#444' : isListening ? '#dc2626' : '#2563eb',
                flexShrink: 0,
                opacity: isSpeaking ? 0.5 : 1
              }}
            >
              {isListening ? (
                <MicOff size={22} color="#fff" />
              ) : (
                <Mic size={22} color="#fff" />
              )}
            </button>

            {/* Send Button */}
            <button
              onClick={handleManualSend}
              disabled={!transcript.trim() || isSpeaking}
              style={{
                width: '50px',
                height: '50px',
                borderRadius: '50%',
                border: 'none',
                cursor: transcript.trim() && !isSpeaking ? 'pointer' : 'not-allowed',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: transcript.trim() && !isSpeaking ? '#22c55e' : '#333',
                flexShrink: 0,
                opacity: transcript.trim() && !isSpeaking ? 1 : 0.5
              }}
            >
              <Send size={22} color="#fff" />
            </button>

            {/* Clear Echo Button */}
            <button
              onClick={clearEcho}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#ef4444',
                flexShrink: 0
              }}
              title="Clear Echo"
            >
              <X size={18} color="#fff" />
            </button>

            {/* Dual Hindi+English Button */}
            <button
              onClick={switchToDualMode}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                border: 'none',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: '#3b82f6',
                flexShrink: 0,
                fontSize: '11px',
                fontWeight: 'bold'
              }}
              title="Dual: Hindi + English"
            >
              हि+En
            </button>
          </div>

          {/* Status Text + Stop Button */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px'
          }}>
            {isSpeaking && (
              <button
                onClick={() => {
                  speechService.stopSpeaking();
                  setSpeaking(false);
                  toast.info('Stopped AI');
                }}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#dc2626',
                  border: 'none',
                  borderRadius: '20px',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '13px',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <Square size={14} fill="#fff" /> Stop AI
              </button>
            )}
            <p style={{
              color: '#666',
              fontSize: '12px',
              textAlign: 'center',
              margin: 0
            }}>
              {isSpeaking ? (
                '🔊 AI speaking...'
              ) : isListening ? (
                '🎤 Listening... (Hindi/English) tap mic to stop'
              ) : (
                'Speak Hindi or English • AI will translate!'
              )}
            </p>
          </div>
        </div>
      </div>

      <style>{`
        * {
          -webkit-tap-highlight-color: transparent;
        }
      `}</style>
    </div>
  );
}
