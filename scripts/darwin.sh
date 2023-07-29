#!/bin/sh

echo "Building for x86_64..."

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-darwin-x86_64
cd flac-$1-darwin-x86_64
CC=clang ./configure --with-ogg=no --enable-debug=no --enable-shared --disable-static --disable-examples
make
mkdir ../darwin-x86_64
cp src/libFLAC/.libs/libFLAC.12.dylib ../darwin-x86_64/
cd ../darwin-x86_64
install_name_tool -id @rpath/libFLAC.12.dylib libFLAC.12.dylib
llvm-strip libFLAC.12.dylib

echo "Building for arm64..."

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-darwin-arm64
cd flac-$1-darwin-arm64
./configure --host=aarch64-apple-darwin --with-ogg=no --enable-debug=no CFLAGS="-arch arm64 -target arm64-apple-macos11" CXXFLAGS="-arch arm64 -target arm64-apple-macos11" --enable-shared --disable-static --disable-examples
make
mkdir ../darwin-arm64
cp src/libFLAC/.libs/libFLAC.12.dylib ../darwin-arm64/
cd ../darwin-arm64
install_name_tool -id @rpath/libFLAC.12.dylib libFLAC.12.dylib
llvm-strip libFLAC.12.dylib
