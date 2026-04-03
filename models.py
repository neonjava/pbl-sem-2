from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False) # donor, recipient, hospital
    phone = db.Column(db.String(15))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-one links
    donor_profile = db.relationship('Donor', backref='user', uselist=False, lazy=True)
    recipient_profile = db.relationship('Recipient', backref='user', uselist=False, lazy=True)
    hospital_profile = db.relationship('Hospital', backref='user', uselist=False, lazy=True)

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    age = db.Column(db.Integer)
    last_donation_date = db.Column(db.DateTime)
    weight = db.Column(db.Float)
    city = db.Column(db.String(100)) # Added for profile fix
    available = db.Column(db.Boolean, default=True) # Added for profile fix
    status = db.Column(db.String(20), default='Available') # Available, Busy, Pending
    is_eligible = db.Column(db.Boolean, default=True)

    donations = db.relationship('Donation', backref='donor', lazy=True)
    badges = db.relationship('Badge', backref='donor', lazy=True)
    sos_responses = db.relationship('SOSResponse', backref='donor', lazy=True)

class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    
    blood_requests = db.relationship('BloodRequest', backref='recipient', lazy=True)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    
    stock = db.relationship('BloodStock', backref='hospital', lazy=True)
    camps = db.relationship('DonationCamp', backref='hospital', lazy=True)
    sos_alerts = db.relationship('SOSAlert', backref='hospital', lazy=True)

class BloodStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Fulfilled, Canceled
    urgency = db.Column(db.String(20), default='Normal') # Critical, Urgent, Normal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SOSAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient.id')) # Can be hospital or recipient
    blood_group = db.Column(db.String(5), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Active') # Active, Completed, Expired
    urgency = db.Column(db.String(20), default='Critical')
    location = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    responses = db.relationship('SOSResponse', backref='sos_alert', lazy=True)

class SOSResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sos_id = db.Column(db.Integer, db.ForeignKey('sos_alert.id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Accepted, Completed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    camp_id = db.Column(db.Integer, db.ForeignKey('donation_camp.id'))
    units = db.Column(db.Integer, default=1)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Completed') # Scheduled, Completed, Missed

class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False) # Pioneer, Life-Saver, Frequent-Donor
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

class DonationCamp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Upcoming')

    donations = db.relationship('Donation', backref='camp', lazy=True)
