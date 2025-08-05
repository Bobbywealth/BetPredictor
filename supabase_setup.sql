-- Spizo Database Setup Script
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0
);

-- Create predictions table with daily betting support
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    home_team VARCHAR(100) NOT NULL,
    away_team VARCHAR(100) NOT NULL,
    sport VARCHAR(50) DEFAULT 'NFL',
    game_date DATE NOT NULL,
    predicted_winner VARCHAR(100) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    ai_analysis JSONB NOT NULL,
    game_data JSONB,
    actual_winner VARCHAR(100),
    was_correct BOOLEAN,
    is_daily_bet BOOLEAN DEFAULT FALSE,
    bet_rank INTEGER,
    bet_amount DECIMAL(8,2) DEFAULT 100.00,
    bet_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create API usage tracking table
CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost DECIMAL(8,4) DEFAULT 0.0,
    request_type VARCHAR(50),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create user sessions table
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create daily betting summary table
CREATE TABLE IF NOT EXISTS daily_betting_summary (
    id SERIAL PRIMARY KEY,
    bet_date DATE NOT NULL UNIQUE,
    total_bets INTEGER DEFAULT 0,
    won_bets INTEGER DEFAULT 0,
    lost_bets INTEGER DEFAULT 0,
    pending_bets INTEGER DEFAULT 0,
    total_wagered DECIMAL(10,2) DEFAULT 0.00,
    total_won DECIMAL(10,2) DEFAULT 0.00,
    net_profit DECIMAL(10,2) DEFAULT 0.00,
    win_rate DECIMAL(5,2) DEFAULT 0.00,
    roi DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_predictions_user_date ON predictions(user_id, game_date);
CREATE INDEX IF NOT EXISTS idx_predictions_daily_bets ON predictions(is_daily_bet, game_date);
CREATE INDEX IF NOT EXISTS idx_api_usage_date ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_daily_summary_date ON daily_betting_summary(bet_date);

-- Insert default admin user (password: sportsbet2024)
INSERT INTO users (username, email, password_hash, is_admin, total_predictions, correct_predictions)
VALUES ('admin', 'admin@spizo.com', '$2b$12$LQv3c1yqBzulbNFXCJHGHeBJa2kE4xRqD8zYKcI8vHjJVhKJ6zO2u', true, 0, 0)
ON CONFLICT (username) DO NOTHING;

-- Create function to update daily betting summary
CREATE OR REPLACE FUNCTION update_daily_betting_summary()
RETURNS TRIGGER AS $$
BEGIN
    -- Update or insert daily summary
    INSERT INTO daily_betting_summary (
        bet_date,
        total_bets,
        won_bets,
        lost_bets,
        pending_bets,
        total_wagered,
        total_won,
        net_profit,
        win_rate,
        roi,
        updated_at
    )
    SELECT 
        NEW.game_date,
        COUNT(*),
        COUNT(*) FILTER (WHERE was_correct = true),
        COUNT(*) FILTER (WHERE was_correct = false),
        COUNT(*) FILTER (WHERE was_correct IS NULL),
        SUM(bet_amount),
        SUM(CASE WHEN was_correct = true THEN bet_amount * 1.91 ELSE 0 END), -- Assuming -110 odds
        SUM(CASE WHEN was_correct = true THEN bet_amount * 0.91 WHEN was_correct = false THEN -bet_amount ELSE 0 END),
        CASE WHEN COUNT(*) FILTER (WHERE was_correct IS NOT NULL) > 0 
             THEN ROUND((COUNT(*) FILTER (WHERE was_correct = true)::decimal / COUNT(*) FILTER (WHERE was_correct IS NOT NULL)) * 100, 2)
             ELSE 0 END,
        CASE WHEN SUM(bet_amount) > 0 
             THEN ROUND((SUM(CASE WHEN was_correct = true THEN bet_amount * 0.91 WHEN was_correct = false THEN -bet_amount ELSE 0 END) / SUM(bet_amount)) * 100, 2)
             ELSE 0 END,
        NOW()
    FROM predictions 
    WHERE is_daily_bet = true AND game_date = NEW.game_date
    ON CONFLICT (bet_date) DO UPDATE SET
        total_bets = EXCLUDED.total_bets,
        won_bets = EXCLUDED.won_bets,
        lost_bets = EXCLUDED.lost_bets,
        pending_bets = EXCLUDED.pending_bets,
        total_wagered = EXCLUDED.total_wagered,
        total_won = EXCLUDED.total_won,
        net_profit = EXCLUDED.net_profit,
        win_rate = EXCLUDED.win_rate,
        roi = EXCLUDED.roi,
        updated_at = EXCLUDED.updated_at;
        
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update daily summary
CREATE TRIGGER trigger_update_daily_betting_summary
    AFTER INSERT OR UPDATE OF was_correct ON predictions
    FOR EACH ROW
    WHEN (NEW.is_daily_bet = true)
    EXECUTE FUNCTION update_daily_betting_summary();

-- Grant necessary permissions
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon;