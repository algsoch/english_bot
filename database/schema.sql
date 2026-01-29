-- AI Speaking Partner Database Schema
-- English learning platform with conversation tracking

-- Drop existing tables if they exist (for clean setup)
DROP TABLE IF EXISTS message_feedback CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS user_progress CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    native_language VARCHAR(50) DEFAULT 'unknown',
    english_level VARCHAR(20) DEFAULT 'intermediate', -- beginner, intermediate, advanced
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(100),
    mode VARCHAR(50) DEFAULT 'free_talk', -- free_talk, grammar_focus, vocabulary, pronunciation
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

-- Messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant
    content TEXT NOT NULL,
    audio_duration FLOAT, -- for voice messages
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Message feedback (grammar corrections, suggestions)
CREATE TABLE message_feedback (
    id SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50), -- grammar, vocabulary, pronunciation, fluency
    original_text TEXT,
    corrected_text TEXT,
    suggestion TEXT,
    severity VARCHAR(20), -- info, warning, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User progress tracking
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    total_conversations INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    speaking_time_seconds INTEGER DEFAULT 0,
    vocabulary_learned INTEGER DEFAULT 0,
    grammar_corrections INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);

-- Create indexes for better query performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_user_progress_user_date ON user_progress(user_id, date);

-- Insert sample users for testing
INSERT INTO users (username, email, full_name, english_level) VALUES
('demo_user', 'demo@example.com', 'Demo User', 'intermediate'),
('student1', 'student1@example.com', 'Student One', 'beginner');

-- Function to update user's last active timestamp
CREATE OR REPLACE FUNCTION update_user_last_active()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = NEW.user_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update last active time
CREATE TRIGGER trigger_update_last_active
AFTER INSERT ON conversations
FOR EACH ROW
EXECUTE FUNCTION update_user_last_active();

-- Function to update conversation message count
CREATE OR REPLACE FUNCTION update_conversation_message_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET message_count = message_count + 1 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update message count
CREATE TRIGGER trigger_update_message_count
AFTER INSERT ON messages
FOR EACH ROW
EXECUTE FUNCTION update_conversation_message_count();

COMMENT ON TABLE users IS 'Stores user profiles and English learning preferences';
COMMENT ON TABLE conversations IS 'Tracks individual conversation sessions with AI';
COMMENT ON TABLE messages IS 'Stores all messages exchanged during conversations';
COMMENT ON TABLE message_feedback IS 'AI-generated feedback for improving English';
COMMENT ON TABLE user_progress IS 'Daily progress metrics for each user';
