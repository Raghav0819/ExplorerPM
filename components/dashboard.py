import streamlit as st
import pandas as pd
import numpy as np
from utils.visualizations import FinancialVisualizations
from utils.data_preprocessing import DataPreprocessor
import plotly.graph_objects as go

class Dashboard:
    def __init__(self, firebase_service, gemini_service, financial_models):
        self.firebase_service = firebase_service
        self.gemini_service = gemini_service
        self.financial_models = financial_models
        self.visualizations = FinancialVisualizations()
        self.preprocessor = DataPreprocessor()
    
    def render(self):
        """Render the main dashboard"""
        st.title("📊 Financial Dashboard")
        
        # Check if user data exists
        if not st.session_state.get('user_data'):
            st.warning("⚠️ No financial data found. Please input your data first to view the dashboard.")
            st.info("💡 Use the sidebar navigation to go to 'Data Input' to enter your financial information.")
            return
        
        user_data = st.session_state.user_data
        
        # Calculate financial health score
        health_score = self.calculate_financial_health_score(user_data)
        
        # Dashboard header with key metrics
        self.render_key_metrics(user_data, health_score)
        
        # Main dashboard content
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Overview", 
            "💰 Income & Expenses", 
            "📊 Investments & Assets", 
            "⚠️ Risk Analysis"
        ])
        
        with tab1:
            self.render_overview_tab(user_data, health_score)
        
        with tab2:
            self.render_income_expense_tab(user_data)
        
        with tab3:
            self.render_investment_tab(user_data)
        
        with tab4:
            self.render_risk_tab(user_data)
        
        # AI Insights section
        self.render_ai_insights(user_data)
    
    def render_key_metrics(self, user_data, health_score):
        """Render key financial metrics at the top"""
        st.markdown("### 🎯 Key Financial Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            net_worth = user_data.get('total_net_worth', 0)
            st.metric(
                "Net Worth",
                f"₹{net_worth:,.0f}",
                delta=f"{(net_worth * 0.05):,.0f}" if net_worth > 0 else None
            )
        
        with col2:
            monthly_income = user_data.get('net_monthly_income', 0)
            st.metric(
                "Monthly Income",
                f"₹{monthly_income:,.0f}",
                delta=f"{(monthly_income * 0.03):,.0f}" if monthly_income > 0 else None
            )
        
        with col3:
            total_expenses = user_data.get('fixed_costs_total', 0)
            st.metric(
                "Monthly Expenses",
                f"₹{total_expenses:,.0f}",
                delta=f"-{(total_expenses * 0.02):,.0f}" if total_expenses > 0 else None
            )
        
        with col4:
            savings = user_data.get('savings_total', 0)
            st.metric(
                "Total Savings",
                f"₹{savings:,.0f}",
                delta=f"{(savings * 0.08):,.0f}" if savings > 0 else None
            )
        
        with col5:
            st.metric(
                "Financial Health",
                f"{health_score:.0f}/100",
                delta=self.get_health_status(health_score)
            )
    
    def render_overview_tab(self, user_data, health_score):
        """Render overview tab content"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Financial Health Gauge
            st.plotly_chart(
                self.visualizations.create_financial_health_gauge(health_score),
                use_container_width=True
            )
        
        with col2:
            # Quick financial ratios
            st.markdown("#### 📊 Financial Ratios")
            ratios = self.preprocessor.calculate_financial_ratios(user_data)
            
            for ratio_name, ratio_value in ratios.items():
                if ratio_name == 'emergency_fund_months':
                    st.metric(
                        "Emergency Fund",
                        f"{ratio_value:.1f} months",
                        delta="Good" if ratio_value >= 6 else "Needs improvement"
                    )
                elif ratio_name == 'debt_to_income':
                    st.metric(
                        "Debt-to-Income",
                        f"{ratio_value:.1%}",
                        delta="Good" if ratio_value < 0.4 else "High"
                    )
                elif ratio_name == 'savings_rate':
                    st.metric(
                        "Savings Rate",
                        f"{ratio_value:.1%}",
                        delta="Excellent" if ratio_value > 0.2 else "Good" if ratio_value > 0.1 else "Low"
                    )
        
        # Income flow visualization
        st.markdown("#### 💸 Income Flow Analysis")
        st.plotly_chart(
            self.visualizations.create_income_expense_sankey(user_data),
            use_container_width=True
        )
    
    def render_income_expense_tab(self, user_data):
        """Render income and expense analysis tab"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Expense breakdown pie chart
            st.plotly_chart(
                self.visualizations.create_expense_breakdown_pie(user_data),
                use_container_width=True
            )
        
        with col2:
            # Monthly budget analysis
            st.markdown("#### 📋 Monthly Budget Analysis")
            
            income = user_data.get('net_monthly_income', 0)
            expenses = user_data.get('fixed_costs_total', 0)
            remaining = income - expenses
            
            budget_data = pd.DataFrame({
                'Category': ['Income', 'Expenses', 'Remaining'],
                'Amount': [income, expenses, remaining],
                'Percentage': [100, (expenses/income)*100 if income > 0 else 0, (remaining/income)*100 if income > 0 else 0]
            })
            
            st.dataframe(budget_data, use_container_width=True)
            
            # Budget recommendations
            if remaining < 0:
                st.error("⚠️ Your expenses exceed your income!")
            elif remaining < income * 0.1:
                st.warning("💡 Consider reducing expenses to increase savings.")
            else:
                st.success("✅ Good budget management!")
        
        # Expense trend analysis
        st.markdown("#### 📈 Expense Categories Analysis")
        
        expense_categories = {
            'Essential': user_data.get('rent_mortgage', 0) + user_data.get('utilities', 0) + user_data.get('groceries', 0),
            'Transportation': user_data.get('transportation', 0),
            'Insurance': user_data.get('insurance', 0),
            'Discretionary': user_data.get('clothes', 0) + user_data.get('subscriptions', 0) + user_data.get('miscellaneous', 0),
            'Communication': user_data.get('phone', 0)
        }
        
        # Create horizontal bar chart
        categories = list(expense_categories.keys())
        amounts = list(expense_categories.values())
        
        fig = go.Figure(go.Bar(
            x=amounts,
            y=categories,
            orientation='h',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        ))
        
        fig.update_layout(
            title="Expense Categories Breakdown",
            xaxis_title="Amount (₹)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_investment_tab(self, user_data):
        """Render investment and assets tab"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Portfolio allocation chart
            st.plotly_chart(
                self.visualizations.create_investment_portfolio_chart(user_data),
                use_container_width=True
            )
        
        with col2:
            # Investment metrics
            st.markdown("#### 📊 Investment Metrics")
            
            total_assets = user_data.get('assets_total', 0)
            investments = user_data.get('investments_total', 0)
            savings = user_data.get('savings_total', 0)
            
            if total_assets > 0:
                investment_ratio = investments / total_assets
                st.metric("Investment Allocation", f"{investment_ratio:.1%}")
            
            if investments > 0:
                # Estimate monthly investment (assuming SIPs)
                monthly_investment = investments * 0.05  # Rough estimate
                st.metric("Est. Monthly Investment", f"₹{monthly_investment:,.0f}")
            
            # Emergency fund status
            monthly_expenses = user_data.get('fixed_costs_total', 0)
            emergency_fund = user_data.get('emergency_fund', 0)
            
            if monthly_expenses > 0:
                emergency_months = emergency_fund / monthly_expenses
                status = "✅ Adequate" if emergency_months >= 6 else "⚠️ Insufficient"
                st.metric("Emergency Fund", f"{emergency_months:.1f} months", delta=status)
        
        # Asset allocation recommendations
        st.markdown("#### 💡 Asset Allocation Recommendations")
        
        age = user_data.get('age', 30)  # Default age if not provided
        
        # Age-based allocation suggestion
        equity_percentage = min(100 - age, 80)  # Rule of thumb: 100 - age in equity
        debt_percentage = 100 - equity_percentage
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Suggested Equity", f"{equity_percentage}%")
        
        with col2:
            st.metric("Suggested Debt", f"{debt_percentage}%")
        
        with col3:
            risk_level = "High" if equity_percentage > 60 else "Moderate" if equity_percentage > 40 else "Conservative"
            st.metric("Risk Profile", risk_level)
    
    def render_risk_tab(self, user_data):
        """Render risk analysis tab"""
        # Calculate risk factors
        risk_factors = self.calculate_risk_factors(user_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk assessment radar chart
            st.plotly_chart(
                self.visualizations.create_risk_assessment_radar(risk_factors),
                use_container_width=True
            )
        
        with col2:
            # Risk factor breakdown
            st.markdown("#### ⚠️ Risk Factor Analysis")
            
            for factor, score in risk_factors.items():
                risk_level = "High" if score > 7 else "Medium" if score > 4 else "Low"
                color = "🔴" if score > 7 else "🟡" if score > 4 else "🟢"
                st.metric(f"{color} {factor}", f"{score:.1f}/10", delta=risk_level)
        
        # Risk mitigation suggestions
        st.markdown("#### 🛡️ Risk Mitigation Suggestions")
        
        suggestions = []
        
        if risk_factors.get('Debt Risk', 0) > 6:
            suggestions.append("Consider debt consolidation or faster repayment strategies")
        
        if risk_factors.get('Emergency Fund', 0) > 6:
            suggestions.append("Build emergency fund to cover 6 months of expenses")
        
        if risk_factors.get('Investment Risk', 0) > 7:
            suggestions.append("Diversify your investment portfolio")
        
        if risk_factors.get('Insurance Coverage', 0) > 6:
            suggestions.append("Review and increase your insurance coverage")
        
        for suggestion in suggestions:
            st.info(f"💡 {suggestion}")
    
    def render_ai_insights(self, user_data):
        """Render AI-generated insights section"""
        st.markdown("### 🤖 AI-Powered Insights")
        
        with st.expander("View Detailed Financial Analysis", expanded=False):
            with st.spinner("Generating AI insights..."):
                # Get predictions for context
                predictions = self.financial_models.generate_predictions(user_data)
                
                # Generate comprehensive analysis
                analysis = self.gemini_service.analyze_financial_profile(user_data, predictions)
                st.markdown(analysis)
        
        # Quick tips
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💡 Personalized Tips")
            tips = self.gemini_service.generate_personalized_tips(user_data)
            for i, tip in enumerate(tips[:3], 1):
                st.info(f"{i}. {tip}")
        
        with col2:
            st.markdown("#### 🎯 Action Items")
            action_items = self.generate_action_items(user_data)
            for item in action_items:
                st.success(f"✅ {item}")
    
    def calculate_financial_health_score(self, user_data):
        """Calculate overall financial health score"""
        score = 0
        
        # Income stability (20 points)
        if user_data.get('net_monthly_income', 0) > 0:
            score += 20
        
        # Savings rate (25 points)
        income = user_data.get('net_monthly_income', 0)
        savings = user_data.get('savings_total', 0)
        if income > 0:
            monthly_savings = savings / 12
            savings_rate = monthly_savings / income
            score += min(25, savings_rate * 125)  # 20% savings rate = 25 points
        
        # Debt management (20 points)
        debt = user_data.get('debts_total', 0)
        annual_income = income * 12 if income > 0 else 1
        debt_ratio = debt / annual_income
        if debt_ratio < 0.2:
            score += 20
        elif debt_ratio < 0.4:
            score += 15
        elif debt_ratio < 0.6:
            score += 10
        else:
            score += 5
        
        # Emergency fund (15 points)
        emergency_fund = user_data.get('emergency_fund', 0)
        monthly_expenses = user_data.get('fixed_costs_total', 0)
        if monthly_expenses > 0:
            emergency_months = emergency_fund / monthly_expenses
            if emergency_months >= 6:
                score += 15
            elif emergency_months >= 3:
                score += 10
            elif emergency_months >= 1:
                score += 5
        
        # Investment allocation (20 points)
        investments = user_data.get('investments_total', 0)
        total_assets = user_data.get('assets_total', 0)
        if total_assets > 0:
            investment_ratio = investments / total_assets
            if investment_ratio >= 0.3:
                score += 20
            elif investment_ratio >= 0.15:
                score += 15
            elif investment_ratio >= 0.05:
                score += 10
            else:
                score += 5
        
        return min(100, score)
    
    def get_health_status(self, score):
        """Get health status based on score"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def calculate_risk_factors(self, user_data):
        """Calculate various risk factors"""
        risk_factors = {}
        
        # Debt Risk
        income = user_data.get('net_monthly_income', 0)
        debt = user_data.get('debts_total', 0)
        if income > 0:
            debt_ratio = debt / (income * 12)
            risk_factors['Debt Risk'] = min(10, debt_ratio * 25)
        else:
            risk_factors['Debt Risk'] = 10
        
        # Emergency Fund Risk
        emergency_fund = user_data.get('emergency_fund', 0)
        monthly_expenses = user_data.get('fixed_costs_total', 0)
        if monthly_expenses > 0:
            emergency_months = emergency_fund / monthly_expenses
            risk_factors['Emergency Fund'] = max(0, 10 - emergency_months * 1.5)
        else:
            risk_factors['Emergency Fund'] = 8
        
        # Investment Risk
        investments = user_data.get('investments_total', 0)
        total_assets = user_data.get('assets_total', 0)
        if total_assets > 0:
            investment_ratio = investments / total_assets
            # Higher concentration might mean higher risk
            if investment_ratio > 0.8:
                risk_factors['Investment Risk'] = 7
            elif investment_ratio < 0.1:
                risk_factors['Investment Risk'] = 6
            else:
                risk_factors['Investment Risk'] = 3
        else:
            risk_factors['Investment Risk'] = 5
        
        # Insurance Coverage Risk
        insurance = user_data.get('insurance', 0)
        if income > 0:
            insurance_ratio = insurance / income
            risk_factors['Insurance Coverage'] = max(0, 8 - insurance_ratio * 20)
        else:
            risk_factors['Insurance Coverage'] = 8
        
        # Expense Risk
        expenses = user_data.get('fixed_costs_total', 0)
        if income > 0:
            expense_ratio = expenses / income
            risk_factors['Expense Management'] = min(10, expense_ratio * 12)
        else:
            risk_factors['Expense Management'] = 8
        
        return risk_factors
    
    def generate_action_items(self, user_data):
        """Generate actionable items based on financial data"""
        action_items = []
        
        # Emergency fund check
        emergency_fund = user_data.get('emergency_fund', 0)
        monthly_expenses = user_data.get('fixed_costs_total', 0)
        if monthly_expenses > 0:
            emergency_months = emergency_fund / monthly_expenses
            if emergency_months < 3:
                action_items.append("Build emergency fund to cover 3-6 months of expenses")
        
        # Debt management
        debt = user_data.get('debts_total', 0)
        income = user_data.get('net_monthly_income', 0)
        if debt > 0 and income > 0:
            if debt > income * 6:
                action_items.append("Create a debt repayment plan to reduce high debt levels")
        
        # Investment diversification
        investments = user_data.get('investments_total', 0)
        savings = user_data.get('savings_total', 0)
        if savings > investments * 2:
            action_items.append("Consider moving some savings to investments for better returns")
        
        # Insurance review
        insurance = user_data.get('insurance', 0)
        if income > 0 and insurance < income * 0.1:
            action_items.append("Review and potentially increase your insurance coverage")
        
        return action_items[:4]  # Return max 4 action items
