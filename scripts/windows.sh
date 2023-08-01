#!/bin/sh

echo "Building for x86_64..."
echo "Now just download the -win.zip files from FLAC downloads instead to get the DLL"
echo "And download from https://packages.msys2.org/package/"
echo "Renaming libFLAC.dll.a to FLAC-12.lib"
exit

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-windows-x86_64
cd flac-$1-windows-x86_64
./configure --host=x86_64-w64-mingw32 --with-ogg=no --enable-debug=no --enable-shared --disable-static --disable-examples
make
mkdir ../windows-x86_64
cp src/libFLAC/.libs/libFLAC-12.dll ../windows-x86_64/
cp src/libFLAC/.libs/libFLAC.dll.a ../windows-x86_64/FLAC-12.lib

echo "Building for i686..."

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-windows-i686
cd flac-$1-windows-i686
./configure --host=i686-w64-mingw32 --with-ogg=no --enable-debug=no --enable-shared --disable-static --disable-examples
make
mkdir ../windows-i686
cp src/libFLAC/.libs/libFLAC-12.dll ../windows-i686/
cp src/libFLAC/.libs/libFLAC.dll.a ../windows-i686/FLAC-12.lib
