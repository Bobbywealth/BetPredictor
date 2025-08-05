# 🗄️ Database Setup Guide - Supabase Integration

This guide will help you set up a PostgreSQL database using Supabase for the Spizo sports prediction platform.

## 🚀 Quick Setup

### 1. Create Supabase Account
1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign up with GitHub or email

### 2. Create New Project
1. Click "New Project"
2. Choose your organization
3. Enter project details:
   - **Name**: `spizo-predictions`
   - **Database Password**: Choose a strong password
   - **Region**: Select closest to your users
4. Click "Create new project"

### 3. Get API Credentials
1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://abc123.supabase.co`)
   - **anon/public key** (starts with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

### 4. Set Environment Variables

#### For Local Development:
Create a `.env` file in your project root:
```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

#### For Streamlit Cloud:
1. Go to your app settings in Streamlit Cloud
2. Click "Secrets"
3. Add these secrets:
```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-anon-key-here"
```

## 📊 Database Schema

The app automatically creates these tables:

### `users` Table
```sql
CREATE TABLE users (
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
```

### `predictions` Table
```sql
CREATE TABLE predictions (
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
    created_at TIMESTAMP DEFAULT NOW()
);
```

### `api_usage` Table
```sql
CREATE TABLE api_usage (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost DECIMAL(8,4) DEFAULT 0.0,
    request_type VARCHAR(50),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Features Enabled by Database

### ✅ What You Get:
- **Persistent Storage**: All predictions saved permanently
- **User Management**: Real user accounts and authentication
- **API Cost Tracking**: Real-time cost monitoring
- **Prediction History**: Track accuracy over time
- **Analytics**: Performance metrics and trends
- **Admin Dashboard**: Comprehensive management tools

### 🚀 Advanced Features:
- **Real-time Updates**: Live prediction updates
- **Data Analytics**: SQL-powered insights
- **Backup & Recovery**: Automatic backups
- **Scalability**: Handle millions of predictions
- **Security**: Row-level security policies

## 🛠️ Manual Table Creation (if needed)

If automatic table creation fails, run this SQL in Supabase:

```sql
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

-- Create predictions table
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_predictions_user_date ON predictions(user_id, game_date);
CREATE INDEX IF NOT EXISTS idx_api_usage_date ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
```

## 🔒 Security (Row Level Security)

Enable RLS for better security:

```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can view own predictions" ON predictions
    FOR SELECT USING (auth.uid()::text = user_id::text);
```

## 🚨 Troubleshooting

### Connection Issues:
1. Check your `SUPABASE_URL` and `SUPABASE_ANON_KEY`
2. Ensure your project is active (not paused)
3. Check Supabase dashboard for any errors

### Table Creation Issues:
1. Run the manual SQL above in Supabase SQL Editor
2. Check for proper permissions
3. Ensure extensions are installed

### Performance Issues:
1. Add database indexes
2. Consider connection pooling
3. Monitor Supabase dashboard metrics

## 📈 Monitoring

Monitor your database usage:
1. Go to Supabase Dashboard
2. Check **Database** → **Usage**
3. Monitor API requests, storage, and bandwidth

## 💰 Pricing

Supabase offers:
- **Free Tier**: 2 databases, 500MB storage, 2GB bandwidth
- **Pro Tier**: $25/month - Production ready
- **Team/Enterprise**: Custom pricing

Perfect for getting started with real data storage! 🚀