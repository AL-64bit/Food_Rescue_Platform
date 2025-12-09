from flask import Flask, render_template, url_for, redirect, session, flash, request
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

# Create admin user on startup if it doesn't exist
def create_admin_user():
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin_user = User(username='admin', password=hashed_password)
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")

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
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid password.', 'danger')
        else:
            flash('Username not found.', 'danger')
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
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------------- REGISTER PAGE ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ============ DONOR ROUTES ============
@app.route('/donor', methods=['GET', 'POST'])
@login_required
def donor_dashboard():
    form = DonorForm()
    if form.validate_on_submit():
        donor = Donor(foodType=form.foodType.data, quantity=form.quantity.data)
        db.session.add(donor)
        db.session.commit()
        flash('Donation added successfully!', 'success')
        return redirect(url_for('donor_dashboard'))
    
    # Show all donations
    donations = Donor.query.all()
    return render_template('donor_dashboard.html', form=form, donations=donations)

# ============ RECIPIENT ROUTES ============
@app.route('/recipient', methods=['GET', 'POST'])
@login_required
def recipient_dashboard():
    # Show available donations
    donations = Donor.query.filter_by(status="available").all()

    # Handle request action from the template
    if request.method == 'POST':
        donation_id = request.args.get('donation_id')
        if donation_id:
            donation = Donor.query.get_or_404(int(donation_id))
            if donation.status == "available":
                donation.status = "requested"
                db.session.commit()
                flash("Donation requested!", 'success')
            else:
                flash("Donation is not available.", 'warning')
        return redirect(url_for('recipient_dashboard'))

    return render_template('recipient_dashboard.html', donations=donations)


# ============ ADMIN DECORATOR & ROUTES ============
def admin_required(func):
    # simple admin gate: only allow user with username 'admin'
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.username != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return decorated_view


@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # show all donations and requested ones
    all_donations = Donor.query.order_by(Donor.id.desc()).all()
    requested = Donor.query.filter_by(status='requested').all()
    total_available = Donor.query.filter_by(status='available').count()
    return render_template('admin.html', donations=all_donations, requests=requested, total_available=total_available)


@app.route('/admin/donation/<int:donation_id>/update', methods=['POST'])
@login_required
@admin_required
def admin_update_donation(donation_id):
    donation = Donor.query.get_or_404(donation_id)
    # allow status update via form field 'status'
    new_status = request.form.get('status')
    if new_status:
        donation.status = new_status
        db.session.commit()
        flash('Donation status updated.', 'success')
    else:
        flash('No status provided.', 'warning')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/donation/<int:donation_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_donation(donation_id):
    donation = Donor.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    flash('Donation deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin_user()
    app.run(debug=True)