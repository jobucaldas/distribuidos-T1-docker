import zmq
import threading

def broker_video():
    context = zmq.Context()
    frontend = context.socket(zmq.SUB)
    frontend.bind("tcp://*:5555")
    frontend.setsockopt_string(zmq.SUBSCRIBE, "")
    backend = context.socket(zmq.PUB)
    backend.bind("tcp://*:5556")

    while True:
        json = frontend.recv_json()
        message = frontend.recv()
        backend.send_json(json, zmq.SNDMORE)
        backend.send(message)

def broker_audio():
    context = zmq.Context()
    frontend = context.socket(zmq.SUB)
    frontend.bind("tcp://*:5557")
    frontend.setsockopt_string(zmq.SUBSCRIBE, "")
    backend = context.socket(zmq.PUB)
    backend.bind("tcp://*:5558")

    while True:
        message = frontend.recv()
        backend.send(message)

def broker_text():
    context = zmq.Context()
    frontend = context.socket(zmq.SUB)
    frontend.bind("tcp://*:5559")
    frontend.setsockopt_string(zmq.SUBSCRIBE, "")
    backend = context.socket(zmq.PUB)
    backend.bind("tcp://*:5560")

    while True:
        message = frontend.recv()
        backend.send(message)

if __name__ == "__main__":
    video_thread = threading.Thread(target=broker_video)
    audio_thread = threading.Thread(target=broker_audio)
    text_thread = threading.Thread(target=broker_text)

    video_thread.start()
    audio_thread.start()
    text_thread.start()

    print("broker started")

    video_thread.join()
    audio_thread.join()
    text_thread.join()
