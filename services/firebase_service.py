import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# load environment variables from .env
load_dotenv()

class FirebaseService:
    def __init__(self):
        self.db = MockFirestore()  # fallback mock DB
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            if not firebase_admin._apps:
                # get service account JSON string from .env
                firebase_creds = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
                
                if firebase_creds:
                    cred_dict = json.loads(firebase_creds)
                    cred = credentials.Certificate(cred_dict)
                    
                    firebase_admin.initialize_app(cred, {
                        "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
                    })
                    self.db = firestore.client()
                    st.success("Connected to Firebase successfully.")
                    return
                else:
                    st.warning("No Firebase credentials found in .env; using local mock Firestore.")
                    self.db = MockFirestore()
                    return
            
            self.db = firestore.client()
        except Exception as e:
            st.warning("Firebase initialization failed. Using local mock Firestore.")
            st.error(f"Error: {e}")
            self.db = MockFirestore()
    
    def save_user_data(self, user_id, user_data):
        """Save user financial data to Firestore"""
        try:
            user_data['timestamp'] = datetime.now()
            user_data['user_id'] = user_id
            
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(user_data, merge=True)
            return True
            
        except Exception as e:
            st.error(f"Error saving user data: {str(e)}")
            return False
    
    def get_user_data(self, user_id):
        """Retrieve user financial data from Firestore"""
        try:
            doc_ref = self.db.collection('users').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists():
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            st.error(f"Error retrieving user data: {str(e)}")
            return None
    
    def save_chat_history(self, user_id, chat_history):
        """Save chat history to Firestore"""
        try:
            chat_data = {
                'user_id': user_id,
                'chat_history': chat_history,
                'timestamp': datetime.now().isoformat(),
            }
            
            self.db.collection('chats').document(user_id).set(chat_data, merge=True)
            return True
            
        except Exception as e:
            st.error(f"Error saving chat history: {str(e)}")
            return False
    
    def get_chat_history(self, user_id):
        """Retrieve chat history from Firestore"""
        try:
            doc_ref = self.db.collection('chat_history').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists():
                return doc.to_dict().get('chat_history', [])
            else:
                return []
        except Exception as e:
            st.error(f"Error retrieving chat history: {str(e)}")
            return []
    
    def save_predictions(self, user_id, predictions):
        """Save financial predictions to Firestore"""
        try:
            prediction_data = {
                'user_id': user_id,
                'predictions': predictions,
                'timestamp': datetime.now()
            }
            
            doc_ref = self.db.collection('predictions').document(user_id)
            doc_ref.set(prediction_data, merge=True)
            return True
            
        except Exception as e:
            st.error(f"Error saving predictions: {str(e)}")
            return False
    
    def save_user_profile(self, user_id, user_data):
        """Save user profile data to Firestore"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_ref.set(user_data, merge=True)
            return True
        except Exception as e:
            st.error(f"Error saving user profile: {str(e)}")
            return False
    
    def get_user_by_email(self, email):
        """Get user by email address"""
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = query.get()
            
            for doc in docs:
                return {'id': doc.id, 'data': doc.to_dict()}
            return None
        except Exception as e:
            st.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_verification_token(self, token):
        """Get user by verification token"""
        try:
            users_ref = self.db.collection('users')
            query = users_ref.where('verification_token', '==', token).limit(1)
            docs = query.get()
            
            for doc in docs:
                return {'id': doc.id, 'data': doc.to_dict()}
            return None
        except Exception as e:
            st.error(f"Error getting user by verification token: {e}")
            return None

    def get_all_users_summary(self):
        """Get summary data for all users (for analytics)"""
        try:
            users_ref = self.db.collection('users')
            docs = users_ref.stream()
            
            summary_data = []
            for doc in docs:
                user_data = doc.to_dict()
                summary_data.append({
                    'user_id': doc.id,
                    'income': user_data.get('net_monthly_income', 0),
                    'savings': user_data.get('savings_total', 0),
                    'timestamp': user_data.get('timestamp', '')
                })
            return summary_data
            
        except Exception as e:
            st.error(f"Error retrieving users summary: {str(e)}")
            return []

# ========== Mock Firestore classes ==========

class MockFirestore:
    """Mock Firestore service for local testing"""
    def __init__(self):
        self.data = {}
    
    def collection(self, collection_name):
        return MockCollection(self.data, collection_name)

class MockCollection:
    def __init__(self, data, collection_name):
        self.data = data
        self.collection_name = collection_name
        if collection_name not in self.data:
            self.data[collection_name] = {}
    
    def document(self, doc_id):
        return MockDocument(self.data[self.collection_name], doc_id)
    
    def where(self, field, operator, value):
        return MockQuery(self.data[self.collection_name], field, operator, value)
    
    def stream(self):
        docs = []
        for doc_id, doc_data in self.data[self.collection_name].items():
            docs.append(MockDocumentSnapshot(doc_id, doc_data))
        return docs

class MockQuery:
    def __init__(self, collection_data, field, operator, value):
        self.collection_data = collection_data
        self.field = field
        self.operator = operator
        self.value = value
        self.limit_count = None
    
    def limit(self, count):
        self.limit_count = count
        return self
    
    def get(self):
        results = []
        count = 0
        for doc_id, doc_data in self.collection_data.items():
            if self.operator == '==' and doc_data.get(self.field) == self.value:
                results.append(MockDocumentSnapshot(doc_id, doc_data))
                count += 1
                if self.limit_count and count >= self.limit_count:
                    break
        return results

class MockDocument:
    def __init__(self, collection_data, doc_id):
        self.collection_data = collection_data
        self.doc_id = doc_id
    
    def set(self, data, merge=False):
        if merge and self.doc_id in self.collection_data:
            self.collection_data[self.doc_id].update(data)
        else:
            self.collection_data[self.doc_id] = data
    
    def get(self):
        return MockDocumentSnapshot(self.doc_id, self.collection_data.get(self.doc_id))

class MockDocumentSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self.data = data
    
    def exists(self):
        return self.data is not None
    
    def to_dict(self):
        return self.data or {}
