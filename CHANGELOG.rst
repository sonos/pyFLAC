pyFLAC Changelog
----------------

**v3.0.0**

* Fixed bug in the shutdown behaviour of the `StreamDecoder` (see #22 and #23).
* Automatically detect bit depth of input data in the `FileEncoder`, and
  raise an error if not 16-bit or 32-bit PCM (see #24).
* Added a new `OneShotDecoder` to decode a buffer of FLAC data in a single
  blocking operation, without the use of threads. Courtesy of @GOAE.

**v2.2.0**

* Updated FLAC library to v1.4.3.
    See `FLAC Changelog <https://xiph.org/flac/changelog.html>`_.
* Added support for `int32` data
* Added `limit_min_bitrate` property.
* Removed support for Python 3.7

**v2.1.0**

* Added support for Linux `arm64` architectures
* Added support for Darwin `arm64` architectures (macOS Apple Silicon)
* Fixed Raspberry Pi Zero library (see #13)
* Updated FLAC library to v1.3.4

**v2.0.0**

* Added `seek` and `tell` callbacks to `StreamEncoder`
* Renamed the write callbacks from `callback` to `write_callback` for `StreamEncoder` and `StreamDecoder`

**v1.0.0**

* Added a `StreamEncoder` to compress raw audio data on-the-fly into a FLAC byte stream
* Added a `StreamDecoder` to decompress a FLAC byte stream back to raw audio data
* Added a `FileEncoder` to convert a WAV file to FLAC encoded data, optionally saving to a FLAC file
* Added a `FileDecoder` to convert a FLAC file to raw audio data, optionally saving to a WAV file
* Bundled with libFLAC version 1.3.3
