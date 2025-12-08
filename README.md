# MediCore Hospital Management System

A lightweight, modern Hospital Management System built with **Flask** (Python) and **Tailwind CSS**.

## Features

### 🏥 Patient Management
- **Search**: Real-time searching by Name, Chart Number, or Phone.
- **CRUD**: Full Create, Read, Update, Delete capabilities.
- **Validation**: Strict validation for phone numbers (10-15 digits).
- **Status Tracking**: Visual badges for patient status.

### 📅 Appointment Scheduling
- **Visual Calendar**: Interactive provider schedule with "Blue Card" slots.
- **Conflict Detection**: Prevents double-booking logic with alert banners.
- **Status Updates**: Mark appointments as Completed, Canceled (with reason), or Scheduled.
- **Visit Types**: Track Consults, Checkups, Follow-ups, etc.

### 💰 Billing & Invoicing
- **Invoices**: Create detailed invoices with multiple line items.
- **Auto-Calculation**: Automatic totaling of quantity x unit price.
- **Payments**: Record partial or full payments with status tracking (OPEN, PARTIAL, PAID).
- **History**: View full billing history per patient.

---

## 🚀 Getting Started (Mac & Linux)

### Prerequisites
- **Python 3.8+**
- **Git**

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/MatthewKuilan/hospital_mvp.git
    cd hospital_mvp
    ```

2.  **Set Up Virtual Environment (Recommended)**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the Server**
    ```bash
    python3 app.py
    ```
    *You should see output indicating the server is running on `http://127.0.0.1:8000`*

2.  **Access the App**
    Open your web browser and navigate to:
    **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 🔑 Default Credentials
Use these credentials to log in:
- **Username**: `staff1`
- **Password**: `Pass123`

---

## Database Management
The application uses a local **SQLite** database (`hms.db`).
- The database is automatically created and seeded with sample data on the first run.
- **Reset Database**: To wipe all data and restore defaults, visit:
  `http://127.0.0.1:8000/reset-db`

## Troubleshooting
- **Port In Use**: If port 8000 is busy, kill the process using standard tools (`lsof -ti:8000 | xargs kill -9`) or change the port in the `app.run` call in `app.py`.
- **Python not found**: Ensure you are using `python3` command if `python` refers to legacy Python 2.7.
