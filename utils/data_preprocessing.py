import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import streamlit as st

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
    
    def load_financial_data(self, file_path=None):
        """Load financial data from CSV file"""
        try:
            if file_path:
                data = pd.read_csv(file_path)
            else:
                # Load from attached assets
                data = pd.read_csv('attached_assets/financial_data_final_1751103631294.csv')
            
            return data
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
    
    def clean_financial_data(self, data):
        """Clean and preprocess financial data"""
        if data is None:
            return None
        
        # Make a copy to avoid modifying original data
        cleaned_data = data.copy()
        
        # Handle missing values
        numeric_columns = cleaned_data.select_dtypes(include=[np.number]).columns
        categorical_columns = cleaned_data.select_dtypes(include=['object']).columns
        
        # Fill numeric columns with median
        for col in numeric_columns:
            cleaned_data[col].fillna(cleaned_data[col].median(), inplace=True)
        
        # Fill categorical columns with mode
        for col in categorical_columns:
            cleaned_data[col].fillna(cleaned_data[col].mode()[0] if not cleaned_data[col].mode().empty else 'unknown', inplace=True)
        
        # Remove outliers using IQR method for numeric columns
        for col in numeric_columns:
            if col != 'user_id':  # Don't remove outliers from ID column
                Q1 = cleaned_data[col].quantile(0.25)
                Q3 = cleaned_data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Cap outliers instead of removing them
                cleaned_data[col] = np.clip(cleaned_data[col], lower_bound, upper_bound)
        
        return cleaned_data
    
    def encode_categorical_features(self, data, fit=True):
        """Encode categorical features"""
        if data is None:
            return None
        
        encoded_data = data.copy()
        categorical_columns = ['income_type', 'class', 'financial_stress', 'owns_home', 'user_goals']
        
        for col in categorical_columns:
            if col in encoded_data.columns:
                if fit:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                    encoded_data[col] = self.label_encoders[col].fit_transform(encoded_data[col].astype(str))
                else:
                    if col in self.label_encoders:
                        # Handle unseen labels
                        unique_labels = set(encoded_data[col].astype(str))
                        known_labels = set(self.label_encoders[col].classes_)
                        
                        # Replace unseen labels with the most frequent known label
                        if not unique_labels.issubset(known_labels):
                            most_frequent = self.label_encoders[col].classes_[0]
                            encoded_data[col] = encoded_data[col].astype(str).apply(
                                lambda x: x if x in known_labels else most_frequent
                            )
                        
                        encoded_data[col] = self.label_encoders[col].transform(encoded_data[col].astype(str))
        
        return encoded_data
    
    def create_feature_matrix(self, data):
        """Create feature matrix for ML models"""
        if data is None:
            return None
        
        # Define feature columns
        self.feature_columns = [
            'household_size', 'number_of_kids', 'income_type', 'class',
            'gross_monthly_income', 'net_monthly_income', 'assets_total',
            'investments_total', 'savings_total', 'debts_total',
            'rent_mortgage', 'utilities', 'insurance', 'transportation',
            'groceries', 'clothes', 'phone', 'subscriptions', 'miscellaneous'
        ]
        
        # Select only available columns
        available_columns = [col for col in self.feature_columns if col in data.columns]
        X = data[available_columns].copy()
        
        # Fill any remaining missing values
        X.fillna(0, inplace=True)
        
        return X
    
    def scale_features(self, X, fit=True):
        """Scale features using StandardScaler"""
        if X is None:
            return None
        
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    def prepare_user_data(self, user_input):
        """Prepare user input data for prediction"""
        if not user_input:
            return None
        
        # Create a DataFrame from user input
        user_df = pd.DataFrame([user_input])
        
        # Encode categorical features
        user_encoded = self.encode_categorical_features(user_df, fit=False)
        
        # Create feature matrix
        X_user = self.create_feature_matrix(user_encoded)
        
        # Fill missing columns with zeros
        for col in self.feature_columns:
            if col not in X_user.columns:
                X_user[col] = 0
        
        # Reorder columns to match training data
        X_user = X_user[self.feature_columns]
        
        # Scale features
        X_user_scaled = self.scale_features(X_user, fit=False)
        
        return X_user_scaled
    
    def get_financial_summary(self, data):
        """Get summary statistics of financial data"""
        if data is None:
            return {}
        
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        summary = {}
        
        for col in numeric_columns:
            if col != 'user_id':
                summary[col] = {
                    'mean': data[col].mean(),
                    'median': data[col].median(),
                    'std': data[col].std(),
                    'min': data[col].min(),
                    'max': data[col].max()
                }
        
        return summary
    
    def calculate_financial_ratios(self, user_data):
        """Calculate important financial ratios"""
        ratios = {}
        
        # Income-based ratios
        net_income = user_data.get('net_monthly_income', 0)
        gross_income = user_data.get('gross_monthly_income', 0)
        
        if gross_income > 0:
            ratios['tax_efficiency'] = net_income / gross_income
        
        # Expense ratios
        fixed_costs = user_data.get('fixed_costs_total', 0)
        if net_income > 0:
            ratios['expense_ratio'] = fixed_costs / net_income
        
        # Savings ratio
        savings = user_data.get('savings_total', 0)
        if net_income > 0:
            ratios['savings_rate'] = (savings / 12) / net_income  # Monthly savings rate
        
        # Debt-to-income ratio
        debts = user_data.get('debts_total', 0)
        if net_income > 0:
            ratios['debt_to_income'] = debts / (net_income * 12)  # Annual debt to annual income
        
        # Investment ratio
        investments = user_data.get('investments_total', 0)
        assets = user_data.get('assets_total', 0)
        if assets > 0:
            ratios['investment_allocation'] = investments / assets
        
        # Emergency fund ratio (assuming 6 months of expenses as target)
        emergency_fund = user_data.get('emergency_fund', 0)
        if fixed_costs > 0:
            ratios['emergency_fund_months'] = emergency_fund / fixed_costs
        
        return ratios
