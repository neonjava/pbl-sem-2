from database import Database

class Auth:
    def __init__(self, db):
        self.db = db
        self.current_user = None

    def login(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        user = self.db.fetch_one(query, (username, password))
        if user:
            self.current_user = user
            return True, user['role']
        return False, None

    def logout(self):
        self.current_user = None

    def get_current_user(self):
        return self.current_user
