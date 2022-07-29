# send json requests to an API endpoint

# import necessary modules
import requests
import json

# define the endpoint
endpoint = "http://192.168.1.117:8090/json-rpc"

# define the headers
headers = {'Content-Type': 'application/json',
           'Accept': 'application/json'}

data = {
    "command": "componentstate",
    "componentstate":
        {
            "component": "LEDDEVICE",
            "state": True
        }
}

# send the request
response = requests.post(endpoint, data=json.dumps(data), headers=headers)

# print the response
print(response.text)
