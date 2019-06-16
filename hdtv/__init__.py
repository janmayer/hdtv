import os

# This needs to happen before "import ROOT" is called the first time –
# if not, there will be a header not found error
# for *some* ROOT versions and install methods
import hdtv.rootext
hdtv.rootext.UpdateRootIncludePath()

installdir = os.path.dirname(__file__)
datadir = os.path.join(installdir, "share")
