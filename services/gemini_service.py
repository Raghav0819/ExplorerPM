import os
import json
import streamlit as st
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# load variables from .env
load_dotenv()

class FinancialAdvice(BaseModel):
    category: str
    current_status: str
    recommended_action: str
    priority: str
    explanation: str

class FinancialAnalysis(BaseModel):
    overall_health_score: float
    advice_list: List[FinancialAdvice]
    key_insights: List[str]
    recommended_actions: List[str]

def serialize_data(data):
    """Convert datetime objects to strings for JSON serialization"""
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif hasattr(data, 'isoformat'):  # datetime objects
        return data.isoformat()
    else:
        return data

class GeminiService:
    def __init__(self):
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Gemini client"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                st.warning("Gemini API key not found. Chat features will be limited.")
                return
            
            self.client = genai.Client(api_key=api_key)
            
        except Exception as e:
            st.error(f"Error initializing Gemini client: {str(e)}")
    
    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        if not self.client:
            return "I'm sorry, I'm currently unable to process your request. Please check the API configuration."
        
        try:
            if context:
                serialized_context = serialize_data(context)
                context_str = f"User Financial Context: {json.dumps(serialized_context, indent=2)}\n\n"
                full_prompt = context_str + prompt
            else:
                full_prompt = prompt
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            
            return response.text or "I couldn't generate a response. Please try again."
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I'm experiencing technical difficulties. Please try again later."
    
    def analyze_financial_profile(self, user_data: Dict[str, Any], predictions: Optional[Dict[str, Any]] = None) -> str:
        if not self.client:
            return "Financial analysis service is currently unavailable."
        
        try:
            system_prompt = """
You are an expert financial advisor AI. Analyze the user's financial profile and provide 
comprehensive insights in a friendly, encouraging tone. Focus on:
1. Current financial health assessment
2. Areas for improvement
3. Specific actionable recommendations
4. Future financial outlook

Structure your response in a clear, easy-to-read format with headers and bullet points.
Be encouraging and provide practical advice that the user can implement.
"""
            serialized_user_data = serialize_data(user_data)
            serialized_predictions = serialize_data(predictions or {})
            
            user_prompt = f"""
Please analyze this financial profile and provide detailed insights:

Financial Data:
{json.dumps(serialized_user_data, indent=2)}

Predictions:
{json.dumps(serialized_predictions, indent=2)}

Please provide a comprehensive financial health analysis with specific recommendations.
"""
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=system_prompt + "\n\n" + user_prompt)])
                ]
            )
            
            return response.text or "Unable to generate financial analysis."
        except Exception as e:
            st.error(f"Error analyzing financial profile: {str(e)}")
            return "Financial analysis service is temporarily unavailable."
    
    def answer_financial_question(self, question: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        if not self.client:
            return "I'm currently unable to answer questions. Please check back later."
        
        try:
            system_prompt = """
You are an expert financial advisor AI with deep understanding of personal finance. 
Analyze questions carefully and provide personalized, actionable advice based on the user's financial situation.

Guidelines:
- Always use the user's actual financial data when available
- Provide specific numbers and calculations when possible
- Break down complex advice into simple steps
- Consider Indian financial products and market conditions
- Be encouraging but realistic about financial goals
- If asking about saving for specific goals, calculate monthly amounts needed
"""
            context_info = ""
            if user_context:
                monthly_income = user_context.get('net_monthly_income', 0)
                monthly_expenses = user_context.get('fixed_costs_total', 0)
                savings = user_context.get('savings_total', 0)
                investments = user_context.get('investments_total', 0)
                
                context_info = f"""
User's Financial Profile:
- Monthly Income: ₹{monthly_income:,}
- Monthly Expenses: ₹{monthly_expenses:,}
- Current Savings: ₹{savings:,}
- Current Investments: ₹{investments:,}
- Monthly Surplus: ₹{monthly_income - monthly_expenses:,}
- Age: {user_context.get('age', 'Not provided')}
- Family Size: {user_context.get('household_size', 'Not provided')}
- Financial Goals: {user_context.get('user_goals', 'Not specified')}
"""
            question_lower = question.lower()
            specialized_context = ""
            if any(word in question_lower for word in ['vacation', 'trip', 'travel']):
                specialized_context = "\nThis appears to be about vacation planning. Suggest monthly savings."
            elif any(word in question_lower for word in ['emergency', 'fund']):
                specialized_context = "\nThis is about emergency funds. Recommend 6–12 months of expenses."
            elif any(word in question_lower for word in ['house', 'property']):
                specialized_context = "\nThis is about home purchase. Suggest down payment and loan eligibility."
            elif any(word in question_lower for word in ['retirement', 'pension']):
                specialized_context = "\nThis is about retirement planning. Include inflation estimates."

            full_prompt = f"{system_prompt}{context_info}{specialized_context}\n\nUser Question: {question}"
            
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=full_prompt
            )
            return response.text or "I couldn't process your question. Please try rephrasing."
        except Exception as e:
            st.error(f"Error answering question: {str(e)}")
            return "I'm experiencing technical difficulties. Please try asking your question again."
    
    def generate_personalized_tips(self, user_data: Dict[str, Any]) -> List[str]:
        if not self.client:
            return ["Please configure Gemini API to receive personalized tips."]
        
        try:
            serialized_data = serialize_data(user_data)
            
            prompt = f"""
Based on this user's financial profile, generate 5 specific, actionable financial tips:

{json.dumps(serialized_data, indent=2)}

Each tip should be:
- Specific to their situation
- Actionable and practical
- Easy to understand
- Encouraging and positive

Return the tips as a simple list, one per line.
"""
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response.text:
                tips = [tip.strip() for tip in response.text.split('\n') if tip.strip()]
                return tips[:5]
            else:
                return ["Build an emergency fund", "Track your expenses", "Diversify investments"]
        except Exception as e:
            st.error(f"Error generating tips: {str(e)}")
            return ["Review your budget", "Save for emergencies", "Consider investments"]
    
    def analyze_expense_pattern(self, expense_data: Dict[str, Any]) -> str:
        if not self.client:
            return "Expense analysis is currently unavailable."
        
        try:
            serialized_expense_data = serialize_data(expense_data)
            prompt = f"""
Analyze this expense pattern and provide insights:

{json.dumps(serialized_expense_data, indent=2)}

Provide:
1. Key spending patterns
2. Areas to save
3. Better budget allocation suggestions
4. Any warning signs

Keep it concise but insightful.
"""
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text or "Unable to analyze expense patterns."
        except Exception as e:
            st.error(f"Error analyzing expenses: {str(e)}")
            return "Expense analysis service is temporarily unavailable."
    
    def suggest_investment_strategy(self, user_profile: Dict[str, Any]) -> str:
        if not self.client:
            return "Investment strategy suggestions are currently unavailable."
        
        try:
            serialized_profile = serialize_data(user_profile)
            prompt = f"""
Based on this financial profile, suggest a personalized investment strategy:

{json.dumps(serialized_profile, indent=2)}

Consider:
- Risk tolerance based on age and situation
- Investment timeline and goals
- Current savings and income
- Diversification
- Indian investment instruments

Provide practical, actionable investment advice.
"""
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text or "Unable to generate investment strategy."
        except Exception as e:
            st.error(f"Error generating investment strategy: {str(e)}")
            return "Investment strategy service is temporarily unavailable."
