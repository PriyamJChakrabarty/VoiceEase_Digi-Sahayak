"""
Test Script: Generate Sample Complaints for Dashboard Testing
Creates realistic complaint scenarios across different departments and priorities
"""

from conversation_manager import ConversationManager
from db import engine
from ticket_classifier import TicketClassifier
from datetime import datetime, timedelta
import random

print("="*70)
print("COMPLAINT SYSTEM TEST - Sample Data Generation")
print("="*70)

# Initialize managers
conv_manager = ConversationManager(engine)
classifier = TicketClassifier()

# Test queries that should create complaints across different departments
test_queries = [
    # Network Operations (NETWORK_ISSUE)
    "Mera internet bahut slow hai pichhle 3 din se, please help",
    "Network down since morning in my area, urgent issue",
    "Mobile data not working, showing no connection error",
    "4G speed very slow, YouTube not playing properly",
    "Poor network signal, calls dropping frequently in Delhi",

    # Billing Department (BILLING_COMPLAINT)
    "Bill mein extra 200 rupees charge ho gaya hai without reason",
    "Wrong deduction from my account, need immediate refund",
    "Charged twice for same recharge plan, please fix billing",
    "International roaming charges added but I never traveled",
    "Auto-debit happened twice this month, money deducted double",

    # Technical Support (TECHNICAL_SUPPORT)
    "SIM card not working after recharge, please replace",
    "Mobile app crashing when I try to check balance",
    "Cannot activate new SIM card, showing invalid error",
    "Hotspot feature stopped working suddenly",
    "VoLTE calls not connecting, only 2G calls work",

    # Non-complaint queries (should NOT create complaints)
    "Mera data balance kitna hai remaining?",
    "500 rupees wala best plan batao",
    "Customer care number kya hai?",
]

# Test users (from ingest.py seed data)
test_users = [
    (1, '9876543210', 'Rajesh Kumar'),
    (2, '9123456789', 'Priya Sharma'),
    (3, '9988776655', 'Amit Singh'),
    (4, '9555444333', 'Sneha Gupta'),
    (5, '9111222333', 'Vikash Yadav')
]

print("\n[INFO] Initializing Ticket Classifier...")
print("[INFO] Generating test complaints...\n")

conversation_count = 0
complaint_count = 0
skipped_count = 0

for i, query in enumerate(test_queries):
    # Classify query
    result = classifier.classify_query(query)
    result['original_query'] = query

    # Random user
    user_id, phone, name = random.choice(test_users)

    # Random timestamp in last 30 days
    days_ago = random.randint(0, 30)
    timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

    print(f"[{i+1}/{len(test_queries)}] Processing: {query[:60]}...")
    print(f"     User: {name} ({phone})")
    print(f"     Intent: {result['primary_intent']} | Priority: {result['priority']}")

    # Save conversation
    conv_id = conv_manager.save_conversation(
        user_id=user_id,
        phone=phone,
        query=query,
        response="[Test Response] Thank you for contacting us. We are looking into your issue.",
        classification_result=result
    )
    conversation_count += 1
    print(f"     [SAVED] Conversation ID: {conv_id}")

    # Create complaint (only for NETWORK_ISSUE, BILLING_COMPLAINT, TECHNICAL_SUPPORT)
    complaint_id = conv_manager.create_complaint(
        conversation_id=conv_id,
        user_id=user_id,
        phone=phone,
        classification_result=result
    )

    if complaint_id:
        dept = conv_manager.COMPLAINT_INTENTS.get(result['primary_intent'], 'Unknown')
        complaint_count += 1
        print(f"     [COMPLAINT] ID: {complaint_id} | Department: {dept}")
    else:
        skipped_count += 1
        print(f"     [SKIPPED] Not a complaint intent (informational query)")

    print()

print("="*70)
print("TEST COMPLETED SUCCESSFULLY")
print("="*70)
print(f"\nSummary:")
print(f"  Total Conversations: {conversation_count}")
print(f"  Complaints Created: {complaint_count}")
print(f"  Skipped (Non-Complaints): {skipped_count}")
print()
print("Department Breakdown (Expected):")
print("  - Network Operations: ~5 complaints (NETWORK_ISSUE)")
print("  - Billing Department: ~5 complaints (BILLING_COMPLAINT)")
print("  - Technical Support: ~5 complaints (TECHNICAL_SUPPORT)")
print()
print("Next Steps:")
print("  1. Start Streamlit app: streamlit run app.py")
print("  2. Access dashboard: http://localhost:8501/Complaint_Dashboard")
print("  3. Test query: Try asking 'Mera internet slow hai' in the app")
print("  4. Check dashboard: Verify complaint appears in dashboard")
print("  5. Generate summary: Click 'Generate Summary' button")
print("="*70)
