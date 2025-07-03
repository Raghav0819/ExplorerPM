import os
import json
import streamlit as st
from datetime import datetime
import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
collections.Sequence = collections.abc.Sequence
collections.Callable = collections.abc.Callable
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

class AuthManager:
    def __init__(self, firebase_service):
        self.firebase_service = firebase_service
        self.firebase_config = {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID"),
        }
        
        missing = [k for k, v in self.firebase_config.items() if not v]
        if missing:
            st.error(f"Missing Firebase config keys: {missing}")
            raise Exception("Incomplete Firebase config")
        
        self.firebase = pyrebase.initialize_app(self.firebase_config)
        self.auth = self.firebase.auth()
        
        if not firebase_admin._apps:
            cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
            if cred_json:
                cred = credentials.Certificate(json.loads(cred_json))
                firebase_admin.initialize_app(cred)
            else:
                st.error("Missing FIREBASE_SERVICE_ACCOUNT_KEY")
                raise Exception("Missing service account key")

        self.db = firestore.client()

    def register_user(self, email, password, full_name):
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            self.auth.send_email_verification(user['idToken'])
            
            user_data = {
                "uid": user['localId'],
                "email": email,
                "full_name": full_name,
                "email_verified": False,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
            }
            self.db.collection("users").document(user['localId']).set(user_data)
            return True, (
                "Registration successful! A verification email has been sent. "
                "Please verify your email before logging in."
            )
        except Exception as e:
            err = str(e)
            if "EMAIL_EXISTS" in err:
                return False, "This email already exists."
            elif "WEAK_PASSWORD" in err:
                return False, "Password should be at least 6 characters."
            elif "INVALID_EMAIL" in err:
                return False, "Invalid email format."
            else:
                return False, f"Registration failed: {err}"

    def login_user(self, email, password):
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            user_info = self.auth.get_account_info(user['idToken'])
            verified = user_info['users'][0]['emailVerified']
            
            if not verified:
                return False, (
                    "Your email is not verified. Please check your inbox for the verification email."
                )
            
            # get full name
            user_doc = self.db.collection("users").document(user['localId']).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                full_name = user_data.get("full_name", "")
            else:
                full_name = user_info['users'][0].get("displayName", "") or ""

            # update
            self.db.collection("users").document(user['localId']).update({
                "last_login": datetime.now().isoformat(),
                "email_verified": True
            })
            
            st.session_state.user_id = user['localId']
            st.session_state.user_email = email
            st.session_state.user_name = full_name if full_name else "User"
            st.session_state["is_logged_in"] = True

            # restore user_data
            try:
                if user_doc.exists:
                    st.session_state.user_data = user_doc.to_dict()
                else:
                    st.session_state.user_data = {}
            except Exception as e:
                st.warning(f"Could not load user_data from Firestore: {e}")
                st.session_state.user_data = {}

            # restore chat_history
            try:
                chat_doc = self.db.collection("chats").document(user['localId']).get()
                if chat_doc.exists:
                    messages = chat_doc.to_dict().get("messages", [])
                    st.session_state.chat_history = messages
                    st.session_state.chat_messages = messages
                else:
                    st.session_state.chat_history = []
                    st.session_state.chat_messages = []
            except Exception as e:
                st.warning(f"Could not load chat history from Firestore: {e}")
                st.session_state.chat_history = []
                st.session_state.chat_messages = []

            return True, "Login successful!"

        except Exception as e:
            err = str(e)
            if "INVALID_PASSWORD" in err or "EMAIL_NOT_FOUND" in err:
                return False, "Invalid email or password."
            elif "USER_DISABLED" in err:
                return False, "Account disabled."
            else:
                return False, f"Login failed: {err}"

    def reset_password(self, email):
        try:
            self.auth.send_password_reset_email(email)
            return True, "Password reset email sent! Please check your inbox."
        except Exception as e:
            return False, f"Reset failed: {str(e)}"

    def logout_user(self):
        for key in ['user_id', 'user_email', 'user_name', 'is_logged_in']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    def is_logged_in(self):
        return st.session_state.get('is_logged_in', False)

    def get_current_user_data(self):
        if not self.is_logged_in():
            return None
        try:
            user_doc = self.db.collection("users").document(st.session_state.user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            st.error(f"Error retrieving user data: {str(e)}")
            return None

    def render_auth_page(self):
        st.title("🔐 Explorer PM - Financial Portfolio Manager")
        st.markdown("### Secure Login to Your Financial Dashboard")

        tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "Reset Password"])

        with tab1:
            self.render_login_form()
        with tab2:
            self.render_signup_form()
        with tab3:
            self.render_reset_form()

    def render_login_form(self):
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email address")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            if submitted:
                if not email or not password:
                    st.error("Please fill in both email and password")
                else:
                    with st.spinner("Logging in..."):
                        success, msg = self.login_user(email, password)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    def render_signup_form(self):
        st.subheader("Create New Account")
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email = st.text_input("Email", placeholder="Enter your email address")
            password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter your password")
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            if submitted:
                if not all([name, email, password, confirm]):
                    st.error("All fields are required")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif password != confirm:
                    st.error("Passwords do not match")
                else:
                    with st.spinner("Creating account..."):
                        success, msg = self.register_user(email, password, name)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

    def render_reset_form(self):
        st.subheader("Reset Password")
        with st.form("reset_form"):
            email = st.text_input("Email", placeholder="Enter your email address")
            submitted = st.form_submit_button("Send Reset Email", use_container_width=True)
            if submitted:
                if not email:
                    st.error("Please enter your email address")
                else:
                    with st.spinner("Sending reset email..."):
                        success, msg = self.reset_password(email)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

    def save_chat_history(self, user_id, chat_history):
        """
        Save chat history to Firestore
        """
        try:
            if not chat_history:
                return False  # do not save empty
            
            chat_data={
                "user_id": user_id,
                "messages": chat_history,
                "timestamp": datetime.now().isoformat()
            }
            self.db.collection("chats").document(user_id).set(chat_data, merge=True)
            return True
        except Exception as e:
            st.error(f"Error saving chat history: {str(e)}")
            return False

    def render_user_profile(self):
        if self.is_logged_in():
            user_data = self.get_current_user_data()
            with st.sidebar:
                st.markdown("---")
                st.markdown("### 👤 User Profile")
                if user_data:
                    st.markdown(f"**{user_data.get('full_name', 'User')}**")
                    st.markdown(f"📧 {st.session_state.user_email}")
                    if user_data.get('last_login'):
                        st.markdown(f"🕒 Last login: {user_data['last_login'][:10]}")
                else:
                    st.markdown(f"**{st.session_state.get('user_name', 'User')}**")
                    st.markdown(f"📧 {st.session_state.user_email}")
                
                st.markdown("---")
                if st.button("🚪 Logout", use_container_width=True):
                    self.logout_user()
