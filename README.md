# T1 - Sistemas Distribuídos - Grupo 10
Aplicação de video chamadas com chat de texto que utiliza uma implementação de PUB/SUB em [ZeroMQ](https://zeromq.org/)

## Grupo
- Augusto Cesar do Amaral | RA: 
- Caique Rocha Goncalves | RA: 
- João Victor Bueno de Caldas | RA: 769657
- Lucas Pereira Quadros | RA: 800981

## Requisitos
Considerando o deployment em uma máquina com ubuntu linux 24.04, é necessário instalar os seguintes pacotes antes da execução da aplicação
```sh
sudo apt update
sudo apt install npm python3-zmq python3-flask python3-flask-cors
```

## Instruções de Execução
Realize a clonagem do repositório:
```sh
git clone https://github.com/lucaspquadros/distribuidos-T1.git
```

Execute o servidor com o arquivo broker.py:
```sh
python3 broker.py
```

Execute o cliente:
```sh
cd flask-backend
python3 app.py
```

Execute a interface que se comunica com nosso cliente ZMQ-Flask:
```sh
cd meet
npm install
npm run start
```
