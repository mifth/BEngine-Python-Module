

def RecvAll(socket, buffer_size: int):
    data = b''

    while True:
        part = socket.recv(buffer_size)

        if not part:
            break

        data += part

        if len(part) < buffer_size:
            # either 0 or end of data
            break

    return data