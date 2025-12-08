
import unittest
from app import app, db, Invoice
from datetime import date

class TestBilling(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
    def login(self):
        return self.client.post('/login', data=dict(
            username='staff1',
            password='Pass123'
        ), follow_redirects=True)

    def test_payment_logic(self):
        self.login()
        
        # 1. Create Invoice
        print("\n[TEST] Creating Invoice...")
        payload = {
            'patient_id': 1,
            'amount': 100.0,
            'date': '2025-01-01'
        }
        rv = self.client.post('/invoices/create', json=payload)
        self.assertEqual(rv.status_code, 200, "Creation failed")
        
        with app.app_context():
            inv = Invoice.query.filter_by(total_amount=100.0, paid_amount=0.0).first()
            inv_id = inv.id
            print(f"  -> Created Invoice ID: {inv_id}")

        # 2. Partial Payment ($50)
        print("[TEST] Making Partial Payment ($50)...")
        rv = self.client.post(f'/invoices/{inv_id}/pay', json={'amount': 50})
        data = rv.get_json()
        self.assertEqual(data['new_status'], 'PARTIAL')
        self.assertEqual(data['new_balance'], 50.0)
        print("  -> Status is PARTIAL")

        # 3. Full Payment ($50 remaining)
        print("[TEST] Making Remaining Payment ($50)...")
        rv = self.client.post(f'/invoices/{inv_id}/pay', json={'amount': 50})
        data = rv.get_json()
        self.assertEqual(data['new_status'], 'PAID')
        self.assertEqual(data['new_balance'], 0.0)
        print("  -> Status is PAID")

if __name__ == '__main__':
    unittest.main()
