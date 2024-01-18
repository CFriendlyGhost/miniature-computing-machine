#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from mfrc522 import MFRC522
from menu import *
import json
from config import *
import RPi.GPIO as GPIO
import board
import neopixel

# The terminal ID - can be any string.
terminal_id = "T0"
# The broker name or IP address.
broker = "localhost"
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client()

pixels = neopixel.NeoPixel(
    board.D18, 8, brightness=1.0 / 32, auto_write=False)

data = {
    "is_successful": None,
    "amount": None,
    "account_id": None
}

buttons = {
    "red": False,
    "green": False
}

encoder_position = 0
encoder_transfer = 0
encoder_mode = None


def buzzer_state(state):
    GPIO.output(buzzerPin, not state)  # pylint: disable=no-member


def buzzer():
    buzzer_state(True)
    time.sleep(1)
    buzzer_state(False)


def blink():
    for i in range(3):
        pixels.fill((0, 255, 0))
        pixels.show()
        time.sleep(0.2)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(0.2)


def light_pixels(color):
    pixels.fill(color)
    pixels.show()


def rfid_read():
    MIFAREReader = MFRC522()
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    if status == MIFAREReader.MI_OK:
        (status, uid) = MIFAREReader.MFRC522_Anticoll()
        if status == MIFAREReader.MI_OK:
            num = 0
            for i in range(0, len(uid)):
                num += uid[i] << (i * 8)

            buzzer()
            blink()
            return num


def handle_balance_response(message):
    data["amount"] = json.loads(message.payload.decode())["value"]


def handle_transaction_response(message):
    data["is_successful"] = json.loads(message.payload.decode())["success"]


def process_message(client, userdata, message):
    topic = message.topic
    if topic == "bank/balance_response":
        handle_balance_response(message)
    elif topic == "bank/transaction_response":
        handle_transaction_response(message)
    # Print message to console.


def send_message_balance(account_id):
    request_data = json.dumps({"accountId": account_id})
    client.publish("bank/request_balance", request_data)


def send_message_transaction(account_id, is_deposit, amount):
    request_data = json.dumps({
        "accountId": account_id,
        "isDeposit": is_deposit,
        "amount": amount
    })
    client.publish("bank/request_transaction", request_data)


def connect_to_broker():
    # Connect to the broker.
    client.connect(broker)

    client.on_message = process_message
    # Starts client and subscribe.
    client.loop_start()
    client.subscribe("bank/balance_response")
    client.subscribe("bank/transaction_response")


def disconnect_from_broker():
    # Disconnet the client.
    client.loop_stop()
    client.disconnect()


def turn_encoder(channel):

    encoder_right_current_state = GPIO.input(encoderRight)

    if encoder_mode == "menu position":
        global encoder_position

        if encoder_right_current_state == 0 and encoder_position > 0:
            encoder_position -= 1
        elif encoder_position < 3:
            encoder_position += 1

    if encoder_mode == "transfer value":
        global encoder_transfer

        if encoder_right_current_state == 0 and encoder_transfer > 0:
            encoder_transfer -= 100
        elif encoder_transfer < 1000:
            encoder_transfer += 100



def register_loop():
    last_read = None
    while True:
        num = rfid_read()
        if num is not None and num != last_read:
            send_message_balance(num)
            data["account_id"] = num
            return True
        last_read = num

        register_menu()

        if buttons["red"]:
            buttons["red"] = False
            return False


def menu_loop():
    while True:
        main_menu(encoder_position)

        if buttons["green"]:
            buttons["green"] = False
            return encoder_position


def balance_menu():
    while True:
        amount = data["amount"]
        if amount is None:
            amount = "Waiting..."
        interaction_menu("balance:", amount)

        if buttons["green"]:
            buttons["green"] = False
            return

        if buttons["red"]:
            buttons["red"] = False
            return


def transfer_response_loop():
    while data["is_successful"] is None:
        show_message("waiting for response")

    message, color = ("transfer successful", (0, 255, 0)) if data["is_successful"] else ("transfer failed", (255, 0, 0))
    data["is_successful"] = None

    while True:
        light_pixels(color)
        interaction_menu(message)

        if buttons["green"]:
            buttons["green"] = False
            light_pixels((0, 0, 0))
            return

        if buttons["red"]:
            buttons["red"] = False
            light_pixels((0, 0, 0))
            return


def transfer_loop(is_deposit):
    message = "deposit:" if is_deposit else "withdraw:"
    while True:
        interaction_menu(message, encoder_transfer)
        if buttons["red"]:
            buttons["red"] = False
            return
        if buttons["green"]:
            buttons["green"] = False
            send_message_transaction(data["account_id"], is_deposit, encoder_transfer)
            transfer_response_loop()


def loop():
    global encoder_mode

    if not register_loop():
        return

    while True:
        encoder_mode = "menu position"
        menu_loop()
        position = encoder_position
        encoder_mode = "transfer value"
        match position:
            case 0:
                transfer_loop(False)
            case 1:
                transfer_loop(True)
            case 2:
                balance_menu()
            case 3:
                return


def button_pressed_callback(color):
    buttons[color] = True


def main():
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=lambda _: button_pressed_callback("red"), bouncetime=200)
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=lambda _: button_pressed_callback("green"), bouncetime=200)
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=turn_encoder, bouncetime=200)

    connect_to_broker()

    loop()

    disconnect_from_broker()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        disp.clear()
        disp.reset()
