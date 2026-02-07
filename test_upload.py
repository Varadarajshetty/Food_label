
import requests
import os

url = 'http://127.0.0.1:5000/api/upload-image'
files = {'image': open(r'C:\Users\ASUS\Desktop\Screenshot 2025-12-22 221858.png', 'rb')}

print(f"Sending POST request to {url}...")
try:
    response = requests.post(url, files=files, timeout=60)
    print(f"Response Status Code: {response.status_code}")
    try:
        print("Response JSON:", response.json())
    except:
        print("Response Text:", response.text)
except Exception as e:
    print(f"Request Failed: {e}")
