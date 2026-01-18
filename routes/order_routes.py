from flask import Blueprint, render_template, session, redirect, flash, request
from db import get_db
from datetime import datetime

order_bp = Blueprint("order", __name__)

@order_bp.route("/cart")
def cart():
    cart_dict = session.get("cart", {})
    
    if not cart_dict:
        return render_template("cart.html", cart_items=[], total=0)
    
    db = get_db()
    cart_items = []
    total = 0
    
    for product_id, quantity in cart_dict.items():
        product = db.execute("SELECT * FROM products WHERE id = ?", (int(product_id),)).fetchone()
        if product:
            item_total = product["price"] * quantity
            total += item_total
            cart_items.append({
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "quantity": quantity,
                "total": item_total
            })
    
    return render_template("cart.html", cart_items=cart_items, total=total)


@order_bp.route("/update-cart/<int:pid>", methods=["POST"])
def update_cart(pid):
    cart = session.get("cart", {})
    action = request.form.get("action")
    
    if action == "remove":
        cart.pop(str(pid), None)
        flash("Item removed from cart!", "success")
    elif action == "decrease":
        if str(pid) in cart:
            if cart[str(pid)] > 1:
                cart[str(pid)] -= 1
            else:
                cart.pop(str(pid), None)
                flash("Item removed from cart!", "success")
    elif action == "increase":
        cart[str(pid)] = cart.get(str(pid), 0) + 1
    
    session["cart"] = cart
    return redirect("/cart")


@order_bp.route("/place-order", methods=["POST"])
def place_order():
    if "user_id" not in session:
        flash("Please login to place an order.", "error")
        return redirect("/login")

    cart_dict = session.get("cart", {})
    
    if not cart_dict:
        flash("Your cart is empty!", "error")
        return redirect("/products")

    db = get_db()
    cart_items = []
    total = 0
    
    for product_id, quantity in cart_dict.items():
        product = db.execute("SELECT * FROM products WHERE id = ?", (int(product_id),)).fetchone()
        if product:
            item_total = product["price"] * quantity
            total += item_total
            cart_items.append({
                "product": product,
                "quantity": quantity,
                "total": item_total
            })

    try:
        # Create order
        cur = db.execute(
            "INSERT INTO orders (user_id, total, status, created_at) VALUES (?, ?, ?, ?)",
            (session["user_id"], total, "pending", datetime.now())
        )
        order_id = cur.lastrowid

        # Add order items
        for item in cart_items:
            db.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                (order_id, item["product"]["id"], item["quantity"], item["product"]["price"])
            )

        db.commit()
        session["cart"] = {}
        flash(f"Order placed successfully! Order ID: #{order_id}", "success")
        return redirect("/orders")
    except Exception as e:
        db.rollback()
        flash("An error occurred while placing your order. Please try again.", "error")
        return redirect("/cart")


@order_bp.route("/orders")
def orders():
    if "user_id" not in session:
        flash("Please login to view your orders.", "error")
        return redirect("/login")

    db = get_db()
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    
    # Get order items for each order
    orders_with_items = []
    for order in orders:
        items = db.execute(
            """SELECT oi.*, p.name, p.description 
               FROM order_items oi 
               JOIN products p ON oi.product_id = p.id 
               WHERE oi.order_id = ?""",
            (order["id"],)
        ).fetchall()
        # Use 'order_items' as key to avoid conflict with dict.items() method
        orders_with_items.append({
            "order": order,
            "order_items": items
        })
    
    return render_template("orders.html", orders_with_items=orders_with_items)
