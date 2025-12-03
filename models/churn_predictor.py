"""
Churn Prediction Engine
Uses machine learning to predict customer churn probability
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os


class ChurnPredictor:
    """
    AI-powered churn prediction engine
    Uses customer behavior and transaction patterns to predict churn
    """
    
    def __init__(self, model_path='models/churn_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        
        # Load model if exists, otherwise use rule-based approach
        if os.path.exists(model_path):
            self.load_model()
        else:
            print("No pre-trained model found. Using rule-based prediction.")
    
    def calculate_features(self, customer_data):
        """
        Calculate features from customer data for churn prediction
        
        Features:
        - Recency: Days since last transaction
        - Frequency: Number of transactions
        - Monetary: Total transaction value
        - Avg Transaction Value
        - Transaction Trend
        """
        features = {}
        
        # Handle both dict and DataFrame
        if isinstance(customer_data, dict):
            data = customer_data
        else:
            data = customer_data.to_dict()
        
        # Recency (days since last transaction)
        if 'last_transaction_date' in data:
            last_date = pd.to_datetime(data['last_transaction_date'])
            features['recency'] = (datetime.now() - last_date).days
        else:
            features['recency'] = 365  # Default high recency
        
        # Frequency (number of transactions)
        features['frequency'] = data.get('transaction_count', 0)
        
        # Monetary (total value)
        features['monetary'] = data.get('total_spent', 0)
        
        # Average transaction value
        if features['frequency'] > 0:
            features['avg_transaction'] = features['monetary'] / features['frequency']
        else:
            features['avg_transaction'] = 0
        
        # Engagement score (0-100)
        features['engagement_score'] = data.get('engagement_score', 50)
        
        # Account age in days
        if 'registration_date' in data:
            reg_date = pd.to_datetime(data['registration_date'])
            features['account_age'] = (datetime.now() - reg_date).days
        else:
            features['account_age'] = 180  # Default 6 months
        
        # Support tickets
        features['support_tickets'] = data.get('support_tickets', 0)
        
        return features
    
    def predict_churn_probability(self, features):
        """
        Predict churn probability using rule-based scoring
        
        Scoring Logic:
        - High recency (no recent activity) → High churn risk
        - Low frequency → High churn risk
        - Low monetary value → High churn risk
        - High support tickets → Potential issues
        - Low engagement → High churn risk
        """
        score = 0.0
        
        # Recency scoring (40% weight)
        recency = features['recency']
        if recency > 90:
            score += 0.40
        elif recency > 60:
            score += 0.30
        elif recency > 30:
            score += 0.15
        else:
            score += 0.05
        
        # Frequency scoring (25% weight)
        frequency = features['frequency']
        if frequency == 0:
            score += 0.25
        elif frequency <= 2:
            score += 0.20
        elif frequency <= 5:
            score += 0.10
        else:
            score += 0.02
        
        # Monetary scoring (20% weight)
        monetary = features['monetary']
        if monetary == 0:
            score += 0.20
        elif monetary < 50:
            score += 0.15
        elif monetary < 200:
            score += 0.08
        else:
            score += 0.02
        
        # Engagement scoring (10% weight)
        engagement = features['engagement_score']
        if engagement < 30:
            score += 0.10
        elif engagement < 50:
            score += 0.06
        elif engagement < 70:
            score += 0.03
        
        # Support tickets (5% weight)
        tickets = features['support_tickets']
        if tickets > 5:
            score += 0.05
        elif tickets > 2:
            score += 0.03
        
        # Ensure score is between 0 and 1
        churn_probability = min(max(score, 0.0), 1.0)
        
        return churn_probability
    
    def predict_single(self, customer_data):
        """
        Predict churn for a single customer
        
        Returns:
            dict: {
                'churn_probability': float,
                'risk_level': str,
                'features': dict
            }
        """
        # Calculate features
        features = self.calculate_features(customer_data)
        
        # Predict probability
        churn_prob = self.predict_churn_probability(features)
        
        # Determine risk level
        if churn_prob >= 0.7:
            risk_level = 'High'
        elif churn_prob >= 0.4:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        return {
            'churn_probability': round(churn_prob, 3),
            'risk_level': risk_level,
            'features': features
        }
    
    def predict_batch(self, customers_df):
        """
        Predict churn for multiple customers
        
        Args:
            customers_df: pandas DataFrame or list of dicts
            
        Returns:
            list: List of prediction dictionaries
        """
        predictions = []
        
        # Convert to list of dicts if DataFrame
        if isinstance(customers_df, pd.DataFrame):
            customers_list = customers_df.to_dict('records')
        else:
            customers_list = customers_df
        
        for customer in customers_list:
            pred = self.predict_single(customer)
            pred['customer_id'] = customer.get('id') or customer.get('customer_id')
            pred['customer_name'] = customer.get('name', 'Unknown')
            pred['email'] = customer.get('email', '')
            predictions.append(pred)
        
        return predictions
    
    def get_churn_reasons(self, features, churn_prob):
        """
        Identify main reasons for churn risk
        """
        reasons = []
        
        if features['recency'] > 60:
            reasons.append({
                'factor': 'Inactivity',
                'description': f"No transaction in {features['recency']} days",
                'impact': 'High'
            })
        
        if features['frequency'] <= 2:
            reasons.append({
                'factor': 'Low Engagement',
                'description': f"Only {features['frequency']} transactions",
                'impact': 'High'
            })
        
        if features['monetary'] < 100:
            reasons.append({
                'factor': 'Low Value',
                'description': f"Total spent: ${features['monetary']:.2f}",
                'impact': 'Medium'
            })
        
        if features['support_tickets'] > 3:
            reasons.append({
                'factor': 'Support Issues',
                'description': f"{features['support_tickets']} support tickets",
                'impact': 'Medium'
            })
        
        if features['engagement_score'] < 40:
            reasons.append({
                'factor': 'Poor Engagement',
                'description': f"Engagement score: {features['engagement_score']}/100",
                'impact': 'High'
            })
        
        return reasons
    
    def train_model(self, training_data, labels):
        """
        Train ML model on historical data (for future enhancement)
        """
        # Extract features
        X = []
        for data in training_data:
            features = self.calculate_features(data)
            X.append([
                features['recency'],
                features['frequency'],
                features['monetary'],
                features['avg_transaction'],
                features['engagement_score'],
                features['account_age'],
                features['support_tickets']
            ])
        
        X = np.array(X)
        y = np.array(labels)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        return True
    
    def save_model(self):
        """Save trained model to disk"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            print(f"Model loaded from {self.model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")