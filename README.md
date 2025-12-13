# MediCore Hospital Management System

A lightweight, modern Hospital Management System built with **Flask** (Python) and **Tailwind CSS**.

---

## ✨ Features

### 🏥 Patient Management
- **Search**: Real-time search by Name, Chart Number, or Phone
- **CRUD**: Create, Read, Update, Delete patient records
- **Validation**: Strict phone number validation (10-15 digits)
- **Registration Date**: Track when patients were registered
- **Status Tracking**: Visual badges for patient status (Active/Inactive)

### 📅 Appointment Scheduling
- **Visual Calendar**: Interactive provider schedule with time slots
- **Date Navigation**: Arrow buttons (`<` `>`) to navigate between days
- **Calendar Picker**: Click the date to open a calendar picker
- **Conflict Detection**: Prevents double-booking with alert banners
- **Status Updates**: Mark appointments as Completed, Canceled (with reason), or Scheduled
- **Visit Types**: Track Consults, Checkups, Follow-ups, Lab Work, etc.

### 💰 Billing & Invoicing
- **Line Items**: Create detailed invoices with multiple items
- **Auto-Calculation**: Automatic totaling of quantity × unit price
- **Payments**: Record partial or full payments
- **Status Tracking**: OPEN, PARTIAL, PAID status badges

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** — [Download Python](https://www.python.org/downloads/)
- **Git** — [Download Git](https://git-scm.com/downloads)

### Step 1: Clone the Repository

```bash
git clone https://github.com/MatthewKuilan/hospital_mvp.git
cd hospital_mvp
```

### Step 2: Set Up Virtual Environment (Recommended)

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python3 app.py
```

You should see:
```
Database URI: sqlite:///...hms.db
* Serving Flask app 'app'
* Running on http://127.0.0.1:8000
```

### Step 5: Open in Browser

Navigate to: **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `staff1` | `Pass123` | Admin |

*Other providers (Dr. Sarah Johnson, Dr. Michael Chen, Dr. Emily Rodriguez) also use `Pass123`*

---

## 📋 Quick Start Guide

1. **Login** with `staff1` / `Pass123`
2. **Dashboard**: View daily stats and recent activity
3. **Patients**: Add and manage patient records
4. **Appointments**: Schedule and manage appointments
5. **Billing**: Create invoices and track payments

---

## 🗄️ Database

- **Type**: SQLite (file-based, no setup required)
- **Location**: `hms.db` in project root
- **Auto-Setup**: Database is created automatically on first run

### Reset Database

To wipe all data and restore sample data:
- Visit: `http://127.0.0.1:8000/reset-db`
- Or delete `hms.db` and restart the server

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Mac/Linux
lsof -ti:8000 | xargs kill -9

# Then restart
python3 app.py
```

### Python Command Not Found
- Use `python3` instead of `python` on Mac/Linux
- Ensure Python is added to PATH

### Changes Not Showing
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows/Linux)
- Restart the Flask server

---

## 📁 Project Structure

```
hospital_mvp/
├── app.py              # Main Flask application
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── hms.db              # SQLite database (auto-created)
├── README.md           # This file
└── templates/
    ├── base.html       # Base template with sidebar
    ├── login.html      # Login page
    ├── dashboard.html  # Main dashboard
    ├── patients.html   # Patient management
    ├── schedule.html   # Appointment scheduling
    └── billing.html    # Invoice management
```

---

## 📝 Recent Changes

### Version 1.1 (Dec 13, 2025)
- ✅ Fixed date navigation arrows (`<` `>`) in Appointments
- ✅ Added calendar picker icon for date selection
- ✅ Fixed date display timezone issue
- ✅ Added distinct provider names (Dr. Sarah Johnson, Dr. Michael Chen, etc.)
- ✅ Added Registration Date field to Patient modal
- ✅ Improved phone number validation

### Version 1.0
- Initial release with Patient, Scheduling, and Billing modules
