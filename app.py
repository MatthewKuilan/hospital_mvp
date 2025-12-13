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
    # Staff - Distinct doctor names (staff1 is the login account)
    staff1 = Staff(username='staff1', password='Pass123', role='Admin')
    staff2 = Staff(username='Dr. Sarah Johnson', password='Pass123', role='Doctor')
    staff3 = Staff(username='Dr. Michael Chen', password='Pass123', role='Doctor')
    staff4 = Staff(username='Dr. Emily Rodriguez', password='Pass123', role='Nurse Practitioner')
    
    # Patients
    patient1 = Patient(name='Alex Lee', dob=date(1999, 1, 20), chart_number='CH-1001', phone='555-0101', address='123 Maple Dr, NY', status='Active')
    patient2 = Patient(name='Priya Shah', dob=date(1990, 1, 1), chart_number='CH-1002', phone='555-0102', address='456 Oak Ln, NJ', status='Active')
    
    
    # Commit first to get IDs
    db.session.add(staff1)
    db.session.add(staff2)
    db.session.add(staff3)
    db.session.add(staff4)
    db.session.add(patient1)
    db.session.add(patient2)
    db.session.commit()
    
    # Appointments
    appt = Appointment(staff_id=staff1.id, patient_id=patient1.id, date=date(2025, 12, 1), time=time(9, 0), status='Scheduled', visit_type='Consult')
    db.session.add(appt)
    db.session.commit()
    # Re-reading: In previous seed_data I had a duplicate add block which was a bug (but ignored by SQLAlchemy often if same instance). 
    # Let's create a second appointment properly.
    appt2 = Appointment(staff_id=staff1.id, patient_id=patient2.id, date=date(2025, 12, 1), time=time(11, 0), status='Scheduled', visit_type='General Checkup')
    db.session.add(appt2)
    db.session.commit()
    
    # Invoices for patient1
    inv1 = Invoice(patient_id=patient1.id, date_issued=date(2025, 12, 5), total_amount=150.00, status='OPEN')
    db.session.add(inv1)
    db.session.commit()
    
    # Line Items for inv1
    item1 = InvoiceItem(invoice_id=inv1.id, description="Office Visit - Standard", qty=1, unit_price=100.00)
    item2 = InvoiceItem(invoice_id=inv1.id, description="Lab Fee - Basic Panel", qty=1, unit_price=50.00)
    db.session.add(item1)
    db.session.add(item2)
    
    # Invoice for patient2 - Partially paid
    inv2 = Invoice(patient_id=patient2.id, date_issued=date(2025, 12, 8), total_amount=200.00, paid_amount=75.00, status='PARTIAL')
    db.session.add(inv2)
    db.session.commit()
    
    item3 = InvoiceItem(invoice_id=inv2.id, description="Consultation", qty=1, unit_price=150.00)
    item4 = InvoiceItem(invoice_id=inv2.id, description="Prescription", qty=1, unit_price=50.00)
    db.session.add(item3)
    db.session.add(item4)
    
    # Another invoice for patient1 - Paid
    inv3 = Invoice(patient_id=patient1.id, date_issued=date(2025, 11, 20), total_amount=100.00, paid_amount=100.00, status='PAID')
    db.session.add(inv3)
    db.session.commit()
    
    item5 = InvoiceItem(invoice_id=inv3.id, description="Follow-up Visit", qty=1, unit_price=100.00)
    db.session.add(item5)
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
    pending_invoices = Invoice.query.filter(Invoice.status.in_(['OPEN', 'PARTIAL'])).count()
    
    # Recent Activity (Last 5 appointments)
    recent_activity = Appointment.query.order_by(Appointment.date.desc(), Appointment.time.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_patients=total_patients, 
                           appts_today=appts_today,
                           total_staff=total_staff,
                           pending_invoices=pending_invoices,
                           recent_activity=recent_activity,
                           today=today.strftime('%b %d, %Y'))

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
        'phone': p.phone,
        'address': p.address,
        'status': p.status,
        'registration_date': p.registration_date.isoformat() if p.registration_date else None
    } for p in patients])

@app.route('/patients/<int:id>/stats')
@login_required
def patient_stats(id):
    """Get real stats for a patient: appointments, invoices, balance"""
    patient = Patient.query.get_or_404(id)
    
    # Count appointments
    appointment_count = Appointment.query.filter_by(patient_id=id).count()
    
    # Count invoices and calculate balance
    invoices = Invoice.query.filter_by(patient_id=id).all()
    invoice_count = len(invoices)
    total_balance = sum(inv.balance_due for inv in invoices)
    
    return jsonify({
        'appointments': appointment_count,
        'invoices': invoice_count,
        'balance': round(total_balance, 2)
    })

@app.route('/patients/add', methods=['POST'])
@login_required
def patients_add():
    data = request.get_json()
    
    # Validation
    if not data.get('phone'):
        return jsonify({'error': 'Phone number is required'}), 400
    
    # Simple strict 10-digit validation or standard formats
    # For now, let's enforce 10-15 chars, maybe allowing dashes/spaces but strip them for storage?
    # User asked for "Strict number requirements".
    # Regex: ^\d{10}$ (if strictly 10 digits) or similar.
    # Let's clean the phone first
    raw_phone = data['phone']
    import re
    # Remove non-digits
    clean_phone = re.sub(r'\D', '', raw_phone)
    if not (10 <= len(clean_phone) <= 15):
         return jsonify({'error': 'Phone number must be 10-15 digits'}), 400
        
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    full_name = f"{first_name} {last_name}".strip()
    
    if not full_name:
         return jsonify({'error': 'Name is required'}), 400
    
    try:
        reg_date = None
        if data.get('registration_date'):
            reg_date = datetime.strptime(data['registration_date'], '%Y-%m-%dT%H:%M')
        
        new_patient = Patient(
            name=full_name,
            dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
            chart_number=data['chart_number'],
            phone=data['phone'],
            address=data.get('address'),
            status='Active',
            registration_date=reg_date
        )
        db.session.add(new_patient)
        db.session.commit()
        return jsonify({'message': 'Patient Saved'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/patients/<int:id>', methods=['PUT'])
@login_required
def patients_update(id):
    patient = Patient.query.get_or_404(id)
    data = request.get_json()
    
    # Validation
    raw_phone = data.get('phone', patient.phone)
    import re
    clean_phone = re.sub(r'\D', '', raw_phone)
    if not (10 <= len(clean_phone) <= 15):
         return jsonify({'error': 'Phone number must be 10-15 digits'}), 400
         
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    if first_name or last_name:
         full_name = f"{first_name} {last_name}".strip()
         if full_name:
             patient.name = full_name
             
    if 'dob' in data:
        patient.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
    
    patient.phone = data.get('phone', patient.phone)
    patient.address = data.get('address', patient.address)
    patient.chart_number = data.get('chart_number', patient.chart_number)
    
    if data.get('registration_date'):
        patient.registration_date = datetime.strptime(data['registration_date'], '%Y-%m-%dT%H:%M')
    
    try:
        db.session.commit()
        return jsonify({'message': 'Patient Updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/patients/<int:id>', methods=['DELETE'])
@login_required
def patients_delete(id):
    patient = Patient.query.get_or_404(id)
    try:
        db.session.delete(patient)
        db.session.commit()
        return jsonify({'message': 'Patient Deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/appointments')
@login_required
def appointments_view():
    staff = Staff.query.all()
    today = date.today().strftime('%Y-%m-%d')
    return render_template('schedule.html', staff=staff, today=today)

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
        'visit_type': a.visit_type,
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
    visit_type = data.get('visit_type', 'General Checkup')
    
    if not all([staff_id, patient_id, date_str, time_str]):
        return jsonify({'error': 'Missing fields'}), 400
        
    try:
        appt_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        appt_time = datetime.strptime(time_str, '%H:%M').time()
        
        # Conflict Check
        existing = Appointment.query.filter_by(
            staff_id=staff_id,
            date=appt_date,
            time=appt_time
        ).first()
        
        if existing and existing.status != 'Canceled':
            return jsonify({'error': 'This time slot is already booked.'}), 409
            
        new_appt = Appointment(
            staff_id=staff_id,
            patient_id=patient_id,
            date=appt_date,
            time=appt_time,
            visit_type=visit_type,
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
    appt = Appointment.query.get_or_404(id)
    data = request.get_json()
    
    new_status = data.get('status')
    reason = data.get('reason')
    
    if new_status:
        appt.status = new_status
        if new_status == 'Canceled':
             if not reason:
                 return jsonify({'error': 'Reason required for cancellation'}), 400
             appt.reason = reason
        else:
            # Clear reason if re-scheduled or completed?
            # Ideally keep reason history, but for simple MVP:
            pass 
            
        db.session.commit()
        return jsonify({'message': 'Status Updated'}), 200
        
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
