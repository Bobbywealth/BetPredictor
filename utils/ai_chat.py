import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.cache_manager import CacheManager

# Import AI clients
import openai
from google import genai
from google.genai import types

class DualAIChat:
    """Interactive chat interface with both ChatGPT and Gemini for sports analysis"""
    
    def __init__(self):
        self.cache = CacheManager()
        
        # Initialize OpenAI
        self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Initialize Gemini
        self.gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Initialize chat history if not exists
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        if 'ai_contexts' not in st.session_state:
            st.session_state.ai_contexts = {
                'openai': [],
                'gemini': []
            }
    
    def get_sports_context(self) -> str:
        """Get current sports context for the chat"""
        try:
            from utils.live_games import LiveGamesManager
            from utils.odds_api import OddsAPIManager
            from datetime import date
            
            games_manager = LiveGamesManager()
            odds_manager = OddsAPIManager()
            
            # Get today's games
            today_games = games_manager.get_upcoming_games_all_sports(target_date=date.today())
            odds_data = odds_manager.get_comprehensive_odds()
            
            context = f"""
Current Sports Context:
- Today's Games Available: {len(today_games)}
- Live Odds Available: {len(odds_data)} games
- Date: {date.today().strftime('%B %d, %Y')}

You are a sports analysis expert with access to real-time data. Help users analyze games, 
discuss betting strategies (for educational purposes), and provide insights based on current 
sports information. Always include responsible gambling reminders.
"""
            return context
            
        except Exception as e:
            return f"Sports context unavailable: {str(e)}"
    
    def chat_with_openai(self, user_message: str, include_context: bool = True) -> str:
        """Chat with ChatGPT about sports picks"""
        try:
            # Build conversation context
            messages = [
                {
                    "role": "system", 
                    "content": f"""You are a sports analysis expert helping users discuss sports picks and betting strategies.
                    
{self.get_sports_context() if include_context else ''}

Rules:
1. Provide educational analysis only
2. Always remind users about responsible gambling
3. Be conversational and helpful
4. Reference current games when relevant
5. Discuss strategy, not guaranteed wins
6. Keep responses concise but informative"""
                }
            ]
            
            # Add conversation history (last 6 messages for context)
            recent_openai_context = st.session_state.ai_contexts['openai'][-6:] if st.session_state.ai_contexts['openai'] else []
            messages.extend(recent_openai_context)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Update context
            st.session_state.ai_contexts['openai'].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ])
            
            # Keep context manageable (last 12 messages)
            if len(st.session_state.ai_contexts['openai']) > 12:
                st.session_state.ai_contexts['openai'] = st.session_state.ai_contexts['openai'][-12:]
            
            return ai_response
            
        except Exception as e:
            return f"ChatGPT Error: {str(e)}"
    
    def chat_with_gemini(self, user_message: str, include_context: bool = True) -> str:
        """Chat with Gemini about sports picks"""
        try:
            # Build system instruction
            system_instruction = f"""You are a sports analysis expert helping users discuss sports picks and betting strategies.

{self.get_sports_context() if include_context else ''}

Rules:
1. Provide educational analysis only
2. Always remind users about responsible gambling
3. Be conversational and helpful
4. Reference current games when relevant
5. Discuss strategy, not guaranteed wins
6. Keep responses concise but informative"""
            
            # Build conversation history
            conversation_parts = []
            
            # Add recent context (last 6 messages)
            recent_gemini_context = st.session_state.ai_contexts['gemini'][-6:] if st.session_state.ai_contexts['gemini'] else []
            
            for msg in recent_gemini_context:
                if msg['role'] == 'user':
                    conversation_parts.append(types.Part(text=f"User: {msg['content']}"))
                else:
                    conversation_parts.append(types.Part(text=f"Assistant: {msg['content']}"))
            
            # Add current message
            conversation_parts.append(types.Part(text=f"User: {user_message}"))
            
            # Get response from Gemini
            response = self.gemini_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=conversation_parts,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=500,
                    temperature=0.7
                )
            )
            
            ai_response = response.text if response.text else "No response generated"
            
            # Update context
            st.session_state.ai_contexts['gemini'].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": ai_response}
            ])
            
            # Keep context manageable (last 12 messages)
            if len(st.session_state.ai_contexts['gemini']) > 12:
                st.session_state.ai_contexts['gemini'] = st.session_state.ai_contexts['gemini'][-12:]
            
            return ai_response
            
        except Exception as e:
            return f"Gemini Error: {str(e)}"
    
    def get_consensus_response(self, user_message: str) -> Dict[str, str]:
        """Get responses from both AIs and analyze consensus"""
        
        # Get responses from both AIs
        openai_response = self.chat_with_openai(user_message)
        gemini_response = self.chat_with_gemini(user_message)
        
        # Analyze consensus (simple keyword matching for now)
        consensus_analysis = self.analyze_consensus(openai_response, gemini_response, user_message)
        
        return {
            'openai': openai_response,
            'gemini': gemini_response,
            'consensus': consensus_analysis
        }
    
    def analyze_consensus(self, openai_response: str, gemini_response: str, user_message: str) -> str:
        """Analyze consensus between AI responses"""
        
        # Simple consensus analysis
        openai_lower = openai_response.lower()
        gemini_lower = gemini_response.lower()
        
        # Check for agreement indicators
        agreement_keywords = ['agree', 'similar', 'same', 'both', 'consensus']
        disagreement_keywords = ['however', 'but', 'different', 'disagree', 'contrary']
        
        openai_sentiment = 'positive' if any(word in openai_lower for word in ['good', 'strong', 'confident', 'likely']) else 'neutral'
        gemini_sentiment = 'positive' if any(word in gemini_lower for word in ['good', 'strong', 'confident', 'likely']) else 'neutral'
        
        if openai_sentiment == gemini_sentiment:
            return f"🤝 **AI Consensus**: Both AIs show {openai_sentiment} sentiment. This suggests alignment in their analysis."
        else:
            return f"🔄 **Mixed Analysis**: Different perspectives detected. ChatGPT leans {openai_sentiment}, Gemini leans {gemini_sentiment}. Consider both viewpoints."
    
    def clear_chat_history(self):
        """Clear chat history and contexts"""
        st.session_state.chat_history = []
        st.session_state.ai_contexts = {
            'openai': [],
            'gemini': []
        }
    
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