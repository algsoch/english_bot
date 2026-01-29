"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    native_language = Column(String(50), default="unknown")
    english_level = Column(String(20), default="intermediate")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    learning_insights = relationship("LearningInsight", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(100))
    summary = Column(String(200))  # Brief conversation summary for history
    mode = Column(String(50), default="free_talk")
    personality = Column(String(50), default="teacher")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # Learning progress tracking
    hindi_words_translated = Column(Integer, default=0)
    grammar_corrections = Column(Integer, default=0)
    vocabulary_learned = Column(Text)  # JSON list of new words learned
    user_progress_notes = Column(Text)  # AI's notes on user improvement
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    audio_duration = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    feedback = relationship("MessageFeedback", back_populates="message", cascade="all, delete-orphan")

class MessageFeedback(Base):
    __tablename__ = "message_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(String(50))  # grammar, vocabulary, pronunciation, fluency
    original_text = Column(Text)
    corrected_text = Column(Text)
    suggestion = Column(Text)
    severity = Column(String(20))  # info, warning, error
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    message = relationship("Message", back_populates="feedback")

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, server_default=func.current_date())
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    speaking_time_seconds = Column(Integer, default=0)
    vocabulary_learned = Column(Integer, default=0)
    
    # Detailed learning analytics
    common_mistakes = Column(Text)  # JSON: frequently repeated errors
    improvement_areas = Column(Text)  # JSON: what user needs to work on
    strong_points = Column(Text)     # JSON: what user is good at
    hindi_usage_frequency = Column(Integer, default=0)  # How often they speak Hindi
    english_confidence_score = Column(Integer, default=50)  # 1-100 scale
    topics_discussed = Column(Text)  # JSON: topics user talks about
    
    # Relationships
    user = relationship("User", back_populates="progress")
    
class LearningInsight(Base):
    """Track specific learning insights and patterns"""
    __tablename__ = "learning_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)
    
    insight_type = Column(String(50))  # 'mistake_pattern', 'improvement', 'strength', 'hindi_dependency'
    description = Column(Text)  # What was observed
    example_text = Column(Text)  # User's original text
    corrected_text = Column(Text)  # AI's correction/suggestion
    frequency = Column(Integer, default=1)  # How often this happens
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    grammar_corrections = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="learning_insights")
    conversation = relationship("Conversation")
