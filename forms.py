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
            ('grains', 'Grains')
        ],
        validators=[DataRequired()]
    )
    quantity = IntegerField(
        'Quantity', 
        validators=[DataRequired(), NumberRange(min=0, max=200)
        ]
    )
    submit = SubmitField("Add Donation")




 