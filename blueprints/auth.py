from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Donor

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'donor')
        blood_group = request.form.get('blood_group')
        phone = request.form.get('phone')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_pw, role=role, phone=phone)
        db.session.add(user)
        db.session.commit()

        if role == 'donor':
            donor = Donor(user_id=user.id, blood_group=blood_group)
            db.session.add(donor)
            db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.name

        flash(f'Welcome back, {user.name}!', 'success')

        if user.role == 'donor':
            return redirect(url_for('donor.dashboard'))
        elif user.role == 'hospital':
            return redirect(url_for('hospital.dashboard'))
        elif user.role == 'recipient':
            return redirect(url_for('recipient.dashboard'))
        else:
            return redirect(url_for('public.home'))

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
