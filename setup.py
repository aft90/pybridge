#!/usr/bin/env python

import glob
from distutils.core import setup
from pybridge import __version__

# To create a standalone Windows executable using py2exe, run:
# python setup.py py2exe

try:
	import py2exe
except ImportError:
	pass

opts = {'py2exe': {'packages' : 'encodings',
                   'includes' : 'pango, atk, gobject, gtk, gtk.glade' } }

setup(
	name = 'pybridge',
	version = __version__,
	author = 'Michael Banks',
	author_email = 'michael@banksie.co.uk',
	url = 'http://sourceforge.net/projects/pybridge/',
	description = 'A free online bridge game.',
	download_url = 'http://sourceforge.net/project/showfiles.php?group_id=114287',
	packages = ['pybridge', 'pybridge.bridge', 'pybridge.interfaces',
                'pybridge.network', 'pybridge.server', 'pybridge.ui'],
	scripts = ['bin/pybridge', 'bin/pybridge-server'],
	package_data = {'pybridge' : ['glade/pybridge.glade', 'locale/' 'pixmaps/*.png']},
	console = ['bin/pybridge', 'bin/pybridge-server'],
	data_files = [('glade', glob.glob('glade/*.glade')),
                  ('locale', glob.glob('locale/')),
                  ('pixmaps', glob.glob('pixmaps/*.png')), ],

	options = opts,
)
