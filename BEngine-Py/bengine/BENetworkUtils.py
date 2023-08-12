
FIRST_MSG_LEN = 256


def DoSend(client_socket, final_msg_bytes, is_pickle: bool):
    client_socket.sendall(str(len(final_msg_bytes)).encode())  # Send First Message
    client_socket.recv(FIRST_MSG_LEN)

    client_socket.sendall(str(int(is_pickle)).encode())  # Send Second Message
    client_socket.recv(FIRST_MSG_LEN)

    client_socket.sendall(final_msg_bytes)  # Send Final Message


def DoReceive(client_socket, buffer_size):
    first_msg_bytes = client_socket.recv(FIRST_MSG_LEN) # Get First Message
    client_socket.sendall("First Message Received".encode())

    second_msg_bytes = client_socket.recv(FIRST_MSG_LEN) # Get First Message
    client_socket.sendall("Second Message Received".encode())

    final_msg_len = int(first_msg_bytes.decode())
    is_pickle = bool(int(second_msg_bytes.decode()))

    final_msg_bytes = RecvAll(client_socket, buffer_size, final_msg_len)

    return final_msg_bytes, is_pickle


# Receive Big Data
def RecvAll(socket, buffer_size: int, msg_length: int):
    data = b''

    while True:
        part = socket.recv(buffer_size)

        if not part:
            break

        data += part

        if len(data) >= msg_length:
            break

    return data