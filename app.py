import streamlit as st
import pandas as pd
import numpy as np

# fix for Pyrebase / collections with Python 3.10+
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Sequence = collections.abc.Sequence
collections.Callable = collections.abc.Callable
import pyrebase  # keep this for Pyrebase auth

from components.chat_interface import ChatInterface
from components.dashboard import Dashboard
from components.data_input import DataInput
from components.auth import AuthManager    # make sure you updated AuthManager to accept firebase_service
from services.firebase_service import FirebaseService
from services.gemini_service import GeminiService
from models.financial_models import FinancialModels

# Page configuration
st.set_page_config(
    page_title="Explorer PM - AI Financial Portfolio Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def initialize_services():
    firebase_service = FirebaseService()
    gemini_service = GeminiService()
    financial_models = FinancialModels()
    auth_manager = AuthManager(firebase_service)   # make sure AuthManager.__init__ expects firebase_service
    return firebase_service, gemini_service, financial_models, auth_manager

def main():
    firebase_service, gemini_service, financial_models, auth_manager = initialize_services()
    
    # check if logged in
    if not auth_manager.is_logged_in():
        auth_manager.render_auth_page()
        return
    
    # session state
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'predictions' not in st.session_state:
        st.session_state.predictions = {}
    
    # sidebar
    st.sidebar.title("🏦 Explorer PM")
    st.sidebar.markdown("*AI-Powered Financial Portfolio Manager*")
    
    # user profile
    auth_manager.render_user_profile()
    
    # navigation
    page = st.sidebar.selectbox(
        "Navigate to:",
        ["🏠 Home", "📊 Dashboard", "💬 AI Chat", "📋 Data Input", "🎯 Predictions"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📊 Dashboard":
        dashboard = Dashboard(firebase_service, gemini_service, financial_models)
        dashboard.render()
    elif page == "💬 AI Chat":
        chat_interface = ChatInterface(gemini_service, firebase_service, auth_manager)
        chat_interface.render()
    elif page == "📋 Data Input":
        data_input = DataInput(firebase_service, financial_models)
        data_input.render()
    elif page == "🎯 Predictions":
        show_predictions_page(financial_models, gemini_service)

def show_home_page():
    st.title("🌟 Welcome to Explorer PM")
    st.markdown("### Your AI-Powered Financial Janam Patri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🎯 What is Explorer PM?
        Explorer PM is your digital financial astrologer - just like a Janam Patri predicts life events, 
        our AI analyzes your financial footprint and provides personalized predictions for:
        
        - 💸 **Expense Management**
        - 📈 **Investment Strategies**
        - ⚠️ **Risk Assessment**
        - 🛡️ **Insurance Coverage**
        """)
        
    with col2:
        st.markdown("""
        #### 🚀 Key Features
        
        - **AI-Powered Analysis**: Google Gemini AI for intelligent insights
        - **Natural Language Chat**: Ask questions in plain English
        - **Personalized Predictions**: 1, 3, and 10-year financial forecasts
        - **Visual Dashboard**: Interactive charts and metrics
        - **Secure Storage**: Firebase backend for data protection
        """)
    
    st.markdown("---")
    
    st.markdown("#### 🚀 Quick Start Guide")
    
    steps = [
        ("1️⃣ Input Your Data", "Go to 'Data Input' to enter your financial information"),
        ("2️⃣ View Dashboard", "Check your financial health on the 'Dashboard'"),
        ("3️⃣ Get Predictions", "See AI-generated forecasts in 'Predictions'"),
        ("4️⃣ Chat with AI", "Ask questions using natural language in 'AI Chat'")
    ]
    
    for step, description in steps:
        st.markdown(f"**{step}**: {description}")

def show_predictions_page(financial_models, gemini_service):
    st.title("🎯 Financial Predictions")
    
    if not st.session_state.user_data:
        st.warning("Please input your financial data first to get predictions.")
        return
    
    st.markdown("### Your Financial Janam Patri")
    
    with st.spinner("Generating AI-powered predictions..."):
        predictions = financial_models.generate_predictions(st.session_state.user_data)
        ai_analysis = gemini_service.analyze_financial_profile(st.session_state.user_data, predictions)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 1-Year Forecast", "🎯 3-Year Outlook", "🌟 10-Year Vision", "🤖 AI Insights"])
    
    with tab1:
        st.markdown("#### 1-Year Financial Forecast")
        display_forecast_period(predictions.get('1_year', {}), "1 year")
    
    with tab2:
        st.markdown("#### 3-Year Financial Outlook")
        display_forecast_period(predictions.get('3_year', {}), "3 years")
    
    with tab3:
        st.markdown("#### 10-Year Financial Vision")
        display_forecast_period(predictions.get('10_year', {}), "10 years")
    
    with tab4:
        st.markdown("#### AI-Generated Insights")
        st.markdown(ai_analysis)

def display_forecast_period(forecast_data, period):
    if not forecast_data:
        st.info(f"No forecast data available for {period}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Expected Savings Growth", 
                  f"₹{forecast_data.get('savings_growth', 0):,.0f}")
        st.metric("Investment Returns", 
                  f"₹{forecast_data.get('investment_returns', 0):,.0f}")
    
    with col2:
        st.metric("Risk Score", f"{forecast_data.get('risk_score', 0):.1f}/10")
        st.metric("Financial Health", forecast_data.get('health_status', 'Unknown'))

if __name__ == "__main__":
    main()
