#!/usr/bin/env python
from flask import Flask, render_template, Response
from camera import Camera
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app)

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
    return "Bell Rang!!"



if __name__ == "__main__":
    #socketio.run(app, host="0.0.0.0")
    app.run(host="0.0.0.0", debug=True, threaded=True)
