import zmq
import threading

def send_video():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5555")
    while True:
        video_data = b"video frame"  # Placeholder for actual video data
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
        audio_data = b"audio frame"  # Placeholder for actual audio data
        socket.send(audio_data)

def receive_audio():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5558")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        audio_data = socket.recv()
        #print("Received audio data")

def send_text(username):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5559")
    while True:
        text_data = input(" ")
        socket.send(f"{username}: {text_data}".encode('utf-8'))

def receive_text():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5560")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        text_data = socket.recv().decode('utf-8')
        #print("Received text data")
        print(text_data)

if __name__ == "__main__":
    username = input("Enter username: ")
    video_send_thread = threading.Thread(target=send_video)
    video_receive_thread = threading.Thread(target=receive_video)
    audio_send_thread = threading.Thread(target=send_audio)
    audio_receive_thread = threading.Thread(target=receive_audio)
    text_send_thread = threading.Thread(target=send_text, args=(username,))
    text_receive_thread = threading.Thread(target=receive_text)

    video_send_thread.start()
    video_receive_thread.start()
    audio_send_thread.start()
    audio_receive_thread.start()
    text_send_thread.start()
    text_receive_thread.start()

    video_send_thread.join()
    video_receive_thread.join()
    audio_send_thread.join()
    audio_receive_thread.join()
    text_send_thread.join()
    text_receive_thread.join()
