
import asyncio
from fastapi.testclient import TestClient
from app.main import app

def verify_endpoints():
    print("🚀 Verifying Advanced Endpoints...")
    client = TestClient(app)
    
    # Test cases: (method, url, expected_status)
    test_cases = [
        ("GET", "/", 200), # Root
        ("GET", "/api/multi-agent/capabilities", 200), # Advanced endpoint
        ("GET", "/api/workflow/list", 200), # Workflow automation
    ]
    
    passed = 0
    failed = 0
    
    for method, url, expected_status in test_cases:
        print(f"Testing {method} {url}...")
        try:
            if method == "GET":
                response = client.get(url)
            elif method == "POST":
                response = client.post(url, json={})
            
            if response.status_code == expected_status:
                print(f"   Passed ({response.status_code})")
                passed += 1
            else:
                print(f"   Failed (Got {response.status_code}, Expected {expected_status})")
                print(f"     Response: {response.text[:200]}")
                failed += 1
        except Exception as e:
            print(f"   Error: {e}")
            failed += 1
            
    print(f"\n Summary: {passed} passed, {failed} failed")
    
    if failed == 0:
        print(" All check passed!")
    else:
        print(" Some checks failed")

if __name__ == "__main__":
    verify_endpoints()
