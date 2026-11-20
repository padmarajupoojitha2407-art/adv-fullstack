import requests

URL = "http://127.0.0.1:8000"
user_credentials = {"username": "AIT", "password": "123456789", "user_type": "admin"}  # "pooji" already exists as ceo with another password
response = requests.post(url=URL+"/register", json=user_credentials)
print(response.status_code)
print(response.json())

response = requests.post(url=URL+"/login", json=user_credentials)
response_json = response.json()
print(response_json)
access_token = response_json["access_token"]
refresh_token = response_json["refresh_token"]

header ={"token": access_token}
response = requests.get(url=URL+"/packages", headers=header)
print(response.json())

package_id = 1
response = requests.get(url=URL+f"/packages/{package_id}", headers=header)
print(response.json())

dispatch_id = 1
response = requests.get(url=URL+"/dispatches", headers=header)
print(response.json())