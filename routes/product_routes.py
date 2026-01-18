from flask import Blueprint, render_template, session, redirect, flash
from db import get_db

product_bp = Blueprint("product", __name__)

@product_bp.route("/products")
def products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    return render_template("products.html", products=products)


@product_bp.route("/add-to-cart/<int:pid>", methods=["POST"])
def add_to_cart(pid):
    # Check if product exists
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
    
    if not product:
        flash("Product not found!", "error")
        return redirect("/products")
    
    # Initialize cart as dict if not exists
    cart = session.get("cart", {})
    
    # Add or increment product in cart
    if str(pid) in cart:
        cart[str(pid)] += 1
    else:
        cart[str(pid)] = 1
    
    session["cart"] = cart
    flash(f"{product['name']} added to cart!", "success")
    return redirect("/products")
