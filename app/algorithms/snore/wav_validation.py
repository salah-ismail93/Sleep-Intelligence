from dataclasses import dataclass
import struct


class InvalidWAVFormatError(ValueError):
    """Raised when WAV container or audio properties violate the supported WAV contract."""

    pass


class MalformedWAVError(ValueError):
    """Raised when WAV header or payload is corrupt, malformed, or truncated."""

    pass


@dataclass(frozen=True)
class WAVMetadata:
    """Immutable metadata extracted from a validated PCM WAV file."""

    sample_rate: int
    frame_count: int
    duration: float


def validate_and_extract_wav_metadata(audio_bytes: bytes) -> WAVMetadata:
    """Validates raw audio bytes against the Version 1 PCM WAV contract.

    Contract requirements:
    - Container: valid RIFF/WAVE
    - RIFF declared size must equal len(audio_bytes) - 8
    - Encoding: uncompressed linear PCM (format 1)
    - Sample width: 16-bit (2 bytes)
    - Channels: 1 (mono)
    - Sample rate: 8,000 to 48,000 Hz inclusive
    - Duration: 0.5 to 30.0 seconds inclusive
    - Complete and aligned frame data
    - Correct block_align and byte_rate fields
    - Verified padding bytes for odd-sized chunks

    Args:
        audio_bytes: Raw binary payload of the uploaded audio file.

    Returns:
        WAVMetadata: Validated immutable audio metadata.

    Raises:
        MalformedWAVError: If the binary data is truncated, corrupt, or unaligned.
        InvalidWAVFormatError: If WAV container or audio properties violate constraints.
    """
    if len(audio_bytes) < 44:
        raise MalformedWAVError("WAV data is truncated or too short for a standard header.")

    if audio_bytes[:4] != b"RIFF" or audio_bytes[8:12] != b"WAVE":
        raise InvalidWAVFormatError("Content is not a valid RIFF/WAVE container.")

    riff_declared_size = struct.unpack("<I", audio_bytes[4:8])[0]
    expected_riff_size = len(audio_bytes) - 8
    if riff_declared_size != expected_riff_size:
        raise MalformedWAVError(
            f"Mismatched RIFF size header: declared {riff_declared_size}, actual {expected_riff_size}."
        )

    offset = 12
    total_len = len(audio_bytes)

    fmt_found = False
    data_found = False

    audio_format = None
    channels = None
    sample_rate = None
    byte_rate = None
    block_align = None
    bits_per_sample = None
    data_bytes_len = 0

    while offset < total_len:
        if offset + 8 > total_len:
            raise MalformedWAVError("WAV chunk header is truncated.")

        chunk_id = audio_bytes[offset : offset + 4]
        chunk_size = struct.unpack("<I", audio_bytes[offset + 4 : offset + 8])[0]
        offset += 8

        if offset + chunk_size > total_len:
            raise MalformedWAVError("Truncated WAV chunk payload.")

        if chunk_id == b"fmt ":
            if chunk_size < 16:
                raise MalformedWAVError("Invalid fmt chunk size in WAV header.")

            (
                audio_format,
                channels,
                sample_rate,
                byte_rate,
                block_align,
                bits_per_sample,
            ) = struct.unpack("<HHIIHH", audio_bytes[offset : offset + 16])
            fmt_found = True
        elif chunk_id == b"data":
            if not fmt_found:
                raise MalformedWAVError("WAV data chunk encountered before fmt chunk.")
            data_bytes_len = chunk_size
            data_found = True

        offset += chunk_size

        # Verify padding byte existence for odd-sized RIFF chunks
        padding = chunk_size % 2
        if padding > 0:
            if offset + padding > total_len:
                raise MalformedWAVError("Missing padding byte for odd-sized WAV chunk.")
            offset += padding

    if not fmt_found or not data_found:
        raise MalformedWAVError("Missing required WAV fmt or data chunk.")

    # Validate WAV properties
    if audio_format != 1:  # 1 == WAVE_FORMAT_PCM
        raise InvalidWAVFormatError(
            f"Unsupported WAV encoding format ({audio_format}). Only uncompressed PCM is supported."
        )

    if channels != 1:
        raise InvalidWAVFormatError(
            f"Unsupported channel count ({channels}). Only mono (1 channel) is supported."
        )

    if bits_per_sample != 16:
        raise InvalidWAVFormatError(
            f"Unsupported sample width ({bits_per_sample} bits). Only 16-bit PCM is supported."
        )

    if sample_rate < 8000 or sample_rate > 48000:
        raise InvalidWAVFormatError(
            f"Sample rate {sample_rate} Hz is out of the supported range (8000-48000 Hz)."
        )

    bytes_per_sample = bits_per_sample // 8
    expected_block_align = channels * bytes_per_sample
    expected_byte_rate = sample_rate * expected_block_align

    if block_align != expected_block_align:
        raise MalformedWAVError(
            f"Corrupt WAV header: block_align is {block_align}, expected {expected_block_align}."
        )

    if byte_rate != expected_byte_rate:
        raise MalformedWAVError(
            f"Corrupt WAV header: byte_rate is {byte_rate}, expected {expected_byte_rate}."
        )

    if data_bytes_len % expected_block_align != 0:
        raise MalformedWAVError("WAV frame data is incomplete or unaligned with frame size.")

    frame_count = data_bytes_len // expected_block_align
    duration = frame_count / sample_rate

    if duration < 0.5 or duration > 30.0:
        raise InvalidWAVFormatError(
            f"Audio duration {duration:.2f}s is out of the supported range (0.5-30.0s)."
        )

    return WAVMetadata(
        sample_rate=sample_rate,
        frame_count=frame_count,
        duration=duration,
    )