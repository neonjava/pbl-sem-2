from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, BloodStock, BloodRequest

# The name should match what app.py expects to import: "hospital"
hospital = Blueprint('hospital', __name__, url_prefix='/hospital')

@hospital.route('/dashboard')
@login_required
def dashboard():
    stocks = BloodStock.query.all()
    requests = BloodRequest.query.all()
    return render_template('hospital/dashboard.html', stocks=stocks, requests=requests)

@hospital.route('/stock', methods=['GET', 'POST'])
@login_required
def stock():
    stocks = BloodStock.query.all()

    if request.method == 'POST':
        blood_group = request.form.get('blood_group')
        units = request.form.get('units')

        stock_item = BloodStock.query.filter_by(blood_group=blood_group).first()

        if stock_item:
            try:
                stock_item.units = int(units)
                db.session.commit()
                flash(f'Stock for {blood_group} updated to {units} units.', 'success')
            except (ValueError, TypeError):
                flash('Invalid units provided.', 'danger')
        else:
            flash('Invalid blood group', 'danger')

        return redirect(url_for('hospital.stock'))

    return render_template('hospital/stock.html', stocks=stocks)

@hospital.route('/emergency')
@login_required
def emergency():
    requests = BloodRequest.query.all()
    return render_template('hospital/emergency.html', requests=requests)
