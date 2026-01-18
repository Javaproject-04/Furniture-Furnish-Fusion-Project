import sqlite3
from flask import g

DATABASE = 'furnishfusion.db'

def get_db():
    """Get database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create order_items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    
    # Create admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create contact_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            country TEXT,
            website TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default contact info if none exists
    cursor.execute("SELECT COUNT(*) as count FROM contact_info")
    contact_count = cursor.fetchone()[0]
    
    if contact_count == 0:
        cursor.execute(
            """INSERT INTO contact_info 
               (company_name, email, phone, address, city, state, zip_code, country, website) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            ("FurnishFusion", "info@furnishfusion.com", "+91 1234567890", 
             "123 Furniture Street", "Mumbai", "Maharashtra", "400001", "India", 
             "https://www.furnishfusion.com")
        )
    
    # Create default admin if no admins exist
    cursor.execute("SELECT COUNT(*) as count FROM admins")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        # Default admin credentials: admin / admin123
        cursor.execute(
            "INSERT INTO admins (username, email, password) VALUES (?, ?, ?)",
            ("admin", "admin@furnishfusion.com", "admin123")
        )
    
    # Add sample products if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM products")
    product_count = cursor.fetchone()[0]
    
    if product_count == 0:
        sample_products = [
            ("Modern Sofa Set", "Comfortable 3-seater sofa with matching cushions. Perfect for your living room.", 45000.00, "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=500"),
            ("Wooden Dining Table", "Elegant 6-seater dining table made from premium oak wood.", 35000.00, "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500"),
            ("Ergonomic Office Chair", "Comfortable office chair with lumbar support and adjustable height.", 12000.00, "https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=500"),
            ("Queen Size Bed Frame", "Sturdy metal bed frame with modern design. Includes headboard.", 28000.00, "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=500"),
            ("Bookshelf Unit", "5-tier bookshelf with adjustable shelves. Perfect for organizing your space.", 15000.00, "https://images.unsplash.com/photo-1594620302200-9a762244a094?w=500"),
            ("Coffee Table", "Glass top coffee table with wooden legs. Modern and elegant design.", 18000.00, "https://images.unsplash.com/photo-1532372320572-cda25653a26d?w=500"),
            ("Wardrobe Cabinet", "Spacious 3-door wardrobe with mirror. Ample storage space.", 42000.00, "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500"),
            ("Study Desk", "Compact study desk with drawers. Perfect for home office.", 22000.00, "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500"),
        ]
        
        cursor.executemany(
            "INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)",
            sample_products
        )
    
    conn.commit()
    conn.close()

def close_db(e=None):
    """Close database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
