#!/usr/bin/env python

from distutils.core import setup

from pybridge.conf import *

setup(  name=NAME,
		version=VERSION,
		description=COMMENTS,
		url=URL,
		author=AUTHORS,
		author_email=AUTHORS_EMAIL,
		packages=[NAME],
		scripts=['scripts/' + NAME],
	 )
