#!/usr/bin/env python

from distutils.core import setup

from pybridge.conf import PYBRIDGE_VERSION

setup(
	name = 'pybridge',
	version = PYBRIDGE_VERSION,
	author = 'Michael Banks',
	author_email = 'michaelbanks@dsl.pipex.com',
	url = 'http://sourceforge.net/projects/pybridge/',
	description = 'Online bridge made easy.',
	download_url = 'http://sourceforge.net/project/showfiles.php?group_id=114287',
	packages = ['pybridge', 'pybridge.client', 'pybridge.common', 'pybridge.server'],
	scripts = ['bin/pybridge-client', 'bin/pybridge-server'],
	package_data = {'pybridge.client' : ['glade/pybridge.glade', 'pixmaps/*.png']},
)

