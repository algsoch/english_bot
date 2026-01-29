#!/usr/bin/env python3
"""
Learning Analytics Generator
Analyze conversation data to generate insights and improve learning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from sqlalchemy import text
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re

def analyze_conversation_patterns():
    """Generate learning insights from existing conversations"""
    db = SessionLocal()
    
    try:
        print("🧠 LEARNING ANALYTICS GENERATOR")
        print("=" * 50)
        
        # Get all conversations with messages
        query = """
        SELECT c.id, c.user_id, c.mode, c.started_at, c.message_count,
               string_agg(m.content, '|||') as all_messages,
               string_agg(m.role, '|||') as all_roles
        FROM conversations c
        LEFT JOIN messages m ON c.id = m.conversation_id
        WHERE c.message_count > 0
        GROUP BY c.id, c.user_id, c.mode, c.started_at, c.message_count
        ORDER BY c.started_at DESC
        LIMIT 20
        """
        
        result = db.execute(text(query))
        conversations = result.fetchall()
        
        print(f"📊 Analyzing {len(conversations)} conversations...")
        
        user_patterns = defaultdict(lambda: {
            'total_conversations': 0,
            'modes_used': Counter(),
            'hindi_words': set(),
            'common_errors': [],
            'improvement_areas': set(),
            'vocabulary_learned': set(),
            'conversation_topics': set(),
            'average_message_length': 0,
            'total_messages': 0
        })
        
        for conv in conversations:
            user_id = conv.user_id
            user_patterns[user_id]['total_conversations'] += 1
            user_patterns[user_id]['modes_used'][conv.mode] += 1
            
            if conv.all_messages and conv.all_roles:
                messages = conv.all_messages.split('|||')
                roles = conv.all_roles.split('|||')
                
                user_messages = [msg for msg, role in zip(messages, roles) if role == 'user']
                ai_messages = [msg for msg, role in zip(messages, roles) if role == 'assistant']
                
                user_patterns[user_id]['total_messages'] += len(user_messages)
                
                # Analyze user messages for learning patterns
                for msg in user_messages:
                    # Find Hindi words (Devanagari script)
                    hindi_words = re.findall(r'[\u0900-\u097F]+', msg)
                    user_patterns[user_id]['hindi_words'].update(hindi_words)
                    
                    # Estimate message length
                    user_patterns[user_id]['average_message_length'] += len(msg.split())
                
                # Analyze AI responses for corrections and translations
                for ai_msg in ai_messages:
                    # Look for correction patterns
                    if "correct" in ai_msg.lower() or "better" in ai_msg.lower():
                        user_patterns[user_id]['improvement_areas'].add("Grammar corrections needed")
                    
                    # Look for translation patterns
                    if "you said" in ai_msg.lower() and ("hindi" in ai_msg.lower() or "english" in ai_msg.lower()):
                        user_patterns[user_id]['improvement_areas'].add("Translation practice")
                    
                    # Extract vocabulary from teaching responses
                    if "pronunciation" in conv.mode:
                        user_patterns[user_id]['conversation_topics'].add("Pronunciation practice")
                    elif "grammar" in conv.mode:
                        user_patterns[user_id]['conversation_topics'].add("Grammar focus")
                    elif "free_talk" in conv.mode:
                        user_patterns[user_id]['conversation_topics'].add("Free conversation")
        
        # Calculate averages
        for user_id in user_patterns:
            if user_patterns[user_id]['total_messages'] > 0:
                user_patterns[user_id]['average_message_length'] /= user_patterns[user_id]['total_messages']
        
        print("\n🎯 USER LEARNING PATTERNS:")
        print("-" * 40)
        
        for user_id, patterns in user_patterns.items():
            print(f"\n👤 User {user_id}:")
            print(f"   📈 Total conversations: {patterns['total_conversations']}")
            print(f"   🎮 Preferred modes: {dict(patterns['modes_used'])}")
            print(f"   🗣️  Hindi words used: {len(patterns['hindi_words'])}")
            print(f"   📝 Average message length: {patterns['average_message_length']:.1f} words")
            print(f"   🎯 Topics discussed: {list(patterns['conversation_topics'])}")
            print(f"   📊 Improvement areas: {list(patterns['improvement_areas'])}")
            
            if patterns['hindi_words']:
                print(f"   🇮🇳 Hindi vocabulary: {list(patterns['hindi_words'])[:5]}...")
        
        # Generate conversation summaries for recent conversations
        print("\n📋 GENERATING CONVERSATION SUMMARIES...")
        print("-" * 40)
        
        summary_updates = []
        for conv in conversations[:10]:  # Top 10 recent conversations
            if conv.all_messages:
                messages = conv.all_messages.split('|||')
                roles = conv.all_roles.split('|||')
                
                # Create conversation summary
                user_messages = [msg for msg, role in zip(messages, roles) if role == 'user']
                ai_messages = [msg for msg, role in zip(messages, roles) if role == 'assistant']
                
                hindi_count = sum(1 for msg in user_messages if re.search(r'[\u0900-\u097F]', msg))
                correction_count = sum(1 for msg in ai_messages if "correct" in msg.lower())
                translation_count = sum(1 for msg in ai_messages if "you said" in msg.lower())
                
                summary = f"{conv.mode} practice: {len(user_messages)} user msgs, {hindi_count} Hindi, {correction_count} corrections"
                
                # Update database with summary and analytics
                update_query = """
                UPDATE conversations 
                SET summary = :summary,
                    hindi_words_translated = :hindi_count,
                    grammar_corrections = :correction_count,
                    vocabulary_learned = :vocab,
                    user_progress_notes = :notes
                WHERE id = :conv_id
                """
                
                vocab_learned = f"Mode: {conv.mode}, Messages: {len(user_messages)}"
                notes = f"Hindi usage: {hindi_count}, Corrections: {correction_count}, Translations: {translation_count}"
                
                summary_updates.append({
                    'conv_id': conv.id,
                    'summary': summary,
                    'hindi_count': hindi_count,
                    'correction_count': correction_count,
                    'vocab': vocab_learned,
                    'notes': notes
                })
        
        # Apply updates
        for update in summary_updates:
            db.execute(text("""
                UPDATE conversations 
                SET summary = :summary,
                    hindi_words_translated = :hindi_count,
                    grammar_corrections = :correction_count,
                    vocabulary_learned = :vocab,
                    user_progress_notes = :notes
                WHERE id = :conv_id
            """), update)
            print(f"✅ Updated conversation {update['conv_id']}: {update['summary']}")
        
        db.commit()
        
        print(f"\n🎉 Learning analytics generated for {len(user_patterns)} users!")
        print(f"📊 Updated {len(summary_updates)} conversation summaries")
        
        # Generate overall insights
        print("\n🔍 OVERALL LEARNING INSIGHTS:")
        print("-" * 40)
        
        total_conversations = sum(p['total_conversations'] for p in user_patterns.values())
        mode_distribution = Counter()
        for p in user_patterns.values():
            mode_distribution.update(p['modes_used'])
        
        print(f"📈 Total learning sessions: {total_conversations}")
        print(f"🎮 Most popular modes: {dict(mode_distribution.most_common(3))}")
        
        hindi_users = sum(1 for p in user_patterns.values() if len(p['hindi_words']) > 0)
        print(f"🇮🇳 Users practicing Hindi: {hindi_users}/{len(user_patterns)}")
        
        improvement_areas = Counter()
        for p in user_patterns.values():
            improvement_areas.update(p['improvement_areas'])
        print(f"🎯 Common improvement areas: {dict(improvement_areas)}")
        
        return user_patterns
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    analyze_conversation_patterns()