#!/bin/sh

die() {
	echo $@
	exit
}

docmd() {
	$@ >> build.log
}

echo
echo "Details in build.log ..."
echo

echo >| build.log

echo "* Unit tests"
docmd ./pack/test.sh || die "$0: Units tests failed to run!"

docmd echo "-------------"

echo "* Unix source distro"
docmd python setup.py sdist || die "$0: Unix dist gen. failed!"

docmd echo "-------------"

echo "* Windows binary distro"
docmd python setup.py bdist_wininst || die "$0: Windows dist gen. failed!"


echo

