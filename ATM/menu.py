from PIL import Image, ImageDraw, ImageFont
import lib.oled.SSD1331 as SSD1331
import adafruit_bme280.advanced as adafruit_bme280
import w1thermsensor
import board
import busio
import time

disp = SSD1331.SSD1331()

disp.Init()
disp.clear()

fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', 13)


def main_menu(position):
    image1 = Image.new("RGB", (disp.width, disp.height), "LIGHTBLUE")
    draw = ImageDraw.Draw(image1)

    draw.text((0, 5), f"\twithdraw", font=fontSmall, fill="BLACK")
    draw.text((0, 15), f"\tdeposit", font=fontSmall, fill="BLACK")
    draw.text((0, 25), f"\taccount balance", font=fontSmall, fill="BLACK")
    draw.text((0, 35), f"\tquit", font=fontSmall, fill="BLACK")

    # draw.text((0, position * 10 + 5), f" >", font=fontSmall, fill="BLACK")
    draw.ellipse((1, position * 10 + 3, 5, position * 10 + 7), "GREEN")

    disp.ShowImage(image1, 0, 0)


def interaction_menu(message, value=None):
    image1 = Image.new("RGB", (disp.width, disp.height), "LIGHTBLUE")
    draw = ImageDraw.Draw(image1)

    if value is not None:
        draw.text((0, 15), f"\t{value}", font=fontSmall, fill="BLACK")
    draw.text((0, 25), f"\t{message}", font=fontSmall, fill="BLACK")
    draw.text((0, 35), f"\tback", font=fontSmall, fill="BLACK")
    draw.text((50, 35), f"\tok", font=fontSmall, fill="BLACK")
    draw.ellipse((1, 33, 5, 37), "RED")
    draw.ellipse((51, 33, 55, 37), "GREEN")

    disp.ShowImage(image1, 0, 0)


def register_menu():
    image1 = Image.new("RGB", (disp.width, disp.height), "LIGHTBLUE")
    draw = ImageDraw.Draw(image1)

    draw.text((0, 25), f"\tuse card to start", font=fontSmall, fill="BLACK")
    draw.text((0, 35), f"\toff", font=fontSmall, fill="BLACK")
    draw.ellipse((1, 33, 5, 37), "RED")

    disp.ShowImage(image1, 0, 0)


def show_message(message):
    image1 = Image.new("RGB", (disp.width, disp.height), "LIGHTBLUE")
    draw = ImageDraw.Draw(image1)

    draw.text((0, 25), f"\t{message}", font=fontSmall, fill="BLACK")
