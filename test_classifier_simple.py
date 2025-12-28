"""
Simple Demo for Smart Ticket Classifier
Shows multi-label classification + NER in action (no emojis for Windows compatibility)
"""

from ticket_classifier import TicketClassifier

print("\n" + "="*80)
print("SMART TICKET CLASSIFIER DEMO")
print("Automated Ticket Tagging & Triage for Telecom Support")
print("="*80 + "\n")

# Initialize classifier
print("Initializing classifier...")
classifier = TicketClassifier()
print("\n")

# Sample queries
test_cases = [
    {
        "query": "Mera internet bahut slow hai aur 500 rupees ka recharge bhi nahi ho raha",
        "description": "Multi-label: Network issue + Recharge problem"
    },
    {
        "query": "Kitna data bacha hai mere account mein",
        "description": "Simple balance check"
    },
    {
        "query": "Bill mein extra 300 rupees charge ho gaya hai",
        "description": "Billing complaint with amount"
    },
    {
        "query": "I want to upgrade from Jio Basic to Airtel Smart under 500 budget",
        "description": "Plan change with plan names"
    },
    {
        "query": "Network toh slow hai hi, customer care pe call bhi nahi lag raha",
        "description": "Complex multi-issue query"
    }
]

for i, test in enumerate(test_cases, 1):
    print("\n" + "="*80)
    print(f"\nTEST CASE {i}/{len(test_cases)}")
    print(f"Description: {test['description']}")
    print(f"\nUser Query: \"{test['query']}\"")
    print("\nANALYSIS:")
    print("-" * 80)

    # Classify
    result = classifier.classify_query(test['query'])

    # Display results
    print("\n  TAGS DETECTED:")
    for tag in result['tags']:
        print(f"    - {tag}")

    print(f"\n  PRIMARY INTENT: {result['primary_intent']}")

    print(f"\n  ALL INTENTS (with confidence):")
    for intent in result['intents']:
        bar = "=" * int(intent['confidence'] * 10)
        print(f"    {intent['label']:<25} {bar} {intent['confidence']:.0%}")

    if result['entities']:
        print(f"\n  ENTITIES EXTRACTED:")
        for key, value in result['entities'].items():
            print(f"    - {key.upper()}: {value}")
    else:
        print(f"\n  ENTITIES EXTRACTED: None")

    priority_marker = {"HIGH": "[!!!]", "MEDIUM": "[!!]", "LOW": "[!]"}
    print(f"\n  {priority_marker.get(result['priority'], '')} PRIORITY: {result['priority']}")
    print(f"  ROUTING: {result['routing'].replace('_', ' ').title()}")

    print("\n" + "-" * 80)

# Summary
print("\n" + "="*80)
print("\nDEMONSTRATION COMPLETE")
print("\nKEY FEATURES:")
print("  1. Multi-Label Classification - Detects multiple intents per query")
print("  2. Named Entity Recognition - Extracts amounts, services, plan names")
print("  3. Priority Detection - Auto-assigns urgency (HIGH/MEDIUM/LOW)")
print("  4. Smart Routing - Routes to appropriate team/system")
print("  5. Zero-Shot Learning - No training data required!")
print("\n" + "="*80 + "\n")
