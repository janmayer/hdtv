# Do not import ROOT here!
import os

modules = ['mfile-root', 'fit', 'display']

libfmt = "lib%s.so"

def UpdateRootIncludePath():
    for module in modules:
        os.environ['ROOT_INCLUDE_PATH'] = os.path.join(os.path.dirname(__file__), module) + os.pathsep + os.environ.get('ROOT_INCLUDE_PATH', '')
