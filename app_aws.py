from flask import Flask
from db import init_db, close_db
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.order_routes import order_bp
from routes.admin_routes import admin_bp
from routes.budget_routes import budget_bp
from routes.pages_routes import pages_bp
import os
import boto3
from botocore.exceptions import ClientError

# -------------------------------------------------
# Flask App Setup
# -------------------------------------------------
app = Flask(__name__)

# Secret key (AWS safe)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-secret-in-production"
)

# -------------------------------------------------
# AWS CONFIGURATION
# -------------------------------------------------
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# Initialize AWS clients ONCE
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
sns = boto3.client("sns", region_name=AWS_REGION)

# DynamoDB tables (must exist)
app.config["USERS_TABLE"] = dynamodb.Table("FF_Users")
app.config["ADMINS_TABLE"] = dynamodb.Table("FF_Admins")
app.config["PRODUCTS_TABLE"] = dynamodb.Table("FF_Products")
app.config["ORDERS_TABLE"] = dynamodb.Table("FF_Orders")

# SNS topic
app.config["SNS_TOPIC_ARN"] = os.environ.get(
    "SNS_TOPIC_ARN",
    "arn:aws:sns:us-east-1:203918855127:furnishfusion_topic"
)

# -------------------------------------------------
# Upload Configuration
# -------------------------------------------------
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------------------------------
# Helper: SNS Notification
# -------------------------------------------------
def send_notification(subject, message):
    try:
        sns.publish(
            TopicArn=app.config["SNS_TOPIC_ARN"],
            Subject=subject,
            Message=message
        )
    except ClientError as e:
        print("SNS error:", e)

# Make SNS helper available to blueprints
app.config["SEND_NOTIFICATION"] = send_notification

# -------------------------------------------------
# Register Blueprints (UNCHANGED)
# -------------------------------------------------
app.register_blueprint(user_bp)
app.register_blueprint(product_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(pages_bp)

# -------------------------------------------------
# Database Init / Teardown
# (Keep this if db.py is still used anywhere)
# -------------------------------------------------
init_db()
app.teardown_appcontext(close_db)

# -------------------------------------------------
# Context Processor (UNCHANGED)
# -------------------------------------------------
@app.context_processor
def inject_wishlist_count():
    from flask import session
    n = 0

    if session.get("user_id"):
        try:
            from db import get_db
            r = get_db().execute(
                "SELECT COUNT(*) as c FROM wishlist WHERE user_id = ?",
                (session["user_id"],)
            ).fetchone()
            n = r["c"] or 0
        except Exception as e:
            print("Wishlist count error:", e)

    return {"wishlist_count": n}

# -------------------------------------------------
# Root Route (UNCHANGED)
# -------------------------------------------------
@app.route("/")
def index():
    from flask import redirect, session

    if "admin_id" in session:
        return redirect("/admin/dashboard")
    elif "user_id" in session:
        return redirect("/dashboard")
    return redirect("/login")

# -------------------------------------------------
# Entry Point (EC2 compatible)
# -------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
