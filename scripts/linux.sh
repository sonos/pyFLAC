#!/bin/sh

echo "Building for x86_64..."

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-linux-x86_64
cd flac-$1-linux-x86_64
CC=clang ./configure --with-ogg=no --enable-debug=no --enable-shared --disable-static --disable-examples
make
mkdir ../linux-x86_64
cp src/libFLAC/.libs/libFLAC.so.12.1.0 ../linux-x86_64/libFLAC-12.1.0.so
cd ../linux-x86_64
patchelf --set-soname libFLAC-12.1.0.so libFLAC-12.1.0.so
llvm-strip-8 libFLAC-12.1.0.so

echo "Building for arm64..."

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-linux-arm64
cd flac-$1-linux-arm64
CC=clang ./configure --host=aarch64-linux-gnu --with-ogg=no --enable-debug=no --enable-shared --disable-static --disable-examples
make
mkdir ../linux-arm64
cp src/libFLAC/.libs/libFLAC.so.12.1.0 ../linux-arm64/libFLAC-12.1.0.so
cd ../linux-arm64
patchelf --set-soname libFLAC-12.1.0.so libFLAC-12.1.0.so
llvm-strip-8 libFLAC-12.1.0.so
