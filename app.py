from flask import Flask, render_template, url_for, redirect, session, flash, request
from datetime import date, timedelta
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm, DonorForm
from models import db, User, Donor, Request
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
        # Determine final food type (use custom if 'Other')
        final_food = form.custom_foodType.data.strip() if form.foodType.data == 'Other' and form.custom_foodType.data else form.foodType.data

        # Determine final location (use custom if 'Other')
        final_location = form.custom_location.data.strip() if form.location.data == 'Other' and form.custom_location.data else form.location.data

        # Determine final expiry (map choices to actual dates or use custom)
        expiry_choice = form.expiry.data
        if expiry_choice == 'Today':
            final_expiry = date.today().isoformat()
        elif expiry_choice == 'Tomorrow':
            final_expiry = (date.today() + timedelta(days=1)).isoformat()
        elif expiry_choice == '3 Days':
            final_expiry = (date.today() + timedelta(days=3)).isoformat()
        elif expiry_choice == '1 Week':
            final_expiry = (date.today() + timedelta(weeks=1)).isoformat()
        elif expiry_choice == 'Custom' and form.custom_expiry.data:
            final_expiry = form.custom_expiry.data.strip()
        else:
            final_expiry = ''

        donor = Donor(
            donor_id=current_user.id,
            foodType=final_food,
            quantity=form.quantity.data,
            location=final_location,
            expiry=final_expiry
        )
        db.session.add(donor)
        db.session.commit()
        flash('Donation added successfully!', 'success')
        return redirect(url_for('donor_dashboard'))
    
    # Show user's donations
    donations = Donor.query.filter_by(donor_id=current_user.id).all()
    return render_template('donor_dashboard.html', form=form, donations=donations)

# View requests for a specific donation
@app.route('/donor/requests/<int:donation_id>', methods=['GET', 'POST'])
@login_required
def view_donation_requests(donation_id):
    donation = Donor.query.get_or_404(donation_id)
    
    # Ensure user owns this donation
    if donation.donor_id != current_user.id:
        flash('You do not have permission to view these requests.', 'danger')
        return redirect(url_for('donor_dashboard'))
    
    # Get all requests for this donation
    requests = Request.query.filter_by(donation_id=donation_id).all()
    
    return render_template('donation_requests.html', donation=donation, requests=requests)

# Approve or reject a request
@app.route('/donor/request/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_request(request_id):
    req = Request.query.get_or_404(request_id)
    donation = req.donation
    
    # Ensure user owns the donation
    if donation.donor_id != current_user.id:
        flash('You do not have permission to approve this request.', 'danger')
        return redirect(url_for('donor_dashboard'))
    
    req.status = 'approved'
    donation.status = 'requested'
    db.session.commit()
    flash('Request approved!', 'success')
    return redirect(url_for('view_donation_requests', donation_id=donation.id))

@app.route('/donor/request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    req = Request.query.get_or_404(request_id)
    donation = req.donation
    
    # Ensure user owns the donation
    if donation.donor_id != current_user.id:
        flash('You do not have permission to reject this request.', 'danger')
        return redirect(url_for('donor_dashboard'))
    
    req.status = 'rejected'
    db.session.commit()
    flash('Request rejected.', 'info')
    return redirect(url_for('view_donation_requests', donation_id=donation.id))

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
                # Create a request instead of directly updating donation status
                donation_request = Request(
                    donor_id=current_user.id,
                    donation_id=int(donation_id),
                    status='pending'
                )
                db.session.add(donation_request)
                db.session.commit()
                flash("Request submitted! Waiting for donor approval.", 'success')
            else:
                flash("Donation is not available.", 'warning')
        return redirect(url_for('recipient_dashboard'))

    return render_template('recipient_dashboard.html', donations=donations)

# View recipient's own requests
@app.route('/recipient/my-requests', methods=['GET'])
@login_required
def my_requests():
    # Get all requests made by this recipient
    requests = Request.query.filter_by(donor_id=current_user.id).all()
    return render_template('my_requests.html', requests=requests)


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
    # Get filter parameters from query string
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status_filter', '').strip()
    
    # Start with all donations ordered by most recent
    query = Donor.query.order_by(Donor.id.desc())
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Apply search filter (search in food type and location)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Donor.foodType.ilike(search_term)) | 
            (Donor.location.ilike(search_term))
        )
    
    all_donations = query.all()
    requested = Donor.query.filter_by(status='requested').all()
    total_available = Donor.query.filter_by(status='available').count()
    return render_template('admin.html', donations=all_donations, requests=requested, total_available=total_available)


@app.route('/admin/donation/<int:donation_id>/requests')
@login_required
@admin_required
def admin_view_donation_requests(donation_id):
    """Admin view: list all requests for a specific donation."""
    donation = Donor.query.get_or_404(donation_id)
    # Load requests for this donation
    requests = Request.query.filter_by(donation_id=donation_id).order_by(Request.created_at.desc()).all()
    return render_template('admin_donation_requests.html', donation=donation, requests=requests)


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