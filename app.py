from flask import Flask
from db import init_db, close_db
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.order_routes import order_bp
from routes.admin_routes import admin_bp
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this to a random secret key

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register blueprints
app.register_blueprint(user_bp)
app.register_blueprint(product_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)

# Initialize database
init_db()

# Register teardown handler to close database connections
app.teardown_appcontext(close_db)

@app.route('/')
def index():
    from flask import redirect, session
    if "admin_id" in session:
        return redirect('/admin/dashboard')
    elif "user_id" in session:
        return redirect('/dashboard')
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
