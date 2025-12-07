from flask import Flask, render_template, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm, DonorForm
from models import db, User, Donor
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

@app.route('/')
def index():
    return render_template("index.html")

# ---------------- LOGIN PAGE ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

# ---------------- LOGOUT ----------------
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------- REGISTER PAGE ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ---------------- DONOR --------------------
@app.route('/donor', methods=['GET', 'POST'])
@login_required
def donor_dashboard():
    form = DonorForm()
    if form.validate_on_submit():
        donor = Donor(foodType=form.foodType.data, quantity=form.quantity.data)
        db.session.add(donor)
        db.session.commit()
        flash('Donation added successfully!', 'success')
        
    return render_template('donor_dashboard.html', form=form)

# ---------------- RECIPIENT --------------------
@app.route('/recipient', methods=['GET'])
def recipient_dashboard():
    donation = Donor.query.all()
    return render_template('recipient_dashboard.html', donation=donation)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)