"""
out vec_out v
"""

import sys


# Initialization
if 'BEInputName' not in self.keys():
    self['BEInputName'] = 'Vector'
if 'BEVector' not in self.keys():
    self['BEVector'] = [0.0, 0.0, 0.0]
if 'BEVectorDefault' not in self.keys():
    self['BEVectorDefault'] = [0.0, 0.0, 0.0]
if 'BEVectorMin' not in self.keys():
    self['BEVectorMin'] = -sys.float_info.max
if 'BEVectorMax' not in self.keys():
    self['BEVectorMax'] = sys.float_info.max

# Outputs
self['BEVectorMin'] = min(self['BEVectorMin'], self['BEVectorMax'])

self['BEVectorDefault'][0] = max(self['BEVectorMin'], min(self['BEVectorDefault'][0], self['BEVectorMax']))
self['BEVector'][0] = max(self['BEVectorMin'], min(self['BEVector'][0], self['BEVectorMax']))

self['BEVectorDefault'][1] = max(self['BEVectorMin'], min(self['BEVectorDefault'][1], self['BEVectorMax']))
self['BEVector'][1] = max(self['BEVectorMin'], min(self['BEVector'][1], self['BEVectorMax']))

self['BEVectorDefault'][2] = max(self['BEVectorMin'], min(self['BEVectorDefault'][2], self['BEVectorMax']))
self['BEVector'][2] = max(self['BEVectorMin'], min(self['BEVector'][2], self['BEVectorMax']))

vec_out = [[tuple(self['BEVector'])]]

# UI
def ui(self, context, layout):
    layout.prop(self, '["BEInputName"]', text="Name")
    layout.separator()
    layout.prop(self, '["BEVector"]', text="Vector")
    layout.separator()
    layout.prop(self, '["BEVectorDefault"]', text="Default")
    layout.prop(self, '["BEVectorMin"]', text="Min")
    layout.prop(self, '["BEVectorMax"]', text="Max")
