
import requests

from config.settings import TAIGA_TOKEN
import requests

# Replace these with your actual values
project_id = 16491003  # Your project ID
token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzNzA4Nzg1LCJqdGkiOiJlNDlhNjgwMjQ1YzA0ZjI1OTM2YWQxMjgyNWZjYTgyNiIsInVzZXJfaWQiOjc1OTg5Nn0.FkmK4xi260OzsyXqvqOyV6DyzTysqUkBp4Vefm_267VKXgHwuTY_dKgVKjcjhYyDkMQWGDvx0v2NOz8Eamx2RKo81jZtb0vgmHBWwQy9pse8Xj5PJIFrDy0znQvF0gMc5Jwr-ebAkiZizufg7E4a4P4T8sEm2OYauup89769TZDWHcHfE3iBoDWW24J2x5m6PlCJZQM-Ro4DZPhXJezAoCi8pewG56VUp02LsNo_yW1S-vB1n3V6xcaEJjKaYLx8iKuQ4FtgMZB6wcCGD-HD9aZmrFfrQf_wi5qCuIz0hf8gMJC33OwGrlsTDr626Xb_qpbnABRLTvxjY0D0NnLq8A'
base_url = 'https://api.taiga.io/api/v1'  # Base URL for the Taiga API

# Set up the headers for authentication
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Construct the URL to get memberships for a specific project
url = f'{base_url}/memberships?project={project_id}'

# Send a GET request to the memberships endpoint
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    memberships = response.json()
    print("Project Members:")
    for membership in memberships:
        # Each membership object contains information about the user and their role
        user_id = membership.get('user')
        role = membership.get('role')
        print(f"User ID: {user_id}, Role: {role}")
else:
    print(f"Error: {response.status_code} - {response.text}")