"""
Natural Language Query Chatbot
Allows users to interact with customer data using natural language
"""

import re
from datetime import datetime


class ChurnChatbot:
    """
    AI chatbot for natural language queries about customer data
    """
    
    def __init__(self):
        self.context = {}
        self.patterns = self.define_patterns()
    
    def define_patterns(self):
        """
        Define patterns for understanding user queries
        """
        return {
            'high_risk': [
                r'high risk.*customers?',
                r'customers?.*high risk',
                r'who.*likely.*churn',
                r'at risk customers?',
                r'customers?.*at risk'
            ],
            'total_customers': [
                r'how many customers?',
                r'total customers?',
                r'number.*customers?',
                r'count.*customers?'
            ],
            'churn_rate': [
                r'churn rate',
                r'what.*churn rate',
                r'percentage.*churned'
            ],
            'recent_activity': [
                r'recent.*activity',
                r'latest.*transactions?',
                r'recent.*customers?'
            ],
            'revenue': [
                r'revenue',
                r'total.*spent',
                r'sales',
                r'monetary.*value'
            ],
            'specific_customer': [
                r'customer.*(\d+)',
                r'tell me about.*customer',
                r'show.*customer.*(\d+)',
                r'info.*customer'
            ],
            'help': [
                r'help',
                r'what can you do',
                r'how.*use',
                r'commands'
            ]
        }
    
    def match_intent(self, message):
        """
        Match user message to an intent using regex patterns
        """
        message_lower = message.lower().strip()
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return 'unknown'
    
    def get_response(self, message, db_manager):
        """
        Generate response based on user message
        
        Args:
            message: User's question/query
            db_manager: Database manager instance
            
        Returns:
            dict: {
                'text': Response text,
                'data': Associated data (optional)
            }
        """
        intent = self.match_intent(message)
        
        try:
            if intent == 'high_risk':
                return self.handle_high_risk_query(db_manager)
            
            elif intent == 'total_customers':
                return self.handle_total_customers_query(db_manager)
            
            elif intent == 'churn_rate':
                return self.handle_churn_rate_query(db_manager)
            
            elif intent == 'recent_activity':
                return self.handle_recent_activity_query(db_manager)
            
            elif intent == 'revenue':
                return self.handle_revenue_query(db_manager)
            
            elif intent == 'specific_customer':
                return self.handle_specific_customer_query(message, db_manager)
            
            elif intent == 'help':
                return self.handle_help_query()
            
            else:
                return self.handle_unknown_query(message)
        
        except Exception as e:
            return {
                'text': f"I encountered an error processing your request: {str(e)}",
                'data': None
            }
    
    def handle_high_risk_query(self, db_manager):
        """Handle queries about high-risk customers"""
        high_risk = db_manager.get_high_risk_customers()
        
        if not high_risk:
            return {
                'text': "Great news! There are currently no high-risk customers in your database.",
                'data': []
            }
        
        response_text = f"I found {len(high_risk)} high-risk customers who are likely to churn:\n\n"
        
        for i, customer in enumerate(high_risk[:5], 1):
            response_text += f"{i}. {customer['name']} - "
            response_text += f"Churn Probability: {customer['churn_probability']*100:.1f}%\n"
        
        if len(high_risk) > 5:
            response_text += f"\n...and {len(high_risk)-5} more. "
        
        response_text += "\n\nI recommend creating a retention campaign for these customers."
        
        return {
            'text': response_text,
            'data': high_risk
        }
    
    def handle_total_customers_query(self, db_manager):
        """Handle queries about total customer count"""
        stats = db_manager.get_dashboard_stats()
        total = stats.get('total_customers', 0)
        
        return {
            'text': f"You have {total} customers in your database.\n\n"
                   f"• High Risk: {stats.get('high_risk_count', 0)}\n"
                   f"• Medium Risk: {stats.get('medium_risk_count', 0)}\n"
                   f"• Low Risk: {stats.get('low_risk_count', 0)}",
            'data': stats
        }
    
    def handle_churn_rate_query(self, db_manager):
        """Handle queries about churn rate"""
        stats = db_manager.get_dashboard_stats()
        
        total = stats.get('total_customers', 0)
        high_risk = stats.get('high_risk_count', 0)
        
        if total > 0:
            churn_rate = (high_risk / total) * 100
        else:
            churn_rate = 0
        
        return {
            'text': f"Current churn risk analysis:\n\n"
                   f"• High-risk customers: {high_risk} ({churn_rate:.1f}%)\n"
                   f"• Total customers: {total}\n\n"
                   f"{'⚠️ Action needed! High churn risk detected.' if churn_rate > 20 else '✓ Churn risk is under control.'}",
            'data': {'churn_rate': churn_rate, 'high_risk': high_risk, 'total': total}
        }
    
    def handle_recent_activity_query(self, db_manager):
        """Handle queries about recent customer activity"""
        recent = db_manager.get_recent_customers(limit=10)
        
        if not recent:
            return {
                'text': "No recent customer data available.",
                'data': []
            }
        
        response_text = f"Here are the {len(recent)} most recently active customers:\n\n"
        
        for i, customer in enumerate(recent, 1):
            response_text += f"{i}. {customer['name']} - "
            response_text += f"Last activity: {customer.get('last_transaction_date', 'N/A')}\n"
        
        return {
            'text': response_text,
            'data': recent
        }
    
    def handle_revenue_query(self, db_manager):
        """Handle queries about revenue"""
        stats = db_manager.get_dashboard_stats()
        
        total_revenue = stats.get('total_revenue', 0)
        at_risk_revenue = stats.get('at_risk_revenue', 0)
        
        return {
            'text': f"Revenue Overview:\n\n"
                   f"• Total Revenue: ${total_revenue:,.2f}\n"
                   f"• Revenue at Risk: ${at_risk_revenue:,.2f}\n"
                   f"• Percentage at Risk: {(at_risk_revenue/total_revenue*100) if total_revenue > 0 else 0:.1f}%\n\n"
                   f"Focus on retention to protect ${at_risk_revenue:,.2f} in revenue!",
            'data': {
                'total_revenue': total_revenue,
                'at_risk_revenue': at_risk_revenue
            }
        }
    
    def handle_specific_customer_query(self, message, db_manager):
        """Handle queries about specific customers"""
        # Try to extract customer ID or name
        match = re.search(r'customer.*?(\d+)', message.lower())
        
        if match:
            customer_id = int(match.group(1))
            customer = db_manager.get_customer_detail(customer_id)
            
            if customer:
                response_text = f"Customer Details:\n\n"
                response_text += f"Name: {customer['name']}\n"
                response_text += f"Email: {customer['email']}\n"
                response_text += f"Churn Risk: {customer.get('risk_level', 'Unknown')}\n"
                response_text += f"Churn Probability: {customer.get('churn_probability', 0)*100:.1f}%\n"
                response_text += f"Total Spent: ${customer.get('total_spent', 0):,.2f}\n"
                response_text += f"Transactions: {customer.get('transaction_count', 0)}\n"
                
                return {
                    'text': response_text,
                    'data': customer
                }
            else:
                return {
                    'text': f"Customer with ID {customer_id} not found.",
                    'data': None
                }
        
        return {
            'text': "Please specify a customer ID. For example: 'Show me customer 123'",
            'data': None
        }
    
    def handle_help_query(self):
        """Handle help queries"""
        help_text = """I can help you with:\n
1. **Customer Risk Analysis**
   • "Show me high-risk customers"
   • "Who is likely to churn?"
   
2. **Statistics**
   • "How many customers do we have?"
   • "What's our churn rate?"
   
3. **Revenue Insights**
   • "Show me revenue statistics"
   • "How much revenue is at risk?"
   
4. **Customer Details**
   • "Tell me about customer 123"
   • "Show customer information"
   
5. **Recent Activity**
   • "Show recent customer activity"
   • "Who are our latest customers?"

Just ask me naturally, and I'll do my best to help!"""
        
        return {
            'text': help_text,
            'data': None
        }
    
    def handle_unknown_query(self, message):
        """Handle queries that don't match any pattern"""
        return {
            'text': "I'm not sure I understand that question. Here are some things you can ask me:\n\n"
                   "• 'Show me high-risk customers'\n"
                   "• 'What's our churn rate?'\n"
                   "• 'How many customers do we have?'\n"
                   "• 'Tell me about customer 123'\n\n"
                   "Type 'help' to see all available queries.",
            'data': None
        }