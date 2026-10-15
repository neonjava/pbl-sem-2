import os

USE_MYSQL = os.getenv("USE_MYSQL", "false").lower() == "true"
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", ""),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "lifesaver_db"),
}
SQLITE_DB = os.getenv("SQLITE_DB", "donor_data_fallback.db")
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
