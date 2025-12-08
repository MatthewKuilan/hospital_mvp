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
