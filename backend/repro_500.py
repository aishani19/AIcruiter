import requests
import json

# Setup
URL = "https://ai-cruiter-weld.vercel.app/api"
TOKEN = "YOUR_TOKEN_HERE" # I'll need a real token or I'll skip auth for testing

def test_submit():
    # 1. Login to get token
    login_resp = requests.post(f"{URL}/login", json={"email": "test@example.com", "password": "password"})
    if login_resp.status_code != 200:
        # Try signup if login fails
        requests.post(f"{URL}/signup", json={"name": "Test", "email": "test@example.com", "password": "password"})
        login_resp = requests.post(f"{URL}/login", json={"email": "test@example.com", "password": "password"})
    
    token = login_resp.json()['token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get a valid question ID
    # For this test, we assume a session exists or we use ID None
    # Let's try sending what the user sent
    data = {
        "question": "Tell me about your experience as a fresher.",
        "question_id": "1", # Mock ID
        "answer_text": "keen about ds",
        "answerFormat": "text"
    }
    
    print(f"Testing submit with data: {data}")
    resp = requests.post(f"{URL}/submit-answer", data=data, headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    try:
        test_submit()
    except Exception as e:
        print(f"Test failed: {e}")
