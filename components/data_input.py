import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

class DataInput:
    def __init__(self, firebase_service, financial_models):
        self.firebase_service = firebase_service
        self.financial_models = financial_models
        
        # Initialize session state for user ID
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
    
    def render(self):
        """Render the data input interface"""
        st.title("📋 Financial Data Input")
        st.markdown("Please provide your financial information to get personalized insights and predictions.")
        
        # Option to load existing data
        self.render_data_management_section()
        
        # Main data input form
        with st.form("financial_data_form"):
            st.markdown("### 👨‍👩‍👧‍👦 Personal Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                household_size = st.number_input(
                    "Household Size", 
                    min_value=1, 
                    max_value=10, 
                    value=st.session_state.get('user_data', {}).get('household_size', 1),
                    help="Total number of people in your household"
                )
                
                number_of_kids = st.number_input(
                    "Number of Children", 
                    min_value=0, 
                    max_value=10, 
                    value=st.session_state.get('user_data', {}).get('number_of_kids', 0)
                )
                
                age = st.number_input(
                    "Your Age",
                    min_value=18,
                    max_value=100,
                    value=st.session_state.get('user_data', {}).get('age', 30)
                )
            
            with col2:
                income_type = st.selectbox(
                    "Income Type", 
                    ["single_income", "dual_income"],
                    index=0 if st.session_state.get('user_data', {}).get('income_type', 'single_income') == 'single_income' else 1,
                    help="Whether you have single or dual income in household"
                )
                
                social_class = st.selectbox(
                    "Social Class", 
                    ["poor", "lower_middle", "middle", "upper_middle", "rich"],
                    index=2,  # Default to middle
                    help="Your household's social economic class"
                )
                
                owns_home = st.selectbox(
                    "Home Ownership",
                    ["yes", "no"],
                    index=0 if st.session_state.get('user_data', {}).get('owns_home', 'no') == 'yes' else 1
                )
            
            st.markdown("### 💰 Income Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                gross_monthly_income = st.number_input(
                    "Gross Monthly Income (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('gross_monthly_income', 0),
                    step=1000,
                    help="Your total monthly income before taxes"
                )
            
            with col2:
                net_monthly_income = st.number_input(
                    "Net Monthly Income (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('net_monthly_income', 0),
                    step=1000,
                    help="Your monthly income after taxes and deductions"
                )
            
            st.markdown("### 🏦 Assets and Investments")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                assets_total = st.number_input(
                    "Total Assets (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('assets_total', 0),
                    step=10000,
                    help="Total value of all your assets"
                )
                
                investments_total = st.number_input(
                    "Total Investments (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('investments_total', 0),
                    step=5000,
                    help="Total value of your investments (stocks, mutual funds, etc.)"
                )
            
            with col2:
                savings_total = st.number_input(
                    "Total Savings (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('savings_total', 0),
                    step=5000,
                    help="Total amount in savings accounts, FDs, etc."
                )
                
                emergency_fund = st.number_input(
                    "Emergency Fund (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('emergency_fund', 0),
                    step=5000,
                    help="Amount set aside specifically for emergencies"
                )
            
            with col3:
                debts_total = st.number_input(
                    "Total Debts (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('debts_total', 0),
                    step=5000,
                    help="Total outstanding debt (loans, credit cards, etc.)"
                )
                
                # Calculate net worth
                net_worth = assets_total + investments_total + savings_total - debts_total
                st.metric("Calculated Net Worth", f"₹{net_worth:,.0f}")
            
            st.markdown("### 💸 Monthly Expenses")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                rent_mortgage = st.number_input(
                    "Rent/Mortgage (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('rent_mortgage', 0),
                    step=1000
                )
                
                utilities = st.number_input(
                    "Utilities (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('utilities', 0),
                    step=500
                )
                
                insurance = st.number_input(
                    "Insurance Premiums (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('insurance', 0),
                    step=500
                )
            
            with col2:
                transportation = st.number_input(
                    "Transportation (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('transportation', 0),
                    step=500
                )
                
                groceries = st.number_input(
                    "Groceries (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('groceries', 0),
                    step=500
                )
                
                clothes = st.number_input(
                    "Clothing (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('clothes', 0),
                    step=500
                )
            
            with col3:
                phone = st.number_input(
                    "Phone Bills (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('phone', 0),
                    step=100
                )
                
                subscriptions = st.number_input(
                    "Subscriptions (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('subscriptions', 0),
                    step=100
                )
                
                miscellaneous = st.number_input(
                    "Miscellaneous (₹)", 
                    min_value=0, 
                    value=st.session_state.get('user_data', {}).get('miscellaneous', 0),
                    step=500
                )
            
            # Calculate total expenses
            total_expenses = (rent_mortgage + utilities + insurance + transportation + 
                            groceries + clothes + phone + subscriptions + miscellaneous)
            
            st.metric("Total Monthly Expenses", f"₹{total_expenses:,.0f}")
            
            # Budget analysis
            if net_monthly_income > 0:
                expense_ratio = total_expenses / net_monthly_income
                remaining = net_monthly_income - total_expenses
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Expense Ratio", f"{expense_ratio:.1%}")
                with col2:
                    st.metric("Monthly Surplus/Deficit", f"₹{remaining:,.0f}")
                
                if expense_ratio > 0.8:
                    st.warning("⚠️ Your expenses are very high relative to your income!")
                elif expense_ratio > 0.6:
                    st.info("💡 Consider reviewing your expenses to increase savings.")
                else:
                    st.success("✅ Good expense management!")
            
            st.markdown("### 🎯 Financial Goals")
            
            user_goals = st.selectbox(
                "Primary Financial Goal",
                [
                    "Build emergency fund", "Retirement savings", "Pay off debt",
                    "Buy a new car", "Upgrade to a bigger house", "Plan a family vacation",
                    "Start an education fund", "Save for kids' college", "Invest in stock market",
                    "Open a PPF account", "Increase term insurance", "Down payment for a house",
                    "Start a small business", "Build wealth for kids", "Fund children's marriage",
                    "Pay medical bills", "Renovate home", "Build passive income",
                    "Travel abroad next year", "Repay credit card dues"
                ],
                help="Select your most important financial goal"
            )
            
            financial_stress = st.selectbox(
                "Do you experience financial stress?",
                ["no", "yes"],
                help="Whether you regularly worry about your finances"
            )
            
            # Submit button
            submitted = st.form_submit_button("💾 Save Financial Data", type="primary")
            
            if submitted:
                self.save_user_data({
                    'household_size': household_size,
                    'number_of_kids': number_of_kids,
                    'age': age,
                    'income_type': income_type,
                    'class': social_class,
                    'owns_home': owns_home,
                    'gross_monthly_income': gross_monthly_income,
                    'net_monthly_income': net_monthly_income,
                    'assets_total': assets_total,
                    'investments_total': investments_total,
                    'savings_total': savings_total,
                    'emergency_fund': emergency_fund,
                    'debts_total': debts_total,
                    'total_net_worth': net_worth,
                    'rent_mortgage': rent_mortgage,
                    'utilities': utilities,
                    'insurance': insurance,
                    'transportation': transportation,
                    'groceries': groceries,
                    'clothes': clothes,
                    'phone': phone,
                    'subscriptions': subscriptions,
                    'miscellaneous': miscellaneous,
                    'fixed_costs_total': total_expenses,
                    'user_goals': user_goals,
                    'financial_stress': financial_stress
                })
    
    def render_data_management_section(self):
        """Render data management options"""
        st.markdown("### 🔧 Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Load Saved Data"):
                self.load_user_data()
        
        with col2:
            if st.button("🔄 Clear All Data"):
                self.clear_user_data()
        
        with col3:
            if st.button("📊 View Sample Data"):
                self.load_sample_data()
        
        # File upload option
        st.markdown("#### 📁 Import from CSV")
        uploaded_file = st.file_uploader(
            "Upload your financial data CSV", 
            type=['csv'],
            help="Upload a CSV file with your financial data"
        )
        
        if uploaded_file is not None:
            self.import_from_csv(uploaded_file)
    
    def save_user_data(self, user_data):
        """Save user data to session state and Firebase"""
        try:
            # Add timestamp
            user_data['last_updated'] = datetime.now().isoformat()
            
            # Save to session state
            st.session_state.user_data = user_data
            
            # Save to Firebase
            success = self.firebase_service.save_user_data(st.session_state.user_id, user_data)
            
            if success:
                st.success("✅ Financial data saved successfully!")
                
                # Train models with new data if needed
                if not self.financial_models.is_trained:
                    with st.spinner("Training AI models with your data..."):
                        self.financial_models.train_models()
                
                # Show next steps
                st.info("💡 You can now view your dashboard and get AI insights! Use the sidebar navigation to go to 'Dashboard'.")
                    
            else:
                st.error("❌ Failed to save data. Please try again.")
                
        except Exception as e:
            st.error(f"Error saving data: {str(e)}")
    
    def load_user_data(self):
        """Load user data from Firebase"""
        try:
            user_data = self.firebase_service.get_user_data(st.session_state.user_id)
            
            if user_data:
                st.session_state.user_data = user_data
                st.success("✅ Data loaded successfully!")
                st.rerun()
            else:
                st.warning("No saved data found for this user.")
                
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    
    def clear_user_data(self):
        """Clear all user data"""
        if 'user_data' in st.session_state:
            del st.session_state.user_data
        
        st.success("✅ All data cleared!")
        st.rerun()
    
    def load_sample_data(self):
        """Load sample data for demonstration"""
        sample_data = {
            'household_size': 4,
            'number_of_kids': 2,
            'age': 35,
            'income_type': 'dual_income',
            'class': 'middle',
            'owns_home': 'yes',
            'gross_monthly_income': 80000,
            'net_monthly_income': 65000,
            'assets_total': 2500000,
            'investments_total': 400000,
            'savings_total': 150000,
            'emergency_fund': 200000,
            'debts_total': 800000,
            'total_net_worth': 2250000,
            'rent_mortgage': 20000,
            'utilities': 3000,
            'insurance': 4000,
            'transportation': 8000,
            'groceries': 12000,
            'clothes': 3000,
            'phone': 2000,
            'subscriptions': 1500,
            'miscellaneous': 5000,
            'fixed_costs_total': 58500,
            'user_goals': 'Retirement savings',
            'financial_stress': 'no'
        }
        
        st.session_state.user_data = sample_data
        st.success("✅ Sample data loaded!")
        st.rerun()
    
    def import_from_csv(self, uploaded_file):
        """Import financial data from CSV file"""
        try:
            df = pd.read_csv(uploaded_file)
            
            # Display preview
            st.markdown("#### 📋 Data Preview")
            st.dataframe(df.head())
            
            if st.button("Import This Data"):
                # Convert first row to user data format
                if len(df) > 0:
                    row = df.iloc[0].to_dict()
                    
                    # Map CSV columns to our format (if needed)
                    user_data = {}
                    for key, value in row.items():
                        if pd.notna(value):
                            user_data[key] = value
                    
                    st.session_state.user_data = user_data
                    st.success("✅ Data imported successfully!")
                    st.rerun()
                else:
                    st.error("CSV file is empty!")
                    
        except Exception as e:
            st.error(f"Error importing CSV: {str(e)}")
    
    def export_user_data(self):
        """Export user data to CSV"""
        if 'user_data' in st.session_state and st.session_state.user_data:
            df = pd.DataFrame([st.session_state.user_data])
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Financial Data",
                data=csv,
                file_name=f"financial_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
