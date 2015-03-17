#! /usr/bin/bash
#
# Script to fetch a tagged RTP Engine repo from github and create
# the needed tarball for rpmbuild
#
if [ "x$1" == "x" ]; then
	echo Missing version number
	echo
	echo IE: getVersion.sh 3.7.2.1
fi
VER=$1
DIR=rtpengine-${VER}
TARBALL=${DIR}.tar.gz
DEST=~/rpmbuild/SOURCES
rm -rf ${TARBALL} ${DIR}
svn export https://github.com/sipwise/rtpengine/tags/mr${VER} ${DIR}
echo "Creating ${TARBALL}..."
tar -czf ${TARBALL} ${DIR}
echo "Copying to ${DEST}..."
cp ${TARBALL} ${DEST}
rm -rf ${TARBALL} ${DIR}
