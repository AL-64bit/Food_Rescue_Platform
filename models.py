from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize the database object
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    donations = db.relationship('Donor', backref='user', lazy=True, cascade='all, delete-orphan')
    requests = db.relationship('Request', backref='user', lazy=True, cascade='all, delete-orphan')

class Donor(db.Model):
    """Donation model for tracking food donations."""
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    foodType = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.String(80))
    status = db.Column(db.String(20), default="available", index=True)  # available, requested, fulfilled
    location = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.String(20), nullable=False, index=True)  # Store as string for simplicity (e.g., '2025-12-31')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    requests = db.relationship('Request', backref='donation', lazy=True, cascade='all, delete-orphan')

class Request(db.Model):
    """Request model for tracking donation requests by recipients."""
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    donation_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    status = db.Column(db.String(20), default="pending", index=True)  # pending, approved, rejected, fulfilled
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

