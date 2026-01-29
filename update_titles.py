#!/usr/bin/env python3
"""
Update Existing Conversations with AI-Generated Titles
Fix all "Quick chat" titles with meaningful conversation summaries
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.ai_service import AIService
from backend.models import Conversation, Message, User
from sqlalchemy import text
import asyncio

async def update_conversation_titles():
    """Update all conversations that have default titles with AI-generated ones"""
    db = SessionLocal()
    ai_service = AIService()
    
    try:
        print("🔄 UPDATING CONVERSATION TITLES")
        print("=" * 40)
        
        # Find conversations with default or missing summaries
        conversations = db.query(Conversation).filter(
            (Conversation.summary == "Quick chat") | 
            (Conversation.summary.is_(None))
        ).order_by(Conversation.started_at.desc()).limit(20).all()
        
        print(f"📊 Found {len(conversations)} conversations to update")
        
        updated_count = 0
        for conv in conversations:
            try:
                # Get messages for this conversation
                messages = db.query(Message).filter(
                    Message.conversation_id == conv.id
                ).order_by(Message.created_at).all()
                
                if len(messages) < 2:
                    print(f"⚠️ Conversation {conv.id}: Too few messages, keeping 'Quick chat'")
                    continue
                
                # Convert to format expected by AI service
                message_dicts = [{"role": m.role, "content": m.content} for m in messages]
                
                # Get user info for better context
                user = db.query(User).filter(User.id == conv.user_id).first()
                user_name = user.username if user else None
                
                # Generate new summary
                print(f"🤖 Generating title for conversation {conv.id} ({len(messages)} messages)...")
                new_summary = await ai_service.generate_conversation_summary(message_dicts, user_name)
                
                # Update the conversation
                if new_summary and new_summary != "Quick chat":
                    conv.summary = new_summary
                    print(f"✅ Updated {conv.id}: '{new_summary}'")
                    updated_count += 1
                else:
                    print(f"⚠️ Conversation {conv.id}: AI returned default title")
                    
            except Exception as e:
                print(f"❌ Error processing conversation {conv.id}: {e}")
        
        # Commit all changes
        db.commit()
        print(f"\n🎉 Successfully updated {updated_count} conversation titles!")
        
        # Show sample of updated conversations
        print(f"\n📋 UPDATED CONVERSATIONS:")
        print("-" * 30)
        updated_convs = db.query(Conversation).filter(
            Conversation.summary != "Quick chat"
        ).order_by(Conversation.started_at.desc()).limit(10).all()
        
        for conv in updated_convs:
            user = db.query(User).filter(User.id == conv.user_id).first()
            username = user.username if user else "Unknown"
            print(f"👤 {username}: {conv.summary}")
        
        return updated_count
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

if __name__ == "__main__":
    result = asyncio.run(update_conversation_titles())