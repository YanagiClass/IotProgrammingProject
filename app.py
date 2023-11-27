#!/usr/bin/env python
from flask import Flask, render_template, Response
from camera import Camera
from flask_socketio import SocketIO
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
from board import SCL, SDA
import busio
import requests
import RPi.GPIO as GPIO
import time

# threading 처리를 위해
import threading

app = Flask(__name__)
socketio = SocketIO(app)

# setting the pin no. and tact switch
button_pin = 15
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# setting buzer and frq.
bz_pin = 18
GPIO.setup(bz_pin, GPIO.OUT)
p = GPIO.PWM(bz_pin, 100)
frq = [262, 294, 330, 349, 392, 440, 493, 523]
speed = 0.5

# create I2C interface
i2c = busio.I2C(SCL, SDA)

display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# initialize OLED display
display.fill(0)
display.show()

# setting the font for display on OLED
font = ImageFont.load_default()

# create the image using mode and size(width, height)
width = display.width
height = display.height

# setting initial y position
y = 0


# define the buzer function
def buzz():
    p.start(10)
    for fr in frq:
        p.ChangeFrequency(fr)
        time.sleep(speed)
    p.stop()


# define displaying
def display_text(text):
    # create the object for drawing on Image
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)
    draw.text((0, y), text, font=font, fill=255)

    # display the image on OLED
    display.image(image)
    display.show()


# checking the door has opened
opened = False


def button_callback(channel):
    global opened
    
    if not opened:
        # 동시 실행을 위한 Threading 처리
        url = 'http://172.20.10.6:5000/bell'  # Flask 앱이 실행되고 있는 주소와 포트
        response = requests.post(url)
        display_thread = threading.Thread(target=display_text, args=("CALLING!",))
        buzz_thread = threading.Thread(target=buzz)

        display_thread.start()
        buzz_thread.start()

        # 자식 스레드의 종료 대기
        display_thread.join()
        buzz_thread.join()
    else:
        display_text("OPENED!")

    opened = not opened




#while 1:
#    time.sleep(0.1)

#p.stop()
#GPIO.cleanup()


@app.route("/")
def index():
    return render_template("index.html")


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(gen(Camera()), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/bell", methods=["POST"])
def bell():
    socketio.emit("ring_bell", {"message": "Bell Rang!!!"})
    buzz()
    return "Bell Rang!!"


GPIO.add_event_detect(button_pin, GPIO.RISING, callback=button_callback, bouncetime=300)

if __name__ == "__main__":
    #socketio.run(app, host="0.0.0.0")
    app.run(host="0.0.0.0", debug=True, threaded=True)

#p.stop()
#GPIO.cleanup()

#while 1:
#    time.sleep(0.1)


