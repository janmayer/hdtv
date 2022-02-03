import os
import random
import time

# Cut using TV


class Cut:
    def __init__(self):
        self.fBgRegions = []

    def Cut(self, matfile, r1, r2):
        tempdir = "/home/braun/Diplom/temp"
        fname = "%032X.asc" % random.randint(0, 2**128)

        tvcmds = "cut activate 0; "
        tvcmds += "cut attach matrix 1; "
        tvcmds += "cut attach dir 2; "

        tvcmds += "cut dir open 2 %s; " % tempdir
        tvcmds += "cut matrix open 1 %s; " % matfile

        # Sub-channel resolution is really useless here,
        # because TV cuts only with channel resolution anyway

        tvcmds += "cut marker cut enter %.1f; " % r1
        tvcmds += "cut marker cut enter %.1f; " % r2

        for bg in self.fBgRegions:
            tvcmds += "cut marker bg-gate enter %.1f;" % bg

        tvcmds += "cut create cut; "

        tvcmds += "spec write %s'txt active; " % (tempdir + "/" + fname)

        tvcmds += "exit; "

        os.spawnl(
            os.P_WAIT,
            "/usr/bin/xvfb-run",
            "/usr/bin/xvfb-run",
            "-w",
            "0",
            "/ikp/bin/tv",
            "-src",
            "-rc",
            "-e",
            tvcmds,
        )

        time.sleep(0.5)

        return tempdir + "/" + fname
