import requests

url = 'http://91.201.215.176:3000/c'

data = {
    'Ver': 'v1',
    'Orderid': '00000013049',
    'Torderid': '12345',
    'Machid': '00000013854',
    'Trackno': '1',
    'Status': '1',
    'Errinfo': 'Error message',
    'Randstr': 'ok76oc1jkh2sy85o',
    'Timestamp': '202311221200',
    'Sign': '4cfd6a28a79db4bce9ed3d41cb0eed0e892958a4'
}


response = requests.post(url, data=data)

if response.status_code == 200:
    try:
        print(response.json())
    except ValueError as e:
        print("Response is not in valid JSON format")
else:
    print("Failed to receive a valid response. Status code:", response.status_code)
