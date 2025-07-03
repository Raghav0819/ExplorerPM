import streamlit as st
from datetime import datetime
import uuid

class ChatInterface:
    def __init__(self, gemini_service, firebase_service, auth_manager):
        self.gemini_service = gemini_service
        self.firebase_service = firebase_service
        self.auth_manager = auth_manager

        # Initialize session state for chat
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
    
    def render(self):
        """Render the chat interface"""
        st.title("💬 AI Financial Assistant")
        st.markdown("Ask me anything about your finances! I can help with budgeting, investments, savings, and more.")
        
        # Load chat history
        self.load_chat_history()
        
        # Chat container
        chat_container = st.container()
        
        # Display chat messages
        with chat_container:
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about your finances..."):
            self.handle_user_message(prompt)
        
        self.auth_manager.save_chat_history(
            st.session_state.user_id,
            st.session_state.chat_messages
        )
        # Sidebar with quick questions
        self.render_quick_questions()
    
    def handle_user_message(self, user_message):
        """Handle user message and generate AI response"""
        # Add user message to chat
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get user context for better responses
                user_context = st.session_state.get('user_data', {})
                
                # Generate response using Gemini
                response = self.gemini_service.answer_financial_question(
                    user_message, 
                    user_context
                )
                
                st.markdown(response)
                
                # Add AI response to chat
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
        
        # Save chat history
        self.save_chat_history()
        
        # Rerun to update the interface
        st.rerun()
    
    def render_quick_questions(self):
        """Render sidebar with quick question buttons"""
        st.sidebar.markdown("### 🚀 Quick Questions")
        
        quick_questions = [
            "How much should I save for summer vacation?",
            "What's the best investment strategy for my age?",
            "How can I reduce my monthly expenses?",
            "Should I pay off debt or invest first?",
            "How much do I need for emergency fund?",
            "What are good tax-saving investments?",
            "How much should I invest monthly?",
            "When can I afford to buy a house?"
        ]
        
        for question in quick_questions:
            if st.sidebar.button(question, key=f"quick_{hash(question)}"):
                self.handle_user_message(question)
        
        # Chat management
        st.sidebar.markdown("### 🛠️ Chat Management")
        
        if st.sidebar.button("Clear Chat History"):
            st.session_state.chat_messages = []
            self.save_chat_history()
            st.rerun()
        
        if st.sidebar.button("Export Chat"):
            self.export_chat_history()
    
    def load_chat_history(self):
        """Load chat history from Firebase"""
        try:
            chat_history = self.firebase_service.get_chat_history(st.session_state.user_id)
            if chat_history and len(chat_history) > len(st.session_state.chat_messages):
                st.session_state.chat_messages = chat_history
        except Exception as e:
            st.error(f"Error loading chat history: {str(e)}")
    
    def save_chat_history(self):
        """Save chat history to Firebase"""
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_messages = []
            for msg in st.session_state.chat_messages:
                serializable_msg = msg.copy()
                if 'timestamp' in serializable_msg:
                    serializable_msg['timestamp'] = serializable_msg['timestamp'].isoformat()
                serializable_messages.append(serializable_msg)
            
            self.firebase_service.save_chat_history(
                st.session_state.user_id, 
                st.session_state.chat_history
            )
        except Exception as e:
            st.error(f"Error saving chat history: {str(e)}")
    
    def export_chat_history(self):
        """Export chat history as text"""
        if not st.session_state.chat_messages:
            st.warning("No chat history to export.")
            return
        
        export_text = "# Financial Chat History\n\n"
        
        for message in st.session_state.chat_messages:
            role = "You" if message["role"] == "user" else "AI Assistant"
            timestamp = message.get("timestamp", "")
            if isinstance(timestamp, str):
                export_text += f"**{role}** ({timestamp}):\n{message['content']}\n\n"
            else:
                export_text += f"**{role}**:\n{message['content']}\n\n"
        
        st.sidebar.download_button(
            label="Download Chat History",
            data=export_text,
            file_name=f"financial_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )
    
    def render_suggested_questions(self, user_data):
        """Render context-aware suggested questions"""
        user_data = st.session_state.get('user_data', {})

        if not user_data:
            return
        
        st.markdown("### 💡 Suggested Questions Based on Your Profile")
        
        suggestions = []
        
        # Generate suggestions based on user data
        income = user_data.get('net_monthly_income', 0)
        savings = user_data.get('savings_total', 0)
        debts = user_data.get('debts_total', 0)
        investments = user_data.get('investments_total', 0)
        
        if income > 0:
            savings_rate = (savings / 12) / income if income > 0 else 0
            
            if savings_rate < 0.1:
                suggestions.append("How can I increase my savings rate?")
            
            if debts > income * 6:
                suggestions.append("What's the best strategy to pay off my debt?")
            
            if investments < savings * 0.5:
                suggestions.append("Should I move some savings to investments?")
        
        # Age-based suggestions
        age = user_data.get('age', 30)
        if age < 30:
            suggestions.append("What investment strategy is best for someone in their 20s?")
        elif age >= 50:
            suggestions.append("How should I prepare for retirement?")
        
        # Display suggestions as clickable buttons
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions[:6]):  # Limit to 6 suggestions
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    self.handle_user_message(suggestion)
