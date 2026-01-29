#!/usr/bin/env python3
"""
Database Inspection Tool
- Analyze what's stored in the database
- Check conversation patterns and learning data
- Understand how to improve the learning system
"""

import sys
import os
import json
from datetime import datetime, timedelta
from collections import Counter

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, engine
from backend.models import User, Conversation, Message, MessageFeedback, UserProgress
from sqlalchemy import text, func

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def inspect_database():
    """Main inspection function"""
    db = SessionLocal()
    
    try:
        # 1. Database Overview
        print_header("DATABASE OVERVIEW")
        
        # Check what tables exist
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"Tables in database: {tables}")
        
        # Count records in each table
        print(f"\nRecord counts:")
        user_count = db.query(User).count()
        conv_count = db.query(Conversation).count()
        msg_count = db.query(Message).count()
        feedback_count = db.query(MessageFeedback).count()
        progress_count = db.query(UserProgress).count()
        
        print(f"  Users: {user_count}")
        print(f"  Conversations: {conv_count}")
        print(f"  Messages: {msg_count}")
        print(f"  Message Feedback: {feedback_count}")
        print(f"  User Progress: {progress_count}")
        
        # 2. Users Analysis
        print_header("USERS ANALYSIS")
        users = db.query(User).all()
        
        for user in users:
            print(f"\n👤 User ID {user.id}: {user.full_name or user.username}")
            print(f"   Email: {user.email}")
            print(f"   Native Language: {user.native_language}")
            print(f"   English Level: {user.english_level}")
            print(f"   Created: {user.created_at}")
            print(f"   Last Active: {user.last_active}")
            
            # User's conversation stats
            user_convs = db.query(Conversation).filter(Conversation.user_id == user.id).all()
            user_msgs = db.query(Message).join(Conversation).filter(Conversation.user_id == user.id).all()
            
            print(f"   Total Conversations: {len(user_convs)}")
            print(f"   Total Messages: {len(user_msgs)}")
            
            if user_convs:
                modes = [c.mode for c in user_convs if c.mode]
                mode_counts = Counter(modes)
                print(f"   Favorite modes: {dict(mode_counts)}")
                
                personalities = [c.personality for c in user_convs if hasattr(c, 'personality') and c.personality]
                if personalities:
                    personality_counts = Counter(personalities)
                    print(f"   Personalities used: {dict(personality_counts)}")
        
        # 3. Conversations Analysis
        print_header("CONVERSATIONS ANALYSIS")
        conversations = db.query(Conversation).order_by(Conversation.started_at.desc()).limit(10).all()
        
        print(f"Recent conversations (last 10):")
        for i, conv in enumerate(conversations, 1):
            user = db.query(User).filter(User.id == conv.user_id).first()
            messages = db.query(Message).filter(Message.conversation_id == conv.id).all()
            
            print(f"\n{i}. Conversation ID {conv.id} ({user.username if user else 'Unknown'})")
            print(f"   Summary: {getattr(conv, 'summary', 'No summary')}")
            print(f"   Mode: {conv.mode} | Personality: {getattr(conv, 'personality', 'Not set')}")
            print(f"   Started: {conv.started_at}")
            print(f"   Duration: {conv.duration_seconds}s | Messages: {len(messages)}")
            
            # Check for learning tracking fields
            if hasattr(conv, 'hindi_words_translated'):
                print(f"   Hindi translations: {conv.hindi_words_translated}")
            if hasattr(conv, 'grammar_corrections'):
                print(f"   Grammar corrections: {conv.grammar_corrections}")
            
            # Sample messages
            user_msgs = [m for m in messages if m.role == 'user']
            ai_msgs = [m for m in messages if m.role == 'assistant']
            
            if user_msgs:
                print(f"   Sample user message: \"{user_msgs[0].content[:80]}...\"")
            if ai_msgs:
                print(f"   Sample AI response: \"{ai_msgs[0].content[:80]}...\"")
        
        # 4. Messages Analysis
        print_header("MESSAGES ANALYSIS")
        
        # Get message statistics
        total_user_msgs = db.query(Message).filter(Message.role == 'user').count()
        total_ai_msgs = db.query(Message).filter(Message.role == 'assistant').count()
        
        print(f"Message distribution:")
        print(f"  User messages: {total_user_msgs}")
        print(f"  AI messages: {total_ai_msgs}")
        
        # Analyze recent user messages for patterns
        recent_user_msgs = db.query(Message).filter(Message.role == 'user').order_by(Message.created_at.desc()).limit(20).all()
        
        print(f"\nRecent user messages analysis:")
        hindi_count = 0
        english_count = 0
        mixed_count = 0
        
        for msg in recent_user_msgs:
            content = msg.content.lower()
            
            # Check for Hindi (Devanagari script)
            has_hindi_script = any('\u0900' <= char <= '\u097F' for char in msg.content)
            
            # Check for common Hindi words
            hindi_words = ['main', 'mujhe', 'aap', 'tum', 'hai', 'hoon', 'kya', 'yeh', 'woh', 'accha', 'theek', 'nahi', 'haan']
            has_hindi_words = any(word in content for word in hindi_words)
            
            if has_hindi_script or has_hindi_words:
                if any(english_word in content for english_word in ['the', 'and', 'is', 'was', 'are', 'have', 'will', 'can']):
                    mixed_count += 1
                else:
                    hindi_count += 1
            else:
                english_count += 1
        
        print(f"  Pure English: {english_count}")
        print(f"  Pure Hindi: {hindi_count}")
        print(f"  Mixed Hindi-English: {mixed_count}")
        
        # Show sample messages with their types
        print(f"\nSample messages by type:")
        for msg in recent_user_msgs[:5]:
            content = msg.content
            has_hindi = any('\u0900' <= char <= '\u097F' for char in content) or \
                       any(word in content.lower() for word in ['main', 'mujhe', 'aap', 'tum', 'hai'])
            
            msg_type = "Hindi/Mixed" if has_hindi else "English"
            print(f"  [{msg_type}] \"{content[:60]}...\"")
        
        # 5. AI Response Analysis
        print_header("AI RESPONSE PATTERNS")
        
        recent_ai_msgs = db.query(Message).filter(Message.role == 'assistant').order_by(Message.created_at.desc()).limit(20).all()
        
        correction_indicators = ['correct', 'should be', 'try saying', 'instead of', 'better to say', 'understood! you said', 'in english:']
        translation_indicators = ['understood!', 'in english:', 'try saying:', 'means']
        
        corrections = 0
        translations = 0
        regular_responses = 0
        
        print("Sample AI responses:")
        for msg in recent_ai_msgs[:10]:
            content_lower = msg.content.lower()
            
            is_correction = any(indicator in content_lower for indicator in correction_indicators)
            is_translation = any(indicator in content_lower for indicator in translation_indicators)
            
            if is_translation:
                translations += 1
                response_type = "TRANSLATION"
            elif is_correction:
                corrections += 1
                response_type = "CORRECTION"
            else:
                regular_responses += 1
                response_type = "CHAT"
            
            print(f"  [{response_type}] \"{msg.content[:70]}...\"")
        
        print(f"\nAI response types (last 20):")
        print(f"  Translations: {translations}")
        print(f"  Corrections: {corrections}")
        print(f"  Regular chat: {regular_responses}")
        
        # 6. Learning Opportunities Analysis
        print_header("LEARNING OPPORTUNITIES")
        
        print("What we can improve:")
        
        # Check conversation summaries
        convs_with_summary = db.query(Conversation).filter(Conversation.summary.isnot(None)).count()
        print(f"  Conversations with summaries: {convs_with_summary}/{conv_count}")
        
        # Check learning tracking
        if hasattr(Conversation, 'hindi_words_translated'):
            convs_with_hindi_tracking = db.query(Conversation).filter(Conversation.hindi_words_translated > 0).count()
            print(f"  Conversations with Hindi tracking: {convs_with_hindi_tracking}/{conv_count}")
        
        # User patterns that could be tracked better
        print(f"\nPotential improvements:")
        print(f"  1. Track repeated mistakes across conversations")
        print(f"  2. Measure improvement in grammar over time")
        print(f"  3. Analyze vocabulary growth")
        print(f"  4. Track Hindi dependency reduction")
        print(f"  5. Personalize teaching based on user patterns")
        
        # 7. Database Structure Check
        print_header("DATABASE STRUCTURE")
        
        # Check if new fields exist
        for table_name in ['conversations', 'users', 'messages']:
            try:
                result = db.execute(text(f"SELECT column_name, data_type, is_nullable, column_default FROM information_schema.columns WHERE table_name='{table_name}' ORDER BY ordinal_position"))
                columns = result.fetchall()
                print(f"\n{table_name.upper()} table columns:")
                for col in columns:
                    nullable = "NULLABLE" if col[2] == 'YES' else "NOT NULL"
                    print(f"  {col[0]} ({col[1]}) - {nullable} - Default: {col[3]}")
            except Exception as e:
                print(f"Error checking {table_name}: {e}")
        
        # 8. Recommendations
        print_header("RECOMMENDATIONS")
        
        print("Based on the data analysis:")
        print("1. ✅ Users are mixing Hindi and English - translation feature is needed")
        print("2. ✅ AI is providing corrections - track effectiveness")
        print("3. 🔧 Need better conversation summaries for history")
        print("4. 🔧 Track learning progress across conversations")
        print("5. 🔧 Analyze user improvement patterns")
        print("6. 🔧 Personalize responses based on user history")
        
        if hindi_count + mixed_count > 0:
            print(f"7. ✅ Hindi recognition is critical - {hindi_count + mixed_count} Hindi messages found")
        
        if corrections > 0:
            print(f"8. ✅ Grammar correction is active - {corrections} corrections in recent messages")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🔍 Starting database inspection...")
    inspect_database()
    print(f"\n✅ Database inspection completed!")