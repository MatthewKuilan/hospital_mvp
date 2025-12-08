
import unittest
from app import app, db, Appointment
from datetime import date, time

class TestSchedulingEnhanced(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
    def login(self):
        return self.client.post('/login', data=dict(
            username='staff1',
            password='Pass123'
        ), follow_redirects=True)

    def test_enhanced_flow(self):
        self.login()
        
        # 1. Book with Visit Type
        print("\n[TEST] Booking 'Consult'...")
        payload = {
            'staff_id': 1,
            'patient_id': 1,
            'date': '2025-12-05',
            'time': '10:00',
            'visit_type': 'Consult'
        }
        rv = self.client.post('/appointments/create', json=payload)
        self.assertEqual(rv.status_code, 200, f"Booking failed: {rv.json}")
        
        with app.app_context():
            appt = Appointment.query.filter_by(date=date(2025, 12, 5), time=time(10, 0)).first()
            self.assertIsNotNone(appt)
            self.assertEqual(appt.visit_type, 'Consult')
            print(f"  -> Verified Visit Type: {appt.visit_type}")
            appt_id = appt.id

        # 2. Update Status to 'Completed' (No reason needed)
        print("[TEST] Updating Status to 'Completed'...")
        rv = self.client.post(f'/appointments/{appt_id}/status', json={'status': 'Completed'})
        self.assertEqual(rv.status_code, 200)
        
        with app.app_context():
            appt = Appointment.query.get(appt_id)
            self.assertEqual(appt.status, 'Completed')
            print("  -> Verified Status: Completed")

        # 3. Update Status to 'Canceled' (Reason required)
        print("[TEST] Updating Status to 'Canceled' without reason...")
        rv = self.client.post(f'/appointments/{appt_id}/status', json={'status': 'Canceled'})
        self.assertEqual(rv.status_code, 400, "Should satisfy reason requirement")

        print("[TEST] Updating Status to 'Canceled' WITH reason...")
        rv = self.client.post(f'/appointments/{appt_id}/status', json={'status': 'Canceled', 'reason': 'Test Reason'})
        self.assertEqual(rv.status_code, 200)
        
        with app.app_context():
            appt = Appointment.query.get(appt_id)
            self.assertEqual(appt.status, 'Canceled')
            self.assertEqual(appt.reason, 'Test Reason')
            print("  -> Verified Status: Canceled with Reason")

if __name__ == '__main__':
    unittest.main()
