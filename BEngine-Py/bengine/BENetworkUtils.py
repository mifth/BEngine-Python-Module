

def DoReceive(client_socket, buffer_size):
    msg_len_bytes = client_socket.recv(1024)
    client_socket.sendall(msg_len_bytes)
    js_received_bytes = RecvAll(client_socket, buffer_size, int(msg_len_bytes.decode()))

    return js_received_bytes


def DoSend(client_socket, bytes_data):
    client_socket.sendall(str(len(bytes_data)).encode())
    client_socket.recv(1024)
    client_socket.sendall(bytes_data)


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