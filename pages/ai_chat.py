import streamlit as st
from datetime import datetime
from utils.ai_chat import DualAIChat
import json

def show_ai_chat():
    """Interactive AI Chat for Sports Analysis"""
    
    st.title("💬 AI Sports Chat")
    st.markdown("**Chat with ChatGPT and Gemini about your sports picks and betting strategies**")
    
    # Responsible gambling notice
    st.warning("""
    ⚠️ **Educational Discussion Only**: This chat provides educational analysis for learning purposes. 
    Sports betting involves risk. Never bet more than you can afford to lose.
    """)
    
    # Initialize chat system
    if 'ai_chat' not in st.session_state:
        st.session_state.ai_chat = DualAIChat()
    
    ai_chat = st.session_state.ai_chat
    
    # Chat controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        chat_mode = st.selectbox(
            "🤖 Chat Mode",
            options=["both", "openai", "gemini"],
            format_func=lambda x: {
                "both": "Dual AI (ChatGPT + Gemini)",
                "openai": "ChatGPT Only", 
                "gemini": "Gemini Only"
            }[x],
            key="chat_mode_selector"
        )
    
    with col2:
        if st.button("🗑️ Clear Chat"):
            ai_chat.clear_chat_history()
            st.rerun()
    
    with col3:
        if st.button("📥 Export Chat"):
            chat_export = ai_chat.export_chat_history()
            st.download_button(
                "💾 Download",
                data=chat_export,
                file_name=f"sports_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col4:
        if st.button("ℹ️ Help"):
            show_chat_help()
    
    st.divider()
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for i, entry in enumerate(st.session_state.chat_history):
                # User message
                st.markdown(f"**🙋 You** *({entry['timestamp']})*")
                st.markdown(f"> {entry['user_message']}")
                
                # AI responses
                if entry['chat_mode'] == 'both':
                    col_gpt, col_gemini = st.columns(2)
                    
                    with col_gpt:
                        st.markdown("**🤖 ChatGPT**")
                        st.markdown(entry['openai_response'])
                    
                    with col_gemini:
                        st.markdown("**🧠 Gemini**")
                        st.markdown(entry['gemini_response'])
                    
                    # Consensus analysis
                    st.info(entry['consensus'])
                    
                elif entry['chat_mode'] == 'openai':
                    st.markdown("**🤖 ChatGPT**")
                    st.markdown(entry['openai_response'])
                    
                elif entry['chat_mode'] == 'gemini':
                    st.markdown("**🧠 Gemini**")
                    st.markdown(entry['gemini_response'])
                
                st.divider()
        else:
            st.info("👋 Start a conversation! Ask about games, betting strategies, or sports analysis.")
    
    # Chat input
    st.markdown("### 💭 Ask the AI")
    
    # Sample questions
    with st.expander("💡 Sample Questions"):
        sample_questions = [
            "What do you think about today's NBA games?",
            "Can you analyze the betting value in tonight's MLB games?",
            "What factors should I consider when betting on NFL games?",
            "How do you evaluate underdog picks?",
            "What's your opinion on the Lakers vs Warriors matchup?",
            "Can you explain Kelly Criterion for sports betting?",
            "What are the key metrics for baseball betting?",
            "How important are weather conditions in NFL betting?"
        ]
        
        for question in sample_questions:
            if st.button(f"💬 {question}", key=f"sample_{hash(question)}"):
                process_chat_message(question, chat_mode, ai_chat)
                st.rerun()
    
    # User input
    user_message = st.text_area(
        "Your message:",
        placeholder="Ask about games, betting strategies, analysis methods, or anything sports-related...",
        height=100,
        key="user_chat_input"
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("Send 📤", type="primary", disabled=not user_message.strip()):
            if user_message.strip():
                process_chat_message(user_message.strip(), chat_mode, ai_chat)
                st.rerun()

def process_chat_message(user_message: str, chat_mode: str, ai_chat: DualAIChat):
    """Process and store chat message"""
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    with st.spinner(f"Getting response from {chat_mode.upper()}..."):
        try:
            if chat_mode == "both":
                responses = ai_chat.get_consensus_response(user_message)
                
                chat_entry = {
                    'timestamp': timestamp,
                    'user_message': user_message,
                    'chat_mode': chat_mode,
                    'openai_response': responses['openai'],
                    'gemini_response': responses['gemini'],
                    'consensus': responses['consensus']
                }
                
            elif chat_mode == "openai":
                openai_response = ai_chat.chat_with_openai(user_message)
                
                chat_entry = {
                    'timestamp': timestamp,
                    'user_message': user_message,
                    'chat_mode': chat_mode,
                    'openai_response': openai_response
                }
                
            elif chat_mode == "gemini":
                gemini_response = ai_chat.chat_with_gemini(user_message)
                
                chat_entry = {
                    'timestamp': timestamp,
                    'user_message': user_message,
                    'chat_mode': chat_mode,
                    'gemini_response': gemini_response
                }
            
            # Add to chat history
            st.session_state.chat_history.append(chat_entry)
            
            # Keep chat history manageable (last 20 exchanges)
            if len(st.session_state.chat_history) > 20:
                st.session_state.chat_history = st.session_state.chat_history[-20:]
                
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")

def show_chat_help():
    """Show chat help information"""
    
    st.info("""
    **🤖 AI Sports Chat Help**
    
    **Chat Modes:**
    - **Dual AI**: Get responses from both ChatGPT and Gemini with consensus analysis
    - **ChatGPT Only**: Chat exclusively with ChatGPT (GPT-4)
    - **Gemini Only**: Chat exclusively with Google Gemini
    
    **What You Can Ask:**
    - Game analysis and predictions
    - Betting strategy discussions
    - Statistical analysis explanations
    - Risk management advice
    - Sports betting education
    - Specific matchup breakdowns
    
    **Features:**
    - Conversation history maintained
    - Export chat for later review
    - Real-time sports context included
    - Responsible gambling reminders
    
    **Tips:**
    - Be specific about games or strategies
    - Ask follow-up questions for deeper analysis
    - Use dual AI mode for comprehensive perspectives
    - Remember this is educational content only
    """)

def main():
    show_ai_chat()

if __name__ == "__main__":
    main()