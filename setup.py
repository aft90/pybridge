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
    scripts = ['bin/pybridge', 'bin/pybridge-server'],
    data_files = [('share/applications', ['bin/pybridge.desktop']),
                  ('share/doc/pybridge', ['AUTHORS', 'COPYING', 'INSTALL', 'NEWS', 'README']),
                  ('share/pybridge/glade', glob.glob('glade/*.glade')),
                  ('share/pybridge/pixmaps', glob.glob('pixmaps/*')), ],
    
    # py2exe
    console = ['bin/pybridge-server'],
    windows = [{'script' : 'bin/pybridge', 'icon_resources' : [(1, 'pixmaps/pybridge.ico')]}],
    options = {'py2exe': {'packages' : 'encodings',
                          'includes' : 'cairo, pango, pangocairo, atk, gobject, gtk.glade' } },
)

