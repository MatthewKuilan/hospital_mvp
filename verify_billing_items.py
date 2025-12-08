
import unittest
from app import app, db, Invoice, InvoiceItem
from datetime import date

class TestBillingItems(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        
    def login(self):
        return self.client.post('/login', data=dict(
            username='staff1',
            password='Pass123'
        ), follow_redirects=True)

    def test_invoice_with_items(self):
        self.login()
        
        # 1. Create Invoice with Items
        print("\n[TEST] Creating Invoice with 2 Items...")
        payload = {
            'patient_id': 1,
            'date': '2025-01-01',
            'items': [
                {'description': 'Item A', 'qty': 1, 'unit_price': 100.0},
                {'description': 'Item B', 'qty': 2, 'unit_price': 25.0}
            ]
        }
        # Expected Total: 100*1 + 25*2 = 150.0
        
        rv = self.client.post('/invoices/create', json=payload)
        self.assertEqual(rv.status_code, 200, f"Creation failed: {rv.json}")
        
        with app.app_context():
            inv = Invoice.query.order_by(Invoice.id.desc()).first()
            print(f"  -> Created Invoice ID: {inv.id}")
            print(f"  -> Total Amount: {inv.total_amount}")
            
            self.assertEqual(inv.total_amount, 150.0, "Total amount calculation incorrect")
            self.assertEqual(len(inv.items), 2, "Should have 2 items")
            print("  -> Verified Items and Total.")
            
    def test_get_details(self):
         self.login()
         # Use seeded invoice #1 which we know has items from seed_data update
         print("\n[TEST] Get Invoice Details...")
         rv = self.client.get('/invoices/1/details')
         data = rv.get_json()
         
         self.assertEqual(data['id'], 1)
         self.assertEqual(data['balance'], 150.0)
         self.assertTrue(len(data['items']) >= 2)
         print("  -> Verified Details API")

if __name__ == '__main__':
    unittest.main()
