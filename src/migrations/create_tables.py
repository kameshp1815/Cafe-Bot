# src/migrations/create_tables.py

from repositories.Database      import Base, engine, get_db
from repositories.schema.schema import MenuItem, Order, OrderItem

def create_tables() -> None:
    """
    Main entry point for database setup. 
    1. Creates all tables in PostgreSQL.
    2. Seeds initial menu items.
    """
    print("--- Database Migration Started ---")
    
    # CRITICAL: Create tables first so PostgreSQL knows they exist
    Base.metadata.create_all(bind=engine)
    print("Tables created/verified successfully.")
    
    _seed_data()
    print("--- Database Migration Finished ---")

def _seed_data() -> None:
    """
    Populates the menu_items table if it is empty.
    Uses the Context Manager provided by get_db.
    """
    # Use 'with' because get_db is decorated with @contextmanager
    with get_db() as session:
        try:
            # Check if the table is already seeded
            if session.query(MenuItem).first():
                print("Menu already contains data. Skipping seed.")
                return

            print("Seeding menu items into 'menu_items' table...")
            
            menu_items = [
                MenuItem(name="Espresso",           description="Strong and bold single shot of coffee",      price=250, stock=100, is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Cappuccino",          description="Espresso topped with steamed milk foam",     price=350, stock=80,  is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Iced Mocha",          description="Chocolate espresso served over ice",         price=400, stock=60,  is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Latte",               description="Smooth espresso with steamed milk",          price=375, stock=90,  is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Caramel Frappuccino", description="Blended caramel coffee with whipped cream",  price=450, stock=50,  is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Americano",           description="Espresso diluted with hot water",            price=300, stock=100, is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Cold Brew",           description="Slow steeped cold coffee served over ice",   price=425, stock=40,  is_available=True,  created_by="SYSTEM", updated_by="SYSTEM"),
                MenuItem(name="Matcha Latte",        description="Japanese green tea with steamed milk",       price=400, stock=0,   is_available=False, created_by="SYSTEM", updated_by="SYSTEM"),
            ]

            session.add_all(menu_items)
            session.commit()
            print("Successfully added 8 menu items! ☕")

        except Exception as e:
            session.rollback()
            print(f"CRITICAL ERROR during seeding: {e}")
            # Re-raise so the app startup fails clearly if the DB isn't ready
            raise
