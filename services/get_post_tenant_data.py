from flask import session
import requests
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

####### JWT AUTH #######
# Login to the API to get JWT token
# API_USERNAME = os.getenv("API_USERNAME")
# API_PASSWORD = os.getenv("API_PASSWORD")

# # Url used for login
# login_api_url = "http://localhost:8080/login"

# response = requests.post(login_api_url, json={"username": API_USERNAME, "password": API_PASSWORD})
# access_token = response.json()["access_token"]
# access_headers = {
#     "Authorization": f"Bearer {access_token}"
# }

#########################
#########################


# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
             "Authorization": f"Bearer {access_token}"
         } 
api_url = os.getenv("API_URL")
teamname = os.getenv("TEAMNAME")
# Url used for games data
tenant_api_url = f"{api_url}/tenant"
tenant_api_url_with_teamname = f"{api_url}/tenant/{teamname}"

def playernumber():
    data = 10   # default value
    try:
        response = requests.get(tenant_api_url_with_teamname, headers=access_headers)
        response.raise_for_status()  # Will raise an HTTPError if the response was unsuccessful
        data = response.json().get("playernum", data)
    except (requests.exceptions.RequestException, KeyError) as err:
        print(f"Error occurred: {err}. Using default player number: {data}")
    return int(data)

def channelid():
    try:
        response = requests.get(tenant_api_url + "/" + teamname, headers=access_headers)
        if response.status_code == 200:
            data = response.json()
            try:
                data = data["channelid"]
                return data
            except KeyError:  
                print("Key 'channelid' not found in the response.")
                return []
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return []

def players_ten():
    # Prepare the updated data
    updated_data = {"playernum": 10}

    # Send a PUT request to update all records
    response = requests.put(tenant_api_url + '/' + teamname, json=updated_data, headers=access_headers)

    if response.status_code == 200:
        print("All records updated successfully")
    else:
        print(f"Failed to update records. Status code: {response.status_code}")

def players_twelve():
    # Prepare the updated data
    updated_data = {"playernum": 12}

    # Send a PUT request to update all records
    response = requests.put(tenant_api_url + '/' + teamname, json=updated_data, headers=access_headers)

    if response.status_code == 200:
        print("All records updated successfully")
    else:
        print(f"Failed to update records. Status code: {response.status_code}")

# This will need a tenant in the db
#get_channelid = channelid()
get_channelid = "1154043593485455500"
playernum = playernumber()