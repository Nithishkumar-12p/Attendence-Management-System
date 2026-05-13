-- PostgreSQL Schema for Attendance Management System

-- Drop tables if they exist
DROP TABLE IF EXISTS salaries;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS shifts;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS settings;

-- Users table for authentication
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'supervisor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settings table
CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT
);

-- Shifts table
CREATE TABLE shifts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    working_hours NUMERIC(4,2) NOT NULL DEFAULT 8.0,
    grace_period INTEGER DEFAULT 15,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Employees table
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    basic_salary DECIMAL(10, 2) NOT NULL,
    designation VARCHAR(50),
    joining_date DATE,
    aadhar_number VARCHAR(12) UNIQUE,
    phone_number VARCHAR(15),
    contract_start_date DATE,
    contract_end_date DATE,
    working_hours_per_day NUMERIC(4, 2) DEFAULT 8.0,
    shift_id INTEGER REFERENCES shifts(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance table
CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    status VARCHAR(5) NOT NULL, -- P, A, CL, SL, HD
    in_time TIME,
    out_time TIME,
    is_late BOOLEAN DEFAULT FALSE,
    tools_count INTEGER DEFAULT 0,
    tools_details TEXT,
    remarks TEXT,
    UNIQUE(employee_id, date)
);

-- Salary table
CREATE TABLE salaries (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(employee_id) ON DELETE CASCADE,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    working_days INTEGER DEFAULT 26,
    present_days DECIMAL(4, 1),
    absent_days DECIMAL(4, 1),
    leaves_taken DECIMAL(4, 1),
    deductions DECIMAL(10, 2),
    final_salary DECIMAL(10, 2),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(employee_id, month, year)
);

-- Insert a default supervisor
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'supervisor');

-- Insert initial settings
INSERT INTO settings (key, value, description) VALUES 
('company_name', 'VIDVAT SOLUTIONS', 'Display name of the organization'),
('shift_start_time', '09:00', 'Standard shift entry time (HH:MM)'),
('shift_end_time', '18:00', 'Standard shift exit time (HH:MM)'),
('grace_period', '15', 'Late arrival grace period in minutes'),
('default_working_hours', '8.0', 'Standard daily working hours for payroll');

-- Insert default shift
INSERT INTO shifts (name, start_time, end_time, working_hours, grace_period)
VALUES ('General Shift', '09:00', '18:00', 8.0, 15);
