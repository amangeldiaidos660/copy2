import requests
from flask import Flask, request, jsonify
from datetime import datetime
import psycopg2
from psycopg2 import sql
from flask_cors import CORS
import hashlib


app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'user': 'postgres',
    'password': 'Sh6asqz9',
    'host': '91.201.215.176',
    'port': 5432,
    'database': 'kaspi'
}

def get_bank_order_id(orderid):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        
        sql_query = """
            SELECT transid FROM tr_orders WHERE orderid = %s
        """

        cur.execute(sql_query, (orderid,))
        result = cur.fetchone()

        if result:
            bank_order_id = result[0]
            print(f"get_bank_order_id({orderid}) returned: {bank_order_id}")
            return bank_order_id
        else:
            return None  
    except Exception as e:
        print(f'Ошибка при получении bank_order_id: {e}')
        return None
    finally:
        cur.close()
        conn.close()



def check_payment_status(orderid):
    bank_order_id = get_bank_order_id(orderid)  

    if bank_order_id is not None:
        bank_check_url = f'https://nscomp.kz/checkord/{bank_order_id}'
        bank_response = requests.get(bank_check_url)

        if bank_response.status_code == 200:
            bank_data = bank_response.json()
            print(f"Response from {bank_check_url}: {bank_data}")
            if bank_data != False:
                return True
            else:
                return False
            
            # bank_data = bank_response.json()
            # result = bank_data.get('result')
            # print(f"check_payment_status({orderid}) returned: {result}")
           
        else:
            print(f"check_payment_status({orderid}) returned: 'Status not 200 from nscomp.kz/checkord/: {bank_response.status_code}'")
            return False
    else:
        print(f"check_payment_status({orderid}) returned: 'bank_order_id not found for the given orderid'")
        return False
    


def get_qr_link(amount, machid):
    try:
        amount_in_kopeks = int(float(amount)) / 100

        static_url = 'https://kaspi.kz/pay/NSCompany?service_id=6692&10661='
        machid = machid.lstrip('0')

        bank_url = f'https://nscomp.kz/neword/{machid}/{amount_in_kopeks}'

        bank_response = requests.get(bank_url)

        #print(amount_in_kopeks, type(amount_in_kopeks), machid.lstrip('0'), type(machid.lstrip('0')))
 

        if bank_response.status_code == 200:
            bank_data = bank_response.json()
            bank_order_id = bank_data.get('id', '')

            final_url = f'{static_url}{bank_order_id}'
            #print(bank_url)
            return final_url, bank_order_id
        else:
            return None, None

    except ValueError as e:
        raise ValueError(f'Invalid amount or error from bank: {e}')

    
@app.route('/a', methods=['GET', 'POST'])
def process_request_a():
    if request.method == 'GET' or request.method == 'POST':
        data = request.form if request.method == 'POST' else request.args  
        required_params = ['ver', 'orderid', 'machid', 'trackno', 'name', 'price', 'channelid', 'randstr', 'timestamp', 'sign']
        
        if all(param in data for param in required_params):
            ver = data['ver']
            orderid = data['orderid']
            machid = data['machid']
            trackno = data['trackno']
            name = data['name']
            price = data['price']
            channelid = data['channelid']
            randstr = data['randstr']
            timestamp = data['timestamp']
            sign = data['sign']

            qr_code, bank_order_id = get_qr_link(price, machid)

            # save_to_postgresql(orderid, bank_order_id)

            # response_data = {
            #     'orderid': orderid,
            #     'torderid': '12345',
            #     'code': '1',
            #     'msg': 'Успешно обработано',
            #     'twocode': qr_code
            # }
            # return jsonify(response_data), 200
        
            

            if qr_code is not None and bank_order_id is not None:
                save_to_postgresql(orderid, bank_order_id)

                response_data = {
                    'orderid': orderid,
                    'torderid': '12345',
                    'code': '1',
                    'msg': 'Успешно обработано',
                    'twocode': qr_code
                }
                return jsonify(response_data), 200
            else:
                error_response = {'error': 'Ошибка при получении QR-кода или ID от сервера банка 1', 'twocode': qr_code, 'bankorder': bank_order_id}
                return jsonify(error_response), 500
        else:
            error_response = {'error': 'Недостаточно параметров'}
            return jsonify(error_response), 400  
    else:
        error_response = {'error': 'Метод не поддерживается'}
        return jsonify(error_response), 405

    































def save_to_postgresql(orderid, bank_order_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # tr_orders
        sql_query = """
            INSERT INTO tr_orders (transid, ver, orderid, machid, trackno, name, price, channelid, randstr, timestamp, sign, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        request_data = {
            'ver': request.form.get('ver'),
            'orderid': str(request.form.get('orderid')),
            'machid': request.form.get('machid'),
            'trackno': request.form.get('trackno'),
            'name': request.form.get('name'),
            'price': int(float(request.form.get('price')) / 100),
            'channelid': request.form.get('channelid'),
            'randstr': request.form.get('randstr'),
            'timestamp': request.form.get('timestamp'),
            'sign': request.form.get('sign'),
            'status': False
        }

        transid_value = bank_order_id

        # transid_value = str(bank_order_id)
        

        cur.execute(sql_query, (
            transid_value,
            request_data['ver'], request_data['orderid'], request_data['machid'],
            request_data['trackno'], request_data['name'], request_data['price'],
            request_data['channelid'], request_data['randstr'], request_data['timestamp'],
            request_data['sign'], request_data['status']
        ))

        
        conn.commit()
        cur.close()
        conn.close()

        return 'Данные успешно записаны в PostgreSQL', None
    except Exception as e:
        return f'Ошибка при записи данных в PostgreSQL: {e}', None



def update_payment_status(orderid):
    try:
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        
        sql_query = """
            UPDATE tr_orders
            SET status = %s
            WHERE orderid = %s
        """

        
        new_status = True

        
        cur.execute(sql_query, (new_status, orderid))

        
        conn.commit()
        cur.close()
        conn.close()

        return True
    except Exception as e:
        print(f"Ошибка при обновлении статуса заказа: {e}")
        return False

    
def check_delivery_status(orderid, status):
    bank_order_id = get_bank_order_id(orderid)  

    if bank_order_id is not None:
        bank_check_url = f'https://nscomp.kz/checkord/{bank_order_id}'
        bank_response = requests.get(bank_check_url)

        if bank_response.status_code == 200:
            bank_data = bank_response.json()
            

            if bank_data and status == '1':
                return '1'
            else:
                return '0'
        else:
            return 'status not 200 from nscomp.kz/checkord/'
    else:
        return 'bank_order_id not found for the given orderid'
    




@app.route('/b', methods=['GET', 'POST'])
def process_request_b():
    if request.method == 'GET' or request.method == 'POST':
        data = request.form if request.method == 'POST' else request.args  
        required_params = ['ver', 'orderid', 'torderid', 'machid', 'channelid', 'randstr', 'timestamp', 'sign']
        if all(param in data for param in required_params):
            ver = data['ver']
            orderid = data['orderid']
            to_orderid = data['torderid']
            machid = data['machid']
            channelid = data['channelid']
            randstr = data['randstr']
            timestamp = data['timestamp']
            sign = data['sign']

            result = check_payment_status(orderid)

            

            if result:
                code = '1'
                msg = 'Успешная оплата'
                
                if update_payment_status(orderid):
                    pass  
                else:
                    code = '4'  
                    msg = 'Заказ не найден или уже закрыт'
            else:  
                code = '2'
                msg = 'Ожидание'


            mockup_response = {
                'orderid': orderid,
                'torderid': to_orderid,
                'code': code,
                'msg': msg
            }

            print(f"process_request_b({orderid}) returned: {mockup_response}")
            return jsonify(mockup_response), 200
        else:
            error_response = {'error': 'Недостаточно параметров'}
            print(f"process_request_b({orderid}) returned: {error_response}")
            return jsonify(error_response), 400
    else:
        error_response = {'error': 'Метод не поддерживается'}
        print(f"process_request_b({orderid}) returned: {error_response}")
        return jsonify(error_response), 405



@app.route('/c', methods=['GET', 'POST'])
def process_request_c():
    if request.method == 'GET' or request.method == 'POST':
        data = request.form if request.method == 'POST' else request.args  
        required_params = ['Ver', 'Orderid', 'Torderid', 'Machid', 'Trackno', 'Status', 'Errinfo', 'Randstr', 'Timestamp', 'Sign']
        if all(param in data for param in required_params):
            Ver = data['Ver']
            Orderid = data['Orderid']
            Torderid = data['Torderid']
            Machid = data['Machid']
            Trackno = data['Trackno']
            Status = data['Status']
            Errinfo = data['Errinfo']
            Randstr = data['Randstr']
            Timestamp = data['Timestamp']
            Sign = data['Sign']

            result = check_delivery_status(Orderid, Status)

            if result == '1':  
                code = '1'
                msg = 'Успешное подтверждение'
            else:  
                code = '0'
                msg = 'ошибка в подтверждений или статус не совпадает'

            response_data = {
                'orderid': Orderid,
                'torderid': Torderid,
                'code': code,
                'msg': msg
            }

            return jsonify(response_data), 200
        else:
            error_response = {'error': 'Недостаточно параметров'}
            return jsonify(error_response), 400
    else:
        error_response = {'error': 'Метод не поддерживается'}
        return jsonify(error_response), 405
    



@app.route('/crm', methods=['GET', 'POST'])
def crm():
    try:
        command = request.json.get('command')
        if command == 'login':
            return login()
        elif command == 'getaccounts':
            return get_accounts()
        elif command == 'getstatic':
            return get_static()
        else:
            return jsonify({'success': False, 'error': 'Invalid command'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def login():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        email = request.json.get('email')
        password = request.json.get('password')
        hashed_password = hash_password(password)
        cur.execute(sql.SQL("SELECT * FROM qr_user_auth WHERE login = %s AND pwd = %s"), (email, hashed_password))
        user = cur.fetchone()

        if user:
            user_data = {
                'id': user[0], 
                'pid': user[1],
                'login': user[2],
                'email': user[4],
                'idrole': user[6]
            }
            return jsonify({'success': True, 'user': user_data})
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    finally:
        if conn:
            conn.close()


def get_accounts():
    try:
        user_id = request.json.get('userId')
        print(f"userId: {user_id}")

        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute(sql.SQL("SELECT * FROM qr_accounts WHERE pid = %s"), (user_id,))
        accounts = cur.fetchall()

        if accounts:
            account_data = []
            for account in accounts:
                account_info = {
                    'id': account[0],
                    'pid': account[1],
                    'name': account[2],
                    'bin': account[3],
                    'devices': [] 
                }

                cur.execute(sql.SQL("SELECT * FROM qr_devices WHERE pid = %s"), (account[0],))
                devices = cur.fetchall()

                if devices:
                    for device in devices:
                        device_info = {
                            'id': device[0],
                            'name': device[1],
                            'pid': device[4],
                            'devtype': device[11],
                            'machid': str(device[12]).zfill(11),
                        }
                        account_info['devices'].append(device_info)

                account_data.append(account_info)

            print(f"Sending accounts data: {account_data}")
            return jsonify({'success': True, 'accounts': account_data})
        else:
            return jsonify({'success': False, 'error': 'User not found in qr_accounts'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    finally:
        if conn:
            conn.close()


def get_static():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        data = request.json

        pid = data.get('pid')
        device_id = data.get('id')
        machid = data.get('machid')
        devtype = data.get('devtype')

        if devtype == "1":
            cur.execute(sql.SQL("SELECT orderid, name, price, timestamp, status FROM tr_orders WHERE machid = %s"), (machid,))
            result = cur.fetchall()
            response_data = {
                'res': [{'name': row[1], 'price': row[2], 'date': row[3], 'status': row[4], 'transid': row[0]} for row in result],
            } 
        else:
            cur.execute(
                sql.SQL("SELECT txn_id, dt, amount FROM qr_transactions WHERE account = %s"), (device_id,)
            )
            transaction_result = cur.fetchall()

            cur.execute(
                sql.SQL("SELECT name, amount FROM qr_prices WHERE pid = %s"), (device_id,)
            )
            price_results = cur.fetchall()
            
            price_mapping = {str(price_result[1]): price_result[0] for price_result in price_results}

            response_data = {
                'res': [{
                    'name': price_mapping.get(str(row[2]), "Unknown"),
                    'price': row[2],
                    'date': row[1],
                    'status': True,
                    'transid': row[0]
                } for row in transaction_result],
            }

        return jsonify({'success': True, 'data': response_data})

    except Exception as e:
        print(f"Error in get_static: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)





# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
    
# def get_bank_order_id(orderid):
#     ref = db.reference('orders')
#     order_ref = ref.child(orderid)
#     bank_order_id = order_ref.child('bank_order_id').get()

#     return bank_order_id
    

# def get_qr_link(amount):
#     try:
#         amount_in_kopeks = int(float(amount))/100
        
#         bank_url = f'https://forpay.kz/neword/{amount_in_kopeks}'
#         bank_response = requests.get(bank_url)

#         if bank_response.status_code == 200:
#             bank_data = bank_response.json()
#             qr_code = bank_data.get('qr', '') 
#             bank_order_id = bank_data.get('id', '')  
#             return qr_code, bank_order_id
#         else:
#             return 'status not 200 from forpay.kz/neword/',  None 
#     except ValueError as e:
#         return f'Invalid amount: {e}', None
    

# cred = credentials.Certificate("bilimallserver-firebase-adminsdk-wsusu-1b35af3c1f.json")  
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://bilimallserver-default-rtdb.asia-southeast1.firebasedatabase.app/'
# })

# def save_to_firebase(orderid, bank_order_id):
#     ref = db.reference('orders')

#     request_data = {
#         'ver': request.form.get('ver'),
#         'orderid': request.form.get('orderid'),
#         'machid': request.form.get('machid'),
#         'trackno': request.form.get('trackno'),
#         'name': request.form.get('name'),
#         'price': int(float(request.form.get('price')) / 100),
#         'channelid': request.form.get('channelid'),
#         'randstr': request.form.get('randstr'),
#         'timestamp': request.form.get('timestamp'),
#         'sign': request.form.get('sign'),
#         'status': 'Не оплачен'
#     }
    
#     ref.child(orderid).set({
#         'request_data': request_data,
#         'bank_order_id': bank_order_id
#     })
    

# def update_payment_status(orderid):
#     ref = db.reference('orders')

    
#     order_ref = ref.child(orderid)
#     order = order_ref.get()

#     if order:
        
#         order['request_data']['status'] = 'Оплачен'
#         ref.child(orderid).set(order)
#         return True
#     else:
#         print(f"Ошибка: заказ с orderid {orderid} не найден")
#         return False
    

# def log_requests():
#     current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  
#     log_data = f"Request time: {current_time}\n"
#     log_data += f"Request method: {request.method}\n"
#     log_data += f"Request path: {request.path}\n"
#     log_data += f"Request body: {request.get_data(as_text=True)}\n"
#     log_data += "-----------------------------------\n"

#     with open('requests_log.txt', 'a') as log_file:
#         log_file.write(log_data)


# @app.before_request
# def log_request_info():
#     log_requests()