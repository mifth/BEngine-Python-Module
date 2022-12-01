"""
out str_out T
"""

# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'String'
if 'BEString' not in self.keys():
    self['BEString'] = ''
if 'BEStringDefault' not in self.keys():
    self['BEStringDefault'] = ''

# Outputs
str_out = [[self['BEString']]]

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop(self, '["BEString"]', text="String")
    layout.separator()
    layout.prop(self, '["BEStringDefault"]', text="Default")
