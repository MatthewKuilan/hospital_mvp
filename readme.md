# Hospital Management System (MVP)

This is a Minimum Viable Product (MVP) for a Django-based hospital management system, focusing on patient record keeping and appointment scheduling, including conflict prevention.

## Features Supported

* **Patient Management (MVP-1, MVP-2):** Create, Edit, and Search patients by name, DOB, or phone (partial matching supported).
* **Appointment Management (MVP-3, MVP-5):** Schedule, edit, and cancel appointments with required conflict prevention (no double booking for patients or providers at the same time).
* **Provider Availability (MVP-4):** View scheduled appointments for any provider on a specific date.

---

## Quick Setup Guide (Windows)

This guide assumes you have Git and Python 3 installed.

### 1. Get the Code and Install Dependencies

Open your Command Prompt or PowerShell, and execute the following commands.

```bash
# 1. Clone the repository
git clone [https://github.com/MatthewKuilan/hospital_mvp.git](https://github.com/MatthewKuilan/hospital_mvp.git)
cd hospital_mvp

# 2. Create the virtual environment (venv)
python -m venv venv

# 3. Activate the virtual environment
.\venv\Scripts\activate

# 4. Install all required packages (must have requirements.txt created first)
pip install -r requirements.txt

# 5. Apply database migrations
python manage.py migrate

# 6. Create a superuser (Follow prompts for username, email, and password)
python manage.py createsuperuser

# 7. Start the server
python manage.py runserver