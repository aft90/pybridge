import time
import os
import re

def filfun(a) :
	# Python module files to exclude
	noinit = re.compile("^__init__.py[co]{0,1}$")
	nobyte = re.compile("^.+?.py[co]{1}$")
	nocvs = re.compile("^CVS$")
	# Check
	if noinit.match(a) : return 0
	if nobyte.match(a) : return 0
	if nocvs.match(a) : return 0
	return 1

def _test() :
	import doctest
	# Get module files
	modlist = os.listdir(os.getcwd()+'/pybridge')
	modlist = filter(filfun, modlist)
	# Metrics
	t0 = time.clock()
	n = 0  # counter
	# Doctest eachy module file
	for modf in modlist :
		# Strip file extension
		mod = re.sub("\.py", "", modf) 
		print "Testing " + mod + " ... "
		comm = compile('import ' + mod, '', 'exec')
		exec comm
		comm = compile('doctest.testmod(' + mod +')', '', 'exec')
		exec comm
		n = n + 1
	t1 = time.clock()
	print "Ran %d doctests in %.1f seconds" % (len(modlist), t1 - t0)


if __name__ == "__main__" :
	_test()
