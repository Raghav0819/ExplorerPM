import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st

class FinancialVisualizations:
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#17becf',
            'light': '#7f7f7f'
        }
    
    def create_income_expense_sankey(self, user_data):
        """Create Sankey diagram showing income flow to expenses and investments"""
        try:
            net_income = user_data.get('net_monthly_income', 0)
            
            # Define expense categories
            expenses = {
                'Housing': user_data.get('rent_mortgage', 0),
                'Utilities': user_data.get('utilities', 0),
                'Insurance': user_data.get('insurance', 0),
                'Transportation': user_data.get('transportation', 0),
                'Groceries': user_data.get('groceries', 0),
                'Miscellaneous': user_data.get('miscellaneous', 0)
            }
            
            # Calculate savings and investments
            total_expenses = sum(expenses.values())
            savings = max(0, net_income - total_expenses)
            
            # Prepare data for Sankey diagram
            labels = ['Income'] + list(expenses.keys()) + ['Savings']
            
            source = [0] * (len(expenses) + 1)  # All from income
            target = list(range(1, len(expenses) + 1)) + [len(labels) - 1]  # To expenses and savings
            values = list(expenses.values()) + [savings]
            
            # Filter out zero values
            filtered_data = [(s, t, v, labels[t]) for s, t, v in zip(source, target, values) if v > 0]
            
            if filtered_data:
                source, target, values, target_labels = zip(*filtered_data)
                
                fig = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=labels,
                        color=self.color_palette['primary']
                    ),
                    link=dict(
                        source=source,
                        target=target,
                        value=values,
                        color='rgba(31, 119, 180, 0.4)'
                    )
                )])
                
                fig.update_layout(
                    title_text="Monthly Income Flow",
                    font_size=10,
                    height=400
                )
                
                return fig
            else:
                return self.create_empty_chart("No income/expense data available")
                
        except Exception as e:
            st.error(f"Error creating Sankey diagram: {str(e)}")
            return self.create_empty_chart("Error creating visualization")
    
    def create_financial_health_gauge(self, health_score):
        """Create a gauge chart for financial health score"""
        try:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=health_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Financial Health Score"},
                delta={'reference': 50},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.color_palette['primary']},
                    'steps': [
                        {'range': [0, 30], 'color': self.color_palette['warning']},
                        {'range': [30, 60], 'color': self.color_palette['secondary']},
                        {'range': [60, 100], 'color': self.color_palette['success']}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=300)
            return fig
            
        except Exception as e:
            st.error(f"Error creating gauge chart: {str(e)}")
            return self.create_empty_chart("Error creating gauge")
    
    def create_expense_breakdown_pie(self, user_data):
        """Create pie chart for expense breakdown"""
        try:
            expenses = {
                'Housing': user_data.get('rent_mortgage', 0),
                'Utilities': user_data.get('utilities', 0),
                'Insurance': user_data.get('insurance', 0),
                'Transportation': user_data.get('transportation', 0),
                'Groceries': user_data.get('groceries', 0),
                'Clothes': user_data.get('clothes', 0),
                'Phone': user_data.get('phone', 0),
                'Subscriptions': user_data.get('subscriptions', 0),
                'Miscellaneous': user_data.get('miscellaneous', 0)
            }
            
            # Filter out zero values
            expenses = {k: v for k, v in expenses.items() if v > 0}
            
            if expenses:
                fig = px.pie(
                    values=list(expenses.values()),
                    names=list(expenses.keys()),
                    title="Monthly Expense Breakdown"
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                return fig
            else:
                return self.create_empty_chart("No expense data available")
                
        except Exception as e:
            st.error(f"Error creating pie chart: {str(e)}")
            return self.create_empty_chart("Error creating expense breakdown")
    
    def create_investment_portfolio_chart(self, user_data):
        """Create chart showing investment portfolio allocation"""
        try:
            total_investments = user_data.get('investments_total', 0)
            total_savings = user_data.get('savings_total', 0)
            emergency_fund = user_data.get('emergency_fund', 0)
            
            portfolio = {
                'Investments': total_investments,
                'Savings': total_savings,
                'Emergency Fund': emergency_fund
            }
            
            # Filter out zero values
            portfolio = {k: v for k, v in portfolio.items() if v > 0}
            
            if portfolio:
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(portfolio.keys()),
                        y=list(portfolio.values()),
                        marker_color=[self.color_palette['primary'], 
                                    self.color_palette['success'], 
                                    self.color_palette['info']]
                    )
                ])
                
                fig.update_layout(
                    title="Portfolio Allocation",
                    xaxis_title="Category",
                    yaxis_title="Amount (₹)",
                    height=400
                )
                
                return fig
            else:
                return self.create_empty_chart("No portfolio data available")
                
        except Exception as e:
            st.error(f"Error creating portfolio chart: {str(e)}")
            return self.create_empty_chart("Error creating portfolio visualization")
    
    def create_financial_timeline(self, predictions):
        """Create timeline chart showing financial predictions"""
        try:
            periods = ['Current', '1 Year', '3 Years', '10 Years']
            
            # Extract data from predictions
            current_savings = 0  # Would come from user data
            savings_1y = predictions.get('1_year', {}).get('savings_growth', 0)
            savings_3y = predictions.get('3_year', {}).get('savings_growth', 0)
            savings_10y = predictions.get('10_year', {}).get('savings_growth', 0)
            
            savings_values = [current_savings, savings_1y, savings_3y, savings_10y]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=periods,
                y=savings_values,
                mode='lines+markers',
                name='Projected Savings',
                line=dict(color=self.color_palette['primary'], width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title="Financial Growth Timeline",
                xaxis_title="Time Period",
                yaxis_title="Amount (₹)",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating timeline chart: {str(e)}")
            return self.create_empty_chart("Error creating timeline")
    
    def create_risk_assessment_radar(self, risk_factors):
        """Create radar chart for risk assessment"""
        try:
            categories = list(risk_factors.keys())
            values = list(risk_factors.values())
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Risk Profile',
                line_color=self.color_palette['warning']
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Risk Assessment Profile",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating radar chart: {str(e)}")
            return self.create_empty_chart("Error creating risk assessment")
    
    def create_comparison_chart(self, user_data, benchmark_data):
        """Create comparison chart with market benchmarks"""
        try:
            categories = ['Savings Rate', 'Investment Rate', 'Expense Ratio', 'Debt Ratio']
            
            user_values = [
                user_data.get('savings_rate', 0) * 100,
                user_data.get('investment_rate', 0) * 100,
                user_data.get('expense_ratio', 0) * 100,
                user_data.get('debt_ratio', 0) * 100
            ]
            
            benchmark_values = [
                benchmark_data.get('savings_rate', 20),
                benchmark_data.get('investment_rate', 15),
                benchmark_data.get('expense_ratio', 50),
                benchmark_data.get('debt_ratio', 30)
            ]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Your Profile',
                x=categories,
                y=user_values,
                marker_color=self.color_palette['primary']
            ))
            
            fig.add_trace(go.Bar(
                name='Market Average',
                x=categories,
                y=benchmark_values,
                marker_color=self.color_palette['secondary']
            ))
            
            fig.update_layout(
                title="Your Financial Profile vs Market Average",
                xaxis_title="Financial Metrics",
                yaxis_title="Percentage (%)",
                barmode='group',
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating comparison chart: {str(e)}")
            return self.create_empty_chart("Error creating comparison")
    
    def create_empty_chart(self, message):
        """Create an empty chart with a message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            height=400
        )
        return fig
