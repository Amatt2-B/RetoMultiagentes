from socket import socket, AF_INET, SOCK_STREAM
from messages import Commands as cmds
from messages import SimState
import struct
from model import CityModel, params

HOST = '127.0.0.1'
PORT = 42069

model = CityModel(params)
def ModelStateMessage():
    # Serialize the state to JSON
    jsonStr = SimState.fromModel(model).toJSON()
    # Encode the string into a byte array
    jsonBytes = jsonStr.encode('utf-8')

    # Prefix the package with its length in big-endian format (network)
    lengthPrefix = struct.pack('>I', len(jsonBytes))
    return lengthPrefix + jsonBytes;

def OnMessage(msg: str, sender: socket):
    if msg == cmds.START.value:
        model.setup()
        sender.sendall(ModelStateMessage())

    if msg == cmds.STEP.value:
        model.step()
        sender.sendall(ModelStateMessage())
        

def main():
    # Create a socket
    server = socket(AF_INET, SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    # Wait for a connection
    print('Waiting for connection')
    client, _ = server.accept()
    print('Client connected')

    while True:
        # Read messages until the connection is closed
        data = client.recv(4096)

        if not data:
            break
        
        # Handle message
        OnMessage(data.decode('utf-8'), client)
    
#     # Cleanup
#     client.close()
#     server.close()


if __name__ == '__main__':
    main()
