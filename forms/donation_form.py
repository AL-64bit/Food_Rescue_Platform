from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class DonationForm(FlaskForm):
    donor_name = StringField("Donor Name", validators=[DataRequired()])
    food_item = StringField("Food Item", validators=[DataRequired()])
    quantity = IntegerField("Quantity", validators=[DataRequired()])
    submit = SubmitField("Donate")
