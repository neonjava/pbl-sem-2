# Health Record Management System (PBL Project)

This is a simple Electronic Health Record (EHR) system developed for small clinics or college health centers using Python and MySQL.

## Features
- **Role-Based Access Control**: Separate dashboards for Staff (Admin) and Patients.
- **Admin Dashboard**:
  - Register new patients.
  - Manage visit records (Diagnosis, Prescription).
  - Create login accounts for patients.
- **Patient Dashboard**:
  - View personal medical history and profile.
- **Database Backend**: Uses MySQL for persistent storage.

## Setup Instructions

### 1. Requirements
- Python 3.x
- MySQL Server
- `mysql-connector-python` library

### 2. Configure Database
- Open `config.py` and update your MySQL username and password.
  ```python
  DB_USER = "root"
  DB_PASSWORD = "your_password_here"
  ```

### 3. Initialize Database
Run the following command to create the database and tables:
```bash
python database.py
```

### 4. Run Application
```bash
python app.py
```

## Default Credentials
- **Username**: `admin`
- **Password**: `REDACTED_PASSWORD`

## Project Structure
- `app.py`: The GUI application (Tkinter).
- `models.py`: Data management logic.
- `database.py`: Database connection helper.
- `auth.py`: Authentication logic.
- `config.py`: Database settings.
- `schema.sql`: SQL structure script.
