"""
out color_out c
"""

# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Color'
if 'BEColor' not in self.keys():
    self['BEColor'] = (0.0, 0.0, 0.0, 1.0)
    col_prop = self.id_properties_ui("BEColor")
    #  Also it could be subtype="COLOR"
    col_prop.update(soft_min=0.0, soft_max=1.0, default=(0, 0, 0, 1.0), subtype="COLOR")  # Maybe COLOR_GAMMA
if 'BEColorDefault' not in self.keys():
    self['BEColorDefault'] = (0.0, 0.0, 0.0, 1.0)
    col_prop = self.id_properties_ui("BEColorDefault")
    #  Also it could be subtype="COLOR"
    col_prop.update(soft_min=0.0, soft_max=1.0, default=(0, 0, 0, 1.0), subtype="COLOR")  # Maybe COLOR_GAMMA

# Outputs
color_out = [[tuple(self['BEColor'])]]

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop(self, '["BEColor"]', text="Color")
    layout.separator()
    layout.prop(self, '["BEColorDefault"]', text="Default")
