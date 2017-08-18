from rhapi import *
import requests
import json
resp = 'http://gem-machine-a:8113/'

query = 'query/15de0ec097c/data'

url = resp + query
print (url)

json_data = requests.get(url).json()

#print (json_data)
json_more = json_data['data'][0]
print(json_more)

