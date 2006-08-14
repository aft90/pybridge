#!/usr/bin/env python

import glob
from distutils.core import setup
from pybridge import __version__

# To create a standalone Windows distribution, run "python setup.py py2exe"
# and then copy the GTK/etc and GTK/lib directories into dist/


try:
    import py2exe
except ImportError:
    pass

setup(
    name = 'pybridge',
    version = __version__,
    author = 'Michael Banks',
    author_email = 'michael@banksie.co.uk',
    url = 'http://sourceforge.net/projects/pybridge/',
    description = 'A free online bridge game.',
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=114287',
    packages = ['pybridge', 'pybridge.bridge', 'pybridge.interfaces', 'pybridge.network', 'pybridge.server', 'pybridge.ui'],
    package_data = {'pybridge' : ['glade/pybridge.glade', 'locale', 'pixmaps/*']},
    scripts = ['bin/pybridge', 'bin/pybridge-server'],
    
    # py2exe
    console = ['bin/pybridge-server'],
    windows = [{'script' : 'bin/pybridge', 'icon_resources' : [(1, 'pixmaps/pybridge.ico')]}],
    data_files = [('.', ['AUTHORS', 'COPYING', 'INSTALL', 'NEWS', 'README']),
	          ('glade', glob.glob('glade/*.glade')),
                  ('pixmaps', glob.glob('pixmaps/*')), ],
    options = {'py2exe': {'packages' : 'encodings',
                          'includes' : 'cairo, pango, pangocairo, atk, gobject, gtk.glade' } },
)

