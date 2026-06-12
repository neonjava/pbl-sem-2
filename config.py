# ==========================================
# DATABASE CREDENTIALS - LifeSaver Network
# ==========================================

# Set to True to use MySQL, False to use SQLite Fallback
USE_MYSQL = False 

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'lifesaver_user',
    'password': 'lifesaver_pass',
    'database': 'lifesaver_db'
}

# SQLite Fallback Configuration
SQLITE_DB = "donor_data_minimal.db"

# Flask Secret Key
SECRET_KEY = "lifesaver_mysql_secret_777"
