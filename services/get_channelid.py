import requests
from dotenv import load_dotenv
import os

##Load the .env file
load_dotenv()

# Create auth header
access_token = os.getenv("API_TOKEN")
access_headers = {
             "Authorization": f"Bearer {access_token}"
         }
api_url = os.getenv("API_URL")
# Url used for games data
tenant_api_url = f"{api_url}/tenant"

#teamname = os.getenv("TEAMNAME")
teamname = "manvsfat"

def get_channelid():
    response = requests.get(tenant_api_url + "/" + teamname, headers=access_headers)
    if response.status_code == 200:
        data = response.json()
        data = data["channelid"]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

def get_playernum():
    response = requests.get(tenant_api_url + "/" + teamname, headers=access_headers)
    if response.status_code == 200:
        data = response.json()
        data = data["playernum"]
        return data
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return []

channelid = "881540439654670336"
playernum = 10