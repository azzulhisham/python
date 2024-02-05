import requests
import json

BASE = "http://127.0.0.1:5000/"

response = requests.put(BASE + "/Video/1", {
    "name": "Hello World",
    "views" : 10000,
    "likes" : 10000
})
print(response.json())