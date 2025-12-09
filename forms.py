from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, NumberRange
from models import User

class RegisterForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length( 
        min=4, max=20)], render_kw={"placeholder": "Username"}
        )
    
    password = PasswordField(validators=[InputRequired(), Length( 
        min=4, max=20)], render_kw={"placeholder": "Password"}
        )
    
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        
        if existing_user_username:
            raise ValidationError(
                "That username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length( 
        min=4, max=20)], render_kw={"placeholder": "Username"}
        )
    
    password = PasswordField(validators=[InputRequired(), Length( 
        min=4, max=20)], render_kw={"placeholder": "Password"}
        )
    
    submit = SubmitField("Login")

class DonorForm(FlaskForm):
    foodType = SelectField(
        'Food Types', 
        choices=[
            ('fruits', 'Fruits'),
            ('vegetables', 'Vegetables'),
            ('proteins', 'Proteins'),
            ('dairy', 'Dairy'),
            ('grains', 'Grains'),
            ('Other', 'Other (please specify below)')
        ],
        validators=[DataRequired()]
    )
    custom_foodType = StringField(
        '',
        render_kw={"placeholder": "If Other, specify food"}
    )
    quantity = IntegerField(
        'Quantity', 
        validators=[DataRequired(), NumberRange(min=0, max=200)]
    )

    location = SelectField(
        'Location',
        choices=[
            ('Community Center', 'Community Center'),
            ('School', 'School'),
            ('Religious Institution', 'Religious Institution'),
            ('Local Park', 'Local Park'),
            ('Other', 'Other (please specify below)')
        ],
        validators=[DataRequired()]
    )
    custom_location = StringField(
        '',
        render_kw={"placeholder": "If Other, specify location"}
    )
    expiry = SelectField(
        'Expiry Date',
        choices=[
            ('Today', 'Today'),
            ('Tomorrow', 'Tomorrow'),
            ('3 Days', 'In 3 Days'),
            ('1 Week', 'In 1 Week'),
            ('Custom', 'Custom Date (YYYY-MM-DD)')
        ],
        validators=[DataRequired()]
    )
    custom_expiry = StringField(
        '',
        render_kw={"placeholder": "If Custom, specify date"}
    )
    submit = SubmitField("Add Donation")