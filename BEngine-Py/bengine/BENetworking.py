import bpy

import socket
import threading
import select

from .Utils import BEUtils
from . import BESettings, BERunNodes, BENetworkUtils
from .BEStartParams import StartParams

import json
import traceback

import pickle

SERVER_SOCKET = None
client_socket_glob = None
addr_glob = None


def HandleClient():
    global client_socket_glob
    global addr_glob

    client_socket = client_socket_glob
    addr = addr_glob

    start_params = StartParams()

    while True:
        if select.select([client_socket], [], [], 0.01)[0]:
            bpy.ops.wm.read_homefile(use_empty=True)

            window = bpy.context.window_manager.windows[0]
            with bpy.context.temp_override(window=window):

                context = bpy.context

                # Receive
                js_received_bytes, is_pickle = BENetworkUtils.DoReceive(client_socket, start_params.buffer_size)
                if is_pickle:
                    js_input_data = pickle.loads(js_received_bytes)
                else:
                    js_input_data = json.loads(js_received_bytes)


                be_base_stuff = BEUtils.BaseStuff(js_input_data["BaseValues"])

                # Load Nodes
                try:
                    process_gn_obj, geom_mod, node_tree = BEUtils.LoadNodesTreeFromJSON(context, be_base_stuff)
                except Exception as e:
                    print("There was a Problem During LoadNodesTreeFromJSON.")
                    print(traceback.format_exc())

                # Run Nodes!
                if be_base_stuff.run_type == BESettings.RunNodesType.RunNodes:
                    js_output_data = {}

                    if node_tree:
                        # Get Data
                        try:
                            js_from_engine = js_input_data["FromEngineData"]
                            js_output_data = BERunNodes.RunNodes(context, js_from_engine, node_tree,
                                                                process_gn_obj, geom_mod, be_base_stuff)

                        except Exception as e:
                            print("There was a Problem During RunNodes.")
                            print(traceback.format_exc())

                            js_output_data = {}
                    else:
                        print("NodeTree is None. Probably the NodeTree is Wrong.")

                    # Send
                    if is_pickle:
                        send_data = pickle.dumps(js_output_data)
                    else:
                        send_data = str.encode(json.dumps(js_output_data))

                    BENetworkUtils.DoSend(client_socket, send_data, is_pickle)

                # Update Nodes! Save/Send Blender Inputs
                elif be_base_stuff.run_type == BESettings.RunNodesType.UpdateNodes:
                    if node_tree:
                        if be_base_stuff.engine_type == BESettings.EngineType.Unreal:
                            inputs_to_send = BERunNodes.MakeInputsJS(node_tree)

                            if is_pickle:
                                inputs_to_send = pickle.dumps(inputs_to_send)
                            else:
                                inputs_to_send = str.encode(json.dumps(inputs_to_send))

                            BENetworkUtils.DoSend(client_socket, inputs_to_send, is_pickle)

                            print("Inputs are Sent!")

                        else:
                            BERunNodes.SaveBlenderInputs(be_base_stuff, node_tree)
                    else:
                        print("NodeTree is None. Probably the NodeTree is Wrong.")

            print("Closing connection with %s" % str(addr))

            client_socket.close()
            # client_sockets.remove(client_socket)

            break


def RunServer():
    global SERVER_SOCKET

    start_params = StartParams()

    SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, start_params.buffer_size)
    SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    SERVER_SOCKET.bind((start_params.host, start_params.port))
    SERVER_SOCKET.listen(1)

    #client_sockets = []

    AddBackgroundServer(0)

    print('Server has started!')


def BackgroundServer():
    while True:
        if select.select([SERVER_SOCKET], [], [], 0.01)[0]:

            global client_socket_glob
            global addr_glob

            client_socket, addr = SERVER_SOCKET.accept()
            print("Got a connection from %s" % str(addr))

            client_socket_glob = client_socket
            addr_glob = addr

            # HandleClient()
            bpy.app.timers.register(HandleClient, first_interval=0)


def AddBackgroundServer(first_interval_int):
    # if not bpy.app.timers.is_registered(BackgroundServer):
    #     bpy.app.timers.register(BackgroundServer, first_interval = first_interval_int)
    #     # bpy.app.timers.register(BackgroundServer)

    client_thread = threading.Thread(target=BackgroundServer, args=())
    client_thread.daemon = True
    client_thread.start()