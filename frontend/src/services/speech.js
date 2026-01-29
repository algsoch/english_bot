class SpeechService {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    // DUAL RECOGNITION STRATEGY: Try both languages and merge results
    this.primaryLanguage = 'hi-IN'; // Better for mixed Hindi-English
    this.fallbackLanguage = 'en-IN'; // Backup for pure English
    this.isDualMode = true;
    this.useSmartSwitching = true; // Automatically switch based on results
    
    // ECHO PREVENTION SYSTEM
    this.isAISpeaking = false; // Track when AI is speaking
    this.recognitionPaused = false; // Track recognition pause state
    this.pendingResume = null; // Timer for resuming recognition
    
    // Check for speech recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.isSupported = !!SpeechRecognition;
    
    // Store the recognition constructor
    this.SpeechRecognition = SpeechRecognition;
    
    // Track recognition attempts and results
    this.recognitionAttempts = 0;
    this.maxAttempts = 3;
    this.lastResults = [];
    
    // Global flag for other components to check
    if (typeof window !== 'undefined') {
      window.aiIsSpeaking = false;
    }
  }

  initRecognition(language = 'hi-IN') {
    // SMART MIXED LANGUAGE STRATEGY:
    // 1. Use hi-IN as primary - captures Hindi + English + mixed content better
    // 2. hi-IN preserves: "I did coding aur mein currently kaam kar raha hoon"
    // 3. en-IN would lose: "I did coding and currently" (drops Hindi words)
    // 4. Smart switching based on result quality
    if (!this.isSupported) {
      console.warn('Speech recognition not supported');
      return null;
    }

    this.recognition = new this.SpeechRecognition();
    this.currentLanguage = language;
    
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = language;
    this.recognition.maxAlternatives = 10; // More alternatives for better mixed results

    console.log(`🎙️ SMART Mixed Language: ${language} (captures Hindi+English together)`);
    return this.recognition;
  }

  // Set language dynamically
  setLanguage(language) {
    this.currentLanguage = language;
    if (this.recognition) {
      this.recognition.lang = language;
      console.log(`🌐 Speech recognition language changed to: ${language}`);
    }
  }

  // Switch between language modes for better recognition
  setLanguageMode(mode) {
    this.languageMode = mode;
    const langMap = {
      'auto': 'hi-IN',      // Hindi mode - picks up Hindi + English + Hinglish
      'hindi': 'hi-IN',     // Pure Hindi
      'english': 'en-US'    // Pure English
    };
    const lang = langMap[mode] || 'hi-IN';
    this.setLanguage(lang);
    console.log(`🇮🇳 Language mode: ${mode} -> ${lang}`);
    return lang;
  }

  // Test what languages browser supports
  getLanguageSupport() {
    const testLangs = ['hi-IN', 'en-IN', 'en-US'];
    console.log('🔍 Testing language support...');
    
    // Create temporary recognition to test
    if (!this.SpeechRecognition) return [];
    
    return testLangs;
  }

  // Force restart recognition with new language
  forceRestartWithLanguage(language) {
    console.log(`🔄 Force restarting recognition with ${language}`);
    this.stopRecognition();
    this.recognition = null;
    return this.initRecognition(language);
  }

  async startRecognition(onResult, onEnd, onError) {
    console.log('🎤 Starting speech recognition...');
    
    // Request microphone permission first
    try {
      console.log('🎤 Requesting microphone permission...');
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('✅ Microphone permission granted');
      // Stop the stream, we just needed permission
      stream.getTracks().forEach(track => track.stop());
    } catch (error) {
      console.error('❌ Microphone permission denied:', error);
      if (onError) onError('not-allowed');
      return;
    }
    
    if (!this.recognition) {
      // Start with hi-IN for BETTER mixed Hindi-English capture
      console.log('🎙️ Starting with hi-IN for complete mixed language support...');
      try {
        this.initRecognition('hi-IN');
      } catch (err) {
        console.log('⚠️ hi-IN failed, trying en-IN...');
        this.initRecognition('en-IN');
      }
    }

    if (!this.recognition) {
      console.error('❌ Recognition initialization failed');
      if (onError) onError('initialization-failed');
      return;
    }

    this.recognition.onresult = (event) => {
      // ECHO PREVENTION: Ignore results if AI is speaking
      if (this.isAISpeaking) {
        console.log('🔇 Ignoring speech result - AI is speaking (echo prevention)');
        return;
      }
      
      console.log('🎙️ Speech result received:', event);
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        
        // Get the best transcription - prioritize mixed content
        let transcript = result[0].transcript;
        
        // For hi-IN, check alternatives for best mixed language coverage
        if (result.length > 1 && this.currentLanguage === 'hi-IN') {
          let bestTranscript = transcript;
          let maxMixedScore = this.calculateMixedLanguageScore(transcript);
          
          // Check up to 5 alternatives for better mixed content
          for (let j = 1; j < Math.min(5, result.length); j++) {
            const alt = result[j].transcript;
            const mixedScore = this.calculateMixedLanguageScore(alt);
            
            console.log(`Alternative ${j}: "${alt}" (mixed score: ${mixedScore}, confidence: ${result[j].confidence || 'N/A'})`);
            
            // Prefer alternatives with better mixed language coverage
            if (mixedScore > maxMixedScore && (result[j].confidence > 0.2 || result[j].confidence === undefined)) {
              bestTranscript = alt;
              maxMixedScore = mixedScore;
              console.log(`✅ Using better mixed alternative: "${alt}"`);
            }
          }
          
          transcript = bestTranscript;
        }
        
        console.log(`Result ${i}: "${transcript}" (final: ${result.isFinal})`);
        
        if (result.isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }

      console.log('Final:', finalTranscript, 'Interim:', interimTranscript);
      onResult({ final: finalTranscript, interim: interimTranscript });
    };

    this.recognition.onend = () => {
      console.log('🛑 Recognition ended - will auto-restart if handlers exist');
      // Auto-restart recognition when it ends (browser stops it after ~60 seconds)
      if (this._autoRestart && this._lastResultHandler) {
        console.log('🔄 Auto-restarting recognition...');
        setTimeout(() => {
          try {
            this.recognition.start();
          } catch (e) {
            console.log('Auto-restart failed:', e);
          }
        }, 100);
      }
      if (onEnd) onEnd();
    };

    this.recognition.onerror = (event) => {
      console.error('❌ Speech recognition error:', event.error, event);
      // Don't stop on "no-speech" error - just keep listening
      if (event.error === 'no-speech') {
        console.log('No speech detected, continuing...');
        return;
      }
      // Restart on "aborted" - happens when browser interrupts
      if (event.error === 'aborted') {
        console.log('Recognition aborted, restarting...');
        setTimeout(() => {
          try {
            this.recognition.start();
          } catch (e) {
            console.log('Restart after abort failed:', e);
          }
        }, 200);
        return;
      }
      if (onError) onError(event.error);
    };

    // Store handlers for auto-restart
    this._autoRestart = true;
    this._lastResultHandler = onResult;

    try {
      this.recognition.start();
      console.log('✅ Recognition started successfully');
    } catch (error) {
      console.error('❌ Failed to start recognition:', error);
      if (onError) onError('start-failed');
    }
  }

  stopRecognition() {
    this._autoRestart = false; // Disable auto-restart when explicitly stopped
    if (this.recognition) {
      this.recognition.stop();
    }
  }

  speak(text, options = {}) {
    // ECHO PREVENTION: Pause speech recognition during AI speech
    this.pauseRecognitionForSpeech();
    
    // CLEAN TEXT - Remove emojis and special characters that TTS mispronounces
    const cleanText = text
      .replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]/gu, '') // Remove emojis
      .replace(/💡|📝|✨|🎯|👍|👎|✅|❌|⚠️|💬|🗣️|📖|🔊|🎤|💭/g, '') // Remove common tip emojis
      .replace(/Tip:|TIP:|tip:/gi, '') // Remove "Tip:" prefix
      .replace(/\s+/g, ' ') // Normalize spaces
      .trim();
    
    console.log('🔊 Speaking (cleaned):', cleanText);
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        console.error('❌ Speech synthesis not supported');
        this.resumeRecognitionAfterSpeech(); // Resume even on error
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      // Cancel any ongoing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(cleanText);
      
      // SLOWER, CLEARER VOICE - Easy to understand
      utterance.rate = options.rate || 0.8;    // Slower speech - easier to understand
      utterance.pitch = options.pitch || 1.05; // Slightly higher, friendly feminine voice
      utterance.volume = options.volume || 1.0;
      utterance.lang = options.lang || 'en-US';

      // Wait for voices to load
      const setVoice = () => {
        const voices = this.synthesis.getVoices();
        console.log(`🎵 Available voices: ${voices.length}`);
        if (voices.length > 0) {
          // PRIORITY: FEMININE voices that sound young and sweet
          const preferredVoices = [
            // macOS Premium Female Voices (highest quality)
            voices.find(v => v.name.includes('Samantha') && v.name.includes('Premium')),
            voices.find(v => v.name === 'Samantha'),  // Young female voice
            voices.find(v => v.name.includes('Ava')),   // Feminine
            voices.find(v => v.name.includes('Allison')), // Feminine
            voices.find(v => v.name.includes('Victoria')), // Feminine
            voices.find(v => v.name.includes('Karen')),
            
            // Windows Female Voices  
            voices.find(v => v.name.includes('Microsoft Zira')), // Female
            voices.find(v => v.name.includes('Microsoft Aria')), // Female natural
            voices.find(v => v.name.includes('Microsoft Jenny')), // Female
            
            // Google Female voices
            voices.find(v => v.name.includes('Google US English Female')),
            voices.find(v => v.lang === 'en-US' && v.name.toLowerCase().includes('female')),
            
            // Any English female voice
            voices.find(v => v.lang === 'en-US' && v.localService),
            voices.find(v => v.lang.startsWith('en') && v.localService),
            voices.find(v => v.lang === 'en-US'),
            voices.find(v => v.lang.startsWith('en'))
          ];
          
          const selectedVoice = preferredVoices.find(v => v) || voices[0];
          utterance.voice = selectedVoice;
          console.log(`🎤 Using voice: ${selectedVoice?.name}`);
        }
      };

      // Voices might not be loaded yet
      if (this.synthesis.getVoices().length === 0) {
        this.synthesis.addEventListener('voiceschanged', setVoice, { once: true });
      } else {
        setVoice();
      }

      utterance.onend = () => {
        console.log('🔇 AI finished speaking - resuming recognition');
        this.resumeRecognitionAfterSpeech();
        resolve();
      };
      
      utterance.onerror = (error) => {
        console.error('Speech synthesis error:', error);
        this.resumeRecognitionAfterSpeech(); // Resume even on error
        reject(error);
      };

      this.synthesis.speak(utterance);
    });
  }

  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
      // Also resume recognition if speaking was stopped manually
      this.resumeRecognitionAfterSpeech();
    }
  }

  // ECHO PREVENTION METHODS
  pauseRecognitionForSpeech() {
    console.log('🔇 Pausing speech recognition - AI is speaking');
    this.isAISpeaking = true;
    if (typeof window !== 'undefined') {
      window.aiIsSpeaking = true;
    }
    
    // Clear any pending resume
    if (this.pendingResume) {
      clearTimeout(this.pendingResume);
      this.pendingResume = null;
    }
    
    // Pause recognition if it's running
    if (this.recognition && !this.recognitionPaused) {
      try {
        this.recognition.abort(); // Stop current recognition
        this.recognitionPaused = true;
      } catch (e) {
        console.log('Recognition pause error (safe to ignore):', e);
      }
    }
  }

  resumeRecognitionAfterSpeech() {
    console.log('🎙️ Resuming speech recognition - AI finished speaking');
    this.isAISpeaking = false;
    if (typeof window !== 'undefined') {
      window.aiIsSpeaking = false;
    }
    
    // Add a small delay to ensure audio output is completely finished
    this.pendingResume = setTimeout(() => {
      if (this.recognitionPaused && this._autoRestart && this._lastResultHandler) {
        try {
          console.log('🔄 Restarting recognition after AI speech');
          this.recognition.start();
          this.recognitionPaused = false;
        } catch (e) {
          console.log('Recognition restart after speech error:', e);
          // Try again after a bit more delay
          setTimeout(() => {
            try {
              this.recognition.start();
              this.recognitionPaused = false;
            } catch (e2) {
              console.log('Second restart attempt failed:', e2);
            }
          }, 500);
        }
      }
      this.pendingResume = null;
    }, 800); // 800ms delay to ensure audio is completely done
  }

  // Check if AI is currently speaking
  isAiSpeaking() {
    return this.isAISpeaking;
  }

  cancel() {
    // Alias for stopSpeaking - stops both speech and recognition
    this.stopSpeaking();
    this.stopRecognition();
  }

  getVoices() {
    return this.synthesis ? this.synthesis.getVoices() : [];
  }

  // Calculate how well a transcript captures mixed Hindi-English
  calculateMixedLanguageScore(text) {
    if (!text) return 0;
    
    const englishWords = text.match(/[a-zA-Z]+/g) || [];
    const hindiWords = text.match(/[\u0900-\u097F]+/g) || [];  
    
    // Common Hindi words in Roman script
    const romanHindiWords = ['mein', 'main', 'hoon', 'hai', 'kar', 'raha', 'rahe', 'kya', 'aur', 'par', 'kaam', 'kuch', 'accha', 'theek', 'nahi', 'haan'];
    const romanHindiCount = romanHindiWords.filter(word => text.toLowerCase().includes(word)).length;
    
    // Score based on language diversity
    let score = 0;
    if (englishWords.length > 0) score += englishWords.length * 0.5;
    if (hindiWords.length > 0) score += hindiWords.length * 1;
    if (romanHindiCount > 0) score += romanHindiCount * 1.5; // Prefer Roman Hindi
    
    // Bonus for mixed sentences
    if (englishWords.length > 0 && (hindiWords.length > 0 || romanHindiCount > 0)) {
      score += 5; // Mixed language bonus
    }
    
    return score;
  }
}

export default new SpeechService();
