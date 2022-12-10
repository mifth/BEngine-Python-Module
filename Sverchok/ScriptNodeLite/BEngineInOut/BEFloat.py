"""
out float_out s
"""

import sys


# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Float'
if 'BEFloat' not in self.keys():
    self['BEFloat'] = 0.0
if 'BEFloatDefault' not in self.keys():
    self['BEFloatDefault'] = 0.0
if 'BEFloatMin' not in self.keys():
    self['BEFloatMin'] = -sys.float_info.max
if 'BEFloatMax' not in self.keys():
    self['BEFloatMax'] = sys.float_info.max

# Outputs
self['BEFloatMin'] = min(self['BEFloatMin'], self['BEFloatMax'])
self['BEFloatDefault'] = max(self['BEFloatMin'], min(self['BEFloatDefault'], self['BEFloatMax']))
self['BEFloat'] = max(self['BEFloatMin'], min(self['BEFloat'], self['BEFloatMax']))
float_out = [[self['BEFloat']]]

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop(self, '["BEFloat"]', text="Float")
    layout.separator()
    layout.prop(self, '["BEFloatDefault"]', text="Default")
    layout.prop(self, '["BEFloatMin"]', text="Min")
    layout.prop(self, '["BEFloatMax"]', text="Max")
