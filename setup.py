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

# http://docs.python.org/library/distutils.html
setup(
    name = 'PyBridge',
    version = __version__,
    author = 'Michael Banks',
    author_email = 'michael@banksie.co.uk',
    url = 'http://www.pybridge.org/',
    description = 'A free online bridge game.',
    long_description = 'With PyBridge, you can play contract bridge with your friends, over the Internet or a local network.',
    download_url = 'http://sourceforge.net/project/showfiles.php?group_id=114287',
    packages = ['pybridge', 'pybridge.common', 'pybridge.games', 'pybridge.games.bridge', 'pybridge.games.bridge.ui', 'pybridge.interfaces', 'pybridge.network', 'pybridge.server', 'pybridge.ui'],
    scripts = ['bin/pybridge', 'bin/pybridge-server'],
    data_files = [('share/applications', ['bin/pybridge.desktop']),
                  ('share/doc/pybridge', ['AUTHORS', 'COPYING', 'INSTALL', 'NEWS', 'README']),
                  ('share/man/man6/', ['man/pybridge.6', 'man/pybridge-server.6']),
                  ('share/pybridge/glade', glob.glob('glade/*.ui')),
                  ('share/pybridge/pixmaps', glob.glob('pixmaps/*.png')+glob.glob('pixmaps/*.svg')), ],
    
    # py2exe
    console = ['bin/pybridge-server'],
    windows = [{'script' : 'bin/pybridge', 'icon_resources' : [(1, 'pixmaps/pybridge.ico')]}],
    options = {'py2exe': {'packages' : 'encodings',
                          'includes' : 'cairo, pango, pangocairo, atk, gobject, gtk.glade' } },
)

