pyFLAC Changelog
----------------

**v1.0.0**

* Added a `StreamEncoder` to compress raw audio data on-the-fly into a FLAC byte stream
* Added a `StreamDecoder` to decompress a FLAC byte stream back to raw audio data
* Added a `FileEncoder` to convert a WAV file to FLAC encoded data, optionally saving to a FLAC file
* Added a `FileDecoder` to convert a FLAC file to raw audio data, optionally saving to a WAV file
* Bundled with libFLAC version 1.3.3
