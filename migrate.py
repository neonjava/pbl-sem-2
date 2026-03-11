from database import Database
import mysql.connector

def migrate():
    db = Database()
    if not db.connect():
        print("Could not connect to database for migration.")
        return

    try:
        # Add status to patients if not exists
        print("Checking patients table...")
        db.execute_query("ALTER TABLE patients ADD COLUMN IF NOT EXISTS status ENUM('Active', 'Inactive') DEFAULT 'Active' AFTER address")
        
        # Add vitals to visits if not exists
        print("Checking visits table...")
        columns_to_add = [
            "ADD COLUMN IF NOT EXISTS blood_pressure VARCHAR(20) AFTER doctor_name",
            "ADD COLUMN IF NOT EXISTS temperature FLOAT AFTER blood_pressure",
            "ADD COLUMN IF NOT EXISTS weight FLOAT AFTER temperature",
            "ADD COLUMN IF NOT EXISTS pulse INT AFTER weight"
        ]
        
        for col in columns_to_add:
            try:
                db.execute_query(f"ALTER TABLE visits {col}")
            except Exception as e:
                # MariaDB/Older MySQL might not support IF NOT EXISTS in ALTER TABLE
                print(f"Column check failed (likely already exists): {e}")

        print("Migration complete.")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
