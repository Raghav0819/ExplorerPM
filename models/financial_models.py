import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score
import joblib
import os
import streamlit as st

class FinancialModels:
    def __init__(self):
        self.expense_model = None
        self.investment_model = None
        self.risk_model = None
        self.insurance_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        
    @st.cache_data
    def load_training_data(_self):
        """Load the training data from the uploaded CSV file"""
        try:
            # Try to load from attached assets
            data = pd.read_csv('attached_assets/financial_data_final_1751103631294.csv')
            return data
        except:
            st.error("Could not load training data. Please ensure the CSV file is available.")
            return None
    
    def preprocess_data(self, data):
        """Preprocess the financial data for training"""
        if data is None:
            return None, None
        
        try:
            # Make a copy to avoid modifying original data
            data_copy = data.copy()
            
            # Handle categorical variables
            categorical_cols = ['income_type', 'class', 'financial_stress', 'owns_home', 'user_goals']
            
            for col in categorical_cols:
                if col in data_copy.columns:
                    if col not in self.label_encoders:
                        self.label_encoders[col] = LabelEncoder()
                        data_copy[col] = self.label_encoders[col].fit_transform(data_copy[col].astype(str))
                    else:
                        data_copy[col] = self.label_encoders[col].transform(data_copy[col].astype(str))
            
            # Define features and targets
            feature_cols = [
                'household_size', 'number_of_kids', 'income_type', 'class',
                'gross_monthly_income', 'net_monthly_income', 'assets_total',
                'investments_total', 'savings_total', 'debts_total'
            ]
            
            # Select only available columns
            available_cols = [col for col in feature_cols if col in data_copy.columns]
            if not available_cols:
                return None, None
                
            X = data_copy[available_cols].fillna(0)
            
            # Different targets for different models
            targets = {
                'expense_prediction': 'fixed_costs_total',
                'investment_score': 'investments_total', 
                'risk_score': 'financial_stress',
                'insurance_gap': 'insurance'
            }
            
            return X, targets
            
        except Exception as e:
            st.error(f"Error preprocessing data: {str(e)}")
            return None, None
    
    def train_models(self):
        """Train all financial prediction models"""
        data = self.load_training_data()
        if data is None:
            return False
        
        X, targets = self.preprocess_data(data)
        if X is None or targets is None:
            return False
        
        try:
            # Ensure consistent data sizes by aligning X with the data length
            min_samples = min(len(X), len(data))
            X = X.iloc[:min_samples]
            data_aligned = data.iloc[:min_samples]
            
            # Expense Prediction Model
            y_expense = data_aligned[targets['expense_prediction']].fillna(0)
            X_train, X_test, y_train_exp, y_test_exp = train_test_split(X, y_expense, test_size=0.2, random_state=42)
            
            self.expense_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.expense_model.fit(X_train, y_train_exp)
            
            # Investment Recommendation Model
            y_investment = data_aligned[targets['investment_score']].fillna(0)
            X_train_inv, X_test_inv, y_train_inv, y_test_inv = train_test_split(X, y_investment, test_size=0.2, random_state=42)
            
            self.investment_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.investment_model.fit(X_train_inv, y_train_inv)
            
            # Risk Assessment Model - Convert financial stress to binary
            y_risk_binary = (data_aligned['financial_stress'] == 'yes').astype(int)
            X_train_risk, X_test_risk, y_train_risk, y_test_risk = train_test_split(X, y_risk_binary, test_size=0.2, random_state=42)
            
            self.risk_model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.risk_model.fit(X_train_risk, y_train_risk)
            
            # Insurance Gap Model
            y_insurance = data_aligned[targets['insurance_gap']].fillna(0)
            X_train_ins, X_test_ins, y_train_ins, y_test_ins = train_test_split(X, y_insurance, test_size=0.2, random_state=42)
            
            self.insurance_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.insurance_model.fit(X_train_ins, y_train_ins)
            
            # Fit scaler
            self.scaler.fit(X_train)
            
            self.is_trained = True
            return True
            
        except Exception as e:
            st.error(f"Error training models: {str(e)}")
            return False
    
    def prepare_user_features(self, user_data):
        """Prepare user data for prediction"""
        if not user_data:
            return None
        
        try:
            # Handle categorical encoding safely
            income_type_encoded = 0
            if 'income_type' in self.label_encoders:
                income_type = user_data.get('income_type', 'single_income')
                if income_type in self.label_encoders['income_type'].classes_:
                    income_type_encoded = self.label_encoders['income_type'].transform([income_type])[0]
            
            class_encoded = 0
            if 'class' in self.label_encoders:
                social_class = user_data.get('class', 'middle')
                if social_class in self.label_encoders['class'].classes_:
                    class_encoded = self.label_encoders['class'].transform([social_class])[0]
            
            # Create feature vector with proper column names
            feature_columns = [
                'household_size', 'number_of_kids', 'income_type', 'class',
                'gross_monthly_income', 'net_monthly_income', 'assets_total',
                'investments_total', 'savings_total', 'debts_total'
            ]
            
            feature_values = [
                user_data.get('household_size', 1),
                user_data.get('number_of_kids', 0),
                income_type_encoded,
                class_encoded,
                user_data.get('gross_monthly_income', 0),
                user_data.get('net_monthly_income', 0),
                user_data.get('assets_total', 0),
                user_data.get('investments_total', 0),
                user_data.get('savings_total', 0),
                user_data.get('debts_total', 0)
            ]
            
            # Return as numpy array for sklearn compatibility
            features = np.array(feature_values).reshape(1, -1)
            return features
            
        except Exception as e:
            st.error(f"Error preparing user features: {str(e)}")
            return None
    
    def predict_expenses(self, user_data):
        """Predict future expenses"""
        if not self.is_trained:
            self.train_models()
        
        features = self.prepare_user_features(user_data)
        if features is None or self.expense_model is None:
            return 0
        
        prediction = self.expense_model.predict(features)
        return float(prediction[0]) if len(prediction) > 0 else 0
    
    def predict_investment_potential(self, user_data):
        """Predict investment potential"""
        if not self.is_trained:
            self.train_models()
        
        features = self.prepare_user_features(user_data)
        if features is None or self.investment_model is None:
            return 0
        
        prediction = self.investment_model.predict(features)
        return float(prediction[0]) if len(prediction) > 0 else 0
    
    def assess_risk(self, user_data):
        """Assess financial risk"""
        if not self.is_trained:
            self.train_models()
        
        features = self.prepare_user_features(user_data)
        if features is None or self.risk_model is None:
            return 0.5
        
        try:
            risk_proba = self.risk_model.predict_proba(features)
            return float(risk_proba[0][1]) if len(risk_proba) > 0 and len(risk_proba[0]) > 1 else 0.5
        except:
            return 0.5
    
    def predict_insurance_need(self, user_data):
        """Predict insurance coverage needed"""
        if not self.is_trained:
            self.train_models()
        
        features = self.prepare_user_features(user_data)
        if features is None or self.insurance_model is None:
            return 0
        
        prediction = self.insurance_model.predict(features)
        return float(prediction[0]) if len(prediction) > 0 else 0
    
    def generate_predictions(self, user_data):
        """Generate comprehensive financial predictions"""
        if not self.is_trained:
            success = self.train_models()
            if not success:
                return {}
        
        # Get base predictions
        expense_pred = self.predict_expenses(user_data)
        investment_pred = self.predict_investment_potential(user_data)
        risk_score = self.assess_risk(user_data)
        insurance_pred = self.predict_insurance_need(user_data)
        
        # Calculate growth projections
        current_income = user_data.get('net_monthly_income', 0)
        current_savings = user_data.get('savings_total', 0)
        
        predictions = {
            '1_year': {
                'savings_growth': current_savings * 1.1 + (current_income * 0.2 * 12),
                'investment_returns': investment_pred * 0.12,
                'risk_score': risk_score * 10,
                'health_status': 'Good' if risk_score < 0.3 else 'Moderate' if risk_score < 0.7 else 'High Risk'
            },
            '3_year': {
                'savings_growth': current_savings * 1.35 + (current_income * 0.2 * 36),
                'investment_returns': investment_pred * 0.4,
                'risk_score': risk_score * 10,
                'health_status': 'Good' if risk_score < 0.3 else 'Moderate' if risk_score < 0.7 else 'High Risk'
            },
            '10_year': {
                'savings_growth': current_savings * 2.5 + (current_income * 0.25 * 120),
                'investment_returns': investment_pred * 1.8,
                'risk_score': risk_score * 10,
                'health_status': 'Excellent' if risk_score < 0.2 else 'Good' if risk_score < 0.5 else 'Moderate'
            }
        }
        
        return predictions
    
    def get_feature_importance(self):
        """Get feature importance from trained models"""
        if not self.is_trained:
            return {}
        
        importance_data = {}
        
        if self.expense_model:
            importance_data['expense'] = self.expense_model.feature_importances_
        if self.investment_model:
            importance_data['investment'] = self.investment_model.feature_importances_
        if self.risk_model:
            importance_data['risk'] = self.risk_model.feature_importances_
        if self.insurance_model:
            importance_data['insurance'] = self.insurance_model.feature_importances_
            
        return importance_data
