from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize the database object
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Donor(db.Model):
    """Donation model for tracking food donations."""
    id = db.Column(db.Integer, primary_key=True)
    foodType = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.String(80))
    status = db.Column(db.String(20), default="available")  # available, requested, fulfilled
    location = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.String(20), nullable=False)  # Store as string for simplicity (e.g., '2025-12-31')
    

