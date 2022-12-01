"""
out obj_out o
"""

# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Object'
if 'BEObject' not in self.keys():
    self['BEObject'] = ''

# Outputs

if self['BEObject'] in bpy.data.objects.keys():
    obj_out = [bpy.data.objects[self['BEObject']]]
else:
    obj_out = []

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop_search(self, '["BEObject"]', bpy.data, "objects", text="Object")
    # layout.prop(self, '["BEObject"]', text="Object")


