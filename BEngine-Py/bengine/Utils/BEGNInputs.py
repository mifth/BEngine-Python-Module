import bpy


def GetNodeTreeInputs(node_tree):
    # Blen 3
    if bpy.app.version[0] == 3:
        return node_tree.inputs.items()

    # Blen 4
    else:
        inputs = []

        for item in node_tree.interface.items_tree:
            if item.item_type == 'SOCKET':
                if item.in_out == 'INPUT':
                    inputs.append(item)

        return inputs


def GetInputIdentifier(input):
    # Blen 3
    if bpy.app.version[0] == 3:
        return input[1].identifier

    # Blen 4
    return input.identifier


def GetInputType(input):
    # Blen 3
    if bpy.app.version[0] == 3:
        return input[1].type

    # Blen 4
    else:
        input_class = str(type(input))

        if "NodeTreeInterfaceSocketFloat" in str(type(input)):
            return "VALUE"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketBool):
            return "BOOLEAN"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketObject):
            return "OBJECT"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketCollection):
            return "COLLECTION"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketColor):
            return "RGBA"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketImage):
            return "IMAGE"
        elif "NodeTreeInterfaceSocketInt" in str(type(input)):
            return "INT"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketMaterial):
            return "MATERIAL"
        elif isinstance(input, bpy.types.NodeTreeInterfaceSocketString):
            return "STRING"
        elif "NodeTreeInterfaceSocketVector" in str(type(input)):
            return "VECTOR"

    return "UNSUPPORTED_TYPE"


def GetInputName(input):
    # Blen 3
    if bpy.app.version[0] == 3:
        return input[1].name

    # Blen 4
    return input.name