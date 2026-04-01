from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
from models import db, User, Donor, Recipient, Hospital, BloodStock, BloodRequest, SOSAlert, SOSResponse, Donation, Badge, DonationCamp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app) # Error here: should be init_app
    
    bcrypt = Bcrypt(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Blueprint registration with separate try-excepts for modularity
        try:
            from blueprints.auth import auth as auth_bp
            app.register_blueprint(auth_bp, url_prefix='/auth')
        except ImportError: pass

        try:
            from blueprints.donor import donor as donor_bp
            app.register_blueprint(donor_bp, url_prefix='/donor')
        except ImportError: pass

        try:
            from blueprints.hospital import hospital as hospital_bp
            app.register_blueprint(hospital_bp, url_prefix='/hospital')
        except ImportError: pass

        try:
            from blueprints.recipient import recipient as recipient_bp
            app.register_blueprint(recipient_bp, url_prefix='/recipient')
        except ImportError: pass

        try:
            from blueprints.public import public as public_bp
            app.register_blueprint(public_bp)
        except ImportError: pass

        try:
            from blueprints.sos import sos as sos_bp
            app.register_blueprint(sos_bp, url_prefix='/sos')
        except ImportError: pass

        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
