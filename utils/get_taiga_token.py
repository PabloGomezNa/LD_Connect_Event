import requests

# Define the login endpoint URL and payload
login_url = "https://api.taiga.io/api/v1/auth"
payload = {
    "password": "ij94$9YeCyvZN9T",
    "type": "normal",
    "username": "pgomezn"
}

# Send the POST request to log in
response = requests.post(login_url, json=payload)
response.raise_for_status()  # Will raise an error if the response status is not 200

# Parse the JSON response
data = response.json()

# Extract the token; a
token = data.get("auth_token")

if token:
    print("Login successful, token retrieved:", token)
else:
    print("Login failed or token not found in the response.")
