"""
Database Manager
Handles all database operations for ChurnGuard
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager


class DatabaseManager:
    """
    Manages all database operations using SQLite
    """
    
    def __init__(self, db_path='database/churnguard.db'):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create all necessary tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Organizations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS organizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    organization_id INTEGER DEFAULT 1,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    phone TEXT,
                    registration_date DATE,
                    last_transaction_date DATE,
                    transaction_count INTEGER DEFAULT 0,
                    total_spent REAL DEFAULT 0.0,
                    engagement_score INTEGER DEFAULT 50,
                    support_tickets INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (organization_id) REFERENCES organizations (id)
                )
            ''')
            
            # Churn scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS churn_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    churn_probability REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    features TEXT,
                    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Campaigns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    target_segment TEXT,
                    channels TEXT,
                    message_template TEXT,
                    status TEXT DEFAULT 'draft',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Campaign events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS campaign_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    sent_at TIMESTAMP,
                    response_received BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (campaign_id) REFERENCES campaigns (id),
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    feedback_text TEXT NOT NULL,
                    sentiment TEXT,
                    sentiment_score REAL,
                    source TEXT DEFAULT 'manual',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            conn.commit()
            
            # Insert default organization if not exists
            cursor.execute('SELECT COUNT(*) FROM organizations')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO organizations (name, email) 
                    VALUES ('Default Organization', 'admin@churnguard.ai')
                ''')
                conn.commit()
            
            print("Database initialized successfully!")
    
    def add_customers(self, customers_data):
        """Add multiple customers to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            count = 0
            for customer in customers_data:
                try:
                    cursor.execute('''
                        INSERT INTO customers (
                            name, email, phone, registration_date, 
                            last_transaction_date, transaction_count, 
                            total_spent, engagement_score, support_tickets
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        customer.get('name', 'Unknown'),
                        customer.get('email', ''),
                        customer.get('phone', ''),
                        customer.get('registration_date', datetime.now().strftime('%Y-%m-%d')),
                        customer.get('last_transaction_date', datetime.now().strftime('%Y-%m-%d')),
                        customer.get('transaction_count', 0),
                        customer.get('total_spent', 0.0),
                        customer.get('engagement_score', 50),
                        customer.get('support_tickets', 0)
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error adding customer: {e}")
                    continue
            
            conn.commit()
            return count
    
    def add_churn_scores(self, predictions):
        """Add churn prediction scores to database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for pred in predictions:
                try:
                    # Delete old score if exists
                    cursor.execute('''
                        DELETE FROM churn_scores WHERE customer_id = ?
                    ''', (pred['customer_id'],))
                    
                    # Insert new score
                    cursor.execute('''
                        INSERT INTO churn_scores (
                            customer_id, churn_probability, risk_level, features
                        ) VALUES (?, ?, ?, ?)
                    ''', (
                        pred['customer_id'],
                        pred['churn_probability'],
                        pred['risk_level'],
                        json.dumps(pred.get('features', {}))
                    ))
                except Exception as e:
                    print(f"Error adding churn score: {e}")
                    continue
            
            conn.commit()
    
    def get_customers_with_scores(self):
        """Get all customers with their churn scores"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.id, c.name, c.email, c.phone,
                    c.transaction_count, c.total_spent,
                    cs.churn_probability, cs.risk_level, cs.scored_at
                FROM customers c
                LEFT JOIN churn_scores cs ON c.id = cs.customer_id
                ORDER BY cs.churn_probability DESC
            ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_customer_detail(self, customer_id):
        """Get detailed information about a specific customer"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.*, cs.churn_probability, cs.risk_level, cs.features
                FROM customers c
                LEFT JOIN churn_scores cs ON c.id = cs.customer_id
                WHERE c.id = ?
            ''', (customer_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_high_risk_customers(self, threshold=0.7):
        """Get customers with high churn risk"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.id, c.name, c.email, c.phone, c.total_spent,
                    cs.churn_probability, cs.risk_level
                FROM customers c
                INNER JOIN churn_scores cs ON c.id = cs.customer_id
                WHERE cs.churn_probability >= ?
                ORDER BY cs.churn_probability DESC
            ''', (threshold,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_recent_customers(self, limit=10):
        """Get recently active customers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    c.*, cs.churn_probability, cs.risk_level
                FROM customers c
                LEFT JOIN churn_scores cs ON c.id = cs.customer_id
                ORDER BY c.last_transaction_date DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_dashboard_stats(self):
        """Get statistics for dashboard"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total customers
            cursor.execute('SELECT COUNT(*) FROM customers')
            total_customers = cursor.fetchone()[0]
            
            # High risk count
            cursor.execute('''
                SELECT COUNT(*) FROM churn_scores WHERE churn_probability >= 0.7
            ''')
            high_risk = cursor.fetchone()[0]
            
            # Medium risk count
            cursor.execute('''
                SELECT COUNT(*) FROM churn_scores 
                WHERE churn_probability >= 0.4 AND churn_probability < 0.7
            ''')
            medium_risk = cursor.fetchone()[0]
            
            # Low risk count
            cursor.execute('''
                SELECT COUNT(*) FROM churn_scores WHERE churn_probability < 0.4
            ''')
            low_risk = cursor.fetchone()[0]
            
            # Total revenue
            cursor.execute('SELECT SUM(total_spent) FROM customers')
            total_revenue = cursor.fetchone()[0] or 0.0
            
            # Revenue at risk (from high-risk customers)
            cursor.execute('''
                SELECT SUM(c.total_spent)
                FROM customers c
                INNER JOIN churn_scores cs ON c.id = cs.customer_id
                WHERE cs.churn_probability >= 0.7
            ''')
            at_risk_revenue = cursor.fetchone()[0] or 0.0
            
            # Active campaigns
            cursor.execute('''
                SELECT COUNT(*) FROM campaigns WHERE status = 'active'
            ''')
            active_campaigns = cursor.fetchone()[0]
            
            return {
                'total_customers': total_customers,
                'high_risk_count': high_risk,
                'medium_risk_count': medium_risk,
                'low_risk_count': low_risk,
                'total_revenue': total_revenue,
                'at_risk_revenue': at_risk_revenue,
                'active_campaigns': active_campaigns
            }
    
    def create_campaign(self, name, target_segment, channels, message_template):
        """Create a new campaign"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO campaigns (
                    name, target_segment, channels, message_template, status
                ) VALUES (?, ?, ?, ?, 'active')
            ''', (name, target_segment, json.dumps(channels), message_template))
            conn.commit()
            return cursor.lastrowid
    
    def get_campaigns(self, status='active'):
        """Get all campaigns"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('''
                    SELECT * FROM campaigns WHERE status = ? ORDER BY created_at DESC
                ''', (status,))
            else:
                cursor.execute('SELECT * FROM campaigns ORDER BY created_at DESC')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_campaign_detail(self, campaign_id):
        """Get campaign details"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_campaign_event(self, campaign_id, customer_id, channel, status='pending'):
        """Create a campaign event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO campaign_events (
                    campaign_id, customer_id, channel, status, sent_at
                ) VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, customer_id, channel, status, datetime.now()))
            conn.commit()
            return cursor.lastrowid
    
    def add_feedback(self, customer_id, feedback_text, source='manual'):
        """Add customer feedback"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Simple sentiment analysis (can be enhanced with ML)
            sentiment, score = self.analyze_sentiment(feedback_text)
            
            cursor.execute('''
                INSERT INTO feedback (
                    customer_id, feedback_text, sentiment, sentiment_score, source
                ) VALUES (?, ?, ?, ?, ?)
            ''', (customer_id, feedback_text, sentiment, score, source))
            conn.commit()
            return cursor.lastrowid
    
    def analyze_sentiment(self, text):
        """Basic sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'happy', 'satisfied', 'love', 'amazing']
        negative_words = ['bad', 'poor', 'terrible', 'unhappy', 'disappointed', 'hate', 'worst']
        
        text_lower = text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive', 0.7 + (pos_count * 0.1)
        elif neg_count > pos_count:
            return 'negative', 0.3 - (neg_count * 0.1)
        else:
            return 'neutral', 0.5
    
    def get_analytics(self):
        """Get analytics data"""
        stats = self.get_dashboard_stats()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Churn distribution
            cursor.execute('''
                SELECT 
                    CASE 
                        WHEN churn_probability >= 0.7 THEN 'High'
                        WHEN churn_probability >= 0.4 THEN 'Medium'
                        ELSE 'Low'
                    END as risk_category,
                    COUNT(*) as count
                FROM churn_scores
                GROUP BY risk_category
            ''')
            churn_distribution = [dict(row) for row in cursor.fetchall()]
            
            # Recent feedback
            cursor.execute('''
                SELECT f.*, c.name as customer_name
                FROM feedback f
                INNER JOIN customers c ON f.customer_id = c.id
                ORDER BY f.created_at DESC
                LIMIT 10
            ''')
            recent_feedback = [dict(row) for row in cursor.fetchall()]
        
        return {
            'stats': stats,
            'churn_distribution': churn_distribution,
            'recent_feedback': recent_feedback
        }