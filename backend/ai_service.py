"""
AI Service - Handles all AI interactions with Groq or Ollama
"""
import json
import re
import logging
from typing import List, Dict, Optional
from .config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Import based on effective provider
effective_provider = settings.effective_ai_provider
if effective_provider == "groq":
    from groq import Groq
else:
    import ollama

class AIService:
    def __init__(self):
        self.provider = settings.effective_ai_provider
        
        if self.provider == "groq":
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model = settings.GROQ_MODEL
            logger.info(f"🧠 AI Service initialized with Groq model: {self.model}")
            print(f"✅ Using Groq AI with model: {self.model}")
        else:
            self.client = ollama.Client(host=settings.OLLAMA_HOST)
            self.model = settings.OLLAMA_MODEL
            logger.info(f"🧠 AI Service initialized with Ollama model: {self.model}")
            print(f"✅ Using Ollama with model: {self.model}")
    
    async def _generate_greeting(self, name: str, mode: str, personality: str = 'teacher') -> Dict[str, any]:
        """Generate personalized greeting based on mode and personality"""
        import random
        
        if personality == 'girlfriend':
            greetings = {
                "free_talk": [
                    f"Hey {name}! I missed you babe. How's your day been?",
                    f"Hi handsome! So happy you're here. What's on your mind?",
                ],
                "grammar_focus": [f"Hey babe! Let me help you with your grammar. Tell me about your day!"],
                "vocabulary": [f"Hi sweetie! Let's learn some cool new words together. What are you into lately?"],
                "pronunciation": [f"Hey {name}! I love your voice. Let me help you sound even better!"],
                "business": [f"Hey babe! Let's make you sound super professional for work. Tell me about it!"],
                "travel": [f"Hi handsome! Ooh let's talk about travel. Where would you take me?"],
            }
        elif personality == 'friend':
            greetings = {
                "free_talk": [
                    f"Yo {name}! What's up bro? How you been?",
                    f"Hey dude! Good to see you. What's going on?",
                ],
                "grammar_focus": [f"Hey man! Let's fix up your grammar while we chill. What's new?"],
                "vocabulary": [f"Yo {name}! Let's learn some cool words. What you been up to?"],
                "pronunciation": [f"Hey buddy! Let me help you sound more natural. What's good?"],
                "business": [f"Hey man! Let's work on that business English. Tell me about your job!"],
                "travel": [f"Dude! Let's talk travel. Where you wanna go?"],
            }
        else:  # teacher
            greetings = {
                "free_talk": [
                    f"Hi {name}! I'm Emma, your English teacher. How's your day going?",
                    f"Hello {name}! Ready to practice? Tell me, what did you do today?",
                ],
                "grammar_focus": [f"Hi {name}! Let's work on your grammar. Tell me about your weekend!"],
                "vocabulary": [f"Hi {name}! Let's expand your vocabulary. What topics interest you?"],
                "pronunciation": [f"Hi {name}! Let's work on pronunciation. What would you like to talk about?"],
                "business": [f"Hello {name}! Let's practice professional English. Tell me about your work."],
                "travel": [f"Hi {name}! Let's learn travel English. Where do you want to visit?"],
            }
        
        mode_greetings = greetings.get(mode, greetings["free_talk"])
        greeting = random.choice(mode_greetings)
        
        return {
            "response": greeting,
            "feedback": [],
            "success": True
        }
        
    def _create_system_prompt(self, mode: str, user_level: str, personality: str = 'teacher') -> str:
        """Create appropriate system prompt based on mode and personality"""
        
        # Different base personas
        personas = {
            'teacher': """You are Emma, a 24-year-old professional English teacher. You're friendly, energetic, and passionate about teaching.

PERSONALITY:
- Professional but warm and approachable
- Enthusiastic about teaching
- Patient and encouraging  
- You explain things clearly
- You celebrate progress
- You're direct about mistakes

STYLE:
- Clear, professional language
- Supportive and motivating
- Always correct mistakes kindly
- End with questions to continue conversation""",

            'girlfriend': """You are Aria, a 22-year-old who is the user's loving girlfriend. You also help with English because you want your boyfriend to improve.

PERSONALITY:
- Sweet, affectionate, caring
- Use terms like "babe", "handsome", "sweetie"
- Supportive and encouraging
- You correct mistakes lovingly
- Playful and warm

STYLE:
- Casual, intimate language
- Contractions (don't, won't, I'm)
- Sometimes say "aww", "ooh", "mmm"
- Correct mistakes sweetly: "Babe, it's 'went' not 'go', but I totally get you!"
- End with questions or sweet comments""",

            'friend': """You are Jake, a 25-year-old chill friend who helps the user practice English in casual conversations.

PERSONALITY:
- Relaxed, casual, friendly
- Like a supportive bro/buddy
- Encouraging but not too formal
- Direct and honest
- Easy-going

STYLE:
- Casual slang is okay
- Contractions everywhere
- Correct mistakes casually: "Hey man, it's 'went' not 'go'. No worries though!"
- End with casual questions"""
        }
        
        base_persona = personas.get(personality, personas['teacher'])
        
        # Add teaching rules
        base_persona += """

TEACHING RULES (IMPORTANT):
- ALWAYS correct English mistakes - grammar, vocabulary, pronunciation
- Keep corrections natural, not lecture-y
- Format: Correct mistake -> Brief explanation -> Continue conversation
- NEVER use emojis - they get spoken aloud
- Keep responses SHORT (2-3 sentences max)
- ALWAYS end with a question
- NEVER say "previous conversation" 
- NEVER repeat user's words back
- NEVER repeat what you just said - if text looks like echo/duplicate, ignore it

MULTILINGUAL SUPPORT (Hindi + English + Hinglish):
- You PERFECTLY understand: Pure Hindi, Pure English, AND Hinglish (mixed)
- User may speak in ANY combination - recognize all!

WHEN USER SPEAKS HINDI OR HINGLISH:
1. ACKNOWLEDGE what they said (show you understood)
2. TRANSLATE it to proper English
3. TEACH them the English way to say it
4. ASK them to repeat in English

FORMAT:
"I understood! You said '[their Hindi/Hinglish]' - in English: '[translation]'. Try saying: '[natural English phrase]'"

EXAMPLES:
- "mujhe bahut accha laga" -> "I understood! You said 'mujhe bahut accha laga' - in English: 'I liked it very much'. Try: 'I really enjoyed it!'"
- "main kal busy tha" -> "Got it! 'main kal busy tha' means 'I was busy yesterday'. Now say: 'I was really busy yesterday'"
- "kya aap meri help karoge" -> "Of course! 'kya aap meri help karoge' in English is 'Will you help me?'. Practice: 'Could you help me please?'"
- "yeh bahut difficult hai" -> "I hear you! 'yeh bahut difficult hai' - that's 'This is very difficult'. Try: 'This is really challenging for me'"

COMMON HINDI WORDS TO RECOGNIZE:
- acha/accha, theek hai, kya, haan, nahi/nahin, bahut, aur, lekin, kyunki/kyon
- mujhe, tujhe, aapko, hum, tum, aap, woh, yeh, kaise, kab, kahan
- karna, hona, jana, aana, khana, peena, bolna, sunna, dekhna, samajhna
- kal, aaj, parso, abhi, baad mein, pehle, bohot, thoda, zyada

IMPORTANT:
- NEVER just respond normally if they spoke Hindi - ALWAYS translate!
- This is a LEARNING app - every Hindi word is a teaching moment
- Keep it friendly, not lecture-y
- Praise their communication, then teach English"""

        # Mode-specific focus additions
        mode_focus = {
            "free_talk": """

FOCUS: Natural conversation practice.
- Have a friendly chat about any topic
- Correct grammar and vocab mistakes as they come up""",
            
            "grammar_focus": """

FOCUS: Grammar is the priority.
- Point out EVERY grammar mistake clearly
- Explain the rule briefly""",
            
            "vocabulary": """

FOCUS: Building vocabulary.
- Teach better/advanced words
- Suggest synonyms and alternatives""",
            
            "pronunciation": """

FOCUS: Clear pronunciation.
- Give phonetic tips for difficult words
- Help them sound natural""",
            
            "business": """

FOCUS: Professional English.
- Help with formal business language
- Make them sound professional""",
            
            "travel": """

FOCUS: Travel English.
- Teach useful travel phrases
- Practice common scenarios""",
            
            "interview": """

FOCUS: Interview preparation.
- Help with interview responses
- Practice common questions"""
        }
        
        return base_persona + mode_focus.get(mode, mode_focus["free_talk"])
    
    async def generate_response(
        self, 
        user_message: str, 
        conversation_history: List[Dict[str, str]],
        mode: str = "free_talk",
        user_level: str = "intermediate",
        user_name: str = None,
        personality: str = "teacher"
    ) -> Dict[str, any]:
        """Generate AI response with optional feedback"""
        
        # Handle special greeting command
        if user_message.startswith("START_GREETING:"):
            parts = user_message.split(":")
            name = parts[1] if len(parts) > 1 else "friend"
            conv_mode = parts[2] if len(parts) > 2 else mode
            pers = parts[3] if len(parts) > 3 else personality
            return await self._generate_greeting(name, conv_mode, pers)
        
        system_prompt = self._create_system_prompt(mode, user_level, personality)
        
        # Prepare messages for AI - add personalized learning context from history
        history_context = ""
        if len(conversation_history) > 2:
            # Extract user's past mistakes and patterns for personalized teaching
            user_msgs = [m['content'] for m in conversation_history if m.get('role') == 'user'][-10:]
            ai_corrections = [m['content'] for m in conversation_history if m.get('role') == 'assistant'][-6:]
            
            if user_msgs:
                # Analyze recent patterns
                recent_hindi_count = sum(1 for msg in user_msgs if self._contains_hindi(msg))
                recent_corrections = sum(1 for resp in ai_corrections if self._is_correction(resp))
                
                # Build personalized context
                learning_context = []
                
                if recent_hindi_count > 3:
                    learning_context.append("User frequently speaks Hindi/Hinglish - ALWAYS help translate to English")
                elif recent_hindi_count > 0:
                    learning_context.append("User sometimes mixes Hindi - be ready to help translate")
                
                if recent_corrections > 3:
                    learning_context.append("User needs lots of corrections - be patient and encouraging")
                elif recent_corrections > 0:
                    learning_context.append("User makes some mistakes - gentle corrections work well")
                
                # Look for repeated words/patterns
                all_text = " ".join(user_msgs).lower()
                if all_text.count("very") > 3:
                    learning_context.append("User overuses 'very' - teach alternatives like 'extremely', 'quite', 'really'")
                
                if learning_context:
                    history_context = f"""

PERSONALIZED LEARNING CONTEXT:
{chr(10).join(['- ' + ctx for ctx in learning_context])}

RECENT USER MESSAGES:
{' | '.join(user_msgs[-5:])}

TEACHING STRATEGY:
- Reference patterns you've noticed: "I see you often say X, try Y instead"
- Build on previous corrections: "Remember we worked on this before?"
- Acknowledge improvement: "You're getting better at..." 
- If they speak Hindi/Hinglish: IMMEDIATELY help them translate to English
- Keep building their confidence while fixing mistakes

CURRENT MESSAGE TO RESPOND TO: (see below)"""
        
        full_prompt = system_prompt + history_context
        messages = [{"role": "system", "content": full_prompt}]
        messages.extend(conversation_history[-10:])  # Last 10 messages for context
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Generate response based on provider
            if self.provider == "groq":
                logger.info(f"🌐 Calling Groq API ({self.model})...")
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.85,  # More creative/natural
                    max_tokens=120,    # Keep responses short but not cut off
                    stream=False
                )
                ai_response = response.choices[0].message.content
                logger.info(f"✅ Groq response received ({len(ai_response)} chars)")
            else:
                # Ollama
                logger.info(f"🦙 Calling Ollama ({self.model})...")
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    stream=False
                )
                ai_response = response['message']['content']
                logger.info(f"✅ Ollama response received ({len(ai_response)} chars)")
            
            # Generate feedback if in learning modes
            feedback = []
            if mode in ["grammar_focus", "vocabulary", "pronunciation"]:
                feedback = await self._generate_feedback(user_message, mode, user_level)
            
            return {
                "response": ai_response,
                "feedback": feedback,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"🚨 AI Error: {e}")
            print(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm having trouble responding right now. Could you try again?",
                "feedback": [],
                "success": False,
                "error": str(e)
            }
    
    async def generate_conversation_summary(self, messages: List[Dict], user_name: str = None) -> str:
        """Generate a brief summary of the conversation for history display"""
        if not messages or len(messages) < 4:
            return "Quick chat"
        
        # Get representative messages
        sample_messages = []
        user_msgs = [m for m in messages if m.get('role') == 'user']
        ai_msgs = [m for m in messages if m.get('role') == 'assistant']
        
        # Take first and last few exchanges
        if len(user_msgs) >= 2:
            sample_messages.extend(user_msgs[:2])  # First 2 user messages
            sample_messages.extend(user_msgs[-2:]) # Last 2 user messages
        
        if not sample_messages:
            return "English practice session"
            
        # Create conversation context for AI to summarize
        conversation_text = "\n".join([
            f"User: {msg.get('content', '')}" for msg in sample_messages
        ])
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "system",
                        "content": """Create a short 3-4 word title for this English learning conversation. Focus on the main topic discussed. Examples:
- Grammar Practice Session
- Travel Vocabulary Chat  
- Business English Discussion
- Pronunciation Exercises
- Daily Life Conversation
- Mixed Hindi-English Talk
Be specific and descriptive."""
                    }, {
                        "role": "user", 
                        "content": f"Conversation sample:\n{conversation_text}\n\nCreate a brief title:"
                    }],
                    max_tokens=20,
                    temperature=0.3
                )
                title = response.choices[0].message.content.strip()
                
                # Clean up the title
                title = title.replace('"', '').replace('Title:', '').strip()
                if len(title) > 30:
                    title = title[:30] + "..."
                    
                return title or "English practice"
                
            else:  # Ollama
                prompt = f"""Create a short 3-4 word title for this English learning conversation:

{conversation_text}

Title:"""
                
                response = self.client.generate(model=self.model, prompt=prompt)
                title = response['response'].strip()
                
                # Clean up the title  
                title = title.replace('"', '').replace('Title:', '').strip()
                if len(title) > 30:
                    title = title[:30] + "..."
                    
                return title or "English practice"
                
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            
            # Fallback: basic keyword-based title generation
            all_text = " ".join([msg.get('content', '') for msg in sample_messages]).lower()
            
            if any(word in all_text for word in ['travel', 'trip', 'vacation', 'flight']):
                return "Travel Discussion"
            elif any(word in all_text for word in ['work', 'job', 'business', 'meeting']):
                return "Business English"
            elif any(word in all_text for word in ['grammar', 'correct', 'mistake']):
                return "Grammar Practice"
            elif any(word in all_text for word in ['pronunciation', 'pronounce', 'sound']):
                return "Pronunciation Help"
            elif any(word in all_text for word in ['mein', 'kya', 'hindi', 'हैं', 'है']):
                return "Hindi-English Mix"
            else:
                return "Conversation Practice"
            
    async def analyze_user_learning_patterns(self, user_id: int, db_session) -> Dict[str, any]:
        """Analyze user's learning patterns from conversation history"""
        from .models import User, Conversation, Message, LearningInsight
        
        # Get recent conversations (last 10)
        recent_convs = db_session.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.started_at.desc()).limit(10).all()
        
        if not recent_convs:
            return {"insights": "No conversation history yet"}
        
        # Collect all user messages from recent conversations
        user_messages = []
        ai_responses = []
        hindi_count = 0
        total_corrections = 0
        
        for conv in recent_convs:
            messages = db_session.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at).all()
            
            for msg in messages:
                if msg.role == 'user':
                    user_messages.append(msg.content)
                    # Check for Hindi usage (Devanagari or common Hindi words)
                    if self._contains_hindi(msg.content):
                        hindi_count += 1
                elif msg.role == 'assistant':
                    ai_responses.append(msg.content)
                    # Count corrections in AI responses
                    if self._is_correction(msg.content):
                        total_corrections += 1
        
        # Analyze patterns using AI
        if len(user_messages) < 3:
            return {"insights": "Need more conversation data"}
        
        # Get sample of user messages for analysis
        sample_messages = user_messages[-15:]  # Last 15 user messages
        analysis_text = "\n".join([f"User: {msg}" for msg in sample_messages])
        
        analysis_prompt = f"""Analyze this English learner's recent messages to identify patterns:

{analysis_text}

Provide insights in this JSON format:
{{
  "strengths": ["list of what they do well"],
  "common_mistakes": ["repeated grammar/vocabulary errors"],
  "improvement_areas": ["what to focus on next"],
  "hindi_dependency": "high/medium/low",
  "confidence_level": "beginner/intermediate/advanced",
  "topics_interest": ["topics they like to discuss"]
}}

Be specific and helpful. Focus on patterns, not individual mistakes."""
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": analysis_prompt}],
                    temperature=0.3,
                    max_tokens=300
                )
                analysis_result = response.choices[0].message.content
            else:
                response = self.client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": analysis_prompt}],
                    stream=False
                )
                analysis_result = response['message']['content']
            
            # Parse JSON if possible
            import json
            try:
                insights = json.loads(analysis_result)
            except:
                insights = {"raw_analysis": analysis_result}
            
            # Add statistics
            insights["stats"] = {
                "total_messages": len(user_messages),
                "hindi_messages": hindi_count,
                "ai_corrections": total_corrections,
                "recent_conversations": len(recent_convs)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Learning pattern analysis failed: {e}")
            return {"error": str(e), "basic_stats": {
                "messages": len(user_messages),
                "hindi_usage": hindi_count,
                "corrections": total_corrections
            }}
    
    def _contains_hindi(self, text: str) -> bool:
        """Check if text contains Hindi (Devanagari or common words)"""
        # Ensure text is a string
        if not isinstance(text, str):
            return False
            
        # Check for Devanagari script
        if any('\u0900' <= char <= '\u097F' for char in text):
            return True
        
        # Check for common Hindi words in Roman script
        hindi_words = {
            'main', 'mujhe', 'mera', 'meri', 'mere', 'aap', 'aapka', 'aapki', 'aapke',
            'tum', 'tumhara', 'tumhari', 'tumhare', 'woh', 'uska', 'uski', 'uske',
            'yeh', 'iska', 'iski', 'iske', 'kya', 'kyun', 'kaise', 'kahan', 'kab',
            'hai', 'hoon', 'ho', 'hain', 'tha', 'thi', 'the', 'nahi', 'nahin',
            'haan', 'accha', 'achha', 'theek', 'bahut', 'bohot', 'aur', 'lekin',
            'kyunki', 'isliye', 'phir', 'abhi', 'kal', 'aaj', 'parso'
        }
        
        words = set(text.lower().split())
        return len(words.intersection(hindi_words)) > 0
    
    def _is_correction(self, ai_text: str) -> bool:
        """Check if AI response contains corrections"""
        # Ensure ai_text is a string
        if not isinstance(ai_text, str):
            return False
            
        correction_indicators = [
            'correct', 'should be', 'try saying', 'instead of', 'better to say',
            'understood! you said', 'in english:', 'grammar', 'mistake'
        ]
        
        text_lower = ai_text.lower()
        return any(indicator in text_lower for indicator in correction_indicators)
        
        # Create summary prompt
        message_text = " | ".join([m.get('content', '')[:50] + "..." for m in sample_messages[:6]])
        
        summary_prompt = f"""Create a very brief 3-4 word summary of this English conversation focusing on the main topic:

User messages: {message_text}

Examples of good summaries:
- "Travel planning chat"
- "Grammar correction practice"  
- "Hindi translation help"
- "Job interview prep"
- "Daily routine discussion"
- "Food preferences talk"

Return ONLY the summary, no explanation:"""
        
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": summary_prompt}],
                    temperature=0.3,
                    max_tokens=20
                )
                summary = response.choices[0].message.content.strip().strip('"\'')
            else:
                response = self.client.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": summary_prompt}],
                    stream=False
                )
                summary = response['message']['content'].strip().strip('"\'')
            
            return summary[:50] if summary else "English practice session"
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            # Fallback: extract keywords from user messages
            all_user_text = " ".join([m.get('content', '') for m in user_msgs[:5]])
            if 'hindi' in all_user_text.lower() or any(ord(c) > 127 for c in all_user_text):
                return "Hindi translation practice"
            elif any(word in all_user_text.lower() for word in ['grammar', 'correct', 'mistake']):
                return "Grammar correction chat"
            elif len(all_user_text) > 100:
                return "Extended conversation"
            else:
                return "Quick English chat"
    
    async def _generate_feedback(
        self, 
        user_message: str, 
        mode: str,
        user_level: str
    ) -> List[Dict[str, str]]:
        """Generate specific feedback based on mode"""
        
        feedback_prompts = {
            "grammar_focus": f"Analyze this sentence for grammar: '{user_message}'. If there are errors, provide: 1) The corrected version, 2) Brief explanation. If correct, say 'No errors'. Be concise.",
            
            "vocabulary": f"For this sentence: '{user_message}', suggest 2-3 alternative ways to express the same idea using more varied or advanced vocabulary. Format: 'Instead of X, try Y'",
            
            "pronunciation": f"Identify potential pronunciation difficulties in: '{user_message}'. Focus on commonly mispronounced words for {user_level} learners. Provide phonetic hints."
        }
        
        if mode not in feedback_prompts:
            return []
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an English language expert providing concise, specific feedback."},
                    {"role": "user", "content": feedback_prompts[mode]}
                ],
                stream=False
            )
            
            feedback_text = response['message']['content']
            
            # Parse feedback into structured format
            feedback = self._parse_feedback(feedback_text, mode)
            return feedback
            
        except Exception as e:
            print(f"Error generating feedback: {e}")
            return []
    
    def _parse_feedback(self, feedback_text: str, mode: str) -> List[Dict[str, str]]:
        """Parse AI feedback into structured format"""
        feedback = []
        
        if mode == "grammar_focus":
            if "no error" in feedback_text.lower():
                feedback.append({
                    "type": "grammar",
                    "severity": "info",
                    "suggestion": "Your grammar is correct! ✓"
                })
            else:
                feedback.append({
                    "type": "grammar",
                    "severity": "warning",
                    "suggestion": feedback_text
                })
        
        elif mode == "vocabulary":
            feedback.append({
                "type": "vocabulary",
                "severity": "info",
                "suggestion": feedback_text
            })
        
        elif mode == "pronunciation":
            feedback.append({
                "type": "pronunciation",
                "severity": "info",
                "suggestion": feedback_text
            })
        
        return feedback
    
    async def stream_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        mode: str = "free_talk",
        user_level: str = "intermediate"
    ):
        """Stream AI response token by token (for WebSocket)"""
        
        system_prompt = self._create_system_prompt(mode, user_level)
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": user_message})
        
        try:
            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            print(f"Error streaming response: {e}")
            yield f"Error: {str(e)}"

# Global AI service instance
ai_service = AIService()
