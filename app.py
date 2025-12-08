from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import or_
from models import db, Staff, Patient, Appointment, Invoice, InvoiceItem
from datetime import date, time, datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key' # Simplified for local dev
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Staff.query.get(int(user_id))

print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
print(f"CWD: {os.getcwd()}")


db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'hms.db')

def initialize_database():
    with app.app_context():
        if not os.path.exists(db_path):
            # Database doesn't exist, create and seed
            print(f"Creating and seeding database at {db_path}...")
            db.create_all()
            seed_data()
        else:
            # Check if tables exist, if not create them
            try:
                # Basic check to see if we can query Staff. If checking all tables is needed, inspect.
                # For this simplified request, we assume if db file exists we might be ok, 
                # but to be robust as requested "create tables AND populate... If not"
                # If the file exists but tables don't, create_all handles that.
                # The prompt says "check if hms.db exists. If not, create tables AND populate".
                # We can stick to that strictly.
                pass
            except Exception:
                pass


def seed_data():
    if Staff.query.first():
        return
    # Staff
    staff1 = Staff(username='staff1', password='Pass123', role='Doctor')
    staff2 = Staff(username='Dr. Smith', password='Pass123', role='Doctor') # Password wasn't specified but needed for model
    
    # Patients
    patient1 = Patient(name='Alex Lee', dob=date(1999, 1, 20), chart_number='CH-1001', phone='555-0101')
    patient2 = Patient(name='Priya Shah', dob=date(1990, 1, 1), chart_number='CH-1002', phone='555-0102') # DOB not specified for Priya, using dummy
    
    # Commit first to get IDs
    db.session.add(staff1)
    db.session.add(staff2)
    db.session.add(patient1)
    db.session.add(patient2)
    db.session.commit()
    
    # Appointment
    # Dr. Rivera (staff1)
    appt = Appointment(staff_id=staff1.id, patient_id=patient1.id, date=date(2025, 12, 1), time=time(9, 0), status='Scheduled')
    db.session.add(appt)
    db.session.commit()
    db.session.add(appt)
    db.session.commit()
    
    # Invoices
    inv1 = Invoice(patient_id=patient1.id, date_issued=date(2025, 12, 5), total_amount=150.00, status='OPEN')
    db.session.add(inv1)
    db.session.commit()
    
    # Line Items for inv1
    item1 = InvoiceItem(invoice_id=inv1.id, description="Office Visit - Standard", qty=1, unit_price=100.00)
    item2 = InvoiceItem(invoice_id=inv1.id, description="Lab Fee - Basic Panel", qty=1, unit_price=50.00)
    db.session.add(item1)
    db.session.add(item2)
    db.session.commit()
    
    print("Database seeded successfully.")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Staff.query.filter_by(username=username).first()
        
        if user and user.password == password: # Plain text as requested
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Stats
    today = date.today()
    total_patients = Patient.query.count()
    appts_today = Appointment.query.filter_by(date=today).count()
    total_staff = Staff.query.count()
    pending_invoices = 0 # Placeholder for Billing
    
    # Recent Activity (Last 5 appointments)
    recent_activity = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_patients=total_patients, 
                           appts_today=appts_today,
                           total_staff=total_staff,
                           pending_invoices=pending_invoices,
                           recent_activity=recent_activity)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reset-db')
def reset_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()
    return jsonify({"message": "Database reset and re-seeded successfully."})

@app.route('/debug/reset')
def debug_reset():
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_data()
    flash('Database reset successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/patients')
@login_required
def patients():
    return render_template('patients.html')

@app.route('/patients/api/search')
@login_required
def patients_search():
    q = request.args.get('q', '')
    if q:
        patients = Patient.query.filter(
            or_(
                Patient.name.ilike(f'%{q}%'),
                Patient.chart_number.ilike(f'%{q}%'),
                Patient.phone.ilike(f'%{q}%')
            )
        ).all()
    else:
        patients = Patient.query.all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'dob': p.dob.strftime('%Y-%m-%d'),
        'chart_number': p.chart_number,
        'phone': p.phone
    } for p in patients])

@app.route('/patients/add', methods=['POST'])
@login_required
def patients_add():
    data = request.get_json()
    
    # Validation
    if not data.get('phone'):
        return jsonify({'error': 'Phone number is required'}), 400
    
    try:
        new_patient = Patient(
            name=data['name'],
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
            chart_number=data['chart_number'],
            phone=data['phone']
        )
        db.session.add(new_patient)
        db.session.commit()
        return jsonify({'message': 'Patient Saved'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/appointments')
@login_required
def appointments_view():
    # If it's an API call (e.g. for the schedule grid), we might want JSON
    # But for now, let's just render the page. The page will fetch data via API or we pass it.
    # The requirement says "View: List time slots".
    # Let's render the template first.
    return render_template('schedule.html')

@app.route('/appointments/api/list')
@login_required
def appointments_list():
    date_str = request.args.get('date', date.today().isoformat())
    staff_id = request.args.get('staff_id')
    
    query = Appointment.query.filter_by(date=datetime.strptime(date_str, '%Y-%m-%d').date())
    
    if staff_id:
        query = query.filter_by(staff_id=staff_id)
        
    # Exclude canceled if you don't want to see them occupying slots? 
    # Or maybe show them as canceled. Requirement says "Render booked slots".
    # Usually we want to see them.
    
    appts = query.all()
    
    return jsonify([{
        'id': a.id,
        'patient_name': a.patient.name,
        'patient_id': a.patient.id,
        'staff_name': a.staff.username,
        'time': a.time.strftime('%H:%M'),
        'status': a.status,
        'reason': a.reason
    } for a in appts])

@app.route('/appointments/create', methods=['POST'])
@login_required
def appointments_create():
    data = request.get_json()
    
    staff_id = data.get('staff_id')
    patient_id = data.get('patient_id')
    date_str = data.get('date')
    time_str = data.get('time')
    
    if not all([staff_id, patient_id, date_str, time_str]):
         return jsonify({'error': 'Missing required fields'}), 400

    appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    # time_str is expected as "HH:MM"
    # We might need to handle single digit hours if not padded, but frontend usually sends HH:MM
    hour, minute = map(int, time_str.split(':'))
    appt_time = time(hour, minute)

    # CRITICAL: Conflict Check
    # "If provider_id AND date AND start_time match an existing record (that is not Canceled)"
    existing = Appointment.query.filter_by(
        staff_id=staff_id,
        date=appt_date,
        time=appt_time
    ).filter(Appointment.status != 'Canceled').first()
    
    if existing:
        return jsonify({'error': f"Scheduling Conflict: {existing.staff.username} is already booked at this time."}), 409
        
    try:
        new_appt = Appointment(
            staff_id=staff_id,
            patient_id=patient_id,
            date=appt_date,
            time=appt_time,
            status='Scheduled'
        )
        db.session.add(new_appt)
        db.session.commit()
        return jsonify({'message': 'Appointment Booked'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/appointments/<int:id>/status', methods=['POST'])
@login_required
def appointments_status(id):
    data = request.get_json()
    status = data.get('status')
    reason = data.get('reason')
    
    appt = Appointment.query.get_or_404(id)
    
    if status == 'Canceled':
        if not reason:
            return jsonify({'error': 'Reason is required for cancellation'}), 400
        appt.status = 'Canceled'
        appt.reason = reason
        db.session.commit()
        return jsonify({'message': 'Appointment canceled'}), 200
        
    return jsonify({'error': 'Invalid status update'}), 400

        
    return jsonify({'error': 'Invalid status update'}), 400

@app.route('/billing')
@login_required
def billing():
    invoices = Invoice.query.order_by(Invoice.date_issued.desc()).all()
    today = date.today().isoformat()
    return render_template('billing.html', invoices=invoices, today=today)

@app.route('/invoices/create', methods=['POST'])
@login_required
def invoices_create():
    data = request.get_json()
    
    patient_id = data.get('patient_id')
    date_str = data.get('date')
    items = data.get('items', []) # List of {description, qty, unit_price}
    
    if not all([patient_id, date_str, items]):
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        # Calculate total
        total_amount = 0
        invoice_items = []
        
        for item in items:
            qty = float(item['qty']) # Use float for safety even for qty if 1.5 allowed, or int
            price = float(item['unit_price'])
            total_amount += (qty * price)
            
        new_inv = Invoice(
            patient_id=patient_id,
            date_issued=datetime.strptime(date_str, '%Y-%m-%d').date(),
            total_amount=total_amount,
            paid_amount=0.0,
            status='OPEN'
        )
        db.session.add(new_inv)
        db.session.commit() # Commit to get ID
        
        # Add Items
        for item in items:
            new_item = InvoiceItem(
                invoice_id=new_inv.id,
                description=item['description'],
                qty=int(item['qty']),
                unit_price=float(item['unit_price'])
            )
            db.session.add(new_item)
            
        db.session.commit()
        return jsonify({'message': 'Invoice Created'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/invoices/<int:id>/details')
@login_required
def invoices_details(id):
    invoice = Invoice.query.get_or_404(id)
    
    items_data = [{
        'description': item.description,
        'qty': item.qty,
        'unit_price': item.unit_price,
        'total': item.total
    } for item in invoice.items]
    
    return jsonify({
        'id': invoice.id,
        'date': invoice.date_issued.strftime('%Y-%m-%d'),
        'patient_name': invoice.patient.name,
        'patient_chart': invoice.patient.chart_number,
        'status': invoice.status,
        'total': invoice.total_amount,
        'paid': invoice.paid_amount,
        'balance': invoice.balance_due,
        'items': items_data
    })

@app.route('/invoices/<int:id>/pay', methods=['POST'])
@login_required
def invoices_pay(id):
    data = request.get_json()
    amount = float(data.get('amount', 0))
    
    if amount <= 0:
        return jsonify({'error': 'Invalid payment amount'}), 400
        
    invoice = Invoice.query.get_or_404(id)
    
    # Update logic
    invoice.paid_amount += amount
    balance = invoice.total_amount - invoice.paid_amount
    
    if balance <= 0:
        invoice.status = 'PAID'
        badge_color = 'green'
        # Optional: handle overpayment logic (set balance to 0 in display, or store negative balance)
    elif invoice.paid_amount > 0:
        invoice.status = 'PARTIAL'
        badge_color = 'orange'
    else:
        invoice.status = 'OPEN' # Should not happen if amount > 0
        badge_color = 'blue'
        
    db.session.commit()
    
    return jsonify({
        'message': 'Payment Recorded',
        'new_balance': max(0.0, balance),
        'new_status': invoice.status,
        'badge_color': badge_color
    })

if __name__ == '__main__':
    # Using 'with app.app_context()' outside of request in main, or before_first_request (deprecated in newer Flask)
    # The requirement asks for "before_first_request or app.with_app_context".
    # I will check existence before running.
    if not os.path.exists(db_path):
        with app.app_context():
            print(f"Initializing database at {db_path}")
            db.create_all()
            seed_data()
            
    app.run(debug=False, port=8000)
