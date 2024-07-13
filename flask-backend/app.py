from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import zmq
import threading
import time
from functools import partial

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def home():
    return "This page is not meant to be accessed"


def send_video():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5555")
    while True:
        video_data = b"video"  # Implementar video
        socket.send(video_data)

def receive_video():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5556")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        video_data = socket.recv()
        #print("Received video data")

def send_audio():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5557")
    while True:
        audio_data = b"audio"  # Implementar audio
        socket.send(audio_data)

def receive_audio():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5558")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        audio_data = socket.recv()
        #print("Received audio data")

@app.route('/send_text', methods=['GET', 'POST'])
@cross_origin()
def send_text():
    content = request.json
    # response = jsonify({"response": textSocket.send(f"{content['id']} - {content['username']}: {content['message']}".encode('utf-8'))})
    # response.headers.add('Access-Control-Allow-Origin', '*')

    return jsonify({"response": textSocket.send_json(content)})

@app.route('/receive_text', methods=['GET', 'POST'])
@cross_origin()
def receive_text():
    content = request.json
    rTextSocket.setsockopt_string(zmq.SUBSCRIBE, content['id'])

    return rTextSocket.recv_json()

if __name__ == '__main__':
    textContext = zmq.Context()
    textSocket = textContext.socket(zmq.PUB)
    textSocket.connect("tcp://localhost:5559")

    rTextContext = zmq.Context()
    rTextSocket = rTextContext.socket(zmq.SUB)
    rTextSocket.connect("tcp://localhost:5560")

    app.run(debug=True)