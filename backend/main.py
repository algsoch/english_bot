"""
FastAPI Main Application with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
import json
from datetime import datetime
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

from .config import settings
from .database import get_db, engine, Base
from .models import User, Conversation, Message, MessageFeedback
from .schemas import (
    UserCreate, UserResponse, ConversationCreate, ConversationResponse,
    MessageResponse, ProgressResponse
)
from .ai_service import ai_service

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI(
    title="AI Speaking Partner API",
    description="Advanced English learning platform with AI conversations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"🔌 User {user_id} CONNECTED via WebSocket")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"❌ User {user_id} DISCONNECTED")
    
    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

# Health check
@app.get("/")
async def root():
    logger.info("📡 GET / - Health check request")
    return {
        "status": "online",
        "service": "AI Speaking Partner",
        "ollama_model": settings.OLLAMA_MODEL
    }

@app.get("/health")
async def health_check():
    """Check if Ollama is running"""
    logger.info("📡 GET /health - System health check")
    try:
        # Test Ollama connection
        response = ai_service.client.list()
        logger.info("✅ Ollama connection healthy")
        return {
            "status": "healthy",
            "ollama": "connected",
            "models": [model['name'] for model in response.get('models', [])]
        }
    except Exception as e:
        logger.warning(f"⚠️ Ollama not connected: {e}")
        return {
            "status": "unhealthy",
            "ollama": "disconnected",
            "error": str(e)
        }

# User endpoints
@app.post("/api/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user or return existing user"""
    logger.info(f"📥 POST /api/users - Creating user: {user.email}")
    
    # Check if user already exists by email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        logger.info(f"👤 Existing user found: ID={existing_user.id}, Name={existing_user.username}")
        return existing_user
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        # Modify username to make it unique
        import random
        user.username = f"{user.username}_{random.randint(1000, 9999)}"
        logger.info(f"📝 Username modified to: {user.username}")
    
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"✅ New user created: ID={db_user.id}, Name={db_user.username}, Level={db_user.english_level}")
    return db_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    logger.info(f"📥 GET /api/users/{user_id} - Fetching user")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"⚠️ User {user_id} not found")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/users", response_model=List[UserResponse])
async def list_users(db: Session = Depends(get_db)):
    """List all users"""
    logger.info("📥 GET /api/users - Listing all users")
    return db.query(User).all()

# Conversation endpoints
@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Start a new conversation"""
    logger.info(f"📥 POST /api/conversations - New conversation for User {user_id}, Mode: {conversation.mode}")
    
    db_conversation = Conversation(
        user_id=user_id,
        **conversation.model_dump()
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    logger.info(f"✅ Conversation created: ID={db_conversation.id}, Topic: {db_conversation.topic}")
    return db_conversation

@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """Get conversation details"""
    logger.info(f"📥 GET /api/conversations/{conversation_id}")
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        logger.warning(f"⚠️ Conversation {conversation_id} not found")
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.get("/api/users/{user_id}/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(user_id: int, limit: int = 20, db: Session = Depends(get_db)):
    """Get user's conversation history"""
    logger.info(f"📥 GET /api/users/{user_id}/conversations - Fetching history")
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user_id
    ).order_by(Conversation.started_at.desc()).limit(limit).all()
    logger.info(f"📋 Found {len(conversations)} conversations for user {user_id}")
    return conversations

@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages in a conversation"""
    logger.info(f"📥 GET /api/conversations/{conversation_id}/messages")
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    logger.info(f"💬 Found {len(messages)} messages in conversation {conversation_id}")
    return messages

@app.post("/api/conversations/{conversation_id}/end")
async def end_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """End an active conversation and generate summary"""
    logger.info(f"📥 POST /api/conversations/{conversation_id}/end - Ending conversation")
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        logger.warning(f"⚠️ Conversation {conversation_id} not found")
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Generate conversation summary before ending
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    if messages:
        message_dicts = [{"role": m.role, "content": m.content} for m in messages]
        user = db.query(User).filter(User.id == conversation.user_id).first()
        user_name = user.full_name or user.username if user else None
        
        # Generate summary using AI service
        summary = await ai_service.generate_conversation_summary(message_dicts, user_name)
        conversation.summary = summary
        logger.info(f"📝 Generated summary: '{summary}'")
        
        # Count Hindi translations and grammar corrections
        ai_messages = [m for m in messages if m.role == 'assistant']
        hindi_count = sum(1 for m in ai_messages if 'hindi' in m.content.lower() or 'understood!' in m.content)
        grammar_count = sum(1 for m in ai_messages if any(word in m.content.lower() for word in ['correct', 'should be', 'try saying']))
        
        conversation.hindi_words_translated = hindi_count
        conversation.grammar_corrections = grammar_count
    else:
        conversation.summary = "Quick chat"
    
    conversation.is_active = False
    conversation.ended_at = datetime.utcnow()
    
    # Calculate duration
    if conversation.started_at:
        duration = (conversation.ended_at - conversation.started_at).total_seconds()
        conversation.duration_seconds = int(duration)
    
    db.commit()
    logger.info(f"✅ Conversation {conversation_id} ended - Summary: '{conversation.summary}' - Duration: {conversation.duration_seconds}s")
    return {"status": "ended", "duration_seconds": conversation.duration_seconds, "summary": conversation.summary}

# Progress endpoint
@app.get("/api/users/{user_id}/progress", response_model=List[ProgressResponse])
async def get_user_progress(user_id: int, days: int = 7, db: Session = Depends(get_db)):
    """Get user's learning progress"""
    from .models import UserProgress
    from datetime import date, timedelta
    
    start_date = date.today() - timedelta(days=days)
    
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.date >= start_date
    ).order_by(UserProgress.date).all()
    
    return progress

@app.get("/api/users/{user_id}/insights")
async def get_user_learning_insights(user_id: int, db: Session = Depends(get_db)):
    """Get personalized learning insights for user"""
    logger.info(f"📥 GET /api/users/{user_id}/insights - Analyzing learning patterns")
    
    try:
        insights = await ai_service.analyze_user_learning_patterns(user_id, db)
        logger.info(f"🧠 Generated insights: {len(str(insights))} chars")
        return insights
    except Exception as e:
        logger.error(f"🚨 Insights generation error: {e}")
        return {"error": "Could not generate insights", "details": str(e)}

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{user_id}/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time voice chat"""
    logger.info(f"🔌 WebSocket connection request: User={user_id}, Conversation={conversation_id}")
    await manager.connect(str(user_id), websocket)
    
    try:
        # Get conversation and user info
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not conversation or not user:
            logger.error(f"❌ Invalid conversation or user: User={user_id}, Conv={conversation_id}")
            await websocket.close(code=1008, reason="Invalid conversation or user")
            return
        
        logger.info(f"✅ WebSocket ready: User={user.username}, Mode={conversation.mode}, Level={user.english_level}")
        
        # Load conversation history
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        logger.info(f"📜 Loaded {len(messages)} previous messages")
        
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to AI Speaking Partner",
            "mode": conversation.mode,
            "user_level": user.english_level
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "user_message":
                user_text = data.get("content", "")
                logger.info(f"💬 USER [{user.username}]: \"{user_text[:100]}{'...' if len(user_text) > 100 else ''}\"")
                
                # Save user message
                user_msg = Message(
                    conversation_id=conversation_id,
                    role="user",
                    content=user_text,
                    audio_duration=data.get("audio_duration")
                )
                db.add(user_msg)
                db.commit()
                
                # Add to conversation history
                conversation_history.append({"role": "user", "content": user_text})
                
                # Generate AI response
                logger.info(f"🤖 Generating AI response using Groq...")
                
                # Ensure user_level is a valid string
                user_level = user.english_level or "intermediate"
                if not isinstance(user_level, str):
                    user_level = "intermediate"
                
                ai_result = await ai_service.generate_response(
                    user_message=user_text,
                    conversation_history=conversation_history,
                    mode=conversation.mode,
                    user_level=user_level,
                    user_name=user.full_name or user.username,
                    personality=data.get("personality", "teacher")
                )
                
                logger.info(f"🤖 AI: \"{ai_result['response'][:100]}{'...' if len(ai_result['response']) > 100 else ''}\"")
                
                # Save AI response
                ai_msg = Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=ai_result["response"]
                )
                db.add(ai_msg)
                db.commit()
                
                # Add to conversation history
                conversation_history.append({"role": "assistant", "content": ai_result["response"]})
                
                # Send AI response
                await websocket.send_json({
                    "type": "ai_response",
                    "content": ai_result["response"],
                    "feedback": ai_result.get("feedback", []),
                    "timestamp": datetime.utcnow().isoformat()
                })
                logger.info(f"📤 Response sent to user {user.username}")
                
                # Save feedback if any
                for fb in ai_result.get("feedback", []):
                    feedback = MessageFeedback(
                        message_id=user_msg.id,
                        feedback_type=fb.get("type"),
                        suggestion=fb.get("suggestion"),
                        severity=fb.get("severity", "info")
                    )
                    db.add(feedback)
                
                db.commit()
    
    except WebSocketDisconnect:
        manager.disconnect(str(user_id))
        logger.info(f"❌ User {user_id} disconnected (WebSocket closed)")
    except Exception as e:
        logger.error(f"🚨 WebSocket error: {e}")
        manager.disconnect(str(user_id))
