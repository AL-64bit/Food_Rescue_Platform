from app import app, db
from models.user import User

with app.app_context():
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", role="admin")
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created (username=admin, password=adminpass)")
    else:
        print("Admin already exists")
