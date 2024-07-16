import zmq
import threading
import numpy as np
import pyaudio
import cv2 as cv
import tkinter as tk
from tkinter import scrolledtext
import base64
import zlib

def init_chat(pub_socket, topic, pub_id, context, threads):
    root = tk.Tk()
    root.title("Meet")

    chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    chat_display.grid(row=0, column=0, columnspan=2)

    msg_entry = tk.Entry(root, width=50)
    msg_entry.grid(row=1, column=0)
    msg_entry.bind("<Return>", lambda event: send_messages(event, msg_entry, pub_socket, topic, pub_id))

    send_button = tk.Button(root, text="Send", command=lambda: send_messages(None, msg_entry, pub_socket, topic, pub_id))
    send_button.grid(row=1, column=1)

    root.protocol("WM_DELETE_WINDOW", lambda: close_chat(root, context, threads))

    return root, chat_display, msg_entry

def close_chat(root, context, threads):
    print("Closing...")
    root.quit()
    context.term()

    for thread in threads:
        thread.join()

def send_messages(event, msg_entry, pub_socket, topic, pub_id):
    message = msg_entry.get()
    pub_socket.send_string(f"{topic};{message};{pub_id}")
    msg_entry.delete(0, tk.END)

def receive_messages(sub_socket, chat_display, pub_id):
    while True:
        data_bytes = sub_socket.recv()
        parts = data_bytes.split(b';')
        if len(parts) == 3:
            topic, message, publisher_id = parts
            chat_display.insert(tk.END, f"({publisher_id.decode()}) : {message.decode()}\n")
            chat_display.yview(tk.END)

def send_video(pub_socket_video, topic, pub_id):
    cap = cv.VideoCapture(0)

    if not cap.isOpened():
        print("Unable to open camera")
        return

    cap.set(cv.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv.CAP_PROP_FPS, 15)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error reading camera frame")
                break

            cv.imshow("Local camera", frame)

            _, buffer = cv.imencode('.jpg', frame, [int(cv.IMWRITE_JPEG_QUALITY), 50])
            compressed_frame = zlib.compress(buffer, level=1)

            pub_socket_video.send_multipart([topic.encode(), pub_id.encode(), compressed_frame])

            if cv.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv.destroyAllWindows()

def receive_video(sub_socket_video, pub_id):
    try:
        while True:
            topic, pub_ID, compressed_frame = sub_socket_video.recv_multipart()
            
            if pub_ID.decode() != pub_id:
                if not compressed_frame:
                    print("No data received")
                    continue

                try:
                    decompressed_frame = zlib.decompress(compressed_frame)
                    jpg_as_np = np.frombuffer(decompressed_frame, dtype=np.uint8)
                    frame = cv.imdecode(jpg_as_np, flags=cv.IMREAD_COLOR)
                except Exception as e:
                    print(f"Error decoding frame: {e}")
                    continue

                cv.namedWindow('Participant', cv.WINDOW_NORMAL)
                if frame is not None:
                    cv.imshow("Participant", frame)
                else:
                    print("Invalid frame")

                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cv.destroyAllWindows()

def send_audio(pub_socket_audio, topic, pub_id):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024)

    try:
        while True:
            data = stream.read(1024, exception_on_overflow=False)
            base64_audio = base64.b64encode(data).decode('utf-8')
            pub_socket_audio.send_multipart([topic.encode(), pub_id.encode(), base64_audio.encode()])
            #print("Audio sent")
    except Exception as e:
        print(f"Error while sending audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def receive_audio(sub_socket_audio, pub_id, topic):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    output=True,
                    frames_per_buffer=1024)

    sub_socket_audio.setsockopt(zmq.RCVTIMEO, 1000)

    try:
        while True:
            try:
                topic, pub_ID, base64_audio = sub_socket_audio.recv_multipart()
                if pub_ID.decode() != pub_id or topic.decode() != topic:
                    continue

                data = base64.b64decode(base64_audio)
                stream.write(data)
                print("Audio successfully received and played")
            except zmq.error.Again as e:
                pass
    except Exception as e:
        print(f"Error decoding or playing audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    pub_id = input("Enter username: ")
    topic = input("Enter channel: ")

    context = zmq.Context()

    pub_socket = context.socket(zmq.PUB)
    pub_socket.connect(f"tcp://localhost:5555")

    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect(f"tcp://localhost:5556")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    pub_socket_video = context.socket(zmq.PUB)
    pub_socket_video.connect(f"tcp://localhost:5589")

    sub_socket_video = context.socket(zmq.SUB)
    sub_socket_video.connect(f"tcp://localhost:5590")
    sub_socket_video.setsockopt_string(zmq.SUBSCRIBE, topic)

    pub_socket_audio = context.socket(zmq.PUB)
    pub_socket_audio.connect(f"tcp://localhost:6000")

    sub_socket_audio = context.socket(zmq.SUB)
    sub_socket_audio.connect(f"tcp://localhost:6001")
    sub_socket_audio.setsockopt_string(zmq.SUBSCRIBE, topic)

    root, chat_display, msg_entry = init_chat(pub_socket, topic, pub_id, context, [])

    threads = []

    receive_thread = threading.Thread(target=receive_messages, args=(sub_socket, chat_display, pub_id), daemon=True)
    receive_thread.start()
    threads.append(receive_thread)

    send_thread_video = threading.Thread(target=send_video, args=(pub_socket_video, topic, pub_id), daemon=True)
    send_thread_video.start()
    threads.append(send_thread_video)

    receive_thread_video = threading.Thread(target=receive_video, args=(sub_socket_video, pub_id), daemon=True)
    receive_thread_video.start()
    threads.append(receive_thread_video)

    send_thread_audio = threading.Thread(target=send_audio, args=(pub_socket_audio, topic, pub_id), daemon=True)
    send_thread_audio.start()
    threads.append(send_thread_audio)

    receive_thread_audio = threading.Thread(target=receive_audio, args=(sub_socket_audio, pub_id), daemon=True)
    receive_thread_audio.start()
    threads.append(receive_thread_audio)

    root.mainloop()
