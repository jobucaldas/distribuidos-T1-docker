import base64
import io
import sys
from flask import Flask, json, request, jsonify, render_template, Response
from flask_cors import CORS, cross_origin
import zmq
import threading
import time
from functools import partial
from collections import defaultdict
import numpy as np

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
online = {}
chat = {}
video = {}
audio = {}

@app.route('/')
def home():
    return "This page is not meant to be accessed"

@app.route('/exit_call/<id>', methods=['GET', 'POST'])
@cross_origin()
def exit_call(id):
    retrieved = request.json

    if retrieved['uid'] in online[id].keys():
        del online[id][retrieved['uid']]
    return jsonify({"response": "Removed"})

@app.route('/enter_call/<id>', methods=['GET', 'POST'])
@cross_origin()
def enter_call(id):
    retrieved = request.json

    if(id not in online.keys()):
        online[id] = {}

    online[id][retrieved['uid']] = retrieved['user']
    return jsonify({"response": "Added: " + online[id][retrieved['uid']]})

@app.route('/get_users/<id>', methods=['GET', 'POST'])
@cross_origin()
def get_online(id):
    tempUsers = []
    for user in online[id]:
        tempUsers.append(user)
    return jsonify({"users": tempUsers})

@app.route('/send_video/<idReq>/<userReq>', methods=['POST'])
@cross_origin()
def send_video(idReq, userReq):
    received = request.files.to_dict()
    file = received['frame'].stream.read()

    # TODO: Fix sending data to zmq socket
    jsonData = dict( id = idReq, user = userReq )
    videoSocket.send_multipart([base64.encodebytes(json.dumps(jsonData).encode()), base64.encodebytes(file)])
    # videoSocket.send_json(jsonData, zmq.SNDMORE)
    # videoSocket.send(base64.encodebytes(file))
    
    return { "id": idReq, "user": userReq, "response": "null" }

@app.route('/get_video/<id>/<user>', methods=['GET', 'POST'])
@cross_origin()
def get_video(id, user):
    if(id not in video.keys()):
        video[id] = {}
        return jsonify({"res": "No video shown"})

    if(user not in video[id].keys()):
        return jsonify({"res": "No video for user"})
    
    data = video[id][user]

    return Response(data, mimetype='image/jpeg')

@app.route('/send_audio', methods=['GET', 'POST'])
@cross_origin()
def send_audio():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5557")
    while True:
        audio_data = b"audio"  # Implementar audio
        socket.send(audio_data)

@app.route('/get_audio', methods=['GET', 'POST'])
@cross_origin()
def get_audio():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5558")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        audio_data = socket.recv()
        #print("Received audio data")

@app.route('/send_message/<id>/<user>', methods=['GET', 'POST'])
@cross_origin()
def send_text(id, user):
    content = request.json

    jsonContent = {
                    "id": id,
                    "user": user,
                    "msg": content['msg']
                }

    return { "json": jsonContent, "response": textSocket.send_json(jsonContent) }

@app.route('/get_chat/<id>', methods=['GET', 'POST'])
@cross_origin()
def get_chat(id):
    response = 401

    if(id in chat.keys()):
        response = chat[id]

    return jsonify(response)

def receive_audio():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5558")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        received_data = socket.recv_json()

        if(received_data["id"] not in audio.keys()):
            audio[received_data["id"]] = {}

        audio[received_data["id"]][received_data["user"]] = received_data["audio"]

def receive_video():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5556")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    while True:
        # received_json = socket.recv_json()
        # received_data = socket.recv()
        received_json, received_data = socket.recv_multipart()
        received_json = json.loads(base64.decodebytes(received_json).decode())

        if(received_json['id'] not in video.keys()):
            video[received_json['id']] = {}

        video[received_json['id']][received_json['user']] = base64.decodebytes(received_data)

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

    audioContext = zmq.Context()
    audioSocket = audioContext.socket(zmq.PUB)
    audioSocket.connect("tcp://localhost:5557")

    text_receive_thread = threading.Thread(target=partial(receive_text))
    video_receive_thread = threading.Thread(target=partial(receive_video))
    audio_receive_thread = threading.Thread(target=partial(receive_audio))

    text_receive_thread.start()
    video_receive_thread.start()
    audio_receive_thread.start()

    app.run(threaded=True)

    text_receive_thread.join()
    video_receive_thread.join()
    audio_receive_thread.join()