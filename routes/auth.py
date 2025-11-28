from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from forms.register_form import RegisterForm
from models.user import User
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = RegisterForm()  # You can create a separate LoginForm if desired
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html', form=form)

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "success")
    return redirect(url_for('home'))
