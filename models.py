from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# Initialize the database object
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    foodType = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.String(80), nullable=False)
    