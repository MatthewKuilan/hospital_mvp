
import unittest
from app import app, db, Appointment
from datetime import date, time

class TestScheduling(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
        # Ensure clean state for test
        with app.app_context():
            # Clear appointments for this specific test day
            Appointment.query.filter_by(date=date(2025,1,1)).delete()
            db.session.commit()

    def login(self):
        return self.client.post('/login', data=dict(
            username='staff1',
            password='Pass123'
        ), follow_redirects=True)

    def test_conflict_logic(self):
        self.login()
        
        payload = {
            'staff_id': 1,
            'patient_id': 1,
            'date': '2025-01-01',
            'time': '10:00'
        }
        
        # 1. Book First Appointment
        print("\n[TEST] Booking first appointment...")
        rv = self.client.post('/appointments/create', json=payload)
        self.assertEqual(rv.status_code, 200, f"Booking failed: {rv.json}")
        print("  -> Success")

        # 2. Try Duplicate (Conflict)
        print("[TEST] Attempting double-booking...")
        rv = self.client.post('/appointments/create', json=payload)
        self.assertEqual(rv.status_code, 409, "Double booking was allowed!")
        print(f"  -> Correctly blocked (409): {rv.json.get('error')}")

        # 3. Cancel Appointment
        print("[TEST] Canceling appointment...")
        # Get ID
        with app.app_context():
            appt = Appointment.query.filter_by(date=date(2025,1,1), time=time(10,0)).first()
            appt_id = appt.id
            
        rv = self.client.post(f'/appointments/{appt_id}/status', json={
            'status': 'Canceled',
            'reason': 'Patient requested'
        })
        self.assertEqual(rv.status_code, 200)
        print("  -> Canceled")

        # 4. Re-book same slot
        print("[TEST] Re-booking same slot after cancellation...")
        rv = self.client.post('/appointments/create', json=payload)
        self.assertEqual(rv.status_code, 200, "Re-booking failed")
        print("  -> Success")

if __name__ == '__main__':
    unittest.main()
