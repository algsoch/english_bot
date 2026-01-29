"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    native_language: Optional[str] = "unknown"
    english_level: Optional[str] = "intermediate"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True

# Conversation schemas
class ConversationCreate(BaseModel):
    topic: Optional[str] = None
    mode: str = "free_talk"

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    topic: Optional[str]
    mode: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: int
    message_count: int
    is_active: bool
    
    class Config:
        from_attributes = True

# Message schemas
class MessageCreate(BaseModel):
    content: str
    audio_duration: Optional[float] = None

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    audio_duration: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Feedback schema
class FeedbackResponse(BaseModel):
    id: int
    feedback_type: str
    original_text: Optional[str]
    corrected_text: Optional[str]
    suggestion: Optional[str]
    severity: str
    
    class Config:
        from_attributes = True

# WebSocket message types
class WSMessage(BaseModel):
    type: str  # "user_message", "ai_response", "feedback", "status"
    content: str
    feedback: Optional[List[FeedbackResponse]] = None
    timestamp: Optional[datetime] = None

# Progress schema
class ProgressResponse(BaseModel):
    date: str
    total_conversations: int
    total_messages: int
    speaking_time_seconds: int
    vocabulary_learned: int
    grammar_corrections: int
    
    class Config:
        from_attributes = True
