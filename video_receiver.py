import cv2
import zmq
import numpy as np

# Contexto zmq para comunicação
context = zmq.Context()

# Socket para se conectar ao servidor de envio de vídeo
socket = context.socket(zmq.SUB)
socket.connect("tcp://localhost:5556")

# Inscreve-se em todos os tópicos (canais)
socket.setsockopt_string(zmq.SUBSCRIBE, '')

# Loop para receber e exibir o vídeo recebido
while True:
    # Recebe o quadro de vídeo como uma mensagem
    message = socket.recv()

    # Converte os dados recebidos em um array numpy de uint8
    np_arr = np.frombuffer(message, dtype=np.uint8)

    # Decodifica o quadro de imagem usando OpenCV
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Exibe o quadro de imagem em uma janela com o título 'Received Video'
    cv2.imshow('Received Video', frame)

    # Espera por 1 milissegundo e verifica se a tecla 'q' foi pressionada para sair do loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fecha todas as janelas abertas do OpenCV
cv2.destroyAllWindows()
