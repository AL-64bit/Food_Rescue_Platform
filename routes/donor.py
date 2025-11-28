from flask import Blueprint, render_template, redirect, url_for, flash
from forms.donation_form import DonationForm
from models.donation import Donation
from database import db
from flask_login import login_required, current_user

donor = Blueprint("donor", __name__)

@donor.route("/donate", methods=["GET", "POST"])
@login_required
def donate():
    if current_user.role not in ("donor", "admin"):
        flash("Only donors (or admin) can post donations.", "warning")
        return redirect(url_for("home"))
    form = DonationForm()
    if form.validate_on_submit():
        donation = Donation(
            food_name=form.food_name.data,
            quantity=form.quantity.data,
            notes=form.notes.data,
            donor_id=current_user.id
        )
        db.session.add(donation)
        db.session.commit()
        flash("Donation posted — thank you!", "success")
        return redirect(url_for("donor.list_my_donations"))
    return render_template("donate.html", form=form)

@donor.route("/donations")
@login_required
def list_my_donations():
    donations = Donation.query.filter_by(donor_id=current_user.id).order_by(Donation.created_at.desc()).all()
    return render_template("donation_list.html", donations=donations)
