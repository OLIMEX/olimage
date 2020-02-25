import pinject
import os

# Setup environment variables
env = os.environ.copy()
env['LC_ALL'] = 'C'
env['LANGUAGE'] = 'C'
env['LANG'] = 'C'
env['DEBIAN_FRONTEND'] = 'noninteractive'
env['DEBCONF_NONINTERACTIVE_SEEN'] = 'true'

# Global paths
root = os.path.dirname(os.path.abspath(__file__))
paths = {
    'root': root,
    'configs': os.path.join(os.path.dirname(root), 'configs'),
    'overlay': os.path.join(os.path.dirname(root), 'overlay'),
    'output': os.path.join(os.path.dirname(root), 'output'),
}

# Global options
options = {}

# Global objects
objects = {}

# Objects
# TODO: Remove this
obj_graph: pinject.object_graph.ObjectGraph = None


