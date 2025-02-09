import requests

url = 'http://91.201.215.176:3000/b'  

data = {
    'ver': 'v1',
    'orderid': '123456789012348',
    'torderid': '12345',
    'machid': '00000013037',
    'channelid': '36',
    'randstr': 'fautzhlbqarmljzw',
    'timestamp': '20231206164722',
    'sign': '4cfd6a28a79db4bce9ed3d41cb0eed0e892958a4'
}

response = requests.post(url, data=data)

if response.status_code == 200:
    try:
        print(response.json())
    except ValueError as e:
        print("Response is not in valid JSON format")
else:
    print("Failed to receive a valid response. Status code:", response.status_code)
