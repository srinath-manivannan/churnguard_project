# ChurnGuard AI - Customer Retention Platform

![ChurnGuard AI](https://img.shields.io/badge/AI-Powered-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Flask](https://img.shields.io/badge/Flask-3.0-red)

An AI-powered agentic platform designed to help organizations predict and prevent customer churn through automated communication and intelligent insights.

## 🚀 Features

- **AI Churn Prediction**: Advanced machine learning models identify customers likely to churn
- **Natural Language Chatbot**: Ask questions about your customers in plain English
- **Automated Campaigns**: Multi-channel communication (email, SMS, calls)
- **Sentiment Analysis**: Understand customer feedback and identify root causes
- **Advanced Analytics**: Track churn trends and campaign performance
- **Real-time Dashboard**: Beautiful visualizations and metrics

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- Visual Studio Code (recommended)

## 🛠️ Installation

### Step 1: Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd churnguard_project

# Or download the ZIP file and extract it
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📁 Project Structure

```
churnguard_project/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── models/                     # AI Models
│   ├── churn_predictor.py     # Churn prediction engine
│   └── chatbot.py             # Natural language chatbot
│
├── database/                   # Database layer
│   ├── db_manager.py          # Database operations
│   └── churnguard.db          # SQLite database (auto-created)
│
├── utils/                      # Utilities
│   └── data_processor.py      # Data processing & validation
│
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Home page
│   ├── dashboard.html         # Dashboard
│   ├── upload.html            # Data upload
│   ├── chatbot.html           # AI Chatbot
│   ├── campaigns.html         # Campaign management
│   └── analytics.html         # Analytics & insights
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Main stylesheet
│   └── js/
│       └── main.js            # JavaScript functions
│
└── uploads/                    # Uploaded files (auto-created)
```

## 📖 Usage Guide

### 1. Upload Customer Data

1. Navigate to **Upload Data** page
2. Click "Choose File" or drag & drop a CSV/Excel file
3. Required columns: `name`, `email`
4. Optional columns: `phone`, `registration_date`, `last_transaction_date`, `transaction_count`, `total_spent`, `engagement_score`, `support_tickets`
5. Click "Upload and Process"

**Sample CSV Format:**
```csv
name,email,phone,transaction_count,total_spent,last_transaction_date
John Smith,john@example.com,+1-555-1234,15,2500.00,2024-11-15
Jane Doe,jane@example.com,+1-555-5678,3,150.00,2024-08-20
```

### 2. View Dashboard

- See total customers and risk breakdown
- View revenue statistics
- Monitor churn risk distribution
- Browse customer list with churn scores

### 3. Use AI Chatbot

Ask questions like:
- "Show me high-risk customers"
- "What's our churn rate?"
- "How many customers do we have?"
- "Show me revenue statistics"
- "Tell me about customer 123"

### 4. Create Campaigns

1. Go to **Campaigns** page
2. Click "Create Campaign"
3. Fill in campaign details:
   - Name
   - Target Segment (High/Medium/Low Risk)
   - Channels (Email, SMS, Call)
   - Message Template
4. Execute campaign to send messages

### 5. View Analytics

- Track key metrics
- View churn distribution
- Read customer feedback
- Get actionable insights

## 🔧 Configuration

### Database

The application uses SQLite by default. Database file is created automatically at `database/churnguard.db`

### File Upload Settings

- Max file size: 16 MB
- Allowed formats: CSV, XLSX, XLS
- Upload directory: `uploads/`

## 🎯 For Interview/Demo

### Quick Start with Sample Data

1. Run the application
2. Go to **Upload Data** page
3. Click "Generate Sample CSV" button
4. Upload the generated sample file
5. Explore all features with sample data

### Key Features to Demonstrate

1. **Data Upload**: Show CSV upload process
2. **Churn Prediction**: Explain the AI scoring system
3. **Dashboard**: Walk through metrics and visualizations
4. **Chatbot**: Ask natural language questions
5. **Campaigns**: Create and execute a retention campaign
6. **Analytics**: Show insights and recommendations

## 🔍 How It Works

### Churn Prediction Algorithm

The system uses a rule-based scoring model that analyzes:

1. **Recency** (40% weight): Days since last transaction
2. **Frequency** (25% weight): Number of transactions
3. **Monetary** (20% weight): Total spending amount
4. **Engagement** (10% weight): Customer engagement score
5. **Support Issues** (5% weight): Number of support tickets

**Risk Levels:**
- **High Risk**: Churn probability ≥ 70%
- **Medium Risk**: Churn probability 40-69%
- **Low Risk**: Churn probability < 40%

### Chatbot NLP

Uses regex pattern matching to understand user queries:
- Intent recognition
- Entity extraction
- Context-aware responses
- Data retrieval from database

## 📊 API Endpoints

### Customer Management
- `GET /api/customers` - List all customers with scores
- `GET /api/customer/<id>` - Get customer details

### Chatbot
- `POST /chatbot` - Send message to chatbot

### Campaigns
- `POST /api/campaigns/create` - Create new campaign
- `POST /api/campaigns/<id>/execute` - Execute campaign

### Feedback
- `POST /api/feedback` - Submit customer feedback

## 🚧 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py, line: app.run(port=5001)
```

### Module Not Found Error
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors
```bash
# Delete database and restart
rm database/churnguard.db
python app.py
```

## 🌟 Future Enhancements

- [ ] Lifetime Value (LTV) prediction
- [ ] Personalized recommendation engine
- [ ] Multi-language support
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] E-commerce integrations
- [ ] Advanced ML models (Random Forest, XGBoost)
- [ ] Real-time email/SMS sending
- [ ] Mobile app

## 📝 Git Commands for Interview

### Initial Setup
```bash
# Initialize repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ChurnGuard AI Platform"

# Add remote repository
git remote add origin <your-repo-url>

# Push to GitHub
git push -u origin main
```

### Making Changes
```bash
# Check status
git status

# Add specific file
git add filename.py

# Commit changes
git commit -m "Description of changes"

# Push to remote
git push origin main
```

## 📄 License

This project is created for educational and interview purposes.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Built with Flask and Python
- UI inspired by modern SaaS applications
- Icons from Font Awesome
- Fonts from Google Fonts

---

**Note**: This is a demonstration project for interviews. For production use, implement proper security measures, authentication, and use production-grade databases.