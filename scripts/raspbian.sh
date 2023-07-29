#!/bin/sh

echo "Building for armv7..."

cd /tmp
wget https://ftp.osuosl.org/pub/xiph/releases/flac/flac-$1.tar.xz
tar xvf flac-$1.tar.xz

mv flac-$1 flac-$1-raspbian-armv7a
cd flac-$1-raspbian-armv7a
./configure --host=arm-linux-gnueabihf --with-ogg=no --enable-debug=no CFLAGS="-mfpu=neon -march=armv7-a -mfloat-abi=hard" --enable-shared --disable-static --disable-examples
make
mkdir ../raspbian-armv7a
cp src/libFLAC/.libs/libFLAC.so.12.1.0 ../raspbian-armv7a/libFLAC-12.1.0.so
cd ../raspbian-armv7a
patchelf --set-soname libFLAC-12.1.0.so libFLAC-12.1.0.so
arm-linux-gnueabihf-strip libFLAC-12.1.0.so
