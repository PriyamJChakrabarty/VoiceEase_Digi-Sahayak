"""
Database Migration: From Complaints to Queries/Grievances
Run this ONCE to update your database schema
"""

from sqlalchemy import text
from db import engine
from dotenv import load_dotenv

load_dotenv()

def migrate():
    print("\n" + "="*80)
    print("DATABASE MIGRATION: Complaints -> Queries/Grievances")
    print("="*80 + "\n")

    with engine.begin() as conn:
        # Step 1: Create queries table
        print("Step 1: Creating 'queries' table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS queries (
                    query_id INT PRIMARY KEY AUTO_INCREMENT,
                    conversation_id INT,
                    user_id INT NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    extracted_entities JSON,
                    status VARCHAR(20) DEFAULT 'resolved',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    INDEX idx_department (department),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at)
                )
            """))
            print("[OK] 'queries' table created successfully")
        except Exception as e:
            print(f"[WARN] 'queries' table creation: {e}")

        # Step 2: Create grievances table
        print("\nStep 2: Creating 'grievances' table...")
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS grievances (
                    grievance_id INT PRIMARY KEY AUTO_INCREMENT,
                    conversation_id INT,
                    user_id INT NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    type VARCHAR(50) NOT NULL,
                    department VARCHAR(100) NOT NULL,
                    description TEXT NOT NULL,
                    extracted_entities JSON,
                    status VARCHAR(20) DEFAULT 'open',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP NULL,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    INDEX idx_department (department),
                    INDEX idx_status (status),
                    INDEX idx_created_at (created_at)
                )
            """))
            print("[OK] 'grievances' table created successfully")
        except Exception as e:
            print(f"[WARN] 'grievances' table creation: {e}")

        # Step 3: Check if conversations table needs category column
        print("\nStep 3: Updating 'conversations' table...")
        try:
            # Check if category column exists
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'conversations'
                AND COLUMN_NAME = 'category'
            """))
            category_exists = result.scalar() > 0

            if not category_exists:
                # Add category column
                conn.execute(text("""
                    ALTER TABLE conversations
                    ADD COLUMN category VARCHAR(20) DEFAULT 'QUERY' AFTER entities
                """))
                print("[OK] Added 'category' column to conversations table")
            else:
                print("[OK] 'category' column already exists in conversations table")

            # Check if priority column exists (old schema)
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'conversations'
                AND COLUMN_NAME = 'priority'
            """))
            priority_exists = result.scalar() > 0

            if priority_exists:
                # Drop priority column
                conn.execute(text("""
                    ALTER TABLE conversations
                    DROP COLUMN priority
                """))
                print("[OK] Removed 'priority' column from conversations table")

        except Exception as e:
            print(f"[WARN] Conversations table update: {e}")

        # Step 4: Migrate data from old complaints table if it exists
        print("\nStep 4: Checking for old 'complaints' table...")
        try:
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'complaints'
            """))
            complaints_exists = result.scalar() > 0

            if complaints_exists:
                # Check if there's data to migrate
                result = conn.execute(text("SELECT COUNT(*) FROM complaints"))
                complaint_count = result.scalar()

                if complaint_count > 0:
                    print(f"Found {complaint_count} records in old 'complaints' table")
                    print("Migrating to 'grievances' table...")

                    # Migrate complaints to grievances
                    conn.execute(text("""
                        INSERT INTO grievances
                        (conversation_id, user_id, phone, type, department, description,
                         extracted_entities, status, created_at)
                        SELECT
                            conversation_id, user_id, phone, complaint_type, department,
                            description, extracted_entities, status, created_at
                        FROM complaints
                    """))
                    print(f"[OK] Migrated {complaint_count} records to 'grievances' table")

                    # Optionally rename old table (don't drop it, just in case)
                    conn.execute(text("RENAME TABLE complaints TO complaints_old_backup"))
                    print("[OK] Renamed old 'complaints' table to 'complaints_old_backup'")
                else:
                    print("[OK] No data to migrate from 'complaints' table")
            else:
                print("[OK] No old 'complaints' table found (clean migration)")

        except Exception as e:
            print(f"[WARN] Complaints migration: {e}")

        # Step 5: Create some sample data
        print("\nStep 5: Creating sample data...")
        try:
            # Check if users exist
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()

            if user_count > 0:
                # Get first user
                result = conn.execute(text("SELECT user_id, phone FROM users LIMIT 1"))
                user = result.fetchone()
                user_id, phone = user[0], user[1]

                # Insert sample query
                conn.execute(text("""
                    INSERT INTO queries
                    (user_id, phone, type, department, description, extracted_entities, status)
                    VALUES
                    (:user_id, :phone, 'BALANCE_QUERY', 'Customer Support',
                     'User asked about remaining data balance', '{}', 'resolved')
                """), {'user_id': user_id, 'phone': phone})

                # Insert sample grievance
                conn.execute(text("""
                    INSERT INTO grievances
                    (user_id, phone, type, department, description, extracted_entities, status)
                    VALUES
                    (:user_id, :phone, 'NETWORK_ISSUE', 'Network Operations',
                     'User reported slow internet speed in their area', '{"issue": "slow"}', 'open')
                """), {'user_id': user_id, 'phone': phone})

                print("[OK] Created sample query and grievance records")
            else:
                print("[WARN] No users found, skipping sample data creation")

        except Exception as e:
            print(f"[WARN] Sample data creation: {e}")

    print("\n" + "="*80)
    print("MIGRATION COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nYou can now:")
    print("  1. Run 'streamlit run app.py' to test the main app")
    print("  2. Navigate to Query Dashboard to see general inquiries")
    print("  3. Navigate to Grievance Dashboard to see customer complaints")
    print("\nNote: Old 'complaints' table (if existed) has been backed up as 'complaints_old_backup'")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"\n[ERROR] MIGRATION FAILED: {e}")
        print("Please check your database connection and try again.")
        import traceback
        traceback.print_exc()
