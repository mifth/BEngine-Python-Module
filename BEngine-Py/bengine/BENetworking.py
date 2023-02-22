import socket
#import threading
import bpy
import select

from .Utils import BEUtils
from . import BESettings, BERunNodes

import json
import pickle
import traceback

# MAX_BYTES = 4096
# host = socket.gethostname() # get name of local machine
# host = '10.0.0.5'
# port = 55555

SERVER_SOCKET = None


def handle_client(client_socket, addr):
    # global SERVER_SOCKET

    be_paths = BESettings.START_PARAMS

    while True:
        if select.select([client_socket], [], [], 0.01)[0]:
            bpy.ops.wm.read_homefile(use_empty=True)

            context = bpy.context

            window = context.window_manager.windows[0]
            with context.temp_override(window=window):

                # Receive
                js_base_stuff_bytes = RecvAll(client_socket, be_paths.buffer_size)
                # js_base_stuff = js_base_stuff_bytes.decode()
                js_base_stuff = json.loads(js_base_stuff_bytes)

                be_base_stuff = BEUtils.BaseStuff(js_base_stuff["BaseValues"])

                # Load Nodes
                try:
                    process_gn_obj, geom_mod, node_tree = BEUtils.LoadNodesTreeFromJSON(context, be_paths, be_base_stuff)
                except Exception as e:
                    print("There was a Problem During LoadNodesTreeFromJSON.")
                    print(traceback.format_exc())

                if be_base_stuff.run_type == BESettings.RunNodesType.RunNodes:
                    js_output_data = {}

                    if node_tree:
                        # Get Data
                        try:
                            js_inputs = js_base_stuff["BEngineInputs"]
                            js_output_data = BERunNodes.RunNodes(context, be_paths, js_inputs, node_tree,
                                                                process_gn_obj, geom_mod, be_base_stuff)

                        except Exception as e:
                            print("There was a Problem During RunNodes.")
                            print(traceback.format_exc())

                            js_output_data = {}
                    else:
                        print("NodeTree is None. Probably the NodeTree is Wrong.")

                    # Send
                    client_socket.sendall(str.encode(json.dumps(js_output_data)))

                elif be_base_stuff.run_type == BESettings.RunNodesType.UpdateNodes:
                    if node_tree:
                        BERunNodes.SaveBlenderInputs(be_base_stuff, node_tree)
                    else:
                        print("NodeTree is None. Probably the NodeTree is Wrong.")


            AddBackServer(0.01)

            client_socket.close()

            print("Closing connection with %s" % str(addr))
            # client_socket.close()
            # client_sockets.remove(client_socket)

            break


def background_server():
    if select.select([SERVER_SOCKET], [], [], 0.01)[0]:
        client_socket, addr = SERVER_SOCKET.accept()
        print("Got a connection from %s" % str(addr))
#        client_sockets.append(client_socket)

#        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
#        client_thread.start()
        handle_client(client_socket, addr)

#    bpy.app.timers.register(1.0)

    return 0.1


def RunServer():
    global SERVER_SOCKET

    SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    SERVER_SOCKET.bind((BESettings.START_PARAMS.host, BESettings.START_PARAMS.port))
    SERVER_SOCKET.listen(1)

    #client_sockets = []

    AddBackServer(0)

    print('Server has started!')


def AddBackServer(first_interval_int):
    if not bpy.app.timers.is_registered(background_server):
        bpy.app.timers.register(background_server, first_interval = first_interval_int)
        # bpy.app.timers.register(background_server)


# def SendAll(sock, msg):
#     # totalsent = 0

#     # while totalsent < len(msg):
#     #     sent = sock.send(msg[totalsent:])

#     #     if sent == 0:
#     #         raise RuntimeError("socket connection broken")
#     #     totalsent = totalsent + sent
#     sock.sendall(msg)


def RecvAll(sock, buff_size):
    data = b''

    while True:
        part = sock.recv(buff_size)

        if not part:
            break

        data += part

        if len(part) < buff_size:
            # either 0 or end of data
            break

    return data