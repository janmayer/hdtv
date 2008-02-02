import os
import random
import time

# Cut using TV
class Cut:
	def __init__(self):
		self.fBgRegions = []
		
	def Cut(self, matfile, r1, r2):
		tempdir = "/home/braun/temp"
		fname = "%032X.asc" % random.randint(0, 2**128)
	
		tvcmds  = "cut activate 0; "
		tvcmds += "cut attach matrix 1; "
		tvcmds += "cut attach dir 2; "

		tvcmds += "cut dir open 2 %s; " % tempdir
		tvcmds += "cut matrix open 1 %s; " % matfile

		tvcmds += "cut marker cut enter %d; " % int(r1)
		tvcmds += "cut marker cut enter %d; " % int(r2)
		
		for bg in self.fBgRegions:
			tvcmds += "cut marker bg-gate enter %d;" % int(bg)

		tvcmds += "cut create cut; "

		tvcmds += "spec write %s'txt active; " % (tempdir + "/" + fname)

		tvcmds += "exit; "
		
		os.spawnl(os.P_WAIT, "/usr/bin/xvfb-run", 
        		             "/usr/bin/xvfb-run",
        		             "-w", "0",
        		             "/usr/local/bin/tv", "-src", "-rc", "-e", tvcmds)
        		             
		time.sleep(0.5)

		return (tempdir + "/" + fname)
	
