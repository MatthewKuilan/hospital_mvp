from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Staff(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False) # In a real app we'd hash this
    role = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Staff {self.username}>'

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    chart_number = db.Column(db.String(20), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)
    registration_date = db.Column(db.DateTime, nullable=True)  # When patient was registered

    def __repr__(self):
        return f'<Patient {self.name}>'

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Scheduled', nullable=False)
    visit_type = db.Column(db.String(50), default='General Checkup', nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    
    staff = db.relationship('Staff', backref=db.backref('appointments', lazy=True))
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Appointment {self.id} - {self.status}>'

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='OPEN', nullable=False) # OPEN, PARTIAL, PAID
    total_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0, nullable=False)

    patient = db.relationship('Patient', backref=db.backref('invoices', lazy=True, cascade="all, delete-orphan"))

    @property
    def balance_due(self):
        return max(0.0, self.total_amount - self.paid_amount)
        
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Invoice {self.id} - {self.status}>'

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    
    @property
    def total(self):
        return self.qty * self.unit_price

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=db.func.now())
    payment_method = db.Column(db.String(50), default='Cash')  # Cash, Card, Insurance, etc.
    reference = db.Column(db.String(100))  # Transaction ID, check number, etc.
    
    invoice = db.relationship('Invoice', backref=db.backref('payments', lazy=True, cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<Payment ${self.amount} on {self.payment_date}>'

# ===== MEDICAL RECORDS MODELS =====

class VisitNote(db.Model):
    """Clinical notes per appointment"""
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # SOAP Note format
    chief_complaint = db.Column(db.Text)  # Why patient is visiting
    subjective = db.Column(db.Text)  # Patient's description of symptoms
    objective = db.Column(db.Text)  # Doctor's observations, vitals, exam findings
    assessment = db.Column(db.Text)  # Diagnosis
    plan = db.Column(db.Text)  # Treatment plan
    
    # Vitals (optional)
    vitals_bp = db.Column(db.String(20))  # Blood pressure
    vitals_pulse = db.Column(db.Integer)  # Heart rate
    vitals_temp = db.Column(db.Float)  # Temperature
    vitals_weight = db.Column(db.Float)  # Weight in lbs
    
    appointment = db.relationship('Appointment', backref=db.backref('visit_notes', lazy=True, cascade="all, delete-orphan"))
    patient = db.relationship('Patient', backref=db.backref('visit_notes', lazy=True))
    staff = db.relationship('Staff', backref=db.backref('visit_notes', lazy=True))
    
    def __repr__(self):
        return f'<VisitNote {self.id} - Appt #{self.appointment_id}>'

class Prescription(db.Model):
    """Medications prescribed to patients"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)  # Prescribing doctor
    visit_note_id = db.Column(db.Integer, db.ForeignKey('visit_note.id'), nullable=True)  # Optional link to visit
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    medication_name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)  # e.g., "500mg"
    frequency = db.Column(db.String(100), nullable=False)  # e.g., "Twice daily with food"
    duration = db.Column(db.String(50))  # e.g., "14 days"
    quantity = db.Column(db.Integer, default=30)
    refills = db.Column(db.Integer, default=0)
    instructions = db.Column(db.Text)  # Special instructions
    status = db.Column(db.String(20), default='Active')  # Active, Completed, Discontinued
    
    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True, cascade="all, delete-orphan"))
    staff = db.relationship('Staff', backref=db.backref('prescriptions', lazy=True))
    visit_note = db.relationship('VisitNote', backref=db.backref('prescriptions', lazy=True))
    
    def __repr__(self):
        return f'<Prescription {self.medication_name} for Patient #{self.patient_id}>'

class MedicalDocument(db.Model):
    """Uploaded documents like lab results, imaging, etc."""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=db.func.now())
    
    document_type = db.Column(db.String(50), nullable=False)  # Lab Result, X-Ray, MRI, Consent Form, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))  # e.g., application/pdf, image/jpeg
    
    patient = db.relationship('Patient', backref=db.backref('documents', lazy=True, cascade="all, delete-orphan"))
    uploader = db.relationship('Staff', backref=db.backref('uploaded_documents', lazy=True))
    
    def __repr__(self):
        return f'<MedicalDocument {self.title} for Patient #{self.patient_id}>'
