from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from mysql.connector import Error
import sqlite3
import os
from datetime import datetime, timedelta, date
import secrets
from matcher import find_matches

# Import Configuration from local config.py
try:
    from config import MYSQL_CONFIG, USE_MYSQL, SQLITE_DB, SECRET_KEY
except ImportError:
    USE_MYSQL = False
    SQLITE_DB = "donor_data_fallback.db"
    SECRET_KEY = "fallback_secret"
    MYSQL_CONFIG = {}

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    if USE_MYSQL:
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn
        except Error as e:
            print(f"MySQL Error: {e}")
            return None
    else:
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    if USE_MYSQL:
        try:
            conn = mysql.connector.connect(
                host=MYSQL_CONFIG['host'],
                user=MYSQL_CONFIG['user'],
                password=MYSQL_CONFIG['password']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']}")
            conn.close()

            conn = get_db()
            if not conn: return
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS sos_requests")
            cursor.execute("DROP TABLE IF EXISTS blood_stock")
            cursor.execute("DROP TABLE IF EXISTS hospitals")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute('''CREATE TABLE users 
                         (id INT AUTO_INCREMENT PRIMARY KEY, 
                          username VARCHAR(50) UNIQUE, 
                          password VARCHAR(100), 
                          donor_temp_id VARCHAR(50), 
                          full_name VARCHAR(100),
                          phone VARCHAR(20),
                          city VARCHAR(50),
                          area VARCHAR(50),
                          blood_type VARCHAR(10),
                          donations_count INT DEFAULT 0,
                          lives_saved INT DEFAULT 0,
                          last_donation DATE,
                          health_status VARCHAR(50),
                          is_available TINYINT(1) DEFAULT 1,
                          reg_date DATE,
                          role VARCHAR(20) DEFAULT 'donor')''')

            cursor.execute('''CREATE TABLE hospitals
                         (id INT AUTO_INCREMENT PRIMARY KEY,
                          hospital_name VARCHAR(120),
                          username VARCHAR(50) UNIQUE,
                          password VARCHAR(100),
                          city VARCHAR(50),
                          contact VARCHAR(20),
                          hospital_id VARCHAR(30) UNIQUE,
                          reg_date DATE)''')

            cursor.execute('''CREATE TABLE blood_stock
                         (id INT AUTO_INCREMENT PRIMARY KEY,
                          hospital_id INT,
                          blood_type VARCHAR(10),
                          units INT DEFAULT 0,
                          last_updated DATETIME,
                          FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE)''')

            cursor.execute('''CREATE TABLE sos_requests
                         (id INT AUTO_INCREMENT PRIMARY KEY,
                          requester_name VARCHAR(100),
                          blood_type VARCHAR(10),
                          units_needed INT,
                          city VARCHAR(50),
                          contact VARCHAR(20),
                          notes VARCHAR(255),
                          status VARCHAR(20),
                          created_at DATETIME)''')

            temp_id = "TEST-ID-888"
            cursor.execute("""INSERT INTO users 
                         (username, password, donor_temp_id, full_name, phone, city, area, blood_type, donations_count, lives_saved, last_donation, health_status, reg_date, role) 
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                         ("test id", "pass123", temp_id, "test id", "+91 9900112233", "Davangere", "Karnataka", "O Positive", 5, 15, "2026-03-10", "Healthy", "2026-01-15", "donor"))

            cursor.execute("""INSERT INTO users (username, password, full_name, role) VALUES (%s, %s, %s, %s)""",
                         ("admin", "REDACTED_PASSWORD", "System Administrator", "admin"))

            cursor.execute("""INSERT INTO hospitals
                         (hospital_name, username, password, city, contact, hospital_id, reg_date)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                         ("City Care Hospital", "citycare", "hospital123", "Davangere", "+91 9876543210", "HSP-DC-001", "2026-01-22"))

            cursor.execute("""INSERT INTO hospitals
                         (hospital_name, username, password, city, contact, hospital_id, reg_date)
                         VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                         ("Unity Blood Center", "unityblood", "hospital123", "Bengaluru", "+91 9012345678", "HSP-BLR-002", "2026-02-10"))

            cursor.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated) VALUES (%s, %s, %s, %s)""", (1, "O+", 12, datetime.now()))
            cursor.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated) VALUES (%s, %s, %s, %s)""", (1, "A+", 8, datetime.now()))
            cursor.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated) VALUES (%s, %s, %s, %s)""", (2, "B+", 10, datetime.now()))

            conn.commit()
            conn.close()
            print("Successfully initialized MySQL Database.")
        except Error as e:
            print(f"DATABASE ERROR: {e}")
    else:
        conn = get_db()
        conn.execute("DROP TABLE IF EXISTS sos_requests")
        conn.execute("DROP TABLE IF EXISTS blood_stock")
        conn.execute("DROP TABLE IF EXISTS hospitals")
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute('''CREATE TABLE users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, 
                      donor_temp_id TEXT, full_name TEXT, phone TEXT, city TEXT, area TEXT, 
                      blood_type TEXT, donations_count INTEGER, lives_saved INTEGER, 
                      last_donation TEXT, health_status TEXT, is_available INTEGER, reg_date TEXT, role TEXT)''')

        conn.execute('''CREATE TABLE hospitals
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, hospital_name TEXT, username TEXT UNIQUE,
                      password TEXT, city TEXT, contact TEXT, hospital_id TEXT UNIQUE, reg_date TEXT)''')

        conn.execute('''CREATE TABLE blood_stock
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, hospital_id INTEGER,
                      blood_type TEXT, units INTEGER, last_updated TEXT,
                      FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE)''')

        conn.execute('''CREATE TABLE sos_requests
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, requester_name TEXT, blood_type TEXT,
                      units_needed INTEGER, city TEXT, contact TEXT, notes TEXT, status TEXT, created_at TEXT)''')

        temp_id = "TEST-ID-888"
        conn.execute("INSERT INTO users (username, password, donor_temp_id, full_name, phone, city, area, blood_type, donations_count, lives_saved, last_donation, health_status, is_available, reg_date, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                     ("test id", "pass123", temp_id, "test id", "+91 9900112233", "Davangere", "Karnataka", "O Positive", 5, 15, "2026-03-10", "Healthy", 1, "2026-01-15", "donor"))
        conn.execute("INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
                     ("admin", "REDACTED_PASSWORD", "System Administrator", "admin"))

        conn.execute("""INSERT INTO hospitals (hospital_name, username, password, city, contact, hospital_id, reg_date) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     ("City Care Hospital", "citycare", "hospital123", "Davangere", "+91 9876543210", "HSP-DC-001", "2026-01-22"))
        conn.execute("""INSERT INTO hospitals (hospital_name, username, password, city, contact, hospital_id, reg_date) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     ("Unity Blood Center", "unityblood", "hospital123", "Bengaluru", "+91 9012345678", "HSP-BLR-002", "2026-02-10"))

        conn.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated) VALUES (?, ?, ?, ?)""", (1, "O+", 12, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated) VALUES (?, ?, ?, ?)""", (1, "A+", 8, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated) VALUES (?, ?, ?, ?)""", (2, "B+", 10, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        conn.commit()
        conn.close()
        print("Successfully initialized SQLite Database.")

@app.context_processor
def inject_user():
    user = None
    hospital = None
    if 'user_id' in session:
        conn = get_db()
        if conn:
            if USE_MYSQL:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
            else:
                user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
            conn.close()
    if 'hospital_id' in session:
        conn = get_db()
        if conn:
            if USE_MYSQL:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM hospitals WHERE id = %s", (session['hospital_id'],))
                hospital = cursor.fetchone()
            else:
                hospital = conn.execute("SELECT * FROM hospitals WHERE id = ?", (session['hospital_id'],)).fetchone()
            conn.close()
    return dict(current_user=user, current_hospital=hospital)

@app.route('/')
def index():
    if 'user_id' in session: return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        if conn:
            if USE_MYSQL:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
                user = cursor.fetchone()
            else:
                user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
            conn.close()

            if user:
                session['user_id'] = user['id']
                session['role'] = user['role']
                if user['role'] == 'admin':
                    return redirect('/admin')
                return redirect('/dashboard')
        flash("Login Failed. Check credentials or Database connection.")
    return render_template('login.html')

@app.route('/hospital/login', methods=['GET', 'POST'])
def hospital_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        if conn:
            if USE_MYSQL:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM hospitals WHERE username = %s AND password = %s", (username, password))
                hospital = cursor.fetchone()
            else:
                hospital = conn.execute("SELECT * FROM hospitals WHERE username = ? AND password = ?", (username, password)).fetchone()
            conn.close()

            if hospital:
                session['hospital_id'] = hospital['id']
                session['role'] = 'hospital'
                return redirect('/hospital/dashboard')
        flash("Hospital login failed. Check credentials.")
    return render_template('hospital_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username   = request.form['username']
        password   = request.form['password']
        full_name  = request.form['full_name']
        phone      = "+91 " + request.form['phone']
        city       = request.form['city']
        area       = request.form['area']
        blood_type = request.form['blood_type']

        temp_id = "DNR-" + secrets.token_hex(4).upper()

        conn = get_db()
        if conn:
            try:
                if USE_MYSQL:
                    cursor = conn.cursor()
                    cursor.execute("""INSERT INTO users 
                                 (username, password, donor_temp_id, full_name, phone, city, area, blood_type, reg_date, health_status, is_available) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                 (username, password, temp_id, full_name, phone, city, area, blood_type,
                                  datetime.now().strftime("%Y-%m-%d"), "Healthy", 1))
                else:
                    conn.execute("""INSERT INTO users 
                                 (username, password, donor_temp_id, full_name, phone, city, area, blood_type, reg_date, health_status, is_available) 
                                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                 (username, password, temp_id, full_name, phone, city, area, blood_type,
                                  datetime.now().strftime("%Y-%m-%d"), "Healthy", 1))
                conn.commit()
                conn.close()
                flash(f"Welcome! Your Donor ID is {temp_id}")
                return redirect('/login')
            except Exception as e:
                print(f"Reg Error: {e}")
                flash("Error during registration. Username may already exist.")
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'donor':
        return redirect('/login')

    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
    else:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()

    next_date = "Now"
    last_don = user['last_donation']
    if last_don:
        if isinstance(last_don, str):
            last_don = datetime.strptime(last_don, "%Y-%m-%d")
        elig = last_don + timedelta(days=90)
        comp = datetime.combine(elig, datetime.min.time()) if isinstance(elig, date) and not isinstance(elig, datetime) else elig
        now  = datetime.now().date() if isinstance(elig, date) and not isinstance(elig, datetime) else datetime.now()
        if elig > now:
            next_date = elig.strftime("%d %b %Y")

    return render_template('dashboard.html', user=user, next_date=next_date)

@app.route('/sos', methods=['GET', 'POST'])
def sos_request():
    if request.method == 'POST':
        name       = request.form['requester_name']
        blood_type = request.form['blood_type']
        units      = request.form['units_needed']
        city       = request.form['city']
        contact    = request.form['contact']
        notes      = request.form.get('notes', '').strip()

        conn = get_db()
        if conn:
            if USE_MYSQL:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO sos_requests
                             (requester_name, blood_type, units_needed, city, contact, notes, status, created_at)
                             VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                             (name, blood_type, units, city, contact, notes, "Open", datetime.now()))
            else:
                conn.execute("""INSERT INTO sos_requests
                             (requester_name, blood_type, units_needed, city, contact, notes, status, created_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                             (name, blood_type, units, city, contact, notes, "Open",
                              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()
            flash("Emergency request submitted. Nearby hospitals are notified.")
            return redirect('/sos')
    return render_template('sos.html')

@app.route('/sos_and_match', methods=['POST'])
def sos_and_match():
    name       = request.form['requester_name']
    blood_type = request.form['blood_type']
    units      = request.form['units_needed']
    city       = request.form['city']
    contact    = request.form['contact']
    notes      = request.form.get('notes', '').strip()

    conn = get_db()
    if not conn:
        flash("Database connection failed.")
        return redirect('/sos')

    # 1. Save the SOS request
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO sos_requests
                         (requester_name, blood_type, units_needed, city, contact, notes, status, created_at)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                         (name, blood_type, units, city, contact, notes, "Open", datetime.now()))
    else:
        conn.execute("""INSERT INTO sos_requests
                         (requester_name, blood_type, units_needed, city, contact, notes, status, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (name, blood_type, units, city, contact, notes, "Open",
                          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

    # 2. Fetch all donors, hospitals, stock for matching
    if USE_MYSQL:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role = 'donor'")
        donors = cursor.fetchall()
        cursor.execute("SELECT * FROM hospitals")
        hospitals = cursor.fetchall()
        cursor.execute("SELECT * FROM blood_stock")
        stock = cursor.fetchall()
    else:
        donors    = [dict(r) for r in conn.execute("SELECT * FROM users WHERE role = 'donor'").fetchall()]
        hospitals = [dict(r) for r in conn.execute("SELECT * FROM hospitals").fetchall()]
        stock     = [dict(r) for r in conn.execute("SELECT * FROM blood_stock").fetchall()]

    conn.close()

    # 3. Run matching engine
    result = find_matches(blood_type, city, donors, hospitals, stock)
    return render_template('match_results.html', result=result)

@app.route('/match', methods=['GET', 'POST'])
def match():
    """Standalone match lookup — no SOS saved, just shows results."""
    if request.method == 'GET':
        return render_template('sos.html')

    blood_type = request.form.get('blood_type', '').strip()
    city       = request.form.get('city', '').strip()

    if not blood_type or not city:
        flash("Please fill in Blood Group and City.")
        return redirect('/sos')

    conn = get_db()
    if not conn:
        flash("Database connection failed.")
        return redirect('/sos')

    if USE_MYSQL:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role = 'donor'")
        donors = cursor.fetchall()
        cursor.execute("SELECT * FROM hospitals")
        hospitals = cursor.fetchall()
        cursor.execute("SELECT * FROM blood_stock")
        stock = cursor.fetchall()
    else:
        donors    = [dict(r) for r in conn.execute("SELECT * FROM users WHERE role = 'donor'").fetchall()]
        hospitals = [dict(r) for r in conn.execute("SELECT * FROM hospitals").fetchall()]
        stock     = [dict(r) for r in conn.execute("SELECT * FROM blood_stock").fetchall()]

    conn.close()

    result = find_matches(blood_type, city, donors, hospitals, stock)
    return render_template('match_results.html', result=result)

@app.route('/toggle_availability', methods=['POST'])
def toggle_availability():
    if 'user_id' not in session: return redirect('/login')
    status    = request.form.get('status')
    available = 1 if status == 'Healthy' else 0

    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET health_status = %s, is_available = %s WHERE id = %s",
                       (status, available, session['user_id']))
    else:
        conn.execute("UPDATE users SET health_status = ?, is_available = ? WHERE id = ?",
                     (status, available, session['user_id']))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/hospital/dashboard')
def hospital_dashboard():
    if session.get('role') != 'hospital': return redirect('/hospital/login')
    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM hospitals WHERE id = %s", (session['hospital_id'],))
        hospital = cursor.fetchone()
        cursor.execute("SELECT * FROM blood_stock WHERE hospital_id = %s ORDER BY blood_type", (session['hospital_id'],))
        stock = cursor.fetchall()
        cursor.execute("SELECT * FROM sos_requests ORDER BY created_at DESC")
        sos_list = cursor.fetchall()
    else:
        hospital = conn.execute("SELECT * FROM hospitals WHERE id = ?", (session['hospital_id'],)).fetchone()
        stock    = conn.execute("SELECT * FROM blood_stock WHERE hospital_id = ? ORDER BY blood_type", (session['hospital_id'],)).fetchall()
        sos_list = conn.execute("SELECT * FROM sos_requests ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('hospital_dashboard.html', hospital=hospital, stock=stock, sos_list=sos_list)

@app.route('/hospital/stock/add', methods=['POST'])
def hospital_add_stock():
    if session.get('role') != 'hospital': return redirect('/hospital/login')
    blood_type = request.form['blood_type']
    units      = request.form['units']
    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated)
                       VALUES (%s, %s, %s, %s)""",
                       (session['hospital_id'], blood_type, units, datetime.now()))
    else:
        conn.execute("""INSERT INTO blood_stock (hospital_id, blood_type, units, last_updated)
                     VALUES (?, ?, ?, ?)""",
                     (session['hospital_id'], blood_type, units, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    flash("Blood stock added.")
    return redirect('/hospital/dashboard')

@app.route('/hospital/stock/update/<int:stock_id>', methods=['POST'])
def hospital_update_stock(stock_id):
    if session.get('role') != 'hospital': return redirect('/hospital/login')
    units = request.form['units']
    conn  = get_db()
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("""UPDATE blood_stock SET units = %s, last_updated = %s
                       WHERE id = %s AND hospital_id = %s""",
                       (units, datetime.now(), stock_id, session['hospital_id']))
    else:
        conn.execute("""UPDATE blood_stock SET units = ?, last_updated = ?
                     WHERE id = ? AND hospital_id = ?""",
                     (units, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stock_id, session['hospital_id']))
    conn.commit()
    conn.close()
    flash("Stock updated.")
    return redirect('/hospital/dashboard')

@app.route('/hospital/stock/delete/<int:stock_id>', methods=['POST'])
def hospital_delete_stock(stock_id):
    if session.get('role') != 'hospital': return redirect('/hospital/login')
    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blood_stock WHERE id = %s AND hospital_id = %s",
                       (stock_id, session['hospital_id']))
    else:
        conn.execute("DELETE FROM blood_stock WHERE id = ? AND hospital_id = ?",
                     (stock_id, session['hospital_id']))
    conn.commit()
    conn.close()
    flash("Stock removed.")
    return redirect('/hospital/dashboard')

@app.route('/hospital/sos/delete/<int:req_id>', methods=['POST'])
def hospital_delete_sos(req_id):
    if session.get('role') != 'hospital': return redirect('/hospital/login')
    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sos_requests WHERE id = %s", (req_id,))
    else:
        conn.execute("DELETE FROM sos_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    flash("SOS request cleared.")
    return redirect('/hospital/dashboard')

@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin': return redirect('/login')
    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE role = 'donor'")
        donors = cursor.fetchall()
        cursor.execute("SELECT * FROM sos_requests ORDER BY created_at DESC")
        sos_list = cursor.fetchall()
    else:
        donors   = conn.execute("SELECT * FROM users WHERE role = 'donor'").fetchall()
        sos_list = conn.execute("SELECT * FROM sos_requests ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin_dashboard.html', donors=donors, sos_list=sos_list)

@app.route('/admin/update_donor/<int:donor_id>', methods=['POST'])
def admin_update_donor(donor_id):
    if session.get('role') != 'admin': return redirect('/login')
    lives     = request.form.get('lives_saved')
    donations = request.form.get('donations_count')
    status    = request.form.get('health_status')

    conn = get_db()
    if USE_MYSQL:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET lives_saved = %s, donations_count = %s, health_status = %s WHERE id = %s",
                       (lives, donations, status, donor_id))
    else:
        conn.execute("UPDATE users SET lives_saved = ?, donations_count = ?, health_status = ? WHERE id = ?",
                     (lives, donations, status, donor_id))
    conn.commit()
    conn.close()
    flash("Donor records updated")
    return redirect('/admin')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    port = 5001 if "mysql" in os.path.dirname(os.path.abspath(__file__)).lower() else 5002
    app.run(debug=True, port=port)