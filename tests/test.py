import time

def _test()  :
	import doctests
	doctests._test()

if __name__ == '__main__' :
	t0 = time.clock()
	_test()
	t1 = time.clock()
	print "Ran tests in %.1f seconds" % (t1 - t0)

