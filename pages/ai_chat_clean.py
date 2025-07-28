import streamlit as st
from datetime import datetime
from utils.ai_chat import DualAIChat

def show_ai_chat():
    """Modern AI Chat Interface - Clean Version"""
    
    # Modern CSS styling
    st.markdown("""
    <style>
    .chat-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 10px 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .ai-message {
        background: #f8f9fa;
        color: #333;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 10px 0;
        margin-right: 20%;
        border-left: 3px solid #28a745;
    }
    
    .quick-btn {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="chat-header">
        <h1>💬 AI Sports Chat</h1>
        <p>Chat with AI experts about sports picks and betting strategies</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize AI Chat
    if 'ai_chat' not in st.session_state:
        st.session_state.ai_chat = DualAIChat()
    
    if 'clean_chat_history' not in st.session_state:
        st.session_state.clean_chat_history = []
    
    ai_chat = st.session_state.ai_chat
    
    # Chat controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        chat_mode = st.selectbox(
            "Choose AI Assistant:",
            ["both", "openai", "gemini"],
            format_func=lambda x: {
                "both": "🤝 Both AIs",
                "openai": "🧠 ChatGPT",
                "gemini": "⚡ Gemini"
            }[x]
        )
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.clean_chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📥 Export"):
            export_data = create_export()
            st.download_button(
                "💾 Download",
                data=export_data,
                file_name=f"ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    st.divider()
    
    # Display chat messages
    if st.session_state.clean_chat_history:
        for entry in st.session_state.clean_chat_history:
            # User message
            st.markdown(f"""
            <div class="user-message">
                <strong>You</strong> • {entry['timestamp']}<br>
                {entry['message']}
            </div>
            """, unsafe_allow_html=True)
            
            # AI responses
            if 'chatgpt_response' in entry:
                st.markdown(f"""
                <div class="ai-message">
                    <strong>🧠 ChatGPT</strong><br>
                    {entry['chatgpt_response']}
                </div>
                """, unsafe_allow_html=True)
            
            if 'gemini_response' in entry:
                st.markdown(f"""
                <div class="ai-message">
                    <strong>⚡ Gemini</strong><br>
                    {entry['gemini_response']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("👋 Welcome! Start chatting by typing a message below or using Quick Actions.")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    quick_actions = [
        "What are today's best NFL picks?",
        "Analyze tonight's NBA games",
        "Help me understand betting odds",
        "What's your MLB strategy?",
        "Explain Kelly Criterion",
        "Review my betting approach"
    ]
    
    cols = st.columns(3)
    for i, action in enumerate(quick_actions):
        with cols[i % 3]:
            if st.button(action, key=f"quick_{i}"):
                send_message(action, chat_mode, ai_chat)
                st.rerun()
    
    st.divider()
    
    # Chat input with form for Enter-to-send
    st.markdown("### 💭 Your Message")
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message...",
            placeholder="Ask about sports picks, betting strategies, or game analysis...",
            height=100,
            label_visibility="collapsed"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            send_clicked = st.form_submit_button("Send 🚀", type="primary", use_container_width=True)
        
        with col2:
            test_clicked = st.form_submit_button("🧪 Test Chat", use_container_width=True)
        
        if send_clicked and user_input.strip():
            send_message(user_input.strip(), chat_mode, ai_chat)
            st.rerun()
        
        if test_clicked:
            send_message("Hello! Can you help me analyze today's games?", chat_mode, ai_chat)
            st.rerun()
    
    # Instructions
    st.info("💡 **Tips:** Type your message and press Ctrl+Enter or click Send. Use Quick Actions for common questions.")

def send_message(message: str, mode: str, ai_chat: DualAIChat):
    """Send message to AI and store response"""
    
    with st.spinner("AI is thinking..."):
        try:
            response = ai_chat.get_chat_response(message, mode)
            
            entry = {
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'message': message
            }
            
            if mode in ["both", "openai"] and 'chatgpt' in response:
                entry['chatgpt_response'] = response['chatgpt']
            
            if mode in ["both", "gemini"] and 'gemini' in response:
                entry['gemini_response'] = response['gemini']
            
            # Add to history
            st.session_state.clean_chat_history.append(entry)
            
            # Keep history manageable
            if len(st.session_state.clean_chat_history) > 25:
                st.session_state.clean_chat_history = st.session_state.clean_chat_history[-25:]
        
        except Exception as e:
            st.error(f"Sorry, there was an error: {str(e)}")

def create_export():
    """Create exportable chat history"""
    if not st.session_state.clean_chat_history:
        return "No chat history to export."
    
    export = f"AI Sports Chat Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export += "=" * 50 + "\n\n"
    
    for entry in st.session_state.clean_chat_history:
        export += f"[{entry['timestamp']}] You: {entry['message']}\n\n"
        
        if 'chatgpt_response' in entry:
            export += f"ChatGPT: {entry['chatgpt_response']}\n\n"
        
        if 'gemini_response' in entry:
            export += f"Gemini: {entry['gemini_response']}\n\n"
        
        export += "-" * 30 + "\n\n"
    
    return export