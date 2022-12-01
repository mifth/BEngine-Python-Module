"""
out bool_out s
"""

# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Boolean'
if 'BEBoolean' not in self.keys():
    self['BEBoolean'] = 0
    bool_prop = self.id_properties_ui("BEBoolean")
    bool_prop.update(min=0, max=1)
if 'BEBooleanDefault' not in self.keys():
    self['BEBooleanDefault'] = 0
    bool_prop = self.id_properties_ui("BEBooleanDefault")
    bool_prop.update(min=0, max=1)

# Outputs
bool_out = [[self['BEBoolean']]]

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop(self, '["BEBoolean"]', text="Boolean")
    layout.separator()
    layout.prop(self, '["BEBooleanDefault"]', text="Default")

