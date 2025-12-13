# MediCore Hospital Management System

A modern, full-featured Hospital Management System built with **Flask** (Python) and **Tailwind CSS**.

---

## ✨ Features

### 🏥 Patient Management
- **Real-time Search**: Filter by Name, Chart Number, or Phone
- **CRUD Operations**: Create, Read, Update, Delete patient records
- **Validation**: Phone number validation (10-15 digits), required fields
- **Confirmation Dialogs**: "Are you sure?" modals before destructive actions

### 📅 Appointment Scheduling
- **Visual Calendar**: Interactive weekly schedule with time slots
- **Date Navigation**: Arrow buttons to browse days
- **Conflict Detection**: Prevents double-booking
- **Status Updates**: Mark as Completed, Canceled, or Scheduled
- **Visit Types**: Consults, Checkups, Follow-ups, Lab Work, etc.

### 💰 Billing & Invoicing
- **Advanced Filters**: Filter by status (Open/Partial/Paid) and date range
- **Sortable Columns**: Click headers to sort by any column
- **Line Items**: Create detailed invoices with multiple items
- **Payment Tracking**: Record partial or full payments
- **Print Invoice**: Client-side printing support

### 📊 Reports & Analytics
- **Monthly Revenue**: Bar chart showing 6-month revenue trends
- **Patient Growth**: Line chart of new registrations
- **Appointment Analytics**: Status breakdown, cancellation rate
- **Busiest Times**: Charts showing peak hours and days
- **Print Report**: One-click printing

### 📋 Medical Records
- **Visit Notes**: SOAP format (Subjective, Objective, Assessment, Plan)
- **Vitals Tracking**: Blood pressure, pulse, temperature, weight
- **Prescriptions**: Medication tracking with dosage, refills, status
- **Documents**: Upload tracking for lab results, X-rays, consent forms

### 🔍 Global Features
- **Global Search**: Search patients, invoices, appointments from anywhere
- **Keyboard Shortcut**: Press `Cmd+K` (Mac) or `Ctrl+K` (Windows) to search
- **Confirmation Dialogs**: Styled modals for all destructive actions
- **Responsive Design**: Clean, professional UI with Tailwind CSS

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** — [Download Python](https://www.python.org/downloads/)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/MatthewKuilan/hospital_mvp.git
cd hospital_mvp

# 2. Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# OR: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python3 app.py
```

Open in browser: **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `staff1` | `Pass123` | Admin |

---

## 📁 Project Structure

```
MediCore/
├── app.py              # Main Flask application & routes
├── models.py           # SQLAlchemy database models
├── requirements.txt    # Python dependencies
├── hms.db              # SQLite database (auto-created)
└── templates/
    ├── base.html       # Base template with sidebar & global search
    ├── login.html      # Authentication page
    ├── dashboard.html  # Stats, charts, notifications
    ├── patients.html   # Patient management
    ├── schedule.html   # Appointment calendar
    ├── billing.html    # Invoice management with filters
    ├── reports.html    # Analytics & charts
    └── records.html    # Medical records viewer
```

---

## 🗄️ Database

- **Type**: SQLite (no setup required)
- **Location**: `hms.db` in project root
- **Auto-Setup**: Created and seeded on first run

### Reset Database

Click **Reset Database** in the sidebar (requires confirmation) or:
```bash
rm hms.db && python3 app.py
```

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
python3 app.py
```

### Changes Not Showing
- Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
- Restart the Flask server

---

## 📝 Version History

### Version 2.0 (December 13, 2025)
- ✅ **Dashboard Enhancements**: Revenue chart, notifications dropdown
- ✅ **Reports Page**: Monthly revenue, patient growth, appointment analytics
- ✅ **Medical Records**: Visit notes (SOAP), prescriptions, documents
- ✅ **Global Search**: Search anywhere with Cmd+K shortcut
- ✅ **Advanced Filters**: Billing page status/date filters
- ✅ **Sortable Tables**: Click column headers to sort
- ✅ **Confirmation Dialogs**: Styled modals for destructive actions

### Version 1.0
- Initial release with Patient, Scheduling, and Billing modules
