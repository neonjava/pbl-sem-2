import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from auth import Auth
from models import PatientManager, VisitManager

class HealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Record Management System")
        self.root.geometry("1000x700")
        
        # Initialize Database and Auth
        self.db = Database()
        if not self.db.connect():
            messagebox.showerror("Error", "Could not connect to database. Please check your MySQL configuration in config.py.")
            # self.root.destroy()
            
        self.auth = Auth(self.db)
        self.patient_manager = PatientManager(self.db)
        self.visit_manager = VisitManager(self.db)
        from models import AccountManager
        self.account_manager = AccountManager(self.db)
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.main_container = tk.Frame(self.root, bg="#f0f2f5")
        self.main_container.pack(fill="both", expand=True)
        
        self.show_login()

    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()
        
        login_frame = tk.Frame(self.main_container, bg="white", padx=40, pady=40, highlightbackground="#ddd", highlightthickness=1)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(login_frame, text="Clinic Login", font=("Arial", 24, "bold"), bg="white", fg="#1a73e8").pack(pady=(0, 20))
        
        tk.Label(login_frame, text="Username", bg="white").pack(anchor="w")
        self.user_entry = ttk.Entry(login_frame, width=30)
        self.user_entry.pack(pady=(0, 10))
        
        tk.Label(login_frame, text="Password", bg="white").pack(anchor="w")
        self.pass_entry = ttk.Entry(login_frame, width=30, show="*")
        self.pass_entry.pack(pady=(0, 20))
        
        login_btn = tk.Button(login_frame, text="Login", command=self.handle_login, bg="#1a73e8", fg="white", 
                             font=("Arial", 12, "bold"), width=25, relief="flat", cursor="hand2")
        login_btn.pack()
        
        tk.Label(login_frame, text="Default Admin: admin / REDACTED_PASSWORD", font=("Arial", 8), bg="white", fg="#777").pack(pady=(20, 0))

    def handle_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        success, role = self.auth.login(username, password)
        if success:
            if role == 'admin':
                self.show_admin_dashboard()
            else:
                self.show_patient_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def show_admin_dashboard(self):
        self.clear_screen()
        # Header
        header = tk.Frame(self.main_container, bg="#1a73e8", height=60)
        header.pack(fill="x")
        tk.Label(header, text="Clinic Admin Dashboard", fg="white", bg="#1a73e8", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=15)
        
        tk.Button(header, text="Logout", command=self.show_login, bg="#f44336", fg="white", relief="flat", padx=15).pack(side="right", padx=20)

        # Content Area
        content = tk.Frame(self.main_container, bg="#f0f2f5")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sidebar/Tabs
        tab_control = ttk.Notebook(content)
        
        self.tab_patients = ttk.Frame(tab_control)
        self.tab_visits = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_patients, text='Manage Patients')
        tab_control.add(self.tab_visits, text='Visit Records')
        tab_control.pack(expand=1, fill="both")
        
        self.setup_patient_tab()
        self.setup_visit_tab()

    def setup_patient_tab(self):
        # Add Patient Form
        form_frame = ttk.LabelFrame(self.tab_patients, text="Add New Patient", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        labels = ["Name", "Age", "Gender", "Contact", "Address"]
        self.patient_entries = {}
        
        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label).grid(row=0, column=i*2, padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=15)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5)
            self.patient_entries[label] = entry
            
        ttk.Button(form_frame, text="Add Patient", command=self.add_patient).grid(row=0, column=10, padx=10)

        button_frame = tk.Frame(self.tab_patients)
        button_frame.pack(fill="x", padx=10)
        ttk.Button(button_frame, text="Refresh List", command=self.refresh_patient_list).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Create Login for Selected", command=self.create_patient_login).pack(side="left", padx=5)

        # Patient List
        list_frame = tk.Frame(self.tab_patients)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Name", "Age", "Gender", "Contact", "Address")
        self.patient_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.patient_tree.heading(col, text=col)
            self.patient_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.patient_tree.yview)
        self.patient_tree.configure(yscroll=scrollbar.set)
        
        self.patient_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_patient_list()

    def refresh_patient_list(self):
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)
        patients = self.patient_manager.get_all_patients()
        for p in patients:
            self.patient_tree.insert("", "end", values=(p['patient_id'], p['name'], p['age'], p['gender'], p['contact'], p['address']))

    def add_patient(self):
        data = {l: e.get() for l, e in self.patient_entries.items()}
        if not data["Name"]:
            messagebox.showwarning("Input Error", "Name is required")
            return
            
        pid = self.patient_manager.add_patient(data["Name"], data["Age"], data["Gender"], data["Contact"], data["Address"])
        if pid:
            messagebox.showinfo("Success", f"Patient added with ID: {pid}")
            self.refresh_patient_list()
            for e in self.patient_entries.values(): e.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Failed to add patient")

    def create_patient_login(self):
        selected = self.patient_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a patient first")
            return
            
        patient_id = self.patient_tree.item(selected)['values'][0]
        patient_name = self.patient_tree.item(selected)['values'][1]
        
        # Open a small dialog for username/password
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Patient Account")
        dialog.geometry("300x250")
        
        tk.Label(dialog, text=f"Creating account for: {patient_name}").pack(pady=10)
        
        tk.Label(dialog, text="Username").pack()
        u_entry = ttk.Entry(dialog)
        u_entry.pack(pady=5)
        u_entry.insert(0, str(patient_name).lower().replace(" ", ""))
        
        tk.Label(dialog, text="Password").pack()
        p_entry = ttk.Entry(dialog, show="*")
        p_entry.pack(pady=5)
        
        def save():
            uname = u_entry.get()
            upass = p_entry.get()
            if uname and upass:
                res = self.account_manager.create_account(uname, upass, 'patient', patient_id)
                if res:
                    messagebox.showinfo("Success", "Patient account created")
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Username might already exist")
            else:
                messagebox.showwarning("Input", "Both fields required")

        ttk.Button(dialog, text="Create", command=save).pack(pady=20)

    def setup_visit_tab(self):
        # Visit Form
        form_frame = ttk.LabelFrame(self.tab_visits, text="Record New Visit", padding=10)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(form_frame, text="Patient ID").grid(row=0, column=0, padx=5)
        self.visit_pid = ttk.Entry(form_frame, width=10)
        self.visit_pid.grid(row=0, column=1, padx=5)
        
        tk.Label(form_frame, text="Diagnosis").grid(row=1, column=0, padx=5)
        self.visit_diag = tk.Text(form_frame, height=3, width=40)
        self.visit_diag.grid(row=1, column=1, columnspan=3, pady=5)
        
        tk.Label(form_frame, text="Prescription").grid(row=2, column=0, padx=5)
        self.visit_pres = tk.Text(form_frame, height=3, width=40)
        self.visit_pres.grid(row=2, column=1, columnspan=3, pady=5)
        
        from datetime import date
        tk.Label(form_frame, text="Date (YYYY-MM-DD)").grid(row=0, column=2, padx=5)
        self.visit_date = ttk.Entry(form_frame)
        self.visit_date.insert(0, date.today().isoformat())
        self.visit_date.grid(row=0, column=3, padx=5)
        
        ttk.Button(form_frame, text="Save Visit", command=self.add_visit).grid(row=2, column=4, padx=10)

        # Visit History List
        list_frame = tk.Frame(self.tab_visits)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("Visit ID", "Patient", "Date", "Diagnosis", "Prescription")
        self.visit_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        for col in columns:
            self.visit_tree.heading(col, text=col)
        
        self.visit_tree.pack(fill="both", expand=True)

    def add_visit(self):
        # Implementation for adding visit
        pid = self.visit_pid.get()
        diag = self.visit_diag.get("1.0", tk.END).strip()
        pres = self.visit_pres.get("1.0", tk.END).strip()
        vdate = self.visit_date.get()
        
        if not pid or not diag:
            messagebox.showwarning("Input Error", "Patient ID and Diagnosis are required")
            return
            
        vid = self.visit_manager.add_visit(pid, vdate, diag, pres, "Dr. Admin")
        if vid:
            messagebox.showinfo("Success", "Visit record saved")
            # Clear fields
            self.visit_pid.delete(0, tk.END)
            self.visit_diag.delete("1.0", tk.END)
            self.visit_pres.delete("1.0", tk.END)
        else:
            messagebox.showerror("Error", "Failed to save visit. Check Patient ID.")

    def show_patient_dashboard(self):
        self.clear_screen()
        # Header
        header = tk.Frame(self.main_container, bg="#4caf50", height=60)
        header.pack(fill="x")
        user = self.auth.get_current_user()
        tk.Label(header, text=f"Patient Portal: {user['username']}", fg="white", bg="#4caf50", font=("Arial", 16, "bold")).pack(side="left", padx=20, pady=15)
        
        tk.Button(header, text="Logout", command=self.show_login, bg="#f44336", fg="white", relief="flat", padx=15).pack(side="right", padx=20)

        content = tk.Frame(self.main_container, bg="white", padx=30, pady=30)
        content.pack(fill="both", expand=True)

        # Fetch patient details
        patient_data = self.patient_manager.get_patient(user['patient_id'])
        if patient_data:
            tk.Label(content, text="Your Profile", font=("Arial", 18, "bold"), bg="white").pack(anchor="w")
            details = f"Name: {patient_data['name']}\nAge: {patient_data['age']}\nGender: {patient_data['gender']}\nContact: {patient_data['contact']}"
            tk.Label(content, text=details, justify="left", bg="white", font=("Arial", 12)).pack(anchor="w", pady=10)
            
            tk.Label(content, text="Visit History", font=("Arial", 18, "bold"), bg="white").pack(anchor="w", pady=(20, 10))
            
            # Show history
            history = self.visit_manager.get_patient_history(user['patient_id'])
            for h in history:
                h_frame = tk.Frame(content, bg="#f9f9f9", pady=5, padx=10, highlightbackground="#eee", highlightthickness=1)
                h_frame.pack(fill="x", pady=5)
                tk.Label(h_frame, text=f"Date: {h['visit_date']} | Doctor: {h['doctor_name']}", font=("Arial", 10, "bold"), bg="#f9f9f9").pack(anchor="w")
                tk.Label(h_frame, text=f"Diagnosis: {h['diagnosis']}", bg="#f9f9f9").pack(anchor="w")
                tk.Label(h_frame, text=f"Prescription: {h['prescription']}", bg="#f9f9f9", fg="#555").pack(anchor="w")
        else:
            tk.Label(content, text="No patient profile linked to this account.", fg="red").pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthApp(root)
    root.mainloop()
