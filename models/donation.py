from database import db

class Donation(db.Model):
    __tablename__ = "donation"
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.String(64))
    notes = db.Column(db.String(300))
    donor_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    donor = db.relationship("User", back_populates="donations")
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"<Donation {self.food_name} ({self.quantity})>"
