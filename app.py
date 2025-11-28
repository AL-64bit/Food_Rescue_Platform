from flask import Flask, render_template
from database import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect


# ----------------------
# App + Config (kept here)
# ----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_rescue.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ----------------------
# Extensions init
# ----------------------
db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

# ----------------------
# Import blueprints (must be after db + login_manager init)
# ----------------------
from routes.auth import auth
from routes.donor import donor
from routes.recipient import recipient
from routes.dashboard import dashboard

app.register_blueprint(auth)
app.register_blueprint(donor)
app.register_blueprint(recipient)
app.register_blueprint(dashboard)

# ----------------------
# User loader
# ----------------------
from models.user import User

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

# ----------------------
# Create DB tables if not exist
# ----------------------
with app.app_context():
    db.create_all()

# ----------------------
# Basic routes
# ----------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ----------------------
# Run
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
