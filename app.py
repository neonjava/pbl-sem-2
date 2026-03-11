import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from database import Database
from auth import Auth
from models import PatientManager, VisitManager, AccountManager
from datetime import date

# Set appearance mode and color theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class HealthApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Clinic Management - Record System")
        self.geometry("1100x700")

        # Initialize Database and Auth
        self.db = Database()
        if not self.db.connect():
            messagebox.showerror("Error", "Could not connect to database. Check config.py.")
            
        self.auth = Auth(self.db)
        self.patient_manager = PatientManager(self.db)
        self.visit_manager = VisitManager(self.db)
        self.account_manager = AccountManager(self.db)

        # Main Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.show_login()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=1)
        
        login_frame = ctk.CTkFrame(self, width=400, height=500, corner_radius=15)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(login_frame, text="Clinic Management", font=ctk.CTkFont(size=30, weight="bold"), text_color="#1a73e8").pack(pady=(40, 5))
        ctk.CTkLabel(login_frame, text="Clinic Management System", font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        self.user_entry = ctk.CTkEntry(login_frame, width=300, height=45, placeholder_text="Username")
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(login_frame, width=300, height=45, placeholder_text="Password", show="*")
        self.pass_entry.pack(pady=10)

        ctk.CTkButton(login_frame, text="Login", command=self.handle_login, width=300, height=45, font=ctk.CTkFont(weight="bold")).pack(pady=30)
        
        ctk.CTkLabel(login_frame, text="Default Admin: admin / REDACTED_PASSWORD", font=ctk.CTkFont(size=11), text_color="gray").pack()

    def handle_login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        
        success, role = self.auth.login(username, password)
        if success:
            self.setup_main_ui(role)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def setup_main_ui(self, role):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="HealthFlow", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)

        self.nav_btns = []
        if role == 'admin':
            self.btn_dash = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
            self.btn_dash.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
            
            self.btn_patients = ctk.CTkButton(self.sidebar_frame, text="Patients", command=self.show_patients_view, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
            self.btn_patients.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

            self.btn_visits = ctk.CTkButton(self.sidebar_frame, text="Record Visit", command=self.show_visits_view, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
            self.btn_visits.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        else:
            self.btn_profile = ctk.CTkButton(self.sidebar_frame, text="My Profile", command=self.show_patient_dashboard, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w")
            self.btn_profile.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkButton(self.sidebar_frame, text="Logout", command=self.show_login, fg_color="#f44336", hover_color="#d32f2f").grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        # Main Content
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        if role == 'admin': self.show_dashboard()
        else: self.show_patient_dashboard()

    def show_dashboard(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        
        stats = self.patient_manager.get_stats()
        
        ctk.CTkLabel(self.content_frame, text="Clinic Overview", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)
        
        # Stat Cards
        self.create_stat_card(stats_frame, "Total Patients", str(stats['total_patients']), "#1a73e8").grid(row=0, column=0, padx=(0, 20))
        self.create_stat_card(stats_frame, "Visits Today", str(stats['today_visits']), "#34a853").grid(row=0, column=1, padx=20)
        
        # Recent Patients table placeholder or search
        ctk.CTkLabel(self.content_frame, text="Quick Actions", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(30, 10))
        actions_frame = ctk.CTkFrame(self.content_frame)
        actions_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(actions_frame, text="Register New Patient", command=self.show_patients_view).pack(side="left", padx=20, pady=20)
        ctk.CTkButton(actions_frame, text="Add Visit Record", command=self.show_visits_view, fg_color="#34a853", hover_color="#2d8e47").pack(side="left", padx=20, pady=20)

    def create_stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, width=200, height=120, corner_radius=10, border_width=2, border_color=color)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color).pack()
        return card

    def show_patients_view(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(self.content_frame, text="Patient Management", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        # Top tools
        tool_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        tool_frame.pack(fill="x", pady=10)
        
        self.search_entry = ctk.CTkEntry(tool_frame, placeholder_text="Search by Name or ID...", width=300)
        self.search_entry.pack(side="left", padx=(0, 10))
        ctk.CTkButton(tool_frame, text="Search", width=100, command=self.handle_search).pack(side="left")
        ctk.CTkButton(tool_frame, text="+ Add Patient", width=120, fg_color="#34a853", hover_color="#2d8e47", command=self.open_patient_dialog).pack(side="right")

        # Results Table (Using a scrollable frame for list)
        self.table_container = ctk.CTkScrollableFrame(self.content_frame, height=400)
        self.table_container.pack(fill="both", expand=True, pady=10)
        
        self.refresh_patient_list()

    def refresh_patient_list(self, patients=None):
        for widget in self.table_container.winfo_children(): widget.destroy()
        
        # Header
        h_frame = ctk.CTkFrame(self.table_container, fg_color="gray80", height=40)
        h_frame.pack(fill="x", pady=2)
        headers = ["ID", "Name", "Age", "Contact", "Actions"]
        widths = [50, 200, 80, 150, 250]
        
        for i, h in enumerate(headers):
            ctk.CTkLabel(h_frame, text=h, width=widths[i], font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)

        if patients is None:
            patients = self.patient_manager.get_all_patients()
            
        for p in patients:
            row = ctk.CTkFrame(self.table_container, height=45)
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(row, text=str(p['patient_id']), width=50).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=p['name'], width=200, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(p['age']), width=80).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=p['contact'], width=150).pack(side="left", padx=5)
            
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="right", padx=5)
            
            ctk.CTkButton(btn_frame, text="History", width=70, height=25, command=lambda pid=p['patient_id']: self.view_history(pid)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="Auth", width=60, height=25, fg_color="purple", command=lambda p=p: self.create_patient_login(p)).pack(side="left", padx=2)
            ctk.CTkButton(btn_frame, text="Del", width=50, height=25, fg_color="#f44336", hover_color="#d32f2f", command=lambda pid=p['patient_id']: self.handle_delete_patient(pid)).pack(side="left", padx=2)

    def handle_search(self):
        term = self.search_entry.get()
        if term:
            results = self.patient_manager.search_patients(term)
            self.refresh_patient_list(results)
        else:
            self.refresh_patient_list()

    def open_patient_dialog(self, patient=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Patient Information")
        dialog.geometry("400x500")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Register Patient", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        name_e = ctk.CTkEntry(dialog, placeholder_text="Full Name", width=300)
        name_e.pack(pady=10)
        
        age_e = ctk.CTkEntry(dialog, placeholder_text="Age", width=300)
        age_e.pack(pady=10)

        gender_v = ctk.StringVar(value="Male")
        gender_f = ctk.CTkFrame(dialog, fg_color="transparent")
        gender_f.pack(pady=10)
        ctk.CTkRadioButton(gender_f, text="Male", variable=gender_v, value="Male").pack(side="left", padx=10)
        ctk.CTkRadioButton(gender_f, text="Female", variable=gender_v, value="Female").pack(side="left", padx=10)

        contact_e = ctk.CTkEntry(dialog, placeholder_text="Contact Number", width=300)
        contact_e.pack(pady=10)

        addr_e = ctk.CTkEntry(dialog, placeholder_text="Address", width=300)
        addr_e.pack(pady=10)

        def save():
            pid = self.patient_manager.add_patient(name_e.get(), age_e.get(), gender_v.get(), contact_e.get(), addr_e.get())
            if pid:
                messagebox.showinfo("Success", "Patient Registered Successfully")
                dialog.destroy()
                self.refresh_patient_list()
        
        ctk.CTkButton(dialog, text="Save Patient", command=save, width=300).pack(pady=30)

    def show_visits_view(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        
        ctk.CTkLabel(self.content_frame, text="Record Medical Visit", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        form = ctk.CTkFrame(self.content_frame, corner_radius=15, padding=20)
        form.pack(fill="both", expand=True)

        # Left Side: Info
        left_p = ctk.CTkFrame(form, fg_color="transparent")
        left_p.pack(side="left", fill="both", expand=True, padx=20)

        ctk.CTkLabel(left_p, text="Patient ID").pack(anchor="w")
        pid_e = ctk.CTkEntry(left_p, width=200)
        pid_e.pack(pady=(0, 15), anchor="w")

        ctk.CTkLabel(left_p, text="Vitals (BP, Temp, Weight, Pulse)").pack(anchor="w")
        vitals_f = ctk.CTkFrame(left_p, fg_color="transparent")
        vitals_f.pack(fill="x", pady=(0, 15))
        bp_e = ctk.CTkEntry(vitals_f, placeholder_text="BP (120/80)", width=100)
        bp_e.pack(side="left", padx=(0, 5))
        temp_e = ctk.CTkEntry(vitals_f, placeholder_text="Temp (°C)", width=80)
        temp_e.pack(side="left", padx=5)
        weight_e = ctk.CTkEntry(vitals_f, placeholder_text="Wt (kg)", width=80)
        weight_e.pack(side="left", padx=5)
        pulse_e = ctk.CTkEntry(vitals_f, placeholder_text="Pulse", width=80)
        pulse_e.pack(side="left", padx=5)

        ctk.CTkLabel(left_p, text="Diagnosis").pack(anchor="w")
        diag_e = ctk.CTkTextbox(left_p, height=80)
        diag_e.pack(fill="x", pady=(0, 15))

        # Right Side: Prescription
        right_p = ctk.CTkFrame(form, fg_color="transparent")
        right_p.pack(side="left", fill="both", expand=True, padx=20)

        ctk.CTkLabel(right_p, text="Prescription / Treatment Plan").pack(anchor="w")
        pres_e = ctk.CTkTextbox(right_p, height=200)
        pres_e.pack(fill="x", pady=(0, 15))

        def save_visit():
            # Basic validation
            p_id = pid_e.get()
            if not p_id:
                messagebox.showwarning("Input Error", "Patient ID is required")
                return

            # Safe conversion for vitals
            try:
                temp = float(temp_e.get()) if temp_e.get() else 0.0
                weight = float(weight_e.get()) if weight_e.get() else 0.0
                pulse = int(pulse_e.get()) if pulse_e.get() else 0
            except ValueError:
                messagebox.showwarning("Input Error", "Temperature, Weight, and Pulse must be numbers")
                return

            vid = self.visit_manager.add_visit(
                p_id, date.today().isoformat(), diag_e.get("1.0", tk.END).strip(),
                pres_e.get("1.0", tk.END).strip(), "Dr. Admin",
                bp_e.get(), temp, weight, pulse
            )
            if vid:
                messagebox.showinfo("Success", "Visit Record Saved")
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Check Patient ID and Input")

        ctk.CTkButton(form, text="Complete & Save Visit Record", command=save_visit, height=50, font=ctk.CTkFont(weight="bold")).pack(side="bottom", fill="x", padx=20, pady=20)

    def show_patient_dashboard(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()
        user = self.auth.get_current_user()
        patient = self.patient_manager.get_patient(user['patient_id'])
        
        ctk.CTkLabel(self.content_frame, text=f"Welcome, {patient['name']}", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", pady=(0, 20))
        
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", pady=10)
        
        details = f"Patient ID: {patient['patient_id']} | Contact: {patient['contact']} | Age: {patient['age']} | Gender: {patient['gender']}"
        ctk.CTkLabel(info_frame, text=details, font=ctk.CTkFont(size=14)).pack(padx=20, pady=20)

        ctk.CTkLabel(self.content_frame, text="My Medical History", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(20, 10))
        
        history_scroll = ctk.CTkScrollableFrame(self.content_frame, height=400)
        history_scroll.pack(fill="both", expand=True)

        history = self.visit_manager.get_patient_history(user['patient_id'])
        for h in history:
            card = ctk.CTkFrame(history_scroll, corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            
            top = ctk.CTkFrame(card, fg_color="gray90")
            top.pack(fill="x")
            ctk.CTkLabel(top, text=f"Date: {h['visit_date']} | Doctor: {h['doctor_name']}", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            
            vitals = f"Vitals: BP {h['blood_pressure']} | Temp {h['temperature']}°C | Wt {h['weight']}kg | Pulse {h['pulse']}"
            ctk.CTkLabel(card, text=vitals, text_color="#1a73e8").pack(anchor="w", padx=10, pady=5)
            
            ctk.CTkLabel(card, text=f"Diagnosis: {h['diagnosis']}", wraplength=700, justify="left").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Prescription: {h['prescription']}", text_color="gray", wraplength=700, justify="left").pack(anchor="w", padx=10, pady=(0, 10))

    def create_patient_login(self, patient):
        # reuse previous logic but with ctk components
        dialog = ctk.CTkToplevel(self)
        dialog.title("Account Management")
        dialog.geometry("350x400")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=f"Account for: {patient['name']}", font=ctk.CTkFont(weight="bold")).pack(pady=20)
        
        u_entry = ctk.CTkEntry(dialog, placeholder_text="Username", width=250)
        u_entry.pack(pady=10)
        u_entry.insert(0, str(patient['name']).lower().replace(" ", ""))
        
        p_entry = ctk.CTkEntry(dialog, placeholder_text="Password", show="*", width=250)
        p_entry.pack(pady=10)
        
        def save():
            if self.account_manager.create_account(u_entry.get(), p_entry.get(), 'patient', patient['patient_id']):
                messagebox.showinfo("Success", "Account Created")
                dialog.destroy()
            else: messagebox.showerror("Error", "Failed. Username taken?")
            
        ctk.CTkButton(dialog, text="Create Portal Access", command=save, width=250).pack(pady=30)

    def view_history(self, pid):
        dialog = ctk.CTkToplevel(self)
        dialog.title("History Viewer")
        dialog.geometry("600x600")
        dialog.attributes("-topmost", True)
        
        scroll = ctk.CTkScrollableFrame(dialog)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        history = self.visit_manager.get_patient_history(pid)
        for h in history:
            card = ctk.CTkFrame(scroll)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=f"{h['visit_date']} - {h['diagnosis']}", font=ctk.CTkFont(weight="bold")).pack(padx=10, pady=5)
            ctk.CTkLabel(card, text=h['prescription'], text_color="gray").pack(padx=10, pady=5)

    def handle_delete_patient(self, pid):
        if messagebox.askyesno("Confirm", "Are you sure you want to deactivate this patient record?"):
            if self.patient_manager.delete_patient(pid):
                self.refresh_patient_list()

if __name__ == "__main__":
    app = HealthApp()
    app.mainloop()
