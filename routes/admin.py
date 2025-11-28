from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.user import User
from database import db
from models.donation import Donation

admin = Blueprint("admin", __name__, url_prefix="/admin")

def role_required(role):
    # small helper (can also use decorator factory pattern)
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                flash("Admin access required", "danger")
                return redirect(url_for("main.home"))
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

@admin.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    users = User.query.all()
    donations = Donation.query.order_by(Donation.created_at.desc()).all()
    return render_template("admin_dashboard.html", users=users, donations=donations)

@admin.route("/delete-donation/<int:donation_id>", methods=["POST"])
@login_required
@role_required("admin")
def delete_donation(donation_id):
    d = Donation.query.get_or_404(donation_id)
    db.session.delete(d)
    db.session.commit()
    flash("Donation removed", "info")
    return redirect(url_for("admin.dashboard"))
