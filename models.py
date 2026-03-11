class PatientManager:
    def __init__(self, db):
        self.db = db

    def add_patient(self, name, age, gender, contact, address):
        query = "INSERT INTO patients (name, age, gender, contact, address) VALUES (%s, %s, %s, %s, %s)"
        return self.db.execute_query(query, (name, age, gender, contact, address))

    def get_patient(self, patient_id):
        return self.db.fetch_one("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))

    def get_all_patients(self):
        return self.db.fetch_all("SELECT * FROM patients")

    def search_patients(self, search_term):
        query = "SELECT * FROM patients WHERE name LIKE %s OR patient_id = %s"
        # Try to see if search_term is numeric for ID search
        patient_id = -1
        if search_term.isdigit():
            patient_id = int(search_term)
        return self.db.fetch_all(query, (f"%{search_term}%", patient_id))

class VisitManager:
    def __init__(self, db):
        self.db = db

    def add_visit(self, patient_id, visit_date, diagnosis, prescription, doctor_name):
        query = "INSERT INTO visits (patient_id, visit_date, diagnosis, prescription, doctor_name) VALUES (%s, %s, %s, %s, %s)"
        return self.db.execute_query(query, (patient_id, visit_date, diagnosis, prescription, doctor_name))

    def get_patient_history(self, patient_id):
        query = "SELECT * FROM visits WHERE patient_id = %s ORDER BY visit_date DESC"
        return self.db.fetch_all(query, (patient_id,))

class AccountManager:
    def __init__(self, db):
        self.db = db

    def create_account(self, username, password, role, patient_id=None):
        query = "INSERT INTO users (username, password, role, patient_id) VALUES (%s, %s, %s, %s)"
        return self.db.execute_query(query, (username, password, role, patient_id))
