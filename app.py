from flask import Flask, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)  # Створюємо веб–додаток Flask
app.config['SECRET_KEY'] = "fghjklkjhgfd"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clothes_shop.db"
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, default = 0)
    description = db.Column(db.Text)
    image = db.Column(db.String, nullable=False)
    category = db.Column(db.String)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    phone = db.Column(db.Text)
    address = db.Column(db.String)
    status = db.Column(db.String, default = 'new')

    items = db.relationship('OrderItem', backref= 'items', lazy = 'dynamic')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    amount = db.Column(db.Integer, default = 1)
    size = db.Column(db.String)
    
def get_cart():
    cart_items = []
    if 'order_id' in session:
        order_id = session['order_id']
        order = Order.query.get(order_id)
        if order and order.status == "new":
            cart_items = db.session.query(OrderItem, Item).join(Item, OrderItem.item_id == Item.id).filter(OrderItem.order_id == order_id).all()
    return cart_items

@app.route("/")  # Вказуємо url-адресу для виклику функції
def index():
    items = Item.query.all()
    cart_items = get_cart()
    return render_template("index.html", title = "Головна сторінка", items = items, cart = cart_items)  # html-сторінка, що повертається у браузер

@app.route ("/item/<item_id>", methods = ['GET', 'POST'])  # Вказуємо url-адресу для виклику функції
def item_page(item_id):
    item = Item.query.get(item_id)
    cart_items = get_cart()
    if request.method == "POST":
        if request.form['size'] == "Вибрати розмір":
            flash("Вибрати розмір", category="alert-warning")
        else:
            if not 'order_id' in session:
                new_order = Order()
                db.session.add(new_order)
                db.session.flush()
                session['order_id'] = new_order.id
            order_id = session['order_id']
            order_item = OrderItem.query.filter(OrderItem.order_id == order_id).filter(OrderItem.item_id == item.id).filter(OrderItem.size == request.form['size']).first()
            
            if order_item:
                order_item.amount += 1
            else:
                new_item = OrderItem(order_id = order_id, item_id = item.id, size = request.form['size'])
                db.session.add(new_item)
            db.session.commit()
            flash("Товар додано в кошик", category="alert-success")
    return render_template("item.html", item = item, cart = cart_items)  # html-сторінка, що повертається у браузер


@app.route("/category/<category_name>")  # Вказуємо url-адресу для виклику функції
def category_page(category_name):
    items = Item.query.filter_by(category=category_name).all()
    cart_items = get_cart()
    if 'order_id' in session:
        order_id = session['order_id']
        order = Order.query.get(order_id)
        if order.status == "new":
            cart_items = OrderItem.query.filter_by(order_id = order.id).all()

    return render_template("index.html", title = category_name, items = items, cart = cart_items )  # html-сторінка, що повертається у браузер

@app.route ("/cart", methods = ['GET', 'POST'])  # Вказуємо url-адресу для виклику функції
def cart_page():
    cart_items = get_cart()
    return render_template("cart.html", cart = cart_items)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # автоматичне оновлення шаблонів
    app.run(debug=True)  # Запускаємо веб-сервер з цього файлу в режимі налагодження
