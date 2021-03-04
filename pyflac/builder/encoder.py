# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC encoder builder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import cffi
import os
import sys

# flake8: noqa: E402
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__))))

from build_args import get_build_kwargs


ffibuilder = cffi.FFI()
ffibuilder.set_source(
    "pyflac._encoder",
    """
    #include <stdint.h>
    #include <FLAC/format.h>
    #include <FLAC/stream_encoder.h>
    """,
    **get_build_kwargs()
)

# flake8: noqa: E501
ffibuilder.cdef("""

// TYPES
typedef int8_t FLAC__int8;
typedef uint8_t FLAC__uint8;

typedef int16_t FLAC__int16;
typedef int32_t FLAC__int32;
typedef int64_t FLAC__int64;
typedef uint16_t FLAC__uint16;
typedef uint32_t FLAC__uint32;
typedef uint64_t FLAC__uint64;

typedef int FLAC__bool;
typedef FLAC__uint8 FLAC__byte;

// ENUMS
typedef enum {
    FLAC__STREAM_ENCODER_OK = 0,
    FLAC__STREAM_ENCODER_UNINITIALIZED,
    FLAC__STREAM_ENCODER_OGG_ERROR,
    FLAC__STREAM_ENCODER_VERIFY_DECODER_ERROR,
    FLAC__STREAM_ENCODER_VERIFY_MISMATCH_IN_AUDIO_DATA,
    FLAC__STREAM_ENCODER_CLIENT_ERROR,
    FLAC__STREAM_ENCODER_IO_ERROR,
    FLAC__STREAM_ENCODER_FRAMING_ERROR,
    FLAC__STREAM_ENCODER_MEMORY_ALLOCATION_ERROR
} FLAC__StreamEncoderState;

extern const char * const FLAC__StreamEncoderStateString[];

typedef enum {
    FLAC__STREAM_ENCODER_INIT_STATUS_OK = 0,
    FLAC__STREAM_ENCODER_INIT_STATUS_ENCODER_ERROR,
    FLAC__STREAM_ENCODER_INIT_STATUS_UNSUPPORTED_CONTAINER,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_CALLBACKS,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_NUMBER_OF_CHANNELS,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_BITS_PER_SAMPLE,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_SAMPLE_RATE,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_BLOCK_SIZE,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_MAX_LPC_ORDER,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_QLP_COEFF_PRECISION,
    FLAC__STREAM_ENCODER_INIT_STATUS_BLOCK_SIZE_TOO_SMALL_FOR_LPC_ORDER,
    FLAC__STREAM_ENCODER_INIT_STATUS_NOT_STREAMABLE,
    FLAC__STREAM_ENCODER_INIT_STATUS_INVALID_METADATA,
    FLAC__STREAM_ENCODER_INIT_STATUS_ALREADY_INITIALIZED
} FLAC__StreamEncoderInitStatus;

extern const char * const FLAC__StreamEncoderInitStatusString[];

typedef enum {
    FLAC__STREAM_ENCODER_READ_STATUS_CONTINUE,
    FLAC__STREAM_ENCODER_READ_STATUS_END_OF_STREAM,
    FLAC__STREAM_ENCODER_READ_STATUS_ABORT,
    FLAC__STREAM_ENCODER_READ_STATUS_UNSUPPORTED
} FLAC__StreamEncoderReadStatus;

typedef enum {
    FLAC__STREAM_ENCODER_SEEK_STATUS_OK,
    FLAC__STREAM_ENCODER_SEEK_STATUS_ERROR,
    FLAC__STREAM_ENCODER_SEEK_STATUS_UNSUPPORTED
} FLAC__StreamEncoderSeekStatus;

typedef enum {
    FLAC__STREAM_ENCODER_TELL_STATUS_OK,
    FLAC__STREAM_ENCODER_TELL_STATUS_ERROR,
    FLAC__STREAM_ENCODER_TELL_STATUS_UNSUPPORTED
} FLAC__StreamEncoderTellStatus;

typedef enum {
    FLAC__STREAM_ENCODER_WRITE_STATUS_OK = 0,
    FLAC__STREAM_ENCODER_WRITE_STATUS_FATAL_ERROR
} FLAC__StreamEncoderWriteStatus;

// STRUCTURES
struct FLAC__StreamEncoderProtected;
struct FLAC__StreamEncoderPrivate;
typedef struct {
    struct FLAC__StreamEncoderProtected *protected_;
    struct FLAC__StreamEncoderPrivate *private_;
} FLAC__StreamEncoder;

// METADATA
typedef enum {
    FLAC__METADATA_TYPE_STREAMINFO = 0,
    FLAC__METADATA_TYPE_PADDING = 1,
    FLAC__METADATA_TYPE_APPLICATION = 2,
    FLAC__METADATA_TYPE_SEEKTABLE = 3,
    FLAC__METADATA_TYPE_VORBIS_COMMENT = 4,
    FLAC__METADATA_TYPE_CUESHEET = 5,
    FLAC__METADATA_TYPE_PICTURE = 6,
    FLAC__METADATA_TYPE_UNDEFINED = 7,
    FLAC__MAX_METADATA_TYPE = 126,
} FLAC__MetadataType;

typedef struct {
    uint32_t min_blocksize, max_blocksize;
    uint32_t min_framesize, max_framesize;
    uint32_t sample_rate;
    uint32_t channels;
    uint32_t bits_per_sample;
    FLAC__uint64 total_samples;
    FLAC__byte md5sum[16];
} FLAC__StreamMetadata_StreamInfo;

typedef struct {
    int dummy;
} FLAC__StreamMetadata_Padding;

typedef struct {
    FLAC__byte id[4];
    FLAC__byte *data;
} FLAC__StreamMetadata_Application;

typedef struct {
    FLAC__uint64 sample_number;
    FLAC__uint64 stream_offset;
    uint32_t frame_samples;
} FLAC__StreamMetadata_SeekPoint;

typedef struct {
    uint32_t num_points;
    FLAC__StreamMetadata_SeekPoint *points;
} FLAC__StreamMetadata_SeekTable;

typedef struct {
    FLAC__uint32 length;
    FLAC__byte *entry;
} FLAC__StreamMetadata_VorbisComment_Entry;

typedef struct {
    FLAC__StreamMetadata_VorbisComment_Entry vendor_string;
    FLAC__uint32 num_comments;
    FLAC__StreamMetadata_VorbisComment_Entry *comments;
} FLAC__StreamMetadata_VorbisComment;

typedef struct {
    FLAC__uint64 offset;
    FLAC__byte number;
} FLAC__StreamMetadata_CueSheet_Index;

typedef struct {
    FLAC__uint64 offset;
    FLAC__byte number;
    char isrc[13];
    uint32_t type:1;
    uint32_t pre_emphasis:1;
    FLAC__byte num_indices;
    FLAC__StreamMetadata_CueSheet_Index *indices;
} FLAC__StreamMetadata_CueSheet_Track;

typedef struct {
    char media_catalog_number[129];
    FLAC__uint64 lead_in;
    FLAC__bool is_cd;
    uint32_t num_tracks;
    FLAC__StreamMetadata_CueSheet_Track *tracks;
} FLAC__StreamMetadata_CueSheet;

typedef enum {
    FLAC__STREAM_METADATA_PICTURE_TYPE_OTHER = 0, /**< Other */
    FLAC__STREAM_METADATA_PICTURE_TYPE_FILE_ICON_STANDARD = 1, /**< 32x32 pixels 'file icon' (PNG only) */
    FLAC__STREAM_METADATA_PICTURE_TYPE_FILE_ICON = 2, /**< Other file icon */
    FLAC__STREAM_METADATA_PICTURE_TYPE_FRONT_COVER = 3, /**< Cover (front) */
    FLAC__STREAM_METADATA_PICTURE_TYPE_BACK_COVER = 4, /**< Cover (back) */
    FLAC__STREAM_METADATA_PICTURE_TYPE_LEAFLET_PAGE = 5, /**< Leaflet page */
    FLAC__STREAM_METADATA_PICTURE_TYPE_MEDIA = 6, /**< Media (e.g. label side of CD) */
    FLAC__STREAM_METADATA_PICTURE_TYPE_LEAD_ARTIST = 7, /**< Lead artist/lead performer/soloist */
    FLAC__STREAM_METADATA_PICTURE_TYPE_ARTIST = 8, /**< Artist/performer */
    FLAC__STREAM_METADATA_PICTURE_TYPE_CONDUCTOR = 9, /**< Conductor */
    FLAC__STREAM_METADATA_PICTURE_TYPE_BAND = 10, /**< Band/Orchestra */
    FLAC__STREAM_METADATA_PICTURE_TYPE_COMPOSER = 11, /**< Composer */
    FLAC__STREAM_METADATA_PICTURE_TYPE_LYRICIST = 12, /**< Lyricist/text writer */
    FLAC__STREAM_METADATA_PICTURE_TYPE_RECORDING_LOCATION = 13, /**< Recording Location */
    FLAC__STREAM_METADATA_PICTURE_TYPE_DURING_RECORDING = 14, /**< During recording */
    FLAC__STREAM_METADATA_PICTURE_TYPE_DURING_PERFORMANCE = 15, /**< During performance */
    FLAC__STREAM_METADATA_PICTURE_TYPE_VIDEO_SCREEN_CAPTURE = 16, /**< Movie/video screen capture */
    FLAC__STREAM_METADATA_PICTURE_TYPE_FISH = 17, /**< A bright coloured fish */
    FLAC__STREAM_METADATA_PICTURE_TYPE_ILLUSTRATION = 18, /**< Illustration */
    FLAC__STREAM_METADATA_PICTURE_TYPE_BAND_LOGOTYPE = 19, /**< Band/artist logotype */
    FLAC__STREAM_METADATA_PICTURE_TYPE_PUBLISHER_LOGOTYPE = 20, /**< Publisher/Studio logotype */
    FLAC__STREAM_METADATA_PICTURE_TYPE_UNDEFINED
} FLAC__StreamMetadata_Picture_Type;

typedef struct {
    FLAC__StreamMetadata_Picture_Type type;
    char *mime_type;
    FLAC__byte *description;
    FLAC__uint32 width;
    FLAC__uint32 height;
    FLAC__uint32 depth;
    FLAC__uint32 colors;
    FLAC__uint32 data_length;
    FLAC__byte *data;
} FLAC__StreamMetadata_Picture;

typedef struct {
    FLAC__byte *data;
} FLAC__StreamMetadata_Unknown;

typedef struct {
    FLAC__MetadataType type;
    FLAC__bool is_last;
    uint32_t length;
    union {
        FLAC__StreamMetadata_StreamInfo stream_info;
        FLAC__StreamMetadata_Padding padding;
        FLAC__StreamMetadata_Application application;
        FLAC__StreamMetadata_SeekTable seek_table;
        FLAC__StreamMetadata_VorbisComment vorbis_comment;
        FLAC__StreamMetadata_CueSheet cue_sheet;
        FLAC__StreamMetadata_Picture picture;
        FLAC__StreamMetadata_Unknown unknown;
    } data;
} FLAC__StreamMetadata;

// CALLBACKS
typedef FLAC__StreamEncoderReadStatus (*FLAC__StreamEncoderReadCallback)(const FLAC__StreamEncoder *encoder, FLAC__byte buffer[], size_t *bytes, void *client_data);
typedef FLAC__StreamEncoderWriteStatus (*FLAC__StreamEncoderWriteCallback)(const FLAC__StreamEncoder *encoder, const FLAC__byte buffer[], size_t bytes, uint32_t samples, uint32_t current_frame, void *client_data);
typedef FLAC__StreamEncoderSeekStatus (*FLAC__StreamEncoderSeekCallback)(const FLAC__StreamEncoder *encoder, FLAC__uint64 absolute_byte_offset, void *client_data);
typedef FLAC__StreamEncoderTellStatus (*FLAC__StreamEncoderTellCallback)(const FLAC__StreamEncoder *encoder, FLAC__uint64 *absolute_byte_offset, void *client_data);
typedef void (*FLAC__StreamEncoderMetadataCallback)(const FLAC__StreamEncoder *encoder, const FLAC__StreamMetadata *metadata, void *client_data);
typedef void (*FLAC__StreamEncoderProgressCallback)(const FLAC__StreamEncoder *encoder, FLAC__uint64 bytes_written, FLAC__uint64 samples_written, uint32_t frames_written, uint32_t total_frames_estimate, void *client_data);

extern "Python" FLAC__StreamEncoderReadStatus _read_callback(const FLAC__StreamEncoder *, FLAC__byte *, size_t *, void *);
extern "Python" FLAC__StreamEncoderWriteStatus _write_callback(const FLAC__StreamEncoder *, const FLAC__byte *, size_t, uint32_t, uint32_t, void *);
extern "Python" FLAC__StreamEncoderSeekStatus _seek_callback(const FLAC__StreamEncoder *, FLAC__uint64, void *);
extern "Python" FLAC__StreamEncoderTellStatus _tell_callback(const FLAC__StreamEncoder *, FLAC__uint64 *, void *);
extern "Python" void _metadata_callback(const FLAC__StreamEncoder *, const FLAC__StreamMetadata *, void *);
extern "Python" void _progress_callback(const FLAC__StreamEncoder *, FLAC__uint64, FLAC__uint64, uint32_t, uint32_t, void *);

// CONSTRUCTOR / DESTRUCTOR
FLAC__StreamEncoder *FLAC__stream_encoder_new(void);
void FLAC__stream_encoder_delete(FLAC__StreamEncoder *encoder);

// SETTERS
FLAC__bool FLAC__stream_encoder_set_verify(FLAC__StreamEncoder *encoder, FLAC__bool value);
FLAC__bool FLAC__stream_encoder_set_channels(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_bits_per_sample(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_sample_rate(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_compression_level(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_blocksize(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_do_mid_side_stereo(FLAC__StreamEncoder *encoder, FLAC__bool value);
FLAC__bool FLAC__stream_encoder_set_loose_mid_side_stereo(FLAC__StreamEncoder *encoder, FLAC__bool value);
FLAC__bool FLAC__stream_encoder_set_apodization(FLAC__StreamEncoder *encoder, const char *specification);
FLAC__bool FLAC__stream_encoder_set_max_lpc_order(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_qlp_coeff_precision(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_do_qlp_coeff_prec_search(FLAC__StreamEncoder *encoder, FLAC__bool value);
FLAC__bool FLAC__stream_encoder_set_do_exhaustive_model_search(FLAC__StreamEncoder *encoder, FLAC__bool value);
FLAC__bool FLAC__stream_encoder_set_min_residual_partition_order(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_max_residual_partition_order(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_rice_parameter_search_dist(FLAC__StreamEncoder *encoder, uint32_t value);
FLAC__bool FLAC__stream_encoder_set_total_samples_estimate(FLAC__StreamEncoder *encoder, FLAC__uint64 value);

// GETTERS
FLAC__StreamEncoderState FLAC__stream_encoder_get_state(const FLAC__StreamEncoder *encoder);
const char *FLAC__stream_encoder_get_resolved_state_string(const FLAC__StreamEncoder *encoder);
void FLAC__stream_encoder_get_verify_decoder_error_stats(const FLAC__StreamEncoder *encoder, FLAC__uint64 *absolute_sample, uint32_t *frame_number, uint32_t *channel, uint32_t *sample, FLAC__int32 *expected, FLAC__int32 *got);
FLAC__bool FLAC__stream_encoder_get_verify(const FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_get_streamable_subset(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_channels(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_bits_per_sample(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_sample_rate(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_blocksize(const FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_get_do_mid_side_stereo(const FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_get_loose_mid_side_stereo(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_max_lpc_order(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_qlp_coeff_precision(const FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_get_do_qlp_coeff_prec_search(const FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_get_do_escape_coding(const FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_get_do_exhaustive_model_search(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_min_residual_partition_order(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_max_residual_partition_order(const FLAC__StreamEncoder *encoder);
uint32_t FLAC__stream_encoder_get_rice_parameter_search_dist(const FLAC__StreamEncoder *encoder);
FLAC__uint64 FLAC__stream_encoder_get_total_samples_estimate(const FLAC__StreamEncoder *encoder);

// PROCESSING
FLAC__StreamEncoderInitStatus FLAC__stream_encoder_init_stream(FLAC__StreamEncoder *encoder, FLAC__StreamEncoderWriteCallback write_callback, FLAC__StreamEncoderSeekCallback seek_callback, FLAC__StreamEncoderTellCallback tell_callback, FLAC__StreamEncoderMetadataCallback metadata_callback, void *client_data);
FLAC__StreamEncoderInitStatus FLAC__stream_encoder_init_ogg_stream(FLAC__StreamEncoder *encoder, FLAC__StreamEncoderReadCallback read_callback, FLAC__StreamEncoderWriteCallback write_callback, FLAC__StreamEncoderSeekCallback seek_callback, FLAC__StreamEncoderTellCallback tell_callback, FLAC__StreamEncoderMetadataCallback metadata_callback, void *client_data);
FLAC__StreamEncoderInitStatus FLAC__stream_encoder_init_FILE(FLAC__StreamEncoder *encoder, FILE *file, FLAC__StreamEncoderProgressCallback progress_callback, void *client_data);
FLAC__StreamEncoderInitStatus FLAC__stream_encoder_init_ogg_FILE(FLAC__StreamEncoder *encoder, FILE *file, FLAC__StreamEncoderProgressCallback progress_callback, void *client_data);
FLAC__StreamEncoderInitStatus FLAC__stream_encoder_init_file(FLAC__StreamEncoder *encoder, const char *filename, FLAC__StreamEncoderProgressCallback progress_callback, void *client_data);
FLAC__StreamEncoderInitStatus FLAC__stream_encoder_init_ogg_file(FLAC__StreamEncoder *encoder, const char *filename, FLAC__StreamEncoderProgressCallback progress_callback, void *client_data);
FLAC__bool FLAC__stream_encoder_finish(FLAC__StreamEncoder *encoder);
FLAC__bool FLAC__stream_encoder_process(FLAC__StreamEncoder *encoder, const FLAC__int32 * const buffer[], uint32_t samples);
FLAC__bool FLAC__stream_encoder_process_interleaved(FLAC__StreamEncoder *encoder, const FLAC__int32 buffer[], uint32_t samples);

""")


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
