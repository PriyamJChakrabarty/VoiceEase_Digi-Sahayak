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

    # Intent to department mapping
    INTENT_TO_DEPARTMENT = {
        'NETWORK_ISSUE': 'Network Operations',
        'BILLING_COMPLAINT': 'Billing Department',
        'TECHNICAL_SUPPORT': 'Technical Support',
        'SUPPORT_REQUEST': 'Customer Support',
        'BALANCE_QUERY': 'Customer Support',
        'RECHARGE_REQUEST': 'Sales',
        'PLAN_CHANGE': 'Sales',
        'OFFER_INQUIRY': 'Sales'
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
        category = classification_result.get('category', 'QUERY')  # QUERY or GRIEVANCE
        routing = classification_result.get('routing', 'customer_support')

        # Insert into conversations table
        with self.engine.begin() as conn:
            result = conn.execute(text("""
                INSERT INTO conversations
                (user_id, phone, query_text, response_text, primary_intent,
                 intent_tags, entities, category, routing)
                VALUES (:user_id, :phone, :query, :response, :intent,
                        :tags, :entities, :category, :routing)
            """), {
                'user_id': user_id,
                'phone': phone,
                'query': query,
                'response': response,
                'intent': primary_intent,
                'tags': intent_tags,
                'entities': entities,
                'category': category,
                'routing': routing
            })

            # Get the auto-generated conversation_id
            conversation_id = result.lastrowid
            return conversation_id

    def create_record(self, conversation_id, user_id, phone, classification_result):
        """
        Auto-create query or grievance record based on category

        Args:
            conversation_id (int): FK to conversations table
            user_id (int): FK to users table
            phone (str): User phone number
            classification_result (dict): Dict from ticket_classifier.classify_query()

        Returns:
            int or None: record_id if created, None otherwise
        """
        category = classification_result.get('category', 'QUERY')
        type_name = classification_result.get('type_name', 'Unknown')  # e.g., "Balance Check", "Network Connectivity Issue"
        department = classification_result.get('department', 'Customer Support')  # From type matching
        description = classification_result.get('original_query', '')
        entities = json.dumps(classification_result.get('entities', {}))

        # Determine table and status based on category
        if category == 'GRIEVANCE':
            table = 'grievances'
            status = 'open'
        else:
            table = 'queries'
            status = 'resolved'  # Queries are typically auto-resolved

        # Create record
        with self.engine.begin() as conn:
            result = conn.execute(text(f"""
                INSERT INTO {table}
                (conversation_id, user_id, phone, type, department,
                 description, extracted_entities, status)
                VALUES (:conv_id, :user_id, :phone, :type, :dept,
                        :desc, :entities, :status)
            """), {
                'conv_id': conversation_id,
                'user_id': user_id,
                'phone': phone,
                'type': type_name,  # Storing human-readable name like "Balance Check"
                'dept': department,
                'desc': description,
                'entities': entities,
                'status': status
            })

            record_id = result.lastrowid
            return record_id

    def get_queries(self, department=None, start_date=None, end_date=None, status=None):
        """
        Fetch general queries with filtering

        Args:
            department (str): Filter by department (None = all)
            start_date (datetime): Filter from date (None = no start filter)
            end_date (datetime): Filter to date (None = no end filter)
            status (str): Filter by status (None = all)

        Returns:
            list: List of query records with user details
        """
        query = """
            SELECT
                q.query_id, q.type, q.department,
                q.description, q.status, q.created_at, q.extracted_entities,
                u.name, u.phone
            FROM queries q
            JOIN users u ON q.user_id = u.user_id
            WHERE 1=1
        """
        params = {}

        if department:
            query += " AND q.department = :dept"
            params['dept'] = department

        if start_date:
            query += " AND q.created_at >= :start"
            params['start'] = start_date

        if end_date:
            query += " AND q.created_at <= :end"
            params['end'] = end_date

        if status:
            query += " AND q.status = :status"
            params['status'] = status

        query += " ORDER BY q.created_at DESC"

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return result.fetchall()

    def get_grievances(self, department=None, start_date=None, end_date=None, status=None):
        """
        Fetch grievances with filtering

        Args:
            department (str): Filter by department (None = all)
            start_date (datetime): Filter from date (None = no start filter)
            end_date (datetime): Filter to date (None = no end filter)
            status (str): Filter by status ('open'/'in_progress'/'resolved'/'closed', None = all)

        Returns:
            list: List of grievance records with user details
        """
        query = """
            SELECT
                g.grievance_id, g.type, g.department,
                g.description, g.status, g.created_at, g.extracted_entities,
                u.name, u.phone
            FROM grievances g
            JOIN users u ON g.user_id = u.user_id
            WHERE 1=1
        """
        params = {}

        if department:
            query += " AND g.department = :dept"
            params['dept'] = department

        if start_date:
            query += " AND g.created_at >= :start"
            params['start'] = start_date

        if end_date:
            query += " AND g.created_at <= :end"
            params['end'] = end_date

        if status:
            query += " AND g.status = :status"
            params['status'] = status

        query += " ORDER BY g.created_at DESC"

        with self.engine.connect() as conn:
            result = conn.execute(text(query), params)
            return result.fetchall()

    def get_query_stats(self, department=None, start_date=None, end_date=None):
        """
        Get aggregate query statistics

        Args:
            department (str): Filter by department (None = all)
            start_date (datetime): Filter from date
            end_date (datetime): Filter to date

        Returns:
            dict: Statistics with counts by status, department
        """
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved
            FROM queries
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
                'pending': row[1] or 0,
                'resolved': row[2] or 0
            }

    def get_grievance_stats(self, department=None, start_date=None, end_date=None):
        """
        Get aggregate grievance statistics

        Args:
            department (str): Filter by department (None = all)
            start_date (datetime): Filter from date
            end_date (datetime): Filter to date

        Returns:
            dict: Statistics with counts by status
        """
        query = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_count,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_count,
                SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) as resolved_count,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed_count
            FROM grievances
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
                'open': row[1] or 0,
                'in_progress': row[2] or 0,
                'resolved': row[3] or 0,
                'closed': row[4] or 0
            }
