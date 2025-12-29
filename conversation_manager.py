"""
Conversation Manager
Handles conversation persistence and complaint tracking in database
"""

from sqlalchemy import text
import json


class ConversationManager:
    """Manages conversation storage and complaint creation"""

    # Department mapping from routing to friendly names
    ROUTING_TO_DEPARTMENT = {
        "technical_support": "Technical Support",
        "billing_team": "Billing Department",
        "sales_team": "Sales & Retention",
        "customer_support": "Customer Support",
        "automated_system": "Customer Support"  # Fallback
    }

    # Complaint intents and their department mapping
    COMPLAINT_INTENTS = {
        'NETWORK_ISSUE': 'Network Operations',
        'BILLING_COMPLAINT': 'Billing Department',
        'TECHNICAL_SUPPORT': 'Technical Support'
    }

    def __init__(self, engine):
        """
        Initialize with SQLAlchemy engine

        Args:
            engine: SQLAlchemy engine from db.py
        """
        self.engine = engine

    def save_conversation(self, user_id, phone, query, response, classification_result):
        """
        Save conversation with classification metadata to database

        Args:
            user_id (int): From users table
            phone (str): User phone number
            query (str): User query text
            response (str): AI response text
            classification_result (dict): Dict from ticket_classifier.classify_query()

        Returns:
            int: conversation_id of newly created record
        """
        # Extract classification data
        primary_intent = classification_result.get('primary_intent', 'UNKNOWN')
        intent_tags = json.dumps(classification_result.get('intents', []))
        entities = json.dumps(classification_result.get('entities', {}))
        priority = classification_result.get('priority', 'MEDIUM')
        routing = classification_result.get('routing', 'customer_support')

        # Insert into conversations table
        with self.engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO conversations
                (user_id, phone, query_text, response_text, primary_intent,
                 intent_tags, entities, priority, routing)
                VALUES (:user_id, :phone, :query, :response, :intent,
                        :tags, :entities, :priority, :routing)
            """), {
                'user_id': user_id,
                'phone': phone,
                'query': query,
                'response': response,
                'intent': primary_intent,
                'tags': intent_tags,
                'entities': entities,
                'priority': priority,
                'routing': routing
            })

            # Get the auto-generated conversation_id
            conversation_id = result.lastrowid
            return conversation_id

    def create_complaint(self, conversation_id, user_id, phone, classification_result):
        """
        Auto-create complaint for tracked intents only

        Only creates complaint if primary_intent is:
        - NETWORK_ISSUE
        - BILLING_COMPLAINT
        - TECHNICAL_SUPPORT

        Args:
            conversation_id (int): FK to conversations table
            user_id (int): FK to users table
            phone (str): User phone number
            classification_result (dict): Dict from ticket_classifier.classify_query()

        Returns:
            int or None: complaint_id if created, None if filtered out
        """
        primary_intent = classification_result.get('primary_intent', 'UNKNOWN')

        # Filter: Only track specific complaint intents
        if primary_intent not in self.COMPLAINT_INTENTS:
            return None

        # Map intent to department
        department = self.COMPLAINT_INTENTS.get(primary_intent, 'Customer Support')
        priority = classification_result.get('priority', 'MEDIUM')
        description = classification_result.get('original_query', '')
        entities = json.dumps(classification_result.get('entities', {}))

        # Create complaint record
        with self.engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO complaints
                (conversation_id, user_id, phone, complaint_type, department,
                 priority, description, extracted_entities, status)
                VALUES (:conv_id, :user_id, :phone, :type, :dept,
                        :priority, :desc, :entities, 'open')
            """), {
                'conv_id': conversation_id,
                'user_id': user_id,
                'phone': phone,
                'type': primary_intent,
                'dept': department,
                'priority': priority,
                'desc': description,
                'entities': entities
            })

            complaint_id = result.lastrowid
            return complaint_id

    def get_complaints_by_department(self, department=None, start_date=None, end_date=None, status='open'):
        """
        Fetch complaints with filtering

        Args:
            department (str): Filter by department (None = all)
            start_date (datetime): Filter from date (None = no start filter)
            end_date (datetime): Filter to date (None = no end filter)
            status (str): Filter by status ('open'/'in_progress'/'resolved'/'closed', None = all)

        Returns:
            list: List of complaint records with user details
        """
        query = """
            SELECT
                c.complaint_id, c.complaint_type, c.department, c.priority,
                c.description, c.status, c.created_at, c.extracted_entities,
                u.name, u.phone
            FROM complaints c
            JOIN users u ON c.user_id = u.user_id
            WHERE 1=1
        """
        params = {}

        if department:
            query += " AND c.department = :dept"
            params['dept'] = department

        if start_date:
            query += " AND c.created_at >= :start"
            params['start'] = start_date

        if end_date:
            query += " AND c.created_at <= :end"
            params['end'] = end_date

        if status:
            query += " AND c.status = :status"
            params['status'] = status

        query += " ORDER BY c.created_at DESC"

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return result.fetchall()

    def get_complaint_stats(self, department=None, start_date=None, end_date=None):
        """
        Get aggregate complaint statistics

        Args:
            department (str): Filter by department (None = all)
            start_date (datetime): Filter from date
            end_date (datetime): Filter to date

        Returns:
            dict: Statistics with counts by priority, status, department
        """
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN priority = 'HIGH' THEN 1 ELSE 0 END) as high_priority,
                SUM(CASE WHEN priority = 'MEDIUM' THEN 1 ELSE 0 END) as medium_priority,
                SUM(CASE WHEN priority = 'LOW' THEN 1 ELSE 0 END) as low_priority,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_count,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_count,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_count
            FROM complaints
            WHERE 1=1
        """
        params = {}

        if department:
            query += " AND department = :dept"
            params['dept'] = department

        if start_date:
            query += " AND created_at >= :start"
            params['start'] = start_date

        if end_date:
            query += " AND created_at <= :end"
            params['end'] = end_date

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            row = result.fetchone()

            return {
                'total': row[0] or 0,
                'high_priority': row[1] or 0,
                'medium_priority': row[2] or 0,
                'low_priority': row[3] or 0,
                'open': row[4] or 0,
                'in_progress': row[5] or 0,
                'resolved': row[6] or 0,
                'closed': row[7] or 0
            }

    def get_department_counts(self, start_date=None, end_date=None):
        """
        Get complaint counts grouped by department

        Args:
            start_date (datetime): Filter from date
            end_date (datetime): Filter to date

        Returns:
            dict: Department name -> count mapping
        """
        query = """
            SELECT department, COUNT(*) as count
            FROM complaints
            WHERE 1=1
        """
        params = {}

        if start_date:
            query += " AND created_at >= :start"
            params['start'] = start_date

        if end_date:
            query += " AND created_at <= :end"
            params['end'] = end_date

        query += " GROUP BY department ORDER BY count DESC"

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return {row[0]: row[1] for row in result}
