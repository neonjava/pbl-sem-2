from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import db, User, Donor, Donation, Badge
from services.eligibility import check_eligibility

donor = Blueprint('donor', __name__, url_prefix='/donor')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@donor.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    donor_profile = Donor.query.filter_by(user_id=user.id).first()
    donations = Donation.query.filter_by(donor_id=donor_profile.id).order_by(Donation.date.desc()).limit(5).all() if donor_profile else []
    badges = Badge.query.filter_by(donor_id=donor_profile.id).all() if donor_profile else []
    eligible, reason = check_eligibility(donor_profile) if donor_profile else (False, 'Profile incomplete')
    return render_template(
        'donor/dashboard.html',
        user=user,
        donor=donor_profile,
        donations=donations,
        badges=badges,
        eligible=eligible,
        eligibility_reason=reason
    )


@donor.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    donor_profile = Donor.query.filter_by(user_id=user.id).first()

    if request.method == 'POST':
        user.name = request.form.get('name', user.name)
        user.phone = request.form.get('phone', user.phone)

        if donor_profile:
            donor_profile.blood_group = request.form.get('blood_group', donor_profile.blood_group)
            donor_profile.age = request.form.get('age', donor_profile.age)
            donor_profile.weight = request.form.get('weight', donor_profile.weight)
            donor_profile.city = request.form.get('city', donor_profile.city)
            donor_profile.available = bool(request.form.get('available'))
        else:
            donor_profile = Donor(
                user_id=user.id,
                blood_group=request.form.get('blood_group'),
                age=request.form.get('age'),
                weight=request.form.get('weight'),
                city=request.form.get('city'),
                available=bool(request.form.get('available'))
            )
            db.session.add(donor_profile)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('donor.profile'))

    return render_template('donor/profile.html', user=user, donor=donor_profile)


@donor.route('/donations')
@login_required
def donations():
    user = User.query.get(session['user_id'])
    donor_profile = Donor.query.filter_by(user_id=user.id).first()
    all_donations = []
    if donor_profile:
        all_donations = Donation.query.filter_by(donor_id=donor_profile.id).order_by(Donation.date.desc()).all()
    return render_template('donor/donations.html', user=user, donor=donor_profile, donations=all_donations)
