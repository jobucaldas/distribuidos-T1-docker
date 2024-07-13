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
chat = defaultdict(list)

def mogrify(topic, msg):
    """ json encode the message and prepend the topic """
    return topic + ' ' + json.dumps(msg)

def demogrify(topicmsg):
    """ Inverse of mogrify() """
    json0 = topicmsg.find('{')
    topic = topicmsg[0:json0].strip()
    msg = json.loads(topicmsg[json0:])
    return topic, msg 

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

@app.route('/send_chat', methods=['GET', 'POST'])
@cross_origin()
def send_text():
    content = request.json
    # response = jsonify({"response": textSocket.send(f"{content['id']} - {content['username']}: {content['message']}".encode('utf-8'))})
    # response.headers.add('Access-Control-Allow-Origin', '*')

    return jsonify({
        "response": textSocket.send(
            mogrify(content['id'], {
                "user": content['user'],
                "msg": content['msg']
            })
        )
    })

@app.route('/get_chat', methods=['GET', 'POST'])
@cross_origin()
def get_chat():
    content = request.json
    return chat[content['id']]


def receive_text():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5560")

    channels = range(1, 9999)

    for channel in channels:
        socket.setsockopt_string(zmq.SUBSCRIBE, channel)

    while True:
        received_data = socket.recv().decode('utf-8')
        print(received_data)


if __name__ == '__main__':
    textContext = zmq.Context()
    textSocket = textContext.socket(zmq.PUB)
    textSocket.connect("tcp://localhost:5559")

    text_receive_thread = threading.Thread(target=partial(receive_text))
    text_receive_thread.start()

    app.run(debug=True)

    text_receive_thread.join()