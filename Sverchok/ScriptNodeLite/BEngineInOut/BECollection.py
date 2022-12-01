"""
out coll_out o
"""

# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Collection'
if 'BECollection' not in self.keys():
    self['BECollection'] = ''

# Outputs
if self['BECollection'] in bpy.data.collections.keys():
    coll_objs = [obj for obj in bpy.data.collections[self['BECollection']].objects.values()]
    coll_out = coll_objs
else:
    coll_out = []

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop_search(self, '["BECollection"]', bpy.data, "collections", text="Collection")
