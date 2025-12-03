"""
Data Processor
Handles data cleaning, validation, and transformation
"""

import pandas as pd
from datetime import datetime, timedelta
import random


class DataProcessor:
    """
    Processes and validates uploaded customer data
    """
    
    def __init__(self):
        self.required_columns = ['name', 'email']
    
    def process_uploaded_file(self, filepath):
        """
        Process uploaded CSV/Excel file
        
        Returns:
            dict: {
                'success': bool,
                'data': list of dicts,
                'error': str (if failed)
            }
        """
        try:
            # Read file based on extension
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                return {'success': False, 'error': 'Unsupported file format'}
            
            # Validate columns
            validation_result = self.validate_data(df)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Clean and transform data
            cleaned_data = self.clean_data(df)
            
            # Convert to list of dicts
            records = cleaned_data.to_dict('records')
            
            return {
                'success': True,
                'data': records,
                'row_count': len(records)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }
    
    def validate_data(self, df):
        """Validate that dataframe has required columns"""
        missing_columns = []
        
        # Check for required columns (case-insensitive)
        df_columns_lower = [col.lower() for col in df.columns]
        
        for req_col in self.required_columns:
            if req_col.lower() not in df_columns_lower:
                missing_columns.append(req_col)
        
        if missing_columns:
            return {
                'valid': False,
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }
        
        return {'valid': True}
    
    def clean_data(self, df):
        """Clean and standardize customer data"""
        # Standardize column names (lowercase)
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Fill missing values
        if 'name' in df.columns:
            df['name'] = df['name'].fillna('Unknown')
        
        if 'email' in df.columns:
            df['email'] = df['email'].fillna('').str.lower().str.strip()
        
        if 'phone' in df.columns:
            df['phone'] = df['phone'].fillna('')
        
        # Add missing columns with defaults
        if 'registration_date' not in df.columns:
            # Generate random registration dates (last 2 years)
            df['registration_date'] = self.generate_random_dates(len(df), days_ago=730)
        
        if 'last_transaction_date' not in df.columns:
            # Generate random transaction dates (last 180 days)
            df['last_transaction_date'] = self.generate_random_dates(len(df), days_ago=180)
        
        if 'transaction_count' not in df.columns:
            df['transaction_count'] = [random.randint(0, 50) for _ in range(len(df))]
        
        if 'total_spent' not in df.columns:
            df['total_spent'] = [round(random.uniform(0, 5000), 2) for _ in range(len(df))]
        
        if 'engagement_score' not in df.columns:
            df['engagement_score'] = [random.randint(10, 90) for _ in range(len(df))]
        
        if 'support_tickets' not in df.columns:
            df['support_tickets'] = [random.randint(0, 10) for _ in range(len(df))]
        
        # Convert dates to string format
        date_columns = ['registration_date', 'last_transaction_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].fillna(pd.Timestamp.now())
                df[col] = df[col].dt.strftime('%Y-%m-%d')
        
        return df
    
    def generate_random_dates(self, count, days_ago=365):
        """Generate random dates within specified range"""
        dates = []
        for _ in range(count):
            random_days = random.randint(1, days_ago)
            date = datetime.now() - timedelta(days=random_days)
            dates.append(date.strftime('%Y-%m-%d'))
        return dates
    
    def generate_sample_data(self, num_customers=50):
        """
        Generate sample customer data for demo/testing
        
        Returns:
            pandas DataFrame with sample customer data
        """
        names = [
            'John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis',
            'James Wilson', 'Emily Taylor', 'David Anderson', 'Jessica Martinez',
            'Robert Thomas', 'Ashley Garcia', 'William Rodriguez', 'Amanda Lopez',
            'Christopher Lee', 'Melissa White', 'Daniel Harris', 'Jennifer Clark',
            'Matthew Lewis', 'Stephanie Hall', 'Joseph Allen', 'Rebecca Young',
            'Ryan King', 'Laura Wright', 'Kevin Scott', 'Michelle Green',
            'Brian Adams', 'Kimberly Baker', 'Jason Nelson', 'Lisa Carter',
            'Andrew Mitchell', 'Mary Roberts', 'Joshua Turner', 'Karen Phillips',
            'Justin Campbell', 'Nancy Parker', 'Brandon Evans', 'Betty Edwards',
            'Jacob Collins', 'Helen Stewart', 'Tyler Morris', 'Sandra Rogers',
            'Aaron Reed', 'Donna Cook', 'Zachary Bell', 'Carol Murphy',
            'Kyle Bailey', 'Sharon Rivera', 'Nathan Cooper', 'Deborah Richardson',
            'Adam Cox', 'Cynthia Howard'
        ]
        
        data = []
        for i in range(num_customers):
            name = names[i % len(names)]
            email = f"{name.lower().replace(' ', '.')}@example.com"
            
            # Generate varied customer patterns
            if i % 4 == 0:  # 25% high risk
                transaction_count = random.randint(0, 2)
                total_spent = round(random.uniform(0, 100), 2)
                last_transaction_days = random.randint(90, 365)
                engagement_score = random.randint(10, 30)
                support_tickets = random.randint(3, 8)
            elif i % 4 == 1:  # 25% medium risk
                transaction_count = random.randint(3, 8)
                total_spent = round(random.uniform(100, 500), 2)
                last_transaction_days = random.randint(30, 90)
                engagement_score = random.randint(40, 60)
                support_tickets = random.randint(1, 3)
            else:  # 50% low risk
                transaction_count = random.randint(10, 50)
                total_spent = round(random.uniform(500, 5000), 2)
                last_transaction_days = random.randint(1, 30)
                engagement_score = random.randint(70, 95)
                support_tickets = random.randint(0, 2)
            
            customer = {
                'name': name,
                'email': email,
                'phone': f'+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}',
                'registration_date': (datetime.now() - timedelta(days=random.randint(180, 730))).strftime('%Y-%m-%d'),
                'last_transaction_date': (datetime.now() - timedelta(days=last_transaction_days)).strftime('%Y-%m-%d'),
                'transaction_count': transaction_count,
                'total_spent': total_spent,
                'engagement_score': engagement_score,
                'support_tickets': support_tickets
            }
            
            data.append(customer)
        
        return pd.DataFrame(data)
    
    def export_sample_csv(self, output_path='sample_customers.csv'):
        """Export sample data to CSV file"""
        df = self.generate_sample_data()
        df.to_csv(output_path, index=False)
        return output_path