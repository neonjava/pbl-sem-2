CREATE DATABASE IF NOT EXISTS health_record_db;
USE health_record_db;

-- Patients Table
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender ENUM('Male', 'Female', 'Other'),
    contact VARCHAR(15),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users Table (for Authentication)
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'patient') NOT NULL,
    patient_id INT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Visit Records Table
CREATE TABLE IF NOT EXISTS visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    visit_date DATE NOT NULL,
    diagnosis TEXT,
    prescription TEXT,
    doctor_name VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- Seed an initial admin user
-- Password is 'REDACTED_PASSWORD' (simplified for now, ideally hashed)
INSERT IGNORE INTO users (username, password, role) VALUES ('admin', 'REDACTED_PASSWORD', 'admin');
