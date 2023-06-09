from app import app, db

with app.app_context():
    db.create_all()
    # User.drop()
    # db.drop_all()