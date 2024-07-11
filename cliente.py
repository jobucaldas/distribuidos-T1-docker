import cv2
import pyaudio
import zmq
import threading
import time
from functools import partial


def send_video():
    """
    Inicia a captura de vídeo da câmera e envia os quadros de vídeo codificados em JPEG via socket PUB zmq.

    O vídeo é capturado a partir da câmera padrão (índice 0). Os quadros de vídeo são capturados,
    codificados em formato JPEG e enviados continuamente através do socket zmq conectado ao endereço
    'tcp://localhost:5555'.

    """
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5555")
    cap = cv2.VideoCapture(0)  # Captura do vídeo da câmera

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        socket.send(buffer.tobytes())

    cap.release()


def receive_video():
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5556")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    while True:
        video_data = socket.recv()
        #print("Received video data")


def send_audio():
    """
    Inicia a captura de áudio do microfone e envia os dados de áudio via socket PUB zmq.

    Utiliza a biblioteca PyAudio para abrir um stream de captura de áudio com formato
    PCM de 16 bits, 1 canal e taxa de amostragem de 44100 Hz. Os dados de áudio são
    continuamente lidos do stream e enviados via socket zmq conectado ao endereço
    'tcp://localhost:5557'.

    """
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.connect("tcp://localhost:5557")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

    while True:
        data = stream.read(1024)
        socket.send(data)


def receive_audio():
    """
    Recebe dados de áudio via socket SUB zmq e reproduz os dados recebidos no dispositivo de saída.

    Configura um socket zmq do tipo SUB para se conectar ao endereço 'tcp://localhost:5558' e
    subscrição em todos os tópicos. Utiliza a biblioteca PyAudio para abrir um stream de saída
    com formato PCM de 16 bits, 1 canal e taxa de amostragem de 44100 Hz. Os dados de áudio
    recebidos via socket são escritos no stream de saída para reprodução.

    """
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:5558")
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True)

    while True:
        message = socket.recv()
        stream.write(message)


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

if __name__ == "__main__":
    username = input("Insira seu nome de usuário: ")
    text_channels = ["t1", "t2", "t3"]
    audio_channels = ["a1", "a2", "a3"]
    video_channels = ["v1", "v2", "v3"]
    print(f"Canais disponíveis:\n Texto: {text_channels}\n Audio: {audio_channels}\n Video:{video_channels}")
    selected_channels = input("Insira os canais aos quais deseja se inscrever (separados por espaço): ").split()

    video_send_thread = threading.Thread(target=send_video)
    video_receive_thread = threading.Thread(target=receive_video)
    audio_send_thread = threading.Thread(target=send_audio)
    audio_receive_thread = threading.Thread(target=receive_audio)
    text_send_thread = threading.Thread(target=send_text, args=(username, selected_channels))
    text_receive_thread = threading.Thread(target=partial(receive_text, selected_channels))

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
