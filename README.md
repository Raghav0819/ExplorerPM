
# Explorer PM - AI Financial Portfolio Manager

## Overview

Explorer PM is an AI-powered financial portfolio management application built with Streamlit. It serves as a "digital Janam Patri" (birth chart) for personal finance, providing comprehensive analysis of expenses, investments, risks, and insurance coverage. The application leverages Google's Gemini AI for intelligent financial advisory and Firebase for data persistence.

---

## 🏗️ How to Set Up This Project

Follow these steps to run Explorer PM locally or deploy it to the cloud.

### 🔧 Prerequisites

- Python 3.9+
- Firebase project with Firestore and Authentication enabled
- Google Gemini AI API Key
- Git

---

### 1. Clone the Repository

```bash
git clone https://github.com/Raghav0819/Explorerpm.git
cd ExplorerPM
```

---

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt


---

### 4. Set Up Environment Variables

Create a `.env` file in the root directory and add:

```
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_API_KEY=ENTER_KEY_HERE
FIREBASE_AUTH_DOMAIN=ENTER_CREDENTIAL
FIREBASE_PROJECT_ID=ENTER_CREDENTIAL
FIREBASE_STORAGE_BUCKET=ENTER_CREDENTIAL
FIREBASE_MESSAGING_SENDER_ID=ENTER_CREDENTIAL
FIREBASE_APP_ID=ENTER_CREDENTIAL
FIREBASE_DATABASE_URL=ENTER_CREDENTIAL
FIREBASE_SERVICE_ACCOUNT_KEY=PASTE_CONTENT_OF_JSON_FILE_HERE
```

Make sure the Firebase credentials JSON file is downloaded from your Firebase project’s settings.

---

### 5. Configure Firebase

- Go to [Firebase Console](https://console.firebase.google.com)
- Enable **Firestore Database**
- Enable **Email/Password Authentication**
- Create a service account and download the credentials (`.json`)

---

### 6. Run the Application

```bash
streamlit run app.py
```

Visit [http://localhost:8501](http://localhost:5000) to use the app locally.

---


## System Architecture

### Frontend Architecture

- **Framework**: Streamlit for web interface  
- **Structure**: Component-based architecture with modular UI components  
- **Navigation**: Multi-page app with sidebar  
- **State Management**: Streamlit session state  

### Backend Architecture

- **Core Services**: Firebase (Firestore + Auth), Gemini AI  
- **ML Models**: Custom models via `scikit-learn`  
- **Data Processing**: `pandas`, `numpy`  

---

## Key Components

1. **Authentication** (`components/auth.py`): Firebase login/signup with email verification  
2. **Chat Interface** (`components/chat_interface.py`): Gemini AI-powered financial advisor  
3. **Dashboard** (`components/dashboard.py`): Visual financial insights  
4. **Data Input** (`components/data_input.py`): User financial data entry  
5. **Financial Models** (`models/financial_models.py`): ML-based risk & investment prediction  

---

## Data Flow

1. **User Input** → via Streamlit forms  
2. **Processing** → cleaned and passed to ML models  
3. **AI Advisory** → Gemini AI generates context-aware advice  
4. **Visualization** → Interactive plots (Plotly)  
5. **Storage** → Firebase Firestore saves data per user  

---

## External Dependencies

| Category       | Library/Service      | Purpose                                           |
|----------------|----------------------|---------------------------------------------------|
| AI Services    | Google Gemini AI     | Financial NLP and Q&A                             |
| Database       | Firebase Firestore   | User data and chat history storage                |
| UI Framework   | Streamlit            | Web app framework                                 |
| ML & Data      | scikit-learn, pandas | Prediction models and data processing             |
| Visualization  | Plotly               | Interactive graphs and dashboards                 |

---

## Deployment Strategy

- **Cloud Ready**: Designed for Streamlit Cloud or custom hosting  
- **Env Management**: API keys via `.env` or Streamlit secrets  
- **Error Handling**: Graceful degradation with mock services  
- **Modular**: Clean separation between components and logic  

---

## Recent Changes

```
Recent Changes:
- June 28, 2025: Complete AI-powered financial portfolio manager implemented
- Enhanced ML models with proper data validation and error handling
- Advanced NLP capabilities for financial question answering
- Integrated Google Gemini AI with context-aware responses
- Added Firebase Authentication with email verification for user signup/login
- Personalized data storage per authenticated user
- Firebase automatically sends verification emails during signup
- Added specialized question detection for vacation planning, emergency funds, real estate
- Fixed data inconsistency issues in model training
- Added comprehensive error handling and fallback mechanisms
```

---

## User Preferences

```
Preferred communication style: Simple, everyday language.
```
