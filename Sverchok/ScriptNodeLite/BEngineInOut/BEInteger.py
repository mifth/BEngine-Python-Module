"""
out int_out s
"""

import sys


# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Integer'
if 'BEInteger' not in self.keys():
    self['BEInteger'] = 0
if 'BEIntegerDefault' not in self.keys():
    self['BEIntegerDefault'] = 0
if 'BEIntegerMin' not in self.keys():
    self['BEIntegerMin'] = -2147483647
if 'BEIntegerMax' not in self.keys():
    self['BEIntegerMax'] = 2147483647

# Outputs
self['BEIntegerMin'] = min(self['BEIntegerMin'], self['BEIntegerMax'])
self['BEIntegerDefault'] = max(self['BEIntegerMin'], min(self['BEIntegerDefault'], self['BEIntegerMax']))
self['BEInteger'] = max(self['BEIntegerMin'], min(self['BEInteger'], self['BEIntegerMax']))
int_out = [[self['BEInteger']]]

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop(self, '["BEInteger"]', text="Integer")
    layout.separator()
    layout.prop(self, '["BEIntegerDefault"]', text="Default")
    layout.prop(self, '["BEIntegerMin"]', text="Min")
    layout.prop(self, '["BEIntegerMax"]', text="Max")

