import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { createUser, createConversation } from '../services/api';
import toast from 'react-hot-toast';
import { Mic, BookOpen, Briefcase, Plane, MessageCircle, Sparkles, ChevronRight, Bot, Star, Globe } from 'lucide-react';
import { motion } from 'framer-motion';
import speechService from '../services/speech';

export default function Home() {
  const navigate = useNavigate();
  const { setUser, setCurrentConversation, setMode, clearMessages } = useStore();
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [level, setLevel] = useState('intermediate');
  const [selectedMode, setSelectedMode] = useState('free_talk');
  const [personality, setPersonality] = useState('teacher');
  const [customTopic, setCustomTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  const [isMobile, setIsMobile] = useState(typeof window !== 'undefined' && window.innerWidth < 768);

  // Responsive listener
  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    handleResize();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const modes = [
    { id: 'free_talk', name: 'Free Talk', icon: MessageCircle, desc: 'Natural conversation', color: '#3b82f6' },
    { id: 'grammar_focus', name: 'Grammar', icon: BookOpen, desc: 'Fix your grammar', color: '#8b5cf6' },
    { id: 'vocabulary', name: 'Vocabulary', icon: Sparkles, desc: 'Learn new words', color: '#ec4899' },
    { id: 'pronunciation', name: 'Speaking', icon: Mic, desc: 'Sound better', color: '#f97316' },
    { id: 'business', name: 'Business', icon: Briefcase, desc: 'Professional English', color: '#10b981' },
    { id: 'travel', name: 'Travel', icon: Plane, desc: 'Travel situations', color: '#06b6d4' },
  ];

  const handleStart = async () => {
    if (!name.trim() || !email.trim()) {
      toast.error('Please enter name and email');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      toast.error('Please enter a valid email address');
      return;
    }

    setLoading(true);

    try {
      const userResponse = await createUser({
        username: name.toLowerCase().replace(/\s+/g, '_'),
        email: email,
        full_name: name,
        english_level: level
      });

      const userData = userResponse.data;
      setUser(userData);

      const convResponse = await createConversation(userData.id, {
        mode: selectedMode,
        topic: customTopic.trim() || modes.find(m => m.id === selectedMode)?.name,
        personality: personality
      });

      const conversationData = convResponse.data;
      
      // IMPORTANT: Clear old messages before starting new conversation
      clearMessages();
      
      setCurrentConversation(conversationData);
      setMode(selectedMode);

      toast.success('Let\'s go!');
      navigate('/chat');
      
    } catch (error) {
      console.error('Setup error:', error);
      
      // Handle specific error types
      if (error.response?.status === 400) {
        const errorMsg = error.response.data?.detail || 'Invalid input. Please check your details.';
        if (errorMsg.toLowerCase().includes('email')) {
          toast.error('Email address is already registered or invalid');
        } else {
          toast.error(errorMsg);
        }
      } else if (error.response?.status === 422) {
        toast.error('Please enter a valid email address');
      } else {
        toast.error('Failed to start. Please check your internet connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      color: '#fff',
      display: 'flex',
      flexDirection: 'column',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        padding: isMobile ? '32px 20px 24px' : '48px 32px 32px',
        textAlign: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.1)'
      }}>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          style={{
            width: isMobile ? '80px' : '100px',
            height: isMobile ? '80px' : '100px',
            borderRadius: '24px',
            background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 24px',
            boxShadow: '0 20px 40px rgba(59,130,246,0.3)'
          }}
        >
          <Bot size={isMobile ? 36 : 44} color="#fff" />
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{ 
            fontSize: isMobile ? '32px' : '42px', 
            fontWeight: 700,
            margin: '0 0 12px',
            background: 'linear-gradient(135deg, #fff 0%, #e2e8f0 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          English AI Partner
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          style={{ 
            color: '#94a3b8', 
            fontSize: isMobile ? '16px' : '18px',
            margin: 0,
            maxWidth: '600px',
            marginInline: 'auto'
          }}
        >
          Master English through natural conversation with AI • Available 24/7 • Completely Free
        </motion.p>
      </div>

      {/* Content */}
      <div style={{
        flex: 1,
        padding: isMobile ? '24px 20px' : '32px 32px',
        maxWidth: '600px',
        margin: '0 auto',
        width: '100%'
      }}>
        {step === 1 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Name Input */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ 
                color: '#e2e8f0', 
                fontSize: '14px', 
                display: 'block', 
                fontWeight: 500,
                marginBottom: '8px' 
              }}>
                Your Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter your name"
                style={{
                  width: '100%',
                  padding: '16px',
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '12px',
                  color: '#fff',
                  fontSize: '16px',
                  outline: 'none',
                  boxSizing: 'border-box',
                  backdropFilter: 'blur(10px)'
                }}
              />
            </div>

            {/* Email Input */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ 
                color: '#e2e8f0', 
                fontSize: '14px', 
                display: 'block', 
                fontWeight: 500,
                marginBottom: '8px' 
              }}>
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                style={{
                  width: '100%',
                  padding: '16px',
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  border: '1px solid rgba(255,255,255,0.2)',
                  borderRadius: '12px',
                  color: '#fff',
                  fontSize: '16px',
                  outline: 'none',
                  boxSizing: 'border-box',
                  backdropFilter: 'blur(10px)'
                }}
              />
            </div>

            {/* Level Select */}
            <div style={{ marginBottom: '32px' }}>
              <label style={{ 
                color: '#e2e8f0', 
                fontSize: '14px', 
                display: 'block', 
                fontWeight: 500,
                marginBottom: '12px' 
              }}>
                English Level
              </label>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: 'repeat(3, 1fr)', 
                gap: '8px' 
              }}>
                {['beginner', 'intermediate', 'advanced'].map(lvl => (
                  <button
                    key={lvl}
                    onClick={() => setLevel(lvl)}
                    style={{
                      padding: '12px 16px',
                      backgroundColor: level === lvl ? '#3b82f6' : 'rgba(255,255,255,0.1)',
                      border: level === lvl ? '1px solid #3b82f6' : '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '10px',
                      color: '#fff',
                      fontSize: '14px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      textTransform: 'capitalize',
                      backdropFilter: 'blur(10px)',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => name && email ? setStep(2) : toast.error('Fill all fields')}
              style={{
                width: '100%',
                padding: '18px',
                background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                border: 'none',
                borderRadius: '12px',
                color: '#fff',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              Choose Mode <ChevronRight size={20} />
            </button>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {/* Back Button */}
            <button
              onClick={() => setStep(1)}
              style={{
                background: 'none',
                border: 'none',
                color: '#94a3b8',
                fontSize: '14px',
                marginBottom: '32px',
                cursor: 'pointer',
                padding: 0,
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              ← Back to Setup
            </button>

            {/* Settings Header */}
            <h1 style={{
              color: '#e2e8f0',
              fontSize: '28px',
              fontWeight: 700,
              marginBottom: '32px',
              textAlign: 'center'
            }}>
              Settings
            </h1>

            {/* AI Personality */}
            <div style={{ marginBottom: '32px' }}>
              <h3 style={{
                color: '#e2e8f0',
                fontSize: '18px',
                fontWeight: 600,
                marginBottom: '16px'
              }}>
                AI Personality
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '12px'
              }}>
                {[
                  { id: 'teacher', name: 'Teacher' },
                  { id: 'girlfriend', name: 'Girlfriend' },
                  { id: 'friend', name: 'Friend' }
                ].map(p => (
                  <button
                    key={p.id}
                    onClick={() => setPersonality(p.id)}
                    style={{
                      padding: '16px',
                      backgroundColor: personality === p.id 
                        ? 'rgba(59,130,246,0.2)' 
                        : 'rgba(255,255,255,0.1)',
                      border: personality === p.id 
                        ? '2px solid #3b82f6' 
                        : '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '12px',
                      color: '#fff',
                      fontSize: '14px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      backdropFilter: 'blur(10px)',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {p.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Change Topic */}
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{
                color: '#e2e8f0',
                fontSize: '18px',
                fontWeight: 600,
                marginBottom: '16px'
              }}>
                Change Topic
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '8px',
                marginBottom: '16px'
              }}>
                {modes.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => {
                      setSelectedMode(m.id);
                      setCustomTopic('');
                    }}
                    style={{
                      padding: '12px 8px',
                      backgroundColor: selectedMode === m.id && !customTopic
                        ? 'rgba(59,130,246,0.2)' 
                        : 'rgba(255,255,255,0.1)',
                      border: selectedMode === m.id && !customTopic
                        ? '2px solid #3b82f6' 
                        : '1px solid rgba(255,255,255,0.2)',
                      borderRadius: '8px',
                      color: '#fff',
                      fontSize: '12px',
                      fontWeight: 500,
                      cursor: 'pointer',
                      backdropFilter: 'blur(10px)',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    {m.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Topic */}
            <div style={{ marginBottom: '32px' }}>
              <h4 style={{
                color: '#e2e8f0',
                fontSize: '16px',
                fontWeight: 500,
                marginBottom: '12px'
              }}>
                Custom Topic
              </h4>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  value={customTopic}
                  onChange={(e) => setCustomTopic(e.target.value)}
                  placeholder="E.g., Job interview, Dating, Movies..."
                  style={{
                    flex: 1,
                    padding: '12px 16px',
                    backgroundColor: 'rgba(255,255,255,0.1)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '14px',
                    outline: 'none',
                    backdropFilter: 'blur(10px)'
                  }}
                />
                <button
                  onClick={() => {
                    if (customTopic.trim()) {
                      setSelectedMode('custom');
                    }
                  }}
                  disabled={!customTopic.trim()}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: customTopic.trim() ? '#3b82f6' : 'rgba(255,255,255,0.1)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                    fontSize: '14px',
                    fontWeight: 500,
                    cursor: customTopic.trim() ? 'pointer' : 'not-allowed',
                    opacity: customTopic.trim() ? 1 : 0.5
                  }}
                >
                  Go
                </button>
              </div>
            </div>

            {/* Start Button */}
            <button
              onClick={handleStart}
              disabled={loading}
              style={{
                width: '100%',
                padding: '20px',
                background: loading 
                  ? 'rgba(59,130,246,0.5)' 
                  : 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                border: 'none',
                borderRadius: '16px',
                color: '#fff',
                fontSize: '18px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '12px',
                boxShadow: loading 
                  ? 'none' 
                  : '0 10px 30px rgba(59,130,246,0.3)',
                transition: 'all 0.3s ease'
              }}
            >
              {loading ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    style={{
                      width: '20px',
                      height: '20px',
                      border: '2px solid rgba(255,255,255,0.3)',
                      borderTop: '2px solid #fff',
                      borderRadius: '50%'
                    }}
                  />
                  Starting...
                </>
              ) : (
                <>
                  <Mic size={24} /> Start Talking
                </>
              )}
            </button>

            {/* Done Button */}
            <button
              onClick={() => setStep(1)}
              style={{
                width: '100%',
                padding: '16px',
                background: 'none',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '12px',
                color: '#94a3b8',
                fontSize: '16px',
                fontWeight: 500,
                cursor: 'pointer',
                marginTop: '16px',
                backdropFilter: 'blur(10px)'
              }}
            >
              Done
            </button>
          </motion.div>
        )}
      </div>

      {/* Footer */}
      <div style={{
        padding: '32px 20px',
        textAlign: 'center',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        background: 'rgba(15,23,42,0.5)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: isMobile ? '32px' : '48px'
        }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            style={{ textAlign: 'center' }}
          >
            <div style={{ 
              color: '#3b82f6', 
              fontSize: '24px', 
              fontWeight: 700,
              marginBottom: '4px'
            }}>
              100%
            </div>
            <div style={{ 
              color: '#94a3b8', 
              fontSize: '13px',
              fontWeight: 500
            }}>
              Free Forever
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            style={{ textAlign: 'center' }}
          >
            <div style={{ 
              color: '#3b82f6', 
              fontSize: '24px', 
              fontWeight: 700,
              marginBottom: '4px'
            }}>
              24/7
            </div>
            <div style={{ 
              color: '#94a3b8', 
              fontSize: '13px',
              fontWeight: 500
            }}>
              Always Available
            </div>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            style={{ textAlign: 'center' }}
          >
            <div style={{ 
              color: '#3b82f6', 
              fontSize: '24px', 
              fontWeight: 700,
              marginBottom: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}>
              <Star size={20} fill="#3b82f6" /> AI
            </div>
            <div style={{ 
              color: '#94a3b8', 
              fontSize: '13px',
              fontWeight: 500
            }}>
              Powered Learning
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
