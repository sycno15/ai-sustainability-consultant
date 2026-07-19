import requests
import time
import random
import sys

BASE_URL = "http://localhost:8000/api/v1"

def main():
    print("--- Starting End-to-End AI Sustainability Consultant Flow Demo ---")
    
    # 1. Generate randomized user credentials
    random_id = random.randint(1000, 9999)
    email = f"demo_user_{random_id}@gmail.com"
    password = "Password123!"
    full_name = f"Demo Business {random_id}"
    
    print(f"Registering user with email: {email}...")
    register_payload = {
        "email": email,
        "password": password,
        "full_name": full_name
    }
    
    registration_failed = False
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_payload)
        response.raise_for_status()
        register_data = response.json()
        print("Registration successful!")
    except Exception as e:
        print(f"Error during registration: {e}")
        if 'response' in locals() and response.text:
            print(f"Server response: {response.text}")
        print("Falling back to pre-registered and confirmed demo user: demo_user_6042@gmail.com")
        email = "demo_user_6042@gmail.com"
        password = "Password123!"
        registration_failed = True
        
    # 2. Log in to get the access token
    print(f"Logging in as {email}...")
    login_payload = {
        "email": email,
        "password": password
    }
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
        response.raise_for_status()
        login_data = response.json()
        token = login_data["data"]["access_token"]
        print("Login successful! Access token obtained.")
    except Exception as e:
        print(f"Error during login: {e}")
        if registration_failed:
            print("Note: Registration failed and fallback login also failed.")
        sys.exit(1)
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 3. Submit a new assessment
    print("Submitting sustainability assessment metrics...")
    assessment_payload = {
        "business_name": "ABC Eco Manufacturing",
        "industry": "Manufacturing",
        "company_size": "Medium",
        "description": "A medium-sized facility producing electronic components. Goal: Reduce scope 1 & 2 carbon footprint by 30%. Priority: ROI-focused.",
        "electricity_usage": 150000.0,
        "diesel_usage": 12000.0,
        "petrol_usage": 5000.0,
        "water_usage": 8500.0,
        "waste_generated": 65.0,
        "annual_revenue": 2500000.0,
        "sustainability_budget": 80000.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/assessments", json=assessment_payload, headers=headers)
        response.raise_for_status()
        assessment_data = response.json()
        assessment_id = assessment_data["data"]["assessment_id"]
        print(f"Assessment created successfully! ID: {assessment_id}")
    except Exception as e:
        print(f"Error submitting assessment: {e}")
        if 'response' in locals() and response.text:
            print(f"Server response: {response.text}")
        sys.exit(1)
        
    # 4. Trigger the multi-agent workflow
    print("Starting multi-agent sustainability consulting workflow...")
    try:
        response = requests.post(f"{BASE_URL}/analysis/{assessment_id}/start", headers=headers)
        response.raise_for_status()
        print("Workflow execution started in background.")
    except Exception as e:
        print(f"Error starting workflow: {e}")
        sys.exit(1)
        
    # 5. Poll the workflow progress
    print("Monitoring workflow status and progress...")
    completed = False
    failed = False
    
    for i in range(45):  # Wait up to 90 seconds
        time.sleep(2)
        try:
            status_resp = requests.get(f"{BASE_URL}/analysis/{assessment_id}/status", headers=headers)
            status_resp.raise_for_status()
            status_info = status_resp.json()["data"]
            
            status_str = status_info["status"]
            progress = status_info["progress"]
            current_agent = status_info["current_agent"]
            
            print(f"[{i*2}s] Status: {status_str} | Progress: {progress}% | Current Agent: {current_agent}")
            
            if status_str == "COMPLETED" or status_str == "APPROVED":
                completed = True
                break
            elif status_str == "FAILED":
                failed = True
                break
        except Exception as e:
            print(f"Error checking status: {e}")
            
    if completed:
        print("\nMulti-agent workflow completed successfully!")
        
        # Get timeline logs
        try:
            timeline_resp = requests.get(f"{BASE_URL}/analysis/{assessment_id}/timeline", headers=headers)
            timeline_resp.raise_for_status()
            timeline_data = timeline_resp.json()["data"]
            print("\nChronological Timeline Log:")
            for item in timeline_data:
                agent = item.get("agent_name", "System")
                msg = item.get("message", "")
                status = item.get("status", "")
                print(f" - [{agent}] {status}: {msg}")
        except Exception as e:
            print(f"Error fetching timeline: {e}")
            
        # Verify if report is created
        print("\nFetching generated sustainability report...")
        try:
            # Let's get dashboard stats or reports
            dash_resp = requests.get(f"{BASE_URL}/dashboard", headers=headers)
            dash_resp.raise_for_status()
            dash_data = dash_resp.json()["data"]
            print(f"Dashboard Stats: {dash_data}")
            
            report_resp = requests.get(f"{BASE_URL}/dashboard/reports", headers=headers)
            report_resp.raise_for_status()
            reports_list = report_resp.json()["data"]
            if reports_list:
                latest_report = reports_list[0]
                print(f"Generated Report ID: {latest_report['id']} for {latest_report['business_name']}")
                print(f"PDF URL: {latest_report.get('pdf_url')}")
            else:
                print("No reports found in report list.")
        except Exception as e:
            print(f"Error fetching reports: {e}")
            
    elif failed:
        print("\nWorkflow failed.")
        sys.exit(1)
    else:
        print("\nWorkflow monitoring timed out.")
        sys.exit(1)

if __name__ == "__main__":
    main()
