#!/usr/bin/env python3
"""
Simple Database Inspector - Just check the core data without complex relationships
"""

import sys
import os
from datetime import datetime
from collections import Counter

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from sqlalchemy import text

def inspect_simple():
    """Simple inspection without model relationships"""
    db = SessionLocal()
    
    try:
        print("🔍 ENGLISHBOT DATABASE INSPECTION")
        print("="*50)
        
        # 1. Check tables
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"📊 Tables: {tables}")
        
        # 2. Count records
        print(f"\n📈 Record Counts:")
        for table in ['users', 'conversations', 'messages', 'message_feedback', 'user_progress']:
            if table in tables:
                count = db.execute(text(f"SELECT COUNT(*) FROM {table}")).fetchone()[0]
                print(f"   {table}: {count} records")
        
        # 3. Check table structures
        print(f"\n🏗️  Table Structures:")
        for table in ['users', 'conversations', 'messages']:
            if table in tables:
                print(f"\n{table.upper()}:")
                result = db.execute(text(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position"))
                for col in result.fetchall():
                    print(f"   {col[0]} ({col[1]})")
        
        # 4. Sample data
        print(f"\n👥 USERS:")
        users = db.execute(text("SELECT id, username, full_name, english_level, native_language FROM users LIMIT 5")).fetchall()
        for user in users:
            print(f"   ID {user[0]}: {user[2] or user[1]} (Level: {user[3]}, Native: {user[4]})")
        
        print(f"\n💬 CONVERSATIONS:")
        convs = db.execute(text("SELECT id, user_id, mode, started_at, message_count, duration_seconds FROM conversations ORDER BY started_at DESC LIMIT 10")).fetchall()
        for conv in convs:
            print(f"   ID {conv[0]} (User {conv[1]}): {conv[2]} mode - {conv[4]} messages, {conv[5]}s duration")
            print(f"      Started: {conv[3]}")
        
        # Check if new summary fields exist
        try:
            summaries = db.execute(text("SELECT id, summary, hindi_words_translated, grammar_corrections FROM conversations WHERE summary IS NOT NULL LIMIT 5")).fetchall()
            if summaries:
                print(f"\n📝 CONVERSATION SUMMARIES:")
                for s in summaries:
                    print(f"   ID {s[0]}: \"{s[1]}\" (Hindi: {s[2]}, Grammar: {s[3]})")
            else:
                print(f"\n❌ No conversation summaries found")
        except Exception as e:
            print(f"\n❌ Summary fields don't exist yet: {e}")
        
        print(f"\n💭 RECENT MESSAGES:")
        messages = db.execute(text("SELECT conversation_id, role, content, created_at FROM messages ORDER BY created_at DESC LIMIT 10")).fetchall()
        
        hindi_count = 0
        english_count = 0
        correction_count = 0
        translation_count = 0
        
        for msg in messages:
            content = msg[2]
            role = msg[1]
            
            # Truncate long messages
            display_content = content[:60] + "..." if len(content) > 60 else content
            print(f"   [{role.upper()}] {display_content}")
            
            if role == 'user':
                # Check language
                has_hindi = any('\u0900' <= char <= '\u097F' for char in content) or \
                          any(word in content.lower() for word in ['main', 'mujhe', 'aap', 'tum', 'hai', 'hoon', 'kya'])
                if has_hindi:
                    hindi_count += 1
                else:
                    english_count += 1
            
            elif role == 'assistant':
                # Check for corrections/translations
                content_lower = content.lower()
                if 'understood!' in content_lower and 'in english' in content_lower:
                    translation_count += 1
                elif any(word in content_lower for word in ['correct', 'should be', 'try saying', 'instead of']):
                    correction_count += 1
        
        print(f"\n📊 MESSAGE ANALYSIS (recent 10):")
        print(f"   User messages: Hindi/Mixed: {hindi_count}, English: {english_count}")
        print(f"   AI responses: Translations: {translation_count}, Corrections: {correction_count}")
        
        # 5. Learning opportunities
        print(f"\n🎯 LEARNING INSIGHTS:")
        
        if hindi_count > 0:
            print(f"   ✅ Hindi support is needed - {hindi_count} Hindi messages detected")
        else:
            print(f"   ❌ No Hindi usage detected in recent messages")
            
        if translation_count > 0:
            print(f"   ✅ AI translation feature is working - {translation_count} translations found")
        else:
            print(f"   ❌ No AI translations detected")
            
        if correction_count > 0:
            print(f"   ✅ Grammar correction is active - {correction_count} corrections found")
        else:
            print(f"   ❌ No grammar corrections detected")
        
        # Check conversation patterns
        total_convs = db.execute(text("SELECT COUNT(*) FROM conversations")).fetchone()[0]
        active_convs = db.execute(text("SELECT COUNT(*) FROM conversations WHERE is_active = true")).fetchone()[0]
        
        print(f"\n🔄 CONVERSATION PATTERNS:")
        print(f"   Total conversations: {total_convs}")
        print(f"   Currently active: {active_convs}")
        
        if total_convs > 0:
            avg_duration = db.execute(text("SELECT AVG(duration_seconds) FROM conversations WHERE duration_seconds > 0")).fetchone()[0]
            avg_messages = db.execute(text("SELECT AVG(message_count) FROM conversations WHERE message_count > 0")).fetchone()[0]
            
            print(f"   Average duration: {avg_duration:.1f} seconds" if avg_duration else "   No duration data")
            print(f"   Average messages: {avg_messages:.1f} per conversation" if avg_messages else "   No message count data")
        
        # 6. Recommendations
        print(f"\n🚀 RECOMMENDATIONS:")
        print("   1. ✅ Implement conversation summaries for better history")
        print("   2. ✅ Track Hindi usage and translation effectiveness")
        print("   3. ✅ Monitor grammar correction patterns")
        print("   4. ✅ Add learning progress analytics")
        print("   5. ✅ Personalize responses based on user patterns")
        
        if hindi_count > english_count:
            print("   6. 🔥 HIGH PRIORITY: Improve Hindi recognition - users prefer Hindi")
        
        if translation_count < hindi_count:
            print("   7. 🔥 HIGH PRIORITY: AI needs better Hindi translation training")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    inspect_simple()