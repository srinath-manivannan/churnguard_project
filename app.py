"""
ChurnGuard - AI-Powered Customer Retention Platform
Main Application File
"""

from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import datetime
import json
from models.churn_predictor import ChurnPredictor
from models.chatbot import ChurnChatbot
from database.db_manager import DatabaseManager
from utils.data_processor import DataProcessor

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'churnguard-secret-key-2024'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('database', exist_ok=True)

# Initialize components
db_manager = DatabaseManager('database/churnguard.db')
churn_predictor = ChurnPredictor()
chatbot = ChurnChatbot()
data_processor = DataProcessor()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard with analytics"""
    stats = db_manager.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload customer data"""
    if request.method == 'POST':
        try:
            # Check if file is present
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if file and allowed_file(file.filename):
                # Save file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Process the data
                result = data_processor.process_uploaded_file(filepath)
                
                if result['success']:
                    # Store in database
                    customers_added = db_manager.add_customers(result['data'])
                    
                    # 🔥 FIX: Fetch customers WITH database IDs
                    with db_manager.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM customers ORDER BY id DESC LIMIT ?', (customers_added,))
                        customers_with_ids = [dict(row) for row in cursor.fetchall()]
                    
                    # Generate churn predictions with proper customer IDs
                    predictions = churn_predictor.predict_batch(customers_with_ids)
                    db_manager.add_churn_scores(predictions)
                    
                    return jsonify({
                        'success': True,
                        'message': f'Successfully processed {customers_added} customers',
                        'customers_count': customers_added,
                        'high_risk_count': len([p for p in predictions if p['churn_probability'] > 0.7])
                    })
                else:
                    return jsonify({'error': result['error']}), 400
            else:
                return jsonify({'error': 'Invalid file type. Please upload CSV or Excel file'}), 400
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('upload.html')


@app.route('/api/customers')
def get_customers():
    """Get list of customers with churn scores"""
    try:
        customers = db_manager.get_customers_with_scores()
        return jsonify({'success': True, 'data': customers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/customer/<int:customer_id>')
def get_customer_detail(customer_id):
    """Get detailed information about a specific customer"""
    try:
        customer = db_manager.get_customer_detail(customer_id)
        if customer:
            return jsonify({'success': True, 'data': customer})
        else:
            return jsonify({'error': 'Customer not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot_interface():
    """Chatbot interface for natural language queries"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            
            if not user_message:
                return jsonify({'error': 'No message provided'}), 400
            
            # Get response from chatbot
            response = chatbot.get_response(user_message, db_manager)
            
            return jsonify({
                'success': True,
                'response': response['text'],
                'data': response.get('data', None)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('chatbot.html')


@app.route('/campaigns')
def campaigns():
    """Campaign management page"""
    active_campaigns = db_manager.get_campaigns()
    return render_template('campaigns.html', campaigns=active_campaigns)


@app.route('/api/campaigns/create', methods=['POST'])
def create_campaign():
    """Create a new retention campaign"""
    try:
        data = request.get_json()
        campaign_id = db_manager.create_campaign(
            name=data['name'],
            target_segment=data.get('target_segment', 'high_risk'),
            channels=data.get('channels', ['email']),
            message_template=data.get('message', '')
        )
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'message': 'Campaign created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/campaigns/<int:campaign_id>/execute', methods=['POST'])
def execute_campaign(campaign_id):
    """Execute a campaign (send messages)"""
    try:
        # Get campaign details
        campaign = db_manager.get_campaign_detail(campaign_id)
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get target customers
        customers = db_manager.get_high_risk_customers()
        
        # Simulate sending messages (in real implementation, integrate with email/SMS APIs)
        events_created = 0
        for customer in customers[:10]:  # Limit to 10 for demo
            db_manager.create_campaign_event(
                campaign_id=campaign_id,
                customer_id=customer['id'],
                channel='email',
                status='sent'
            )
            events_created += 1
        
        return jsonify({
            'success': True,
            'message': f'Campaign executed. Sent to {events_created} customers.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analytics')
def analytics():
    """Analytics and insights page"""
    analytics_data = db_manager.get_analytics()
    return render_template('analytics.html', data=analytics_data)


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit customer feedback"""
    try:
        data = request.get_json()
        
        feedback_id = db_manager.add_feedback(
            customer_id=data['customer_id'],
            feedback_text=data['feedback_text'],
            source=data.get('source', 'manual')
        )
        
        return jsonify({
            'success': True,
            'feedback_id': feedback_id,
            'message': 'Feedback recorded successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate_sample')
def generate_sample():
    """Generate and download sample customer data"""
    try:
        import io
        from flask import send_file
        
        # Generate sample data
        df = data_processor.generate_sample_data(num_customers=50)
        
        # Create CSV in memory
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='sample_customers.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Initialize database when app starts (Flask 3.0 compatible)
with app.app_context():
    db_manager.initialize_database()

if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    print("="*60)
    print("ChurnGuard AI Platform Starting...")
    print(f"Access the application at: http://localhost:{port}")
    print("="*60)
    
    # Use debug mode only in development
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)