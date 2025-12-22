"""
Initialize database with tables and default data
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager

def init_database():
    """Initialize the database"""
    print("Initializing database...")

    # This will create all tables and populate default coins
    db = DatabaseManager()

    print("✓ Database initialized successfully!")
    print(f"✓ Database location: {db.db_path}")

    # Show what was created
    with db.get_session() as session:
        from database.models import Coin
        coins = session.query(Coin).all()
        print(f"✓ Loaded {len(coins)} coins:")
        for coin in coins:
            print(f"  - {coin.symbol}: {coin.name} ({coin.coingecko_id})")

    db.close()

if __name__ == "__main__":
    init_database()
