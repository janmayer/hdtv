# Do not import ROOT here!
import os

modules = ["mfile-root", "fit", "calibration", "display"]

libfmt = "lib%s.so"


def UpdateRootIncludePath():
    oldpath = os.getenv("ROOT_INCLUDE_PATH")
    oldpath = (os.pathsep + oldpath) if oldpath else ""
    os.environ["ROOT_INCLUDE_PATH"] = (
        os.pathsep.join(
            [os.path.join(os.path.dirname(__file__), module) for module in modules]
        )
        + oldpath
    )
