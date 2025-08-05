import streamlit as st
from datetime import datetime
from utils.ai_chat import DualAIChat
import json

def show_modern_ai_chat():
    """Modern, user-friendly AI Chat interface"""
    
    # Custom CSS for modern chat interface
    st.markdown("""
    <style>
    /* Modern chat container */
    .chat-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Chat messages */
    .user-message {
        background: #007bff;
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
        text-align: right;
        box-shadow: 0 2px 8px rgba(0,123,255,0.3);
    }
    
    .ai-message {
        background: #f8f9fa;
        color: #333;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
    }
    
    /* Chat input area */
    .chat-input-container {
        background: white;
        border-radius: 25px;
        padding: 8px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 2px solid #e9ecef;
        margin: 20px 0;
    }
    
    /* Modern buttons */
    .modern-button {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(40,167,69,0.3);
    }
    
    .modern-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(40,167,69,0.4);
    }
    
    /* Typing indicator */
    .typing-indicator {
        background: #f8f9fa;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        margin-right: 20%;
        opacity: 0.8;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    
    /* Quick actions */
    .quick-action {
        background: rgba(255,255,255,0.9);
        border: 1px solid #dee2e6;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
        display: inline-block;
    }
    
    .quick-action:hover {
        background: #007bff;
        color: white;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="chat-container">
        <h1 style="color: white; text-align: center; margin: 0;">💬 AI Sports Chat</h1>
        <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 10px 0 0 0;">
            Chat with AI experts about sports picks and betting strategies
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chat system
    if 'ai_chat' not in st.session_state:
        st.session_state.ai_chat = DualAIChat()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    ai_chat = st.session_state.ai_chat
    
    # Modern chat controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        chat_mode = st.selectbox(
            "🤖 AI Assistant",
            options=["both", "openai", "gemini"],
            format_func=lambda x: {
                "both": "🤝 Both AIs (Recommended)",
                "openai": "🧠 ChatGPT", 
                "gemini": "⚡ Gemini"
            }[x],
            key="modern_chat_mode"
        )
    
    with col2:
        if st.button("🗑️ Clear", help="Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📥 Export", help="Export chat history"):
            chat_export = export_chat_history()
            st.download_button(
                "💾 Download",
                data=chat_export,
                file_name=f"ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col4:
        if st.button("❓ Help", help="Show help information"):
            show_modern_help()
    
    st.divider()
    
    # Chat messages display
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for entry in st.session_state.chat_history:
                # User message
                st.markdown(f"""
                <div class="user-message">
                    <strong>You</strong> • {entry['timestamp']}<br>
                    {entry['user_message']}
                </div>
                """, unsafe_allow_html=True)
                
                # AI responses
                if entry['chat_mode'] == 'both':
                    st.markdown(f"""
                    <div class="ai-message">
                        <strong>🧠 ChatGPT</strong><br>
                        {entry.get('openai_response', 'No response')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="ai-message">
                        <strong>⚡ Gemini</strong><br>
                        {entry.get('gemini_response', 'No response')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif entry['chat_mode'] == 'openai':
                    st.markdown(f"""
                    <div class="ai-message">
                        <strong>🧠 ChatGPT</strong><br>
                        {entry.get('openai_response', 'No response')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif entry['chat_mode'] == 'gemini':
                    st.markdown(f"""
                    <div class="ai-message">
                        <strong>⚡ Gemini</strong><br>
                        {entry.get('gemini_response', 'No response')}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 40px; color: #6c757d;">
                <h3>👋 Welcome to AI Sports Chat!</h3>
                <p>Start a conversation by typing a message below or click on a quick action.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("### ⚡ Quick Actions")
    quick_actions = [
        "What are today's best NFL picks?",
        "Analyze tonight's NBA games",
        "Help me understand betting odds",
        "What's your MLB strategy?",
        "Explain the Kelly Criterion",
        "Review my betting approach"
    ]
    
    cols = st.columns(3)
    for i, action in enumerate(quick_actions):
        with cols[i % 3]:
            if st.button(f"💬 {action}", key=f"quick_{i}", use_container_width=True):
                process_modern_chat_message(action, chat_mode, ai_chat)
                st.rerun()
    
    st.divider()
    
    # Modern chat input with Enter-to-send
    st.markdown("### 💭 Your Message")
    
    # Create form for Enter-to-send functionality
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_area(
            label="Type your message...",
            placeholder="Ask about sports picks, betting strategies, game analysis, or anything sports-related...",
            height=100,
            label_visibility="collapsed",
            key="modern_chat_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submit_button = st.form_submit_button(
                "Send 🚀", 
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.form_submit_button("🧪 Test", use_container_width=True):
                test_message = "Hello! Can you help me with sports betting analysis?"
                process_modern_chat_message(test_message, chat_mode, ai_chat)
                st.rerun()
        
        # Process message when form is submitted
        if submit_button and user_message.strip():
            process_modern_chat_message(user_message.strip(), chat_mode, ai_chat)
            st.rerun()
    
    # Helpful tips
    st.info("""
    💡 **Tips:** 
    • Press **Ctrl+Enter** or click **Send** to send your message
    • Use **Quick Actions** for common questions
    • Switch between AI models for different perspectives
    • Export your chat history for later review
    """)

def process_modern_chat_message(user_message: str, chat_mode: str, ai_chat: DualAIChat):
    """Process chat message with modern loading indicators"""
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Show typing indicator
    typing_placeholder = st.empty()
    typing_placeholder.markdown("""
    <div class="typing-indicator">
        <strong>AI is typing...</strong> 💭
    </div>
    """, unsafe_allow_html=True)
    
    try:
        response = ai_chat.get_chat_response(user_message, chat_mode)
        
        if chat_mode == "both":
            chat_entry = {
                'timestamp': timestamp,
                'user_message': user_message,
                'chat_mode': chat_mode,
                'openai_response': response.get('chatgpt', 'No response available'),
                'gemini_response': response.get('gemini', 'No response available')
            }
        elif chat_mode == "openai":
            chat_entry = {
                'timestamp': timestamp,
                'user_message': user_message,
                'chat_mode': chat_mode,
                'openai_response': response.get('chatgpt', 'No response available')
            }
        elif chat_mode == "gemini":
            chat_entry = {
                'timestamp': timestamp,
                'user_message': user_message,
                'chat_mode': chat_mode,
                'gemini_response': response.get('gemini', 'No response available')
            }
        
        # Add to chat history
        st.session_state.chat_history.append(chat_entry)
        
        # Keep chat history manageable (last 30 exchanges)
        if len(st.session_state.chat_history) > 30:
            st.session_state.chat_history = st.session_state.chat_history[-30:]
        
        # Clear typing indicator
        typing_placeholder.empty()
        
    except Exception as e:
        typing_placeholder.empty()
        st.error(f"Sorry, I encountered an error: {str(e)}")

def export_chat_history():
    """Export chat history in a readable format"""
    if not st.session_state.chat_history:
        return "No chat history to export."
    
    export_text = f"AI Sports Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_text += "=" * 60 + "\n\n"
    
    for entry in st.session_state.chat_history:
        export_text += f"[{entry['timestamp']}] You: {entry['user_message']}\n\n"
        
        if entry['chat_mode'] == 'both':
            if 'openai_response' in entry:
                export_text += f"ChatGPT: {entry['openai_response']}\n\n"
            if 'gemini_response' in entry:
                export_text += f"Gemini: {entry['gemini_response']}\n\n"
        elif entry['chat_mode'] == 'openai' and 'openai_response' in entry:
            export_text += f"ChatGPT: {entry['openai_response']}\n\n"
        elif entry['chat_mode'] == 'gemini' and 'gemini_response' in entry:
            export_text += f"Gemini: {entry['gemini_response']}\n\n"
        
        export_text += "-" * 40 + "\n\n"
    
    return export_text

def show_modern_help():
    """Show modern help modal"""
    st.markdown("""
    ### 🚀 AI Sports Chat Guide
    
    **🤖 AI Assistants:**
    - **Both AIs**: Get insights from ChatGPT and Gemini together
    - **ChatGPT**: Detailed analysis and explanations
    - **Gemini**: Quick responses and alternative perspectives
    
    **💬 How to Chat:**
    - Type your message and press **Ctrl+Enter** or click **Send**
    - Use **Quick Actions** for instant common questions
    - Export your chat history anytime
    
    **🏈 What to Ask:**
    - Game predictions and analysis
    - Betting strategies and tips
    - Statistical breakdowns
    - Risk management advice
    - Educational content about sports betting
    
    **⚠️ Remember:** This is for educational purposes only. Bet responsibly!
    """)

# Use the modern chat interface
def show_ai_chat():
    show_modern_ai_chat()