"""
Demo Script for Smart Ticket Classifier
Shows multi-label classification + NER in action
"""

from ticket_classifier import TicketClassifier

def print_separator():
    print("\n" + "="*80)

def demo_classifier():
    """Run demonstration with sample telecom queries"""
    print_separator()
    print("SMART TICKET CLASSIFIER DEMO")
    print("Automated Ticket Tagging & Triage for Telecom Support")
    print_separator()

    # Initialize classifier
    print("\nInitializing classifier with pre-trained models...")
    classifier = TicketClassifier()
    print("✓ Ready!\n")

    # Sample queries covering different scenarios
    test_cases = [
        {
            "query": "Mera internet bahut slow hai aur 500 rupees ka recharge bhi nahi ho raha",
            "description": "Multi-label query: Network issue + Recharge problem"
        },
        {
            "query": "Kitna data bacha hai mere account mein",
            "description": "Simple balance check (low priority)"
        },
        {
            "query": "Bill mein extra 300 rupees charge ho gaya hai",
            "description": "Billing complaint with amount detection"
        },
        {
            "query": "I want to upgrade from Jio Basic to Airtel Smart under 500 budget",
            "description": "Plan change with plan name + amount extraction"
        },
        {
            "query": "Network toh slow hai hi, customer care pe call bhi nahi lag raha",
            "description": "Complex multi-issue: network + support access"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print_separator()
        print(f"\n📝 TEST CASE {i}/{len(test_cases)}")
        print(f"Description: {test['description']}")
        print(f"\n💬 User Query: \"{test['query']}\"")
        print("\n🔍 ANALYSIS:")
        print("-" * 80)

        # Classify the query
        result = classifier.classify_query(test['query'])

        # Display results
        print(f"\n  🏷️  TAGS DETECTED:")
        for tag in result['tags']:
            print(f"      • {tag}")

        print(f"\n  🎯 PRIMARY INTENT: {result['primary_intent']}")

        print(f"\n  💡 ALL INTENTS (with confidence):")
        for intent in result['intents']:
            confidence_bar = "█" * int(intent['confidence'] * 10)
            print(f"      • {intent['label']:<25} {confidence_bar} {intent['confidence']:.0%}")

        if result['entities']:
            print(f"\n  📊 ENTITIES EXTRACTED (NER):")
            for key, value in result['entities'].items():
                print(f"      • {key.upper()}: {value}")
        else:
            print(f"\n  📊 ENTITIES EXTRACTED (NER): None")

        # Priority & Routing
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        print(f"\n  {priority_emoji.get(result['priority'], '[UNKNOWN]')} PRIORITY: {result['priority']}")
        print(f"  🎯 ROUTING: {result['routing'].replace('_', ' ').title()}")

        print("\n" + "-" * 80)

    # Summary
    print_separator()
    print("\n[SUCCESS] DEMONSTRATION COMPLETE")
    print("\nKEY FEATURES DEMONSTRATED:")
    print("  1. Multi-Label Classification - Detects multiple intents per query")
    print("  2. Named Entity Recognition - Extracts amounts, services, plan names")
    print("  3. Priority Detection - Auto-assigns urgency (HIGH/MEDIUM/LOW)")
    print("  4. Smart Routing - Routes to appropriate team/system")
    print("  5. Zero-Shot Learning - No training data required!")
    print_separator()
    print()


if __name__ == "__main__":
    demo_classifier()
