"""
Database Migration: Add Trending Tracking
==========================================
Adds trending-related columns to existing database
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def migrate_database():
    """Add trending tracking columns to coins table"""

    db_path = Path(__file__).parent / "data" / "memecoin.db"

    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False

    print(f"Migrating database: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(coins)")
        columns = {row[1] for row in cursor.fetchall()}

        migrations = []

        # Add new columns if they don't exist
        if "is_trending" not in columns:
            migrations.append("ALTER TABLE coins ADD COLUMN is_trending BOOLEAN DEFAULT 0")

        if "trending_since" not in columns:
            migrations.append("ALTER TABLE coins ADD COLUMN trending_since DATETIME")

        if "trending_rank" not in columns:
            migrations.append("ALTER TABLE coins ADD COLUMN trending_rank INTEGER")

        if "last_trending_check" not in columns:
            migrations.append("ALTER TABLE coins ADD COLUMN last_trending_check DATETIME")

        if "status" not in columns:
            migrations.append("ALTER TABLE coins ADD COLUMN status VARCHAR(20) DEFAULT 'active'")

        # Execute migrations
        for migration in migrations:
            print(f"  Running: {migration}")
            cursor.execute(migration)

        # Create trending_history table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trending_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin_id INTEGER NOT NULL,
                timestamp DATETIME NOT NULL,
                event_type VARCHAR(20) NOT NULL,
                trending_rank INTEGER,
                previous_rank INTEGER,
                price_usd FLOAT,
                volume_24h FLOAT,
                market_cap FLOAT,
                trending_score FLOAT,
                notes TEXT,
                FOREIGN KEY (coin_id) REFERENCES coins (id)
            )
        """
        )
        print("  Created trending_history table")

        # Create index on timestamp for trending_history
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_trending_history_timestamp
            ON trending_history (timestamp)
        """
        )

        conn.commit()
        print("\n✓ Migration completed successfully!")

        # Show current coin count
        cursor.execute("SELECT COUNT(*) FROM coins")
        count = cursor.fetchone()[0]
        print(f"✓ Database has {count} coins")

        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()
