#!/usr/bin/env python3
"""
Database Migration Script
Add missing learning analytics columns to existing tables
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from sqlalchemy import text

def migrate_database():
    """Add missing columns to conversations table"""
    db = SessionLocal()
    
    try:
        print("🔄 Starting database migration...")
        
        # Add summary and learning tracking columns
        migrations = [
            ("summary", "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS summary VARCHAR(200)"),
            ("personality", "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS personality VARCHAR(50) DEFAULT 'teacher'"),
            ("hindi_words_translated", "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS hindi_words_translated INTEGER DEFAULT 0"),
            ("grammar_corrections", "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS grammar_corrections INTEGER DEFAULT 0"),
            ("vocabulary_learned", "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS vocabulary_learned TEXT"),
            ("user_progress_notes", "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS user_progress_notes TEXT")
        ]
        
        success_count = 0
        for column_name, query in migrations:
            try:
                db.execute(text(query))
                print(f"✅ Added column: {column_name}")
                success_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⚡ Column {column_name} already exists")
                    success_count += 1
                else:
                    print(f"❌ Failed to add {column_name}: {e}")
        
        # Also add learning analytics fields to user_progress table
        user_progress_migrations = [
            ("common_mistakes", "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS common_mistakes TEXT"),
            ("improvement_areas", "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS improvement_areas TEXT"),
            ("strong_points", "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS strong_points TEXT"),
            ("hindi_usage_frequency", "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS hindi_usage_frequency INTEGER DEFAULT 0"),
            ("english_confidence_score", "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS english_confidence_score INTEGER DEFAULT 50"),
            ("topics_discussed", "ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS topics_discussed TEXT")
        ]
        
        for column_name, query in user_progress_migrations:
            try:
                db.execute(text(query))
                print(f"✅ Added user_progress column: {column_name}")
                success_count += 1
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"⚡ Column {column_name} already exists in user_progress")
                    success_count += 1
                else:
                    print(f"❌ Failed to add {column_name} to user_progress: {e}")
        
        db.commit()
        print(f"\n🎉 Database migration completed! {success_count} operations successful")
        
        # Verify the new structure
        print("\n🔍 Verifying new table structure:")
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='conversations' ORDER BY ordinal_position"))
        conv_columns = [row[0] for row in result.fetchall()]
        print(f"Conversations columns: {conv_columns}")
        
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_progress' ORDER BY ordinal_position"))
        progress_columns = [row[0] for row in result.fetchall()]
        print(f"User progress columns: {progress_columns}")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_database()