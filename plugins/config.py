import hdtv.options
import hdtv.cmdline

def RegisterOption(varname, option):
	# FIXME: there is probably a nicer way to do tab extension for these
	def MakeSetCmd(varname):
		return lambda args: ConfigSet([varname] + args)
	def MakeShowCmd(varname):
		return lambda args: ConfigShow([varname] + args)
	
	hdtv.options.RegisterOption(varname, option)
	hdtv.cmdline.AddCommand("config set %s" % varname, MakeSetCmd(varname), nargs=1)
	hdtv.cmdline.AddCommand("config show %s" % varname, MakeShowCmd(varname), nargs=0)


def ConfigSet(args):
	try:
		hdtv.options.Set(args[0], args[1])
	except KeyError:
		print "%s: no such option" % args[0]
	except ValueError:
		print "Invalid value (%s) for option %s" % (args[1], args[0])


def ConfigShow(args):
	if len(args) == 0:
		print hdtv.options.Str(),
	else:
		try:
			print hdtv.options.Show(args[0])
		except KeyError:
			print "%s: no such option" % args[0]
	

hdtv.cmdline.AddCommand("config set", ConfigSet, nargs=2)
hdtv.cmdline.AddCommand("config show", ConfigShow, maxargs=1)
