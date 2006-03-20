#!/usr/bin/env python

from distutils.core import setup

setup(name = 'pybridge',
      version = '0.1',
      author = 'Michael Banks',
      author_email = 'michael@banksie.co.uk',
      url = 'http://sourceforge.net/projects/pybridge',
      description = 'Online bridge made easy.',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=114287',
      packages = ['pybridge.client', 'pybridge.common', 'pybridge.server'],
      scripts = ['scripts/pybridge-client.py', 'scripts/pybridge-server.py'],
)
