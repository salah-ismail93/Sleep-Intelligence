import io
import struct
import wave
import pytest

from app.algorithms.snore.wav_validation import (
    InvalidWAVFormatError,
    MalformedWAVError,
    WAVMetadata,
    validate_and_extract_wav_metadata,
)


def create_wav_bytes(
    sample_rate: int = 16000,
    channels: int = 1,
    sampwidth: int = 2,
    num_frames: int = 16000,
) -> bytes:
    """Helper fixture builder producing standard in-memory PCM WAV bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(sampwidth)
        w.setframerate(sample_rate)
        w.writeframes(b"\x00" * (num_frames * channels * sampwidth))
    return buf.getvalue()


def build_handbuilt_wav(
    fmt_payload: bytes | None = None,
    data_bytes: bytes | None = None,
    extra_chunks: bytes = b"",
    override_riff_size: int | None = None,
) -> bytes:
    """Helper to assemble custom binary WAV files with exact RIFF headers and chunk padding."""
    if fmt_payload is None:
        fmt_payload = struct.pack("<HHIIHH", 1, 1, 16000, 32000, 2, 16)
    if data_bytes is None:
        data_bytes = b"\x00" * 32000  # 1 sec at 16kHz 16-bit mono

    fmt_chunk = b"fmt \x10\x00\x00\x00" + fmt_payload

    # Include odd-size RIFF padding byte if necessary
    data_chunk_size = len(data_bytes)
    padding = b"\x00" if (data_chunk_size % 2 != 0) else b""
    data_chunk = b"data" + struct.pack("<I", data_chunk_size) + data_bytes + padding

    body = extra_chunks + fmt_chunk + data_chunk

    actual_riff_size = len(b"WAVE" + body)
    riff_size = override_riff_size if override_riff_size is not None else actual_riff_size

    header = b"RIFF" + struct.pack("<I", riff_size) + b"WAVE"
    return header + body


# --- Valid WAV & Boundary Tests ---

def test_valid_wav_returns_immutable_metadata():
    wav_bytes = create_wav_bytes(sample_rate=16000, num_frames=16000)
    meta = validate_and_extract_wav_metadata(wav_bytes)

    assert isinstance(meta, WAVMetadata)
    assert meta.sample_rate == 16000
    assert meta.frame_count == 16000
    assert meta.duration == 1.0

    with pytest.raises(Exception):
        meta.sample_rate = 8000  # type: ignore


def test_accepted_sample_rate_boundaries():
    # Min boundary: 8,000 Hz
    min_sr_wav = create_wav_bytes(sample_rate=8000, num_frames=8000)
    meta_min = validate_and_extract_wav_metadata(min_sr_wav)
    assert meta_min.sample_rate == 8000
    assert meta_min.duration == 1.0

    # Max boundary: 48,000 Hz
    max_sr_wav = create_wav_bytes(sample_rate=48000, num_frames=48000)
    meta_max = validate_and_extract_wav_metadata(max_sr_wav)
    assert meta_max.sample_rate == 48000
    assert meta_max.duration == 1.0


def test_boundary_durations_accepted():
    # Min duration boundary: 0.5s at 16,000 Hz = 8,000 frames
    min_wav = create_wav_bytes(sample_rate=16000, num_frames=8000)
    min_meta = validate_and_extract_wav_metadata(min_wav)
    assert min_meta.duration == 0.5

    # Max duration boundary: 30.0s at 16,000 Hz = 480,000 frames
    max_wav = create_wav_bytes(sample_rate=16000, num_frames=480000)
    max_meta = validate_and_extract_wav_metadata(max_wav)
    assert max_meta.duration == 30.0


def test_valid_odd_sized_optional_metadata_chunk_with_padding():
    # 3-byte payload + 1-byte padding = 4 bytes total addition
    odd_chunk = b"test\x03\x00\x00\x00ABC\x00"
    wav_bytes = build_handbuilt_wav(extra_chunks=odd_chunk)
    meta = validate_and_extract_wav_metadata(wav_bytes)

    assert meta.sample_rate == 16000
    assert meta.frame_count == 16000
    assert meta.duration == 1.0


# --- Unsupported WAV Format/Properties Tests ---

def test_non_riff_container_raises_invalid_format():
    invalid_bytes = b"NOT_RIFF" + b"\x00" * 40
    with pytest.raises(InvalidWAVFormatError, match="RIFF/WAVE container"):
        validate_and_extract_wav_metadata(invalid_bytes)


def test_unsupported_pcm_encoding_raises_invalid_format():
    # Format tag 3 (IEEE Float instead of 1 PCM)
    fmt_payload = struct.pack("<HHIIHH", 3, 1, 16000, 32000, 2, 16)
    wav_bytes = build_handbuilt_wav(fmt_payload=fmt_payload)
    with pytest.raises(InvalidWAVFormatError, match="Unsupported WAV encoding format"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_stereo_channels_raises_invalid_format():
    wav_bytes = create_wav_bytes(channels=2)
    with pytest.raises(InvalidWAVFormatError, match="channel count"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_unsupported_sample_width_raises_invalid_format():
    wav_bytes = create_wav_bytes(sampwidth=1)  # 8-bit PCM
    with pytest.raises(InvalidWAVFormatError, match="sample width"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_sample_rate_below_min_boundary_raises_invalid_format():
    wav_bytes = create_wav_bytes(sample_rate=7999, num_frames=8000)
    with pytest.raises(InvalidWAVFormatError, match="Sample rate"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_sample_rate_above_max_boundary_raises_invalid_format():
    wav_bytes = create_wav_bytes(sample_rate=48001, num_frames=48001)
    with pytest.raises(InvalidWAVFormatError, match="Sample rate"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_duration_below_min_boundary_raises_invalid_format():
    wav_bytes = create_wav_bytes(sample_rate=16000, num_frames=6400)  # 0.4s
    with pytest.raises(InvalidWAVFormatError, match="duration"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_duration_above_max_boundary_raises_invalid_format():
    wav_bytes = create_wav_bytes(sample_rate=16000, num_frames=481600)  # 30.1s
    with pytest.raises(InvalidWAVFormatError, match="duration"):
        validate_and_extract_wav_metadata(wav_bytes)


# --- Malformed / Corrupt WAV Header & Payload Tests ---

def test_mismatched_riff_size_raises_malformed_error():
    # Pass an incorrect RIFF size (e.g., 999999)
    wav_bytes = build_handbuilt_wav(override_riff_size=999999)
    with pytest.raises(MalformedWAVError, match="Mismatched RIFF size"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_missing_odd_chunk_padding_byte_raises_malformed_error():
    # Odd chunk placed at the end of the file missing its required 1-byte pad
    fmt_chunk = b"fmt \x10\x00\x00\x00" + struct.pack("<HHIIHH", 1, 1, 16000, 32000, 2, 16)
    data_bytes = b"\x00" * 32000
    data_chunk = b"data" + struct.pack("<I", len(data_bytes)) + data_bytes
    odd_chunk_no_pad = b"test\x03\x00\x00\x00ABC"  # 11 bytes, missing pad

    body = fmt_chunk + data_chunk + odd_chunk_no_pad
    riff_header = b"RIFF" + struct.pack("<I", len(b"WAVE" + body)) + b"WAVE"
    wav_bytes = riff_header + body

    with pytest.raises(MalformedWAVError, match="Missing padding byte"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_corrupt_block_align_raises_malformed_error():
    # Block align for 16-bit mono should be 2, set to 4
    fmt_payload = struct.pack("<HHIIHH", 1, 1, 16000, 32000, 4, 16)
    wav_bytes = build_handbuilt_wav(fmt_payload=fmt_payload)
    with pytest.raises(MalformedWAVError, match="block_align"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_corrupt_byte_rate_raises_malformed_error():
    # Byte rate for 16kHz 16-bit mono should be 32000, set to 16000
    fmt_payload = struct.pack("<HHIIHH", 1, 1, 16000, 16000, 2, 16)
    wav_bytes = build_handbuilt_wav(fmt_payload=fmt_payload)
    with pytest.raises(MalformedWAVError, match="byte_rate"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_unaligned_declared_data_payload_raises_malformed_error():
    # Declare odd data payload size 32001 (with valid RIFF padding byte appended)
    data_bytes = b"\x00" * 32001
    wav_bytes = build_handbuilt_wav(data_bytes=data_bytes)
    with pytest.raises(MalformedWAVError, match="incomplete or unaligned"):
        validate_and_extract_wav_metadata(wav_bytes)


def test_truncated_header_raises_malformed_error():
    short_bytes = b"RIFF1234WAVEfmt "
    with pytest.raises(MalformedWAVError):
        validate_and_extract_wav_metadata(short_bytes)


def test_truncated_frame_payload_raises_malformed_error():
    wav_bytes = create_wav_bytes(sample_rate=16000, num_frames=16000)
    truncated_bytes = wav_bytes[:-100]
    with pytest.raises(MalformedWAVError):
        validate_and_extract_wav_metadata(truncated_bytes)