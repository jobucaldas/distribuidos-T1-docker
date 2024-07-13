from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import zmq
import threading
import time
from functools import partial
from collections import defaultdict

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
chat = {}

@app.route('/')
def home():
    return "This page is not meant to be accessed"

@app.route('/send_frame', methods=['GET', 'POST'])
@cross_origin()
def send_video():
    content = request.json
    
    while True:
        video_data = content
        videoSocket.send(video_data)

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

@app.route('/send_message', methods=['GET', 'POST'])
@cross_origin()
def send_text():
    content = request.json
    # response = jsonify({"response": textSocket.send(f"{content['id']} - {content['username']}: {content['message']}".encode('utf-8'))})
    # response.headers.add('Access-Control-Allow-Origin', '*')
    jsonContent = {
                    "id": content['id'],
                    "user": content['user'],
                    "msg": content['msg']
                }

    return { "json": jsonContent, "response": textSocket.send_json(jsonContent) }

@app.route('/get_chat', methods=['GET', 'POST'])
@cross_origin()
def get_chat():
    content = request.json
    response = 401

    if(content['id'] in chat.keys()):
        response = chat[content['id']]

    return jsonify(response)


def receive_text():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5560")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        received_data = socket.recv_json()

        if(received_data["id"] in chat.keys()):
            chat[received_data["id"]].append({
                "user": received_data["user"],
                "msg": received_data["msg"]
            })
        else:
            chat[received_data["id"]] = [{
                "user": received_data["user"],
                "msg": received_data["msg"]
            }]


if __name__ == '__main__':
    textContext = zmq.Context()
    textSocket = textContext.socket(zmq.PUB)
    textSocket.connect("tcp://localhost:5559")

    videoContext = zmq.Context()
    videoSocket = videoContext.socket(zmq.PUB)
    videoSocket.connect("tcp://localhost:5555")

    text_receive_thread = threading.Thread(target=partial(receive_text))
    text_receive_thread.start()
    print("Starting")

    app.run(threaded=True)

    text_receive_thread.join()