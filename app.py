from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)  # Створюємо веб–додаток Flask
app.config['SECRET_KEY'] = "fghjklkjhgfd"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clothes_shop.db"
db.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, default = 0)
    description = db.Column(db.Text)
    image = db.Column(db.String, nullable=False)
    category = db.Column(db.String)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
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
    cart_items = get_cart()
    return render_template("item.html", item = item, cart = cart_items)  # html-сторінка, що повертається у браузер


@app.route("/category/<category_name>")  # Вказуємо url-адресу для виклику функції
def category_page(category_name):
    items = Item.query.filter_by(category=category_name).all()
    cart_items = get_cart()

    return render_template("index.html", title = category_name, items = items, cart = cart_items )  # html-сторінка, що повертається у браузер

@app.route ("/order", methods = ['GET', 'POST'])  # Вказуємо url-адресу для виклику функції
def order_page():
    cart_items = get_cart()
    if len(cart_items) == 0:
        return redirect(url_for('index'))
    if request.method == "POST":
        order_id = session['order_id']
        order = Order.query.get(order_id)
        order.name = request.form['name']
        order.email = request.form['email']
        order.phone = request.form['phone']
        order.address = request.form['address']
        order.status = "submited"
        db.session.flush()
        user = User.query.filter_by(email=order.email).first()
        if not user:
            user = User(name = order.name, email = order.email)
            db.session.add(user)
        db.session.commit()
        del session['order_id']
        flash("Замовлення оформленно.", "alert-success")
        return redirect(url_for('index'))

    return render_template("order.html", cart = cart_items)

@app.route("/cart/delete/<item_id>", methods = ['GET','POST'])
def item_delete(item_id):
    cart_items = get_cart()
    item = OrderItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('index')) 


@app.route("/help")  # Вказуємо url-адресу для виклику функції
def help_page():
    cart_items = get_cart()
    return render_template("faq.html", title = "Підтримка", cart = cart_items)

@app.route("/search")
def search():
    cart_items = get_cart()
    query = request.args.get("query")
    items = []
    if query:
        items = Item.query.filter(Item.title.contains(query)).all()
    
    return render_template("index.html", title = "Пошук за запитом: "+query, items = items, cart = cart_items)

@app.route ("/login", methods = ['GET', 'POST'])  # Вказуємо url-адресу для виклику функції
def login():
    cart_items = get_cart()
    return render_template("login.html", title = "Увійти в профіль ",  cart = cart_items)


@app.route ("/signup", methods = ['GET', 'POST'])  # Вказуємо url-адресу для виклику функції
def signup():
    cart_items = get_cart()
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash("Користувач з таким email вже існує.", "alert-danger")
        else:
            if request.form['password'] != request.form['password-repeat']:
                flash("Паролі повинні співпадати.", "alert-danger")
            else:
                username = request.form['firstname'].capitalize() + ' ' + request.form['surname'].capitalize()
                hash = generate_password_hash(request.form['password'])
                user = User(name = username, email = request.form['email'], password = hash)
                db.session.add(user)
                db.session.commit()
                flash("Профіль створено.", "alert-success")
                return redirect(url_for('login'))

    return render_template("signup.html", title = "Реєстрація",  cart = cart_items)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True  # автоматичне оновлення шаблонів
    app.run(debug=True)  # Запускаємо веб-сервер з цього файлу в режимі налагодження
