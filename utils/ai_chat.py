import streamlit as st
import openai
import os
from google import genai
from google.genai import types
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import time

class DualAIChat:
    """Enhanced AI Chat system with performance optimizations"""

    def __init__(self):
        # Initialize API clients lazily
        self._openai_client = None
        self._genai_client = None

        # Chat history management
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        if 'chat_context' not in st.session_state:
            st.session_state.chat_context = {
                'current_sport': None,
                'current_games': [],
                'user_preferences': {}
            }

        # Response caching for similar queries
        if 'chat_cache' not in st.session_state:
            st.session_state.chat_cache = {}

    @property
    def openai_client(self):
        """Lazy load OpenAI client"""
        if self._openai_client is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self._openai_client = openai.OpenAI(api_key=api_key)
        return self._openai_client

    @property  
    def genai_client(self):
        """Lazy load Gemini client"""
        if self._genai_client is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                self._genai_client = genai.Client(api_key=api_key)
        return self._genai_client

    def get_chat_response(self, user_message: str, ai_provider: str = "both") -> Dict[str, Any]:
        """Get AI response with performance optimizations"""

        # Check cache first
        cache_key = f"{ai_provider}_{hash(user_message)}"
        if cache_key in st.session_state.chat_cache:
            cached_response = st.session_state.chat_cache[cache_key]
            # Use cache if less than 5 minutes old
            if time.time() - cached_response['timestamp'] < 300:
                return cached_response['response']

        try:
            response = {"timestamp": datetime.now().isoformat()}

            if ai_provider in ["both", "chatgpt"] and self.openai_client:
                response["chatgpt"] = self._get_chatgpt_response(user_message)

            if ai_provider in ["both", "gemini"] and self.genai_client:
                response["gemini"] = self._get_gemini_response(user_message)

            # Cache successful responses
            st.session_state.chat_cache[cache_key] = {
                'response': response,
                'timestamp': time.time()
            }

            return response

        except Exception as e:
            return {
                "error": f"Chat error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _get_chatgpt_response(self, message: str) -> str:
        """Get ChatGPT response with context"""
        try:
            context = self._build_context()

            messages = [
                {"role": "system", "content": f"""You are a sports betting expert assistant. 
                Current context: {context}
                Provide concise, helpful responses about sports analysis and betting insights.
                Focus on facts and statistical analysis."""},
                {"role": "user", "content": message}
            ]

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model for chat
                messages=messages,
                max_tokens=500,  # Limit for faster responses
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"ChatGPT error: {str(e)}"

    def _get_gemini_response(self, message: str) -> str:
        """Get Gemini response with context"""
        try:
            context = self._build_context()

            prompt = f"""You are a sports betting expert assistant.
            Current context: {context}

            User question: {message}

            Provide a concise, helpful response about sports analysis and betting insights.
            Focus on facts and statistical analysis."""

            response = self.genai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text if response.text else "No response generated"

        except Exception as e:
            return f"Gemini error: {str(e)}"

    def _build_context(self) -> str:
        """Build context string for AI responses"""
        context_parts = []

        if st.session_state.chat_context.get('current_sport'):
            context_parts.append(f"Sport: {st.session_state.chat_context['current_sport']}")

        if st.session_state.chat_context.get('current_games'):
            games = st.session_state.chat_context['current_games'][:3]  # Limit context
            context_parts.append(f"Current games: {', '.join(games)}")

        return "; ".join(context_parts) if context_parts else "General sports discussion"

    def add_to_history(self, user_message: str, ai_response: Dict[str, Any]):
        """Add exchange to chat history with size limits"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response
        }

        st.session_state.chat_history.append(entry)

        # Keep only last 20 exchanges for performance
        if len(st.session_state.chat_history) > 20:
            st.session_state.chat_history = st.session_state.chat_history[-20:]

    def clear_history(self):
        """Clear chat history and cache"""
        st.session_state.chat_history = []
        st.session_state.chat_cache = {}

    def update_context(self, sport: str = None, games: List[str] = None):
        """Update chat context for better responses"""
        if sport:
            st.session_state.chat_context['current_sport'] = sport
        if games:
            st.session_state.chat_context['current_games'] = games

    def get_suggested_questions(self) -> List[str]:
        """Get context-aware suggested questions"""
        base_questions = [
            "What are today's best betting opportunities?",
            "Analyze the upcoming games for value bets",
            "What should I know about tonight's matchups?",
            "Compare the AI predictions for accuracy"
        ]

        current_sport = st.session_state.chat_context.get('current_sport')
        if current_sport:
            sport_questions = [
                f"What are the key factors in {current_sport} betting?",
                f"How do weather conditions affect {current_sport} games?",
                f"What's the best strategy for {current_sport} spreads?"
            ]
            return sport_questions + base_questions[:2]

        return base_questions
    
    def export_chat_history(self) -> str:
        """Export chat history as formatted text"""
        if not st.session_state.chat_history:
            return "No chat history to export."
        
        export_text = f"SportsBet Pro AI Chat History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += "=" * 60 + "\n\n"
        
        for entry in st.session_state.chat_history:
            export_text += f"[{entry['timestamp']}]\n"
            export_text += f"USER: {entry['user_message']}\n\n"
            
            if entry['chat_mode'] == 'both':
                export_text += f"ChatGPT: {entry['openai_response']}\n\n"
                export_text += f"Gemini: {entry['gemini_response']}\n\n"
                export_text += f"Consensus: {entry['consensus']}\n\n"
            else:
                ai_name = entry['chat_mode'].upper()
                response_key = f"{entry['chat_mode']}_response"
                export_text += f"{ai_name}: {entry[response_key]}\n\n"
            
            export_text += "-" * 40 + "\n\n"
        
        return export_text