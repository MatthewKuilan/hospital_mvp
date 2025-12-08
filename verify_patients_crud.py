import requests
import json

BASE_URL = "http://127.0.0.1:8000"
SESSION = requests.Session()

def login():
    print("Logging in...")
    # Get login page for CSRF if needed (not needed here based on simple app)
    # Post login
    r = SESSION.post(f"{BASE_URL}/login", data={'username': 'staff1', 'password': 'Pass123'})
    if r.url == f"{BASE_URL}/dashboard":
        print("Login Successful.")
        return True
    else:
        print("Login Failed.")
        return False

def test_validation():
    print("\n--- Test Validation ---")
    data = {
        'first_name': 'Bad',
        'last_name': 'Phone',
        'dob': '2000-01-01',
        'phone': '123', # Invalid
        'chart_number': 'CH-TEST-VAL'
    }
    r = SESSION.post(f"{BASE_URL}/patients/add", json=data)
    if r.status_code == 400 and 'digits' in r.text:
        print("PASS: Validation blocked short phone.")
    else:
        print(f"FAIL: Validation didn't block short phone. Status: {r.status_code}, Resp: {r.text}")

def test_crud_flow():
    print("\n--- Test CRUD Flow ---")
    
    # Defaults
    chart_num = 'CH-CRUD-01'
    
    # Cleanup previous runs
    print("Cleaning up old test data...")
    r = SESSION.get(f"{BASE_URL}/patients/api/search?q=CRUD")
    for p in r.json():
        if 'CRUD' in p['name']:
            print(f"Deleting old test patient {p['id']}...")
            SESSION.delete(f"{BASE_URL}/patients/{p['id']}")

    # 1. Create
    data = {
        'first_name': 'CRUD',
        'last_name': 'Test',
        'dob': '1990-01-01',
        'phone': '5551234567',
        'chart_number': chart_num,
        'address': '123 Test Ln'
    }
    r = SESSION.post(f"{BASE_URL}/patients/add", json=data)
    if r.status_code != 200:
        print(f"FAIL: Create failed. {r.text}")
        return
    print("PASS: Created patient.")

    # Get ID by search
    r = SESSION.get(f"{BASE_URL}/patients/api/search?q=CRUD")
    patients = r.json()
    if not patients:
        print("FAIL: Could not find created patient.")
        return
    
    p_id = patients[0]['id']
    print(f"Found Patient ID: {p_id}")

    # 2. Update (Edit)
    update_data = {
        'first_name': 'CRUD',
        'last_name': 'Updated',
        'phone': '5559998888'
    }
    r = SESSION.put(f"{BASE_URL}/patients/{p_id}", json=update_data)
    if r.status_code == 200:
        print("PASS: Update successful.")
    else:
        print(f"FAIL: Update failed. {r.text}")

    # Verify Update
    r = SESSION.get(f"{BASE_URL}/patients/api/search?q=CRUD")
    patients = r.json()
    if patients[0]['name'] == 'CRUD Updated' and patients[0]['phone'] == '5559998888':
        print("PASS: Update verified in search.")
    else:
        print(f"FAIL: Update verification failed. Got {patients[0]}")

    # 3. Delete
    r = SESSION.delete(f"{BASE_URL}/patients/{p_id}")
    if r.status_code == 200:
        print("PASS: Delete successful.")
    else:
        print(f"FAIL: Delete failed. {r.text}")

    # Verify Delete
    r = SESSION.get(f"{BASE_URL}/patients/api/search?q=CRUD")
    patients = r.json()
    if not patients:
        print("PASS: Delete verified (patient not found).")
    else:
        print("FAIL: Patient still exists after delete.")

if __name__ == "__main__":
    if login():
        test_validation()
        test_crud_flow()
