# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC decoder builder
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
    "pyflac._decoder",
    """
    #include <FLAC/format.h>
    #include <FLAC/stream_decoder.h>
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
    FLAC__STREAM_DECODER_SEARCH_FOR_METADATA = 0,
    FLAC__STREAM_DECODER_READ_METADATA,
    FLAC__STREAM_DECODER_SEARCH_FOR_FRAME_SYNC,
    FLAC__STREAM_DECODER_READ_FRAME,
    FLAC__STREAM_DECODER_END_OF_STREAM,
    FLAC__STREAM_DECODER_OGG_ERROR,
    FLAC__STREAM_DECODER_SEEK_ERROR,
    FLAC__STREAM_DECODER_ABORTED,
    FLAC__STREAM_DECODER_MEMORY_ALLOCATION_ERROR,
    FLAC__STREAM_DECODER_UNINITIALIZED
} FLAC__StreamDecoderState;

extern const char * const FLAC__StreamDecoderStateString[];

typedef enum {
    FLAC__STREAM_DECODER_INIT_STATUS_OK = 0,
    FLAC__STREAM_DECODER_INIT_STATUS_UNSUPPORTED_CONTAINER,
    FLAC__STREAM_DECODER_INIT_STATUS_INVALID_CALLBACKS,
    FLAC__STREAM_DECODER_INIT_STATUS_MEMORY_ALLOCATION_ERROR,
    FLAC__STREAM_DECODER_INIT_STATUS_ERROR_OPENING_FILE,
    FLAC__STREAM_DECODER_INIT_STATUS_ALREADY_INITIALIZED
} FLAC__StreamDecoderInitStatus;

extern const char * const FLAC__StreamDecoderInitStatusString[];

typedef enum {
    FLAC__STREAM_DECODER_READ_STATUS_CONTINUE,
    FLAC__STREAM_DECODER_READ_STATUS_END_OF_STREAM,
    FLAC__STREAM_DECODER_READ_STATUS_ABORT
} FLAC__StreamDecoderReadStatus;

typedef enum {
    FLAC__STREAM_DECODER_SEEK_STATUS_OK,
    FLAC__STREAM_DECODER_SEEK_STATUS_ERROR,
    FLAC__STREAM_DECODER_SEEK_STATUS_UNSUPPORTED
} FLAC__StreamDecoderSeekStatus;

typedef enum {
    FLAC__STREAM_DECODER_TELL_STATUS_OK,
    FLAC__STREAM_DECODER_TELL_STATUS_ERROR,
    FLAC__STREAM_DECODER_TELL_STATUS_UNSUPPORTED
} FLAC__StreamDecoderTellStatus;

typedef enum {
    FLAC__STREAM_DECODER_LENGTH_STATUS_OK,
    FLAC__STREAM_DECODER_LENGTH_STATUS_ERROR,
    FLAC__STREAM_DECODER_LENGTH_STATUS_UNSUPPORTED
} FLAC__StreamDecoderLengthStatus;

typedef enum {
    FLAC__STREAM_DECODER_WRITE_STATUS_CONTINUE,
    FLAC__STREAM_DECODER_WRITE_STATUS_ABORT
} FLAC__StreamDecoderWriteStatus;

typedef enum {
    FLAC__STREAM_DECODER_ERROR_STATUS_LOST_SYNC,
    FLAC__STREAM_DECODER_ERROR_STATUS_BAD_HEADER,
    FLAC__STREAM_DECODER_ERROR_STATUS_FRAME_CRC_MISMATCH,
    FLAC__STREAM_DECODER_ERROR_STATUS_UNPARSEABLE_STREAM
} FLAC__StreamDecoderErrorStatus;

extern const char * const FLAC__StreamDecoderErrorStatusString[];

typedef enum {
    FLAC__FRAME_NUMBER_TYPE_FRAME_NUMBER, /**< number contains the frame number */
    FLAC__FRAME_NUMBER_TYPE_SAMPLE_NUMBER /**< number contains the sample number of first sample in frame */
} FLAC__FrameNumberType;

typedef enum {
    FLAC__CHANNEL_ASSIGNMENT_INDEPENDENT = 0, /**< independent channels */
    FLAC__CHANNEL_ASSIGNMENT_LEFT_SIDE = 1, /**< left+side stereo */
    FLAC__CHANNEL_ASSIGNMENT_RIGHT_SIDE = 2, /**< right+side stereo */
    FLAC__CHANNEL_ASSIGNMENT_MID_SIDE = 3 /**< mid+side stereo */
} FLAC__ChannelAssignment;

typedef enum {
    FLAC__SUBFRAME_TYPE_CONSTANT = 0, /**< constant signal */
    FLAC__SUBFRAME_TYPE_VERBATIM = 1, /**< uncompressed signal */
    FLAC__SUBFRAME_TYPE_FIXED = 2, /**< fixed polynomial prediction */
    FLAC__SUBFRAME_TYPE_LPC = 3 /**< linear prediction */
} FLAC__SubframeType;

typedef enum {
    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE = 0,
    FLAC__ENTROPY_CODING_METHOD_PARTITIONED_RICE2 = 1
} FLAC__EntropyCodingMethodType;

// STRUCTURES
struct FLAC__StreamDecoderProtected;
struct FLAC__StreamDecoderPrivate;
typedef struct {
    struct FLAC__StreamDecoderProtected *protected_; /* avoid the C++ keyword 'protected' */
    struct FLAC__StreamDecoderPrivate *private_; /* avoid the C++ keyword 'private' */
} FLAC__StreamDecoder;

typedef struct {
    uint32_t blocksize;
    uint32_t sample_rate;
    uint32_t channels;
    FLAC__ChannelAssignment channel_assignment;
    uint32_t bits_per_sample;
    FLAC__FrameNumberType number_type;
    union {
        FLAC__uint32 frame_number;
        FLAC__uint64 sample_number;
    } number;
    FLAC__uint8 crc;
} FLAC__FrameHeader;

typedef struct {
    uint32_t *parameters;
    uint32_t *raw_bits;
    uint32_t capacity_by_order;
} FLAC__EntropyCodingMethod_PartitionedRiceContents;

typedef struct {
    uint32_t order;
    const FLAC__EntropyCodingMethod_PartitionedRiceContents *contents;
} FLAC__EntropyCodingMethod_PartitionedRice;

typedef struct {
    FLAC__EntropyCodingMethodType type;
    union {
        FLAC__EntropyCodingMethod_PartitionedRice partitioned_rice;
    } data;
} FLAC__EntropyCodingMethod;

typedef struct {
    FLAC__int32 value; /**< The constant signal value. */
} FLAC__Subframe_Constant;

typedef struct {
    const FLAC__int32 *data; /**< A pointer to verbatim signal. */
} FLAC__Subframe_Verbatim;

typedef struct {
    FLAC__EntropyCodingMethod entropy_coding_method;
    uint32_t order;
    FLAC__int32 warmup[4];
    const FLAC__int32 *residual;
} FLAC__Subframe_Fixed;

typedef struct {
    FLAC__EntropyCodingMethod entropy_coding_method;
    uint32_t order;
    uint32_t qlp_coeff_precision;
    int quantization_level;
    FLAC__int32 qlp_coeff[32];
    FLAC__int32 warmup[32];
    const FLAC__int32 *residual;
} FLAC__Subframe_LPC;

typedef struct {
    FLAC__SubframeType type;
    union {
        FLAC__Subframe_Constant constant;
        FLAC__Subframe_Fixed fixed;
        FLAC__Subframe_LPC lpc;
        FLAC__Subframe_Verbatim verbatim;
    } data;
    uint32_t wasted_bits;
} FLAC__Subframe;

typedef struct {
    FLAC__uint16 crc;
} FLAC__FrameFooter;

typedef struct {
    FLAC__FrameHeader header;
    FLAC__Subframe subframes[8];
    FLAC__FrameFooter footer;
} FLAC__Frame;

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
typedef FLAC__StreamDecoderReadStatus (*FLAC__StreamDecoderReadCallback)(const FLAC__StreamDecoder *decoder, FLAC__byte buffer[], size_t *bytes, void *client_data);
typedef FLAC__StreamDecoderSeekStatus (*FLAC__StreamDecoderSeekCallback)(const FLAC__StreamDecoder *decoder, FLAC__uint64 absolute_byte_offset, void *client_data);
typedef FLAC__StreamDecoderTellStatus (*FLAC__StreamDecoderTellCallback)(const FLAC__StreamDecoder *decoder, FLAC__uint64 *absolute_byte_offset, void *client_data);
typedef FLAC__StreamDecoderLengthStatus (*FLAC__StreamDecoderLengthCallback)(const FLAC__StreamDecoder *decoder, FLAC__uint64 *stream_length, void *client_data);
typedef FLAC__bool (*FLAC__StreamDecoderEofCallback)(const FLAC__StreamDecoder *decoder, void *client_data);
typedef FLAC__StreamDecoderWriteStatus (*FLAC__StreamDecoderWriteCallback)(const FLAC__StreamDecoder *decoder, const FLAC__Frame *frame, const FLAC__int32 * const buffer[], void *client_data);
typedef void (*FLAC__StreamDecoderMetadataCallback)(const FLAC__StreamDecoder *decoder, const FLAC__StreamMetadata *metadata, void *client_data);
typedef void (*FLAC__StreamDecoderErrorCallback)(const FLAC__StreamDecoder *decoder, FLAC__StreamDecoderErrorStatus status, void *client_data);

extern "Python" FLAC__StreamDecoderReadStatus _read_callback(const FLAC__StreamDecoder *, FLAC__byte *, size_t *, void *);
extern "Python" FLAC__StreamDecoderSeekStatus _seek_callback(const FLAC__StreamDecoder *, FLAC__uint64, void *);
extern "Python" FLAC__StreamDecoderTellStatus _tell_callback(const FLAC__StreamDecoder *, FLAC__uint64 *, void *);
extern "Python" FLAC__StreamDecoderLengthStatus _length_callback(const FLAC__StreamDecoder *, FLAC__uint64 *, void *);
extern "Python" FLAC__bool _eof_callback(const FLAC__StreamDecoder *, void *);
extern "Python" FLAC__StreamDecoderWriteStatus _write_callback(const FLAC__StreamDecoder *, const FLAC__Frame *, const FLAC__int32 const **, void *);
extern "Python" void _metadata_callback(const FLAC__StreamDecoder *, const FLAC__StreamMetadata *, void *);
extern "Python" void _error_callback(const FLAC__StreamDecoder *, FLAC__StreamDecoderErrorStatus, void *);

// CONSTRUCTOR / DESTRUCTOR
FLAC__StreamDecoder *FLAC__stream_decoder_new(void);
void FLAC__stream_decoder_delete(FLAC__StreamDecoder *decoder);

// SETTERS
FLAC__bool FLAC__stream_decoder_set_md5_checking(FLAC__StreamDecoder *decoder, FLAC__bool value);
FLAC__bool FLAC__stream_decoder_set_metadata_respond(FLAC__StreamDecoder *decoder, FLAC__MetadataType type);
FLAC__bool FLAC__stream_decoder_set_metadata_respond_application(FLAC__StreamDecoder *decoder, const FLAC__byte id[4]);
FLAC__bool FLAC__stream_decoder_set_metadata_respond_all(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_set_metadata_ignore(FLAC__StreamDecoder *decoder, FLAC__MetadataType type);
FLAC__bool FLAC__stream_decoder_set_metadata_ignore_application(FLAC__StreamDecoder *decoder, const FLAC__byte id[4]);
FLAC__bool FLAC__stream_decoder_set_metadata_ignore_all(FLAC__StreamDecoder *decoder);

// GETTERS
FLAC__StreamDecoderState FLAC__stream_decoder_get_state(const FLAC__StreamDecoder *decoder);
const char *FLAC__stream_decoder_get_resolved_state_string(const FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_get_md5_checking(const FLAC__StreamDecoder *decoder);
FLAC__uint64 FLAC__stream_decoder_get_total_samples(const FLAC__StreamDecoder *decoder);
uint32_t FLAC__stream_decoder_get_channels(const FLAC__StreamDecoder *decoder);
FLAC__ChannelAssignment FLAC__stream_decoder_get_channel_assignment(const FLAC__StreamDecoder *decoder);
uint32_t FLAC__stream_decoder_get_bits_per_sample(const FLAC__StreamDecoder *decoder);
uint32_t FLAC__stream_decoder_get_sample_rate(const FLAC__StreamDecoder *decoder);
uint32_t FLAC__stream_decoder_get_blocksize(const FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_get_decode_position(const FLAC__StreamDecoder *decoder, FLAC__uint64 *position);

// PROCESSING
FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_stream(
    FLAC__StreamDecoder *decoder,
    FLAC__StreamDecoderReadCallback read_callback,
    FLAC__StreamDecoderSeekCallback seek_callback,
    FLAC__StreamDecoderTellCallback tell_callback,
    FLAC__StreamDecoderLengthCallback length_callback,
    FLAC__StreamDecoderEofCallback eof_callback,
    FLAC__StreamDecoderWriteCallback write_callback,
    FLAC__StreamDecoderMetadataCallback metadata_callback,
    FLAC__StreamDecoderErrorCallback error_callback,
    void *client_data
);
FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_ogg_stream(
    FLAC__StreamDecoder *decoder,
    FLAC__StreamDecoderReadCallback read_callback,
    FLAC__StreamDecoderSeekCallback seek_callback,
    FLAC__StreamDecoderTellCallback tell_callback,
    FLAC__StreamDecoderLengthCallback length_callback,
    FLAC__StreamDecoderEofCallback eof_callback,
    FLAC__StreamDecoderWriteCallback write_callback,
    FLAC__StreamDecoderMetadataCallback metadata_callback,
    FLAC__StreamDecoderErrorCallback error_callback,
    void *client_data
);
FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_FILE(
    FLAC__StreamDecoder *decoder,
    FILE *file,
    FLAC__StreamDecoderWriteCallback write_callback,
    FLAC__StreamDecoderMetadataCallback metadata_callback,
    FLAC__StreamDecoderErrorCallback error_callback,
    void *client_data
);
FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_ogg_FILE(
    FLAC__StreamDecoder *decoder,
    FILE *file,
    FLAC__StreamDecoderWriteCallback write_callback,
    FLAC__StreamDecoderMetadataCallback metadata_callback,
    FLAC__StreamDecoderErrorCallback error_callback,
    void *client_data
);
FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_file(
    FLAC__StreamDecoder *decoder,
    const char *filename,
    FLAC__StreamDecoderWriteCallback write_callback,
    FLAC__StreamDecoderMetadataCallback metadata_callback,
    FLAC__StreamDecoderErrorCallback error_callback,
    void *client_data
);
FLAC__StreamDecoderInitStatus FLAC__stream_decoder_init_ogg_file(
    FLAC__StreamDecoder *decoder,
    const char *filename,
    FLAC__StreamDecoderWriteCallback write_callback,
    FLAC__StreamDecoderMetadataCallback metadata_callback,
    FLAC__StreamDecoderErrorCallback error_callback,
    void *client_data
);
FLAC__bool FLAC__stream_decoder_finish(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_flush(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_reset(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_process_single(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_process_until_end_of_metadata(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_process_until_end_of_stream(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_skip_single_frame(FLAC__StreamDecoder *decoder);
FLAC__bool FLAC__stream_decoder_seek_absolute(FLAC__StreamDecoder *decoder, FLAC__uint64 sample);


""")


if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
