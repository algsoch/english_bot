#!/usr/bin/env python3
"""
Fix User Progress Table Structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from sqlalchemy import text

def fix_user_progress_table():
    """Fix user_progress table structure"""
    db = SessionLocal()
    
    try:
        print("🔧 FIXING USER PROGRESS TABLE")
        print("=" * 30)
        
        # Check current structure
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='user_progress' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print("Current columns:")
        for col in columns:
            print(f"  {col[0]} ({col[1]})")
        
        # The issue is vocabulary_learned column conflicts
        # Let's rename the existing one and add the new text fields
        
        fixes = [
            # Rename conflicting column
            "ALTER TABLE user_progress RENAME COLUMN vocabulary_learned TO vocabulary_count",
            
            # Add proper text fields for analytics
            "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS vocabulary_words TEXT",
            "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS learning_notes TEXT"
        ]
        
        for fix in fixes:
            try:
                db.execute(text(fix))
                print(f"✅ Applied: {fix}")
            except Exception as e:
                print(f"⚠️  Skip: {e}")
        
        db.commit()
        
        # Check final structure
        result = db.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name='user_progress' 
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print("\nFinal structure:")
        for col in columns:
            print(f"  {col[0]} ({col[1]})")
        
        # Insert sample progress data with correct structure
        sample_data = {
            'user_id': 3,
            'date': '2026-01-29',
            'total_conversations': 11,
            'total_messages': 30,
            'speaking_time_seconds': 0,
            'vocabulary_count': 5,
            'common_mistakes': '["Grammar focus needed", "Translation practice"]',
            'improvement_areas': '["Grammar corrections", "Sentence structure"]',
            'strong_points': '["Regular practice", "Diverse modes"]',
            'hindi_usage_frequency': 0,
            'english_confidence_score': 60,
            'topics_discussed': '["Pronunciation", "Grammar", "Free talk"]',
            'vocabulary_words': 'pronunciation, grammar, travel, conversation',
            'learning_notes': 'User shows consistent engagement, needs grammar focus'
        }
        
        # Insert or update
        db.execute(text("""
            INSERT INTO user_progress (
                user_id, date, total_conversations, total_messages, speaking_time_seconds,
                vocabulary_count, common_mistakes, improvement_areas, strong_points,
                hindi_usage_frequency, english_confidence_score, topics_discussed,
                vocabulary_words, learning_notes
            ) VALUES (
                :user_id, :date, :total_conversations, :total_messages, :speaking_time_seconds,
                :vocabulary_count, :common_mistakes, :improvement_areas, :strong_points,
                :hindi_usage_frequency, :english_confidence_score, :topics_discussed,
                :vocabulary_words, :learning_notes
            )
            ON CONFLICT (user_id, date) DO UPDATE SET
                total_conversations = EXCLUDED.total_conversations,
                common_mistakes = EXCLUDED.common_mistakes,
                improvement_areas = EXCLUDED.improvement_areas,
                strong_points = EXCLUDED.strong_points,
                hindi_usage_frequency = EXCLUDED.hindi_usage_frequency,
                english_confidence_score = EXCLUDED.english_confidence_score,
                topics_discussed = EXCLUDED.topics_discussed,
                vocabulary_words = EXCLUDED.vocabulary_words,
                learning_notes = EXCLUDED.learning_notes
        """), sample_data)
        
        db.commit()
        print("✅ Sample user progress data inserted")
        
        # Verify the data
        result = db.execute(text("""
            SELECT user_id, hindi_usage_frequency, english_confidence_score, topics_discussed
            FROM user_progress
            WHERE user_id = 3
        """))
        
        row = result.fetchone()
        if row:
            print(f"\n📊 User 3 Progress:")
            print(f"   Hindi usage: {row[1]}%")
            print(f"   English confidence: {row[2]}%")
            print(f"   Topics: {row[3]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_progress_table()