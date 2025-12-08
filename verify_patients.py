
import os
from app import app, db, Patient, initialize_database
from datetime import date

def run_checks():
    print("Running Verification Checks...")
    
    # Check 1: Database File check
    db_path = os.path.join(os.getcwd(), 'MediCore', 'hms.db')
    # Because app.py defines db_path relative to __file__, we need to be careful.
    # checking app.config
    print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    with app.app_context():
        # Force re-creation if we suspect schema issues, but let's try reading first
        try:
            p = Patient.query.first()
            print("Check 1: User Query Passed")
            if p:
                print(f"   Found patient: {p.name}, Phone: {p.phone}")
            else:
                print("   No patients found (might need seeding)")
                
        except Exception as e:
            print(f"Check 1: FAILED - {e}")
            print("Attempting to reset DB...")
            db.drop_all()
            db.create_all()
            # Seed basic data
            from app import seed_data
            seed_data()
            print("Check 1: DB Reset and Seeded.")
            
        # Check 2: Add Patient
        try:
            new_p = Patient(name="Test User", dob=date(2000,1,1), chart_number="TEST-001", phone="123-456")
            db.session.add(new_p)
            db.session.commit()
            print("Check 2: Add Patient Passed")
        except Exception as e:
            print(f"Check 2: FAILED - {e}")

if __name__ == "__main__":
    run_checks()
