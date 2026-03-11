class PatientManager:
    def __init__(self, db):
        self.db = db

    def add_patient(self, name, age, gender, contact, address):
        query = "INSERT INTO patients (name, age, gender, contact, address) VALUES (%s, %s, %s, %s, %s)"
        return self.db.execute_query(query, (name, age, gender, contact, address))

    def update_patient(self, patient_id, name, age, gender, contact, address, status='Active'):
        query = "UPDATE patients SET name=%s, age=%s, gender=%s, contact=%s, address=%s, status=%s WHERE patient_id=%s"
        return self.db.execute_query(query, (name, age, gender, contact, address, status, patient_id))

    def delete_patient(self, patient_id):
        # We'll use soft delete by setting status to Inactive
        query = "UPDATE patients SET status='Inactive' WHERE patient_id=%s"
        return self.db.execute_query(query, (patient_id,))

    def get_patient(self, patient_id):
        return self.db.fetch_one("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))

    def get_all_patients(self, include_inactive=False):
        if include_inactive:
            return self.db.fetch_all("SELECT * FROM patients")
        return self.db.fetch_all("SELECT * FROM patients WHERE status = 'Active'")

    def search_patients(self, search_term):
        query = "SELECT * FROM patients WHERE (name LIKE %s OR contact LIKE %s OR patient_id = %s) AND status = 'Active'"
        patient_id = -1
        if search_term.isdigit():
            patient_id = int(search_term)
        return self.db.fetch_all(query, (f"%{search_term}%", f"%{search_term}%", patient_id))

    def get_stats(self):
        total = self.db.fetch_one("SELECT COUNT(*) as count FROM patients WHERE status='Active'")
        visits = self.db.fetch_one("SELECT COUNT(*) as count FROM visits WHERE visit_date = CURDATE()")
        return {
            'total_patients': total['count'] if total else 0,
            'today_visits': visits['count'] if visits else 0
        }

class VisitManager:
    def __init__(self, db):
        self.db = db

    def add_visit(self, patient_id, visit_date, diagnosis, prescription, doctor_name, bp="", temp=0, weight=0, pulse=0):
        query = """INSERT INTO visits (patient_id, visit_date, diagnosis, prescription, doctor_name, 
                   blood_pressure, temperature, weight, pulse) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        return self.db.execute_query(query, (patient_id, visit_date, diagnosis, prescription, doctor_name, bp, temp, weight, pulse))

    def get_patient_history(self, patient_id):
        query = "SELECT * FROM visits WHERE patient_id = %s ORDER BY visit_date DESC"
        return self.db.fetch_all(query, (patient_id,))

    def delete_visit(self, visit_id):
        return self.db.execute_query("DELETE FROM visits WHERE visit_id = %s", (visit_id,))

class AccountManager:
    def __init__(self, db):
        self.db = db

    def create_account(self, username, password, role, patient_id=None):
        query = "INSERT INTO users (username, password, role, patient_id) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(query, (username, password, role, patient_id))
