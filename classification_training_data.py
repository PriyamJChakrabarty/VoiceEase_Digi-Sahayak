"""
Comprehensive Training Data for Query/Grievance Type Classification
Robust dataset with 20+ types covering all telecom scenarios
"""

# QUERY TYPES - Informational/Transactional Requests (Auto-Resolved)
QUERY_TYPES = {
    "BALANCE_CHECK": {
        "name": "Balance Check",
        "department": "Customer Support",
        "description": "User wants to check remaining data, SMS, call balance",
        "examples": [
            "Kitna data bacha hai?",
            "How much data is left?",
            "Mera balance batao",
            "Data balance check karna hai",
            "Remaining quota kitna hai",
            "SMS balance kitna hai",
            "Call balance check",
            "Mere paas kitna data remaining hai",
            "Balance inquiry",
            "Data usage batao"
        ]
    },

    "PLAN_INQUIRY": {
        "name": "Plan Information",
        "department": "Customer Support",
        "description": "User asking about current plan, plan details, validity",
        "examples": [
            "Mera current plan kya hai?",
            "What is my active plan?",
            "Plan details batao",
            "Validity kitni baki hai",
            "Plan expiry kab hai",
            "Current subscription details",
            "Active plan check",
            "Plan information chahiye",
            "Mera plan konsa hai",
            "Plan ka naam batao"
        ]
    },

    "RECHARGE_INQUIRY": {
        "name": "Recharge Plans",
        "department": "Sales",
        "description": "User asking about recharge options, plan prices",
        "examples": [
            "500 rupees mein best plan",
            "Recharge plans batao",
            "300 ka plan hai kya",
            "Best budget plan",
            "Affordable recharge options",
            "Cheapest plan under 200",
            "Recharge kaise kare",
            "Online recharge process",
            "New plan lena hai",
            "Plan upgrade karna hai"
        ]
    },

    "OFFER_INQUIRY": {
        "name": "Offers & Promotions",
        "department": "Sales",
        "description": "User asking about discounts, cashback, deals",
        "examples": [
            "Koi offer chal raha hai?",
            "Discount available hai kya",
            "Cashback milega kya",
            "Current deals batao",
            "Promotional offers",
            "Special discount hai",
            "Festive offer check",
            "Student discount",
            "Family pack offer",
            "Combo plans"
        ]
    },

    "VALIDITY_INQUIRY": {
        "name": "Validity Check",
        "department": "Customer Support",
        "description": "User wants to know plan expiry, validity remaining",
        "examples": [
            "Plan kab expire hoga?",
            "Validity kitni baki hai",
            "Expiry date kya hai",
            "Plan validity check",
            "Kitne din aur valid hai",
            "Recharge kab karna padega",
            "Validity extend kaise kare",
            "Expiry notification",
            "Plan active hai kya",
            "Validity status"
        ]
    },

    "USAGE_INQUIRY": {
        "name": "Usage History",
        "department": "Customer Support",
        "description": "User asking about data usage, call history",
        "examples": [
            "Kitna data use ho gaya",
            "Usage history batao",
            "Call details chahiye",
            "Data consumption check",
            "Daily usage kitna hai",
            "Last recharge ka usage",
            "Internet usage report",
            "Call log details",
            "SMS usage",
            "Weekly data usage"
        ]
    },

    "CUSTOMER_CARE_INQUIRY": {
        "name": "Contact Information",
        "department": "Customer Support",
        "description": "User asking for helpline numbers, support channels",
        "examples": [
            "Customer care number kya hai",
            "Helpline number batao",
            "Support kaise contact kare",
            "Email support hai kya",
            "Chat support available",
            "Toll free number",
            "Complaint number",
            "Technical support contact",
            "Billing support number",
            "Emergency helpline"
        ]
    },

    "SERVICE_ACTIVATION": {
        "name": "Service Activation",
        "department": "Technical Support",
        "description": "User wants to activate services (roaming, DND, VAS)",
        "examples": [
            "Roaming activate kaise kare",
            "DND service chahiye",
            "Caller tune activate",
            "International roaming",
            "SMS pack activation",
            "Data pack subscribe",
            "VAS service activate",
            "Call forwarding setup",
            "Voicemail activate",
            "Mobile hotspot enable"
        ]
    }
}

# GRIEVANCE TYPES - Problems Requiring Resolution (Open Status)
GRIEVANCE_TYPES = {
    "NETWORK_CONNECTIVITY": {
        "name": "Network Connectivity Issue",
        "department": "Network Operations",
        "description": "No network, connection drops, signal problems",
        "severity": "HIGH",
        "examples": [
            "Network nahi aa raha",
            "No signal",
            "Network not working",
            "Connection bar nahi dikh raha",
            "Signal strength bahut weak",
            "Network continuously disconnecting",
            "4G network nahi mil raha",
            "Network coverage problem",
            "Signal drop ho raha hai",
            "Network unavailable hai"
        ]
    },

    "SLOW_INTERNET": {
        "name": "Slow Internet Speed",
        "department": "Network Operations",
        "description": "Internet speed issues, buffering, slow browsing",
        "severity": "MEDIUM",
        "examples": [
            "Internet bahut slow hai",
            "Speed kam hai",
            "Buffering ho raha hai",
            "Data speed slow",
            "Download nahi ho raha",
            "Video load nahi ho raha",
            "Website open nahi ho rahi",
            "Slow browsing",
            "4G speed bahut kam",
            "Internet lag kar raha hai"
        ]
    },

    "BILLING_DISPUTE": {
        "name": "Billing Complaint",
        "department": "Billing Department",
        "description": "Wrong charges, unexpected deductions, billing errors",
        "severity": "HIGH",
        "examples": [
            "Bill mein galat charge hai",
            "Extra amount deduct hua",
            "Wrong billing",
            "Overcharged ho gaya",
            "Unexpected deduction",
            "Bill amount zyada hai",
            "Duplicate charge",
            "Refund chahiye",
            "Billing error",
            "Amount cut gaya galti se"
        ]
    },

    "RECHARGE_FAILURE": {
        "name": "Recharge Failed",
        "department": "Technical Support",
        "description": "Recharge not reflecting, payment deducted but no credit",
        "severity": "HIGH",
        "examples": [
            "Recharge nahi hua",
            "Payment cut gaya par plan nahi mila",
            "Recharge failed",
            "Amount deduct hua but no recharge",
            "Transaction failed",
            "Recharge pending hai",
            "Plan activate nahi hua",
            "Recharge not reflecting",
            "Payment success but no data",
            "Recharge error"
        ]
    },

    "CALL_DROPS": {
        "name": "Call Dropping",
        "department": "Network Operations",
        "description": "Calls getting disconnected frequently",
        "severity": "MEDIUM",
        "examples": [
            "Call bar bar disconnect ho jati hai",
            "Call drop problem",
            "Calls not connecting properly",
            "Call automatically cut ho jata hai",
            "Voice call issues",
            "Call quality poor",
            "Call disconnection problem",
            "Frequent call drops",
            "Incoming calls nahi aa rahe",
            "Outgoing call fail"
        ]
    },

    "DATA_NOT_WORKING": {
        "name": "Mobile Data Not Working",
        "department": "Technical Support",
        "description": "Mobile data not functioning despite active plan",
        "severity": "HIGH",
        "examples": [
            "Data nahi chal raha",
            "Mobile data not working",
            "Internet on nahi ho raha",
            "Data connection failed",
            "Mobile data disabled",
            "4G not working",
            "Data network unavailable",
            "Internet access nahi hai",
            "Data plan active hai par internet nahi",
            "Mobile data error"
        ]
    },

    "SIM_ISSUE": {
        "name": "SIM Card Problem",
        "department": "Technical Support",
        "description": "SIM not detected, invalid SIM, SIM errors",
        "severity": "HIGH",
        "examples": [
            "SIM detect nahi ho raha",
            "Invalid SIM error",
            "SIM not working",
            "No SIM card detected",
            "SIM card failure",
            "SIM registration failed",
            "Emergency calls only",
            "SIM network locked",
            "SIM inactive",
            "SIM damaged hai kya"
        ]
    },

    "PORT_REQUEST_ISSUE": {
        "name": "Porting Problem",
        "department": "Customer Support",
        "description": "Number portability issues, port request pending/failed",
        "severity": "MEDIUM",
        "examples": [
            "Port request pending hai",
            "Number port nahi ho raha",
            "MNP failed",
            "Porting delay",
            "Port request reject hua",
            "Number portability issue",
            "Port code nahi mila",
            "Porting process stuck",
            "UPC code problem",
            "Port timeline exceed"
        ]
    },

    "SERVICE_DEACTIVATION": {
        "name": "Unwanted Service Deactivation",
        "department": "Technical Support",
        "description": "Services stopped without request, auto-deactivation",
        "severity": "MEDIUM",
        "examples": [
            "Service apne aap band ho gaya",
            "Auto deactivation hua",
            "Plan deactivated without notice",
            "Services stopped suddenly",
            "Roaming disabled automatically",
            "Data pack deactivated",
            "Number suspended",
            "Service disconnected",
            "Plan cancelled without permission",
            "Services not active"
        ]
    },

    "POOR_CALL_QUALITY": {
        "name": "Voice Quality Issue",
        "department": "Network Operations",
        "description": "Echo, distortion, voice breaking in calls",
        "severity": "MEDIUM",
        "examples": [
            "Call mein echo aa raha hai",
            "Voice quality poor",
            "Voice break ho rahi hai",
            "Sound distorted",
            "Call clarity bahut kam",
            "Voice echo problem",
            "Audio breaking",
            "Call mein noise",
            "Voice lag",
            "Sound quality bad"
        ]
    },

    "APP_NOT_WORKING": {
        "name": "Mobile App Issue",
        "department": "Technical Support",
        "description": "Company app crashing, login issues, app errors",
        "severity": "LOW",
        "examples": [
            "App crash ho raha hai",
            "Login nahi ho raha app mein",
            "App not opening",
            "Application error",
            "App hang kar raha hai",
            "App update nahi ho raha",
            "App loading issue",
            "App login failed",
            "My account app problem",
            "App slow hai"
        ]
    },

    "UNWANTED_CHARGES": {
        "name": "Unauthorized Charges",
        "department": "Billing Department",
        "description": "Unknown charges, VAS charges without consent",
        "severity": "HIGH",
        "examples": [
            "Unknown service ka charge",
            "VAS charge kyu hua",
            "Unauthorized deduction",
            "Subscription nahi kiya tha",
            "Random charges aa rahe",
            "Premium service charge",
            "Third party charge",
            "Unexpected service fee",
            "Fraudulent charge",
            "Unauthorized billing"
        ]
    }
}


def get_all_training_examples():
    """
    Get all training examples with labels for classifier training

    Returns:
        list: [(text, category, type, department), ...]
    """
    training_data = []

    # Add query examples
    for type_key, type_info in QUERY_TYPES.items():
        for example in type_info['examples']:
            training_data.append({
                'text': example,
                'category': 'QUERY',
                'type': type_key,
                'type_name': type_info['name'],
                'department': type_info['department']
            })

    # Add grievance examples
    for type_key, type_info in GRIEVANCE_TYPES.items():
        for example in type_info['examples']:
            training_data.append({
                'text': example,
                'category': 'GRIEVANCE',
                'type': type_key,
                'type_name': type_info['name'],
                'department': type_info['department'],
                'severity': type_info.get('severity', 'MEDIUM')
            })

    return training_data


def get_type_info(type_key, category):
    """Get detailed information about a specific type"""
    if category == 'QUERY':
        return QUERY_TYPES.get(type_key)
    else:
        return GRIEVANCE_TYPES.get(type_key)


if __name__ == "__main__":
    # Test: Print training data statistics
    data = get_all_training_examples()

    print(f"\n{'='*80}")
    print("TRAINING DATA STATISTICS")
    print(f"{'='*80}\n")

    query_count = sum(1 for d in data if d['category'] == 'QUERY')
    grievance_count = sum(1 for d in data if d['category'] == 'GRIEVANCE')

    print(f"Total Examples: {len(data)}")
    print(f"Query Examples: {query_count}")
    print(f"Grievance Examples: {grievance_count}")
    print(f"\nQuery Types: {len(QUERY_TYPES)}")
    print(f"Grievance Types: {len(GRIEVANCE_TYPES)}")

    print(f"\n{'='*80}")
    print("QUERY TYPES")
    print(f"{'='*80}\n")
    for key, info in QUERY_TYPES.items():
        print(f"✓ {info['name']} ({key})")
        print(f"  Department: {info['department']}")
        print(f"  Examples: {len(info['examples'])}")
        print()

    print(f"{'='*80}")
    print("GRIEVANCE TYPES")
    print(f"{'='*80}\n")
    for key, info in GRIEVANCE_TYPES.items():
        print(f"⚠ {info['name']} ({key})")
        print(f"  Department: {info['department']}")
        print(f"  Severity: {info.get('severity', 'MEDIUM')}")
        print(f"  Examples: {len(info['examples'])}")
        print()
