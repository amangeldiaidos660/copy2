# import requests
# import concurrent.futures

# url = 'http://185.100.67.122/a'

# data1 = {
#     'ver': 'v1',
#     'orderid': '0000001265823120412',
#     'machid': '00000012658',
#     'trackno': '1',
#     'name': 'эспрессо 185 мл',
#     'price': '50000',
#     'channelid': '36',
#     'randstr': 'ofowkahnmzxwhdjo',
#     'timestamp': '20231206164722',
#     'sign': 'd274a9bbb8b1e7d6ecd75ab9a0e3339f38b0cd1a'
# }

# data2 = {
#     'ver': 'v1',
#     'orderid': '0000001282312014214189',
#     'machid': '00000012659',
#     'trackno': '1',
#     'name': 'кофе 300 мл',
#     'price': '60000',
#     'channelid': '37',
#     'randstr': 'ndfjwoeiqkwhdpoa',
#     'timestamp': '20231206164730',
#     'sign': 'a0e3339f38b0cd1ad274a9bbb8b1e7d6ecd75ab9'
# }

# def send_request(url, data):
#     response = requests.post(url, data=data)
#     return response.json()

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     future_to_data = {executor.submit(send_request, url, data): data for data in [data1, data2]}
#     for future in concurrent.futures.as_completed(future_to_data):
#         data = future_to_data[future]
#         try:
#             response = future.result()
#             print("Response from server:", response)
#         except Exception as e:p
#             print(f"Request failed with exception: {e}")

import requests

url = 'http://91.201.215.176:3000/a'

data1 = {
    'ver': 'v1',
    'orderid': '123456789012349',
    'machid': '00000012658',
    'trackno': '1',
    'name': 'эспрессо 185 мл 2',
    'price': '2500',
    'channelid': '36',
    'randstr': 'ofowkahnmzxwhdjo',
    'timestamp': '20231206164722',
    'sign': 'd274a9bbb8b1e7d6ecd75ab9a0e3339f38b0cd1a'
}

def send_request(url, data):
    response = requests.post(url, data=data)
    try:
        response_json = response.json()
        print("success body:", response_json)
    except Exception as e:
        print("errors body:")
        print(response.content)
        print("Error:", e)

send_request(url, data1)
