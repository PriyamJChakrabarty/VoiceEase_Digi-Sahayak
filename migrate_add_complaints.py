"""
Database Migration: Add Conversations and Complaints Tables
Run once to upgrade database schema for complaint tracking system
"""

from sqlalchemy import text
from db import engine
from datetime import datetime

print("="*70)
print("DATABASE MIGRATION: Adding Complaint Tracking & Conversation History")
print("="*70)

with engine.begin() as conn:
    # Check if tables already exist
    result = conn.execute(text("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_schema = DATABASE()
        AND table_name = 'conversations'
    """))

    if result.scalar() > 0:
        print("\n⚠️  Tables already exist. Skipping migration.")
        print("To re-run migration:")
        print("  1. Drop tables: DROP TABLE complaints; DROP TABLE conversations;")
        print("  2. Run this script again")
        exit(0)

    print("\n[1/2] Creating 'conversations' table...")
    print("      Purpose: Store all user interactions with classification metadata")

    conn.execute(text("""
        CREATE TABLE conversations (
            conversation_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            phone VARCHAR(12) NOT NULL,
            query_text TEXT NOT NULL,
            response_text TEXT NOT NULL,

            -- Classification metadata from ticket_classifier
            primary_intent VARCHAR(50),
            intent_tags JSON,
            entities JSON,
            priority ENUM('HIGH', 'MEDIUM', 'LOW'),
            routing VARCHAR(50),

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            -- Indexes for fast filtering
            INDEX idx_user_id (user_id),
            INDEX idx_phone (phone),
            INDEX idx_created_at (created_at),
            INDEX idx_primary_intent (primary_intent),
            INDEX idx_priority (priority),

            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """))
    print("      ✅ Created 'conversations' table with 6 indexes")

    print("\n[2/2] Creating 'complaints' table...")
    print("      Purpose: Track NETWORK_ISSUE, BILLING_COMPLAINT, TECHNICAL_SUPPORT")

    conn.execute(text("""
        CREATE TABLE complaints (
            complaint_id INT AUTO_INCREMENT PRIMARY KEY,
            conversation_id INT NOT NULL,
            user_id INT NOT NULL,
            phone VARCHAR(12) NOT NULL,

            -- Complaint categorization
            complaint_type VARCHAR(50) NOT NULL,
            department VARCHAR(50) NOT NULL,
            priority ENUM('HIGH', 'MEDIUM', 'LOW') DEFAULT 'MEDIUM',

            -- Complaint details
            description TEXT NOT NULL,
            extracted_entities JSON,

            -- Status tracking
            status ENUM('open', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
            resolution_notes TEXT,

            -- Timestamps
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP NULL,

            -- Indexes for dashboard queries
            INDEX idx_user_id (user_id),
            INDEX idx_complaint_type (complaint_type),
            INDEX idx_department (department),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at),
            INDEX idx_priority_status (priority, status),
            INDEX idx_dept_date (department, created_at),

            FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """))
    print("      ✅ Created 'complaints' table with 7 indexes")

print("\n" + "="*70)
print("✅ MIGRATION COMPLETED SUCCESSFULLY")
print("="*70)

print("\nDatabase Schema Summary:")
print("  📊 conversations table:")
print("     - Stores ALL user interactions (queries + responses)")
print("     - Includes classification metadata (intents, priority, entities)")
print("     - Linked to users table via user_id")
print()
print("  🎫 complaints table:")
print("     - Filtered subset for complaint-only intents")
print("     - Department mapping:")
print("       • NETWORK_ISSUE → Network Operations")
print("       • BILLING_COMPLAINT → Billing Department")
print("       • TECHNICAL_SUPPORT → Technical Support")
print("     - Status tracking: open → in_progress → resolved → closed")
print()
print("Next Steps:")
print("  1. ✅ Migration complete (tables created)")
print("  2. 📝 Implement conversation_manager.py (data layer)")
print("  3. 🔗 Integrate into app.py (save conversations)")
print("  4. 🤖 Build complaint_summarizer.py (AI summaries)")
print("  5. 📊 Create management dashboard")
print()
print("To test the schema:")
print("  python db.py  # Verify connection")
print("  SELECT * FROM conversations;  # Should be empty")
print("  SELECT * FROM complaints;  # Should be empty")
print("="*70)
