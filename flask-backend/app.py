from flask import Flask
import zmq
import threading
import time
from functools import partial

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"


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

def send_text(username, selected_channels):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5559")
    channel = None
    text_data = None
    print("Digite .t para trocar de canal de texto\n")
    while True:
        time.sleep(0.05)
        if channel == None:
            channel = input("Selecione o canal para enviar sua mensagem: \n")
        if channel not in selected_channels:
            print(f"Canal {channel} inválido")
            channel = None
            continue
        text_data = input("Digite sua mensagem: \n")
        if text_data == ".t":
            channel = None
            continue
        socket.send(f"{channel} - {username}: {text_data}".encode('utf-8'))

def receive_text(selected_channels):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5560")
    for channel in selected_channels:
        socket.setsockopt_string(zmq.SUBSCRIBE, channel)
    while True:
        text_data = socket.recv().decode('utf-8')
        print(text_data)

if __name__ == '__main__':
    app.run(debug=True)