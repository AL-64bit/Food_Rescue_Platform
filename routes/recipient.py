from flask import Blueprint, render_template
from models.donation import Donation

recipient = Blueprint('recipient', __name__)

@recipient.route('/recipient')
def available_food():
    # Display all donations to recipients
    donations = Donation.query.all()
    return render_template('recipient.html', donations=donations)
