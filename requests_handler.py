import paho.mqtt.client as mqtt
import json
from database_connection import update_database, account_balance


client = mqtt.Client()
broker="localhost"

def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe("bank/request_balance")
    client.subscribe("bank/request_transaction")

def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

def process_message(client, userdata, message):
    topic = message.topic
    if topic == "bank/request_balance":
        handle_balance_request(message)
    elif topic == "bank/request_transaction":
        handle_transaction_request(message)

def handle_transaction_request(message):
    data = json.loads(message.payload.decode())
    id = data["accountId"]
    is_deposit = data["isDeposit"]
    amount = data["amount"]
    if id is not None and amount is not None and is_deposit is not None:
        is_successful = update_database(id, is_deposit, amount)
        response_data = json.dumps({"succes" : is_successful})
        response_topic = "bank/transaction_response"
        client.publish(response_topic, response_data)

def handle_balance_request(message):
    data = json.loads(message.payload.decode())
    id = data["accountId"]
    if id is not None:
        balance = account_balance(id)
        response_data = json.dumps({"balance" : balance})
        response_topic = "bank/balance_response"
        client.publish(response_topic, response_data)

    




    

    

