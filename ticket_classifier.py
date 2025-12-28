"""
Lightweight Ticket Classifier with Multi-Label Intent Detection + Pattern-Based NER
No Flair dependency - Uses only sentence-transformers + regex
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import re
from typing import Dict, List


class TicketClassifier:
    """
    Lightweight ticket classifier that:
    1. Detects multiple intents per query (multi-label classification)
    2. Extracts entities using regex patterns (no Flair needed!)
    3. Assigns priority/urgency for triage
    4. Routes to appropriate handling

    Example:
        User: "My internet is slow and I want to recharge 500 rupees"
        Tags: [NETWORK_ISSUE, RECHARGE_REQUEST]
        Entities: {service: "internet", issue: "slow", amount: "500"}
        Priority: HIGH
    """

    def __init__(self):
        """Initialize classifier with pre-trained model"""
        print("[Ticket Classifier] Initializing...")

        # Use same model as FAISS for consistency
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        # Pre-compute intent embeddings (one-time cost)
        self.intent_embeddings = self._compute_intent_embeddings()

        print("[Ticket Classifier] Ready (Lightweight version - no Flair)")

    def _compute_intent_embeddings(self):
        """Pre-compute embeddings for all supported intents"""
        # Define intent categories with rich descriptions
        intents = {
            "BALANCE_QUERY": "User wants to check data balance, remaining quota, or how much data is left",
            "NETWORK_ISSUE": "User experiencing slow internet, connection problems, network down, poor signal",
            "RECHARGE_REQUEST": "User wants to recharge, top-up, buy a plan, or inquire about recharge options",
            "BILLING_COMPLAINT": "User has billing issues, wrong charges, unexpected deductions, refund requests",
            "SUPPORT_REQUEST": "User needs help, wants to talk to customer care, has a general complaint",
            "OFFER_INQUIRY": "User asking about discounts, cashback, promotional offers, deals",
            "PLAN_CHANGE": "User wants to upgrade, downgrade, switch plans, or modify their subscription",
            "TECHNICAL_SUPPORT": "User has technical issues like SIM problems, app not working, configuration issues"
        }

        embeddings = {}
        for intent, description in intents.items():
            # Encode description to vector
            emb = self.model.encode(description, convert_to_numpy=True)
            emb = emb / np.linalg.norm(emb)  # Normalize
            embeddings[intent] = emb

        return embeddings

    def classify_query(self, query: str) -> Dict:
        """
        Main classification function

        Args:
            query: User's voice transcript or text input

        Returns:
            {
                "intents": [{"label": "NETWORK_ISSUE", "confidence": 0.89}, ...],
                "entities": {"amount": "500", "service": "internet", "issue": "slow"},
                "priority": "HIGH",
                "tags": ["NETWORK_ISSUE", "RECHARGE_REQUEST"],
                "routing": "technical_support"
            }
        """
        # Step 1: Multi-label intent classification
        intents = self._detect_intents(query)

        # Step 2: Pattern-based entity extraction (no Flair needed!)
        entities = self._extract_entities_regex(query)

        # Step 3: Priority/urgency detection
        priority = self._determine_priority(query, intents)

        # Step 4: Routing recommendation
        routing = self._get_routing(intents, priority)

        return {
            "intents": intents,
            "entities": entities,
            "priority": priority,
            "tags": [i["label"] for i in intents],
            "routing": routing,
            "primary_intent": intents[0]["label"] if intents else "UNKNOWN"
        }

    def _detect_intents(self, query: str, threshold: float = 0.25) -> List[Dict]:
        """
        Detect multiple intents using semantic similarity

        Args:
            query: User query
            threshold: Minimum similarity score (0-1)

        Returns:
            List of detected intents with confidence scores
        """
        # Encode query
        query_emb = self.model.encode(query, convert_to_numpy=True)
        query_emb = query_emb / np.linalg.norm(query_emb)

        # Compare with all intents
        results = []
        for intent, intent_emb in self.intent_embeddings.items():
            # Cosine similarity
            similarity = float(np.dot(query_emb, intent_emb))

            if similarity >= threshold:
                results.append({
                    "label": intent,
                    "confidence": round(similarity, 2)
                })

        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)

        return results

    def _extract_entities_regex(self, query: str) -> Dict:
        """
        Extract entities using ONLY regex patterns (no Flair needed)

        Returns dict with: amount, service, issue, plan_name, etc.
        """
        entities = {}

        # Amount/Money (₹500, 500 rupees, Rs 500)
        money_patterns = [
            r'₹\s*(\d+)',
            r'(\d+)\s*rupees?',
            r'[Rr]s\.?\s*(\d+)',
            r'(\d+)\s*rs'
        ]
        for pattern in money_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                entities['amount'] = match.group(1)
                break

        # Service type (data, internet, call, etc.)
        service_match = re.search(r'\b(data|internet|call|sms|roaming|network|hotspot|wifi)\b', query, re.IGNORECASE)
        if service_match:
            entities['service'] = service_match.group(1).lower()

        # Issue type (slow, not working, etc.)
        issue_match = re.search(r'\b(slow|not working|stopped|failed|down|problem|issue|nahi chal raha|band)\b', query, re.IGNORECASE)
        if issue_match:
            entities['issue'] = issue_match.group(1).lower()

        # Plan names (Jio, Airtel, etc.)
        plan_match = re.search(r'\b(jio|airtel|vi|vodafone|bsnl)\s*(basic|smart|premium|value|max|super)?\b', query, re.IGNORECASE)
        if plan_match:
            entities['plan_name'] = plan_match.group(0)

        # Timeframe
        time_match = re.search(r'\b(today|yesterday|last week|since morning|this month|aaj|kal)\b', query, re.IGNORECASE)
        if time_match:
            entities['timeframe'] = time_match.group(1).lower()

        return entities

    def _determine_priority(self, query: str, intents: List[Dict]) -> str:
        """
        Determine urgency/priority for triage

        Returns: "HIGH", "MEDIUM", or "LOW"
        """
        query_lower = query.lower()

        # HIGH priority keywords
        urgent_keywords = ['not working', 'stopped', 'failed', 'down', 'emergency', 'urgent', 'immediately', 'nahi chal raha', 'band']
        if any(keyword in query_lower for keyword in urgent_keywords):
            return "HIGH"

        # HIGH priority intents
        urgent_intents = ['NETWORK_ISSUE', 'BILLING_COMPLAINT', 'TECHNICAL_SUPPORT']
        if intents and intents[0]['label'] in urgent_intents:
            return "HIGH"

        # MEDIUM priority
        medium_intents = ['RECHARGE_REQUEST', 'PLAN_CHANGE', 'SUPPORT_REQUEST']
        if intents and intents[0]['label'] in medium_intents:
            return "MEDIUM"

        # LOW priority (informational queries)
        return "LOW"

    def _get_routing(self, intents: List[Dict], priority: str) -> str:
        """Determine which team/system should handle this"""
        if not intents:
            return "general_support"

        primary_intent = intents[0]['label']

        routing_map = {
            "NETWORK_ISSUE": "technical_support",
            "TECHNICAL_SUPPORT": "technical_support",
            "BILLING_COMPLAINT": "billing_team",
            "RECHARGE_REQUEST": "automated_system",
            "BALANCE_QUERY": "automated_system",
            "PLAN_CHANGE": "sales_team",
            "OFFER_INQUIRY": "sales_team",
            "SUPPORT_REQUEST": "customer_support"
        }

        return routing_map.get(primary_intent, "general_support")


# Standalone test
if __name__ == "__main__":
    classifier = TicketClassifier()

    test_queries = [
        "Mera internet bahut slow hai aur 500 rupees ka recharge bhi nahi ho raha",
        "Kitna data bacha hai",
        "Bill mein extra charge ho gaya hai",
        "I want to upgrade to Jio Premium"
    ]

    print("\n" + "="*80)
    print("TICKET CLASSIFIER TEST (Lightweight)")
    print("="*80 + "\n")

    for query in test_queries:
        print(f"Query: {query}")
        result = classifier.classify_query(query)

        print(f"  Tags: {result['tags']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Entities: {result['entities']}")
        print(f"  Routing: {result['routing']}")
        print()
