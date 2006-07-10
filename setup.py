#!/usr/bin/env python

from distutils.core import setup
from pybridge.conf import PYBRIDGE_VERSION

# To create a standalone Windows executable using py2exe, run:
# python setup.py py2exe

try:
	import py2exe
except ImportError:
	pass

opts = {'py2exe': {'packages' : 'encodings',
                   'includes' : 'cairo, pango, pangocairo, atk, gobject' } }

setup(
	name = 'pybridge',
	version = PYBRIDGE_VERSION,
	author = 'Michael Banks',
	author_email = 'michaelbanks@dsl.pipex.com',
	url = 'http://sourceforge.net/projects/pybridge/',
	description = 'PyBridge allows you to play the card game of (contract) bridge, with human players, over the Internet or a local network.',
	download_url = 'http://sourceforge.net/project/showfiles.php?group_id=114287',
	packages = ['pybridge', 'pybridge.client', 'pybridge.common', 'pybridge.server'],
	scripts = ['bin/pybridge', 'bin/pybridge-server'],
	package_data = {'pybridge' : ['glade/pybridge.glade', 'pixmaps/*.png']},
	console = ['bin/pybridge', 'bin/pybridge-server'],
	options = opts,
)
