"""Bounded local byte inspection; no upload, diagnosis or automatic deidentification."""
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import warnings
import zlib

MAX_BYTES = 64 * 1024 * 1024
MAX_PIXELS = 16_000_000
MAX_DURATION = 60.0
MAX_FRAMES = 3600
TIMEOUT = 30
MAX_CONTAINER_SEGMENTS = 65536
SIGNATURES = {'.png': ('PNG', 'png_pipe'), '.jpg': ('JPEG', 'jpeg_pipe'),
              '.jpeg': ('JPEG', 'jpeg_pipe'), '.webm': ('WEBM', 'matroska'),
              '.mp4': ('MP4', 'mov')}


def local_path(root, value):
    """Reject aliases, traversal, URL, Windows ADS and links/reparse points."""
    root = Path(root).resolve(strict=True)
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('invalid_local_path')
    parts = PurePosixPath(value)
    if parts.is_absolute() or any(p in {'..', '.'} for p in value.split('/')):
        raise ValueError('invalid_local_path')
    current = root
    for part in parts.parts:
        current = current / part
        if current.is_symlink() or (hasattr(current, 'is_junction') and current.is_junction()):
            raise ValueError('linked_path_forbidden')
        if current.exists() and getattr(current.stat(), 'st_file_attributes', 0) & 0x400:
            raise ValueError('reparse_path_forbidden')
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError('invalid_local_file')
    if resolved.stat().st_nlink > 1:
        raise ValueError('hardlinked_file_forbidden')
    return resolved


def resolve_media_tool(tool):
    """Resolve fixed tools from absolute PATH entries, never the current directory.

    PATH remains an operator-controlled trust boundary, not an OS sandbox.
    Avoid Windows' implicit current-directory search and script launchers.
    """
    if tool not in {'ffmpeg', 'ffprobe'}:
        raise ValueError('local_media_tool_unavailable')
    current = Path.cwd().resolve()
    filename = tool + ('.exe' if os.name == 'nt' else '')
    for entry in os.get_exec_path():
        directory = Path(entry)
        if not directory.is_absolute():
            continue
        try:
            directory = directory.resolve(strict=True)
            if directory == current:
                continue
            executable = (directory / filename).resolve(strict=True)
            if executable.parent != current and executable.is_file() and os.access(executable, os.X_OK):
                return str(executable)
        except (OSError, ValueError, RuntimeError):
            continue
    raise ValueError('local_media_tool_unavailable')


def _run(tool, args):
    executable = resolve_media_tool(tool)
    # Do not echo codec errors, file paths or arbitrary metadata to logs/reports.
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            proc = subprocess.run([executable, *args], stdin=subprocess.DEVNULL,
                                  stdout=out, stderr=err, timeout=TIMEOUT, check=False,
                                  creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError('media_process_failed_or_timed_out') from exc
        if proc.returncode or out.tell() > 1024 * 1024:
            raise ValueError('media_decode_or_probe_failed')
        out.seek(0)
        return out.read()


def _signature(head):
    if head.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'PNG'
    if head.startswith(b'\xff\xd8\xff'):
        return 'JPEG'
    if head.startswith(b'\x1aE\xdf\xa3'):
        return 'WEBM'
    if head[4:8] == b'ftyp':
        return 'MP4'
    return None


def _png_metadata(path):
    """Read every chunk, including post-IDAT data, without trusting Pillow.info.

    Only core image chunks are metadata-free for blind admission. Ancillary,
    private or unknown chunks and trailing bytes are retained but flagged.
    """
    metadata, count, saw_idat = False, 0, False
    size = path.stat().st_size
    with path.open('rb') as stream:
        if stream.read(8) != b'\x89PNG\r\n\x1a\n':
            raise ValueError('invalid_png_structure')
        while True:
            header = stream.read(8)
            count += 1
            if len(header) != 8 or count > MAX_CONTAINER_SEGMENTS:
                raise ValueError('invalid_png_structure')
            length, kind = int.from_bytes(header[:4], 'big'), header[4:]
            if (length > size - stream.tell() - 4 or not re.fullmatch(b'[A-Za-z]{4}', kind)
                    or (count == 1 and (kind != b'IHDR' or length != 13))
                    or (count > 1 and kind == b'IHDR')):
                raise ValueError('invalid_png_structure')
            metadata |= kind not in {b'IHDR', b'PLTE', b'IDAT', b'IEND'}
            digest = zlib.crc32(kind)
            remaining = length
            while remaining:
                data = stream.read(min(remaining, 65536))
                if not data:
                    raise ValueError('invalid_png_structure')
                digest = zlib.crc32(data, digest)
                remaining -= len(data)
            crc = stream.read(4)
            if len(crc) != 4 or int.from_bytes(crc, 'big') != digest & 0xffffffff:
                raise ValueError('invalid_png_structure')
            if kind == b'IDAT':
                saw_idat = True
            if kind == b'IEND':
                if length or not saw_idat:
                    raise ValueError('invalid_png_structure')
                return metadata or bool(stream.read(1))


def _jpeg_metadata(path):
    """Walk segments and all entropy scans; embedded EOI bytes are not boundaries."""
    data = path.read_bytes()  # Snapshot is already bounded by MAX_BYTES.
    if not data.startswith(b'\xff\xd8'):
        raise ValueError('invalid_jpeg_structure')
    offset, count, scans, metadata = 2, 0, 0, False
    image_markers = {0xdb, 0xc4, 0xdd, 0xda} | (set(range(0xc0, 0xd0)) - {0xc4, 0xc8, 0xcc})
    while offset < len(data):
        count += 1
        if count > MAX_CONTAINER_SEGMENTS or data[offset] != 0xff:
            raise ValueError('invalid_jpeg_structure')
        while offset < len(data) and data[offset] == 0xff:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker == 0xd9:
            if not scans:
                raise ValueError('invalid_jpeg_structure')
            return metadata or offset != len(data)
        if marker == 0 or marker == 0xd8 or 0xd0 <= marker <= 0xd7:
            raise ValueError('invalid_jpeg_structure')
        if marker == 0x01:
            metadata = True
            continue
        if offset + 2 > len(data):
            break
        length = int.from_bytes(data[offset:offset + 2], 'big')
        end = offset + length
        if length < 2 or end > len(data):
            raise ValueError('invalid_jpeg_structure')
        payload = data[offset + 2:end]
        if marker == 0xe0:
            # Minimal JFIF header only; thumbnails/JFXX/extra APP0 data are not exempt.
            clean_jfif = (len(payload) == 14 and payload[:5] == b'JFIF\0'
                          and payload[5:7] in {b'\x01\x00', b'\x01\x01', b'\x01\x02'}
                          and payload[7] <= 2 and payload[12:14] == b'\0\0')
            metadata |= not clean_jfif
        elif marker not in image_markers:
            metadata = True
        offset = end
        if marker != 0xda:
            continue
        scans += 1
        while True:
            found = data.find(b'\xff', offset)
            if found < 0:
                raise ValueError('invalid_jpeg_structure')
            following = found + 1
            while following < len(data) and data[following] == 0xff:
                following += 1
            if following >= len(data):
                raise ValueError('invalid_jpeg_structure')
            code = data[following]
            if code == 0:
                if following != found + 1:
                    raise ValueError('invalid_jpeg_structure')
                offset = following + 1  # Stuffed entropy byte, not a marker.
            elif 0xd0 <= code <= 0xd7:
                offset = following + 1
            else:
                offset = found  # Next scan/segment/EOI is parsed by the outer loop.
                break
    raise ValueError('invalid_jpeg_structure')


def _webm_doctype(path):
    """Read the bounded EBML header, not arbitrary matching bytes in payload."""
    with path.open('rb') as stream:
        data = stream.read(4096)

    def vint(offset, keep_marker=False):
        if offset >= len(data) or not data[offset]:
            raise ValueError('invalid_ebml_header')
        width = 1
        marker = 0x80
        while not data[offset] & marker:
            marker >>= 1
            width += 1
        if offset + width > len(data) or width > (4 if keep_marker else 8):
            raise ValueError('invalid_ebml_header')
        value = int.from_bytes(data[offset:offset + width], 'big')
        if not keep_marker:
            value &= (1 << (7 * width)) - 1
        return value, offset + width

    size, cursor = vint(4)
    end = cursor + size
    if end > len(data):
        raise ValueError('invalid_ebml_header')
    doctype = None
    while cursor < end:
        element, cursor = vint(cursor, True)
        length, cursor = vint(cursor)
        if cursor + length > end:
            raise ValueError('invalid_ebml_header')
        if element == 0x4282:
            if doctype is not None:
                raise ValueError('invalid_ebml_header')
            doctype = data[cursor:cursor + length]
        cursor += length
    if doctype != b'webm':
        raise ValueError('webm_doctype_required')


def _snapshot(root, asset, directory, max_bytes):
    if not isinstance(asset, dict) or not re.fullmatch('[0-9a-f]{64}', str(asset.get('sha256', ''))):
        raise ValueError('invalid_asset_digest')
    expected_size = asset.get('size_bytes')
    if type(expected_size) is not int or not 0 < expected_size <= max_bytes:
        raise ValueError('invalid_or_excessive_size')
    original = local_path(root, asset.get('path'))
    suffix = original.suffix.lower()
    if suffix not in SIGNATURES:
        raise ValueError('unsupported_format_dicom_requires_separate_review')
    if original.stat().st_size != expected_size:
        raise ValueError('size_mismatch')
    snapshot = Path(directory) / ('input' + suffix)
    digest = hashlib.sha256()
    total = 0
    with original.open('rb') as source, snapshot.open('xb') as target:
        if os.fstat(source.fileno()).st_nlink > 1:
            raise ValueError('hardlinked_file_forbidden')
        while chunk := source.read(1024 * 1024):
            total += len(chunk)
            if total > max_bytes or total > expected_size:
                raise ValueError('size_limit_exceeded')
            digest.update(chunk)
            target.write(chunk)
    if total != expected_size or digest.hexdigest() != asset['sha256']:
        raise ValueError('integrity_mismatch')
    with snapshot.open('rb') as stream:
        if _signature(stream.read(32)) != SIGNATURES[suffix][0]:
            raise ValueError('extension_signature_mismatch')
    return snapshot


def _inspect_snapshot(path, max_pixels, max_duration):
    suffix = path.suffix.lower()
    if suffix in {'.png', '.jpg', '.jpeg'}:
        metadata = _png_metadata(path) if suffix == '.png' else _jpeg_metadata(path)
        try:
            from PIL import Image
        except ImportError as exc:
            raise ValueError('pillow_required_for_images') from exc
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(path) as image:
                width, height = image.size
                if not 0 < width * height <= max_pixels:
                    raise ValueError('pixel_limit_exceeded')
                if image.format != SIGNATURES[suffix][0] or getattr(image, 'n_frames', 1) != 1:
                    raise ValueError('image_format_or_animation_not_supported')
                image.verify()
            with Image.open(path) as image:
                image.load()
                metadata |= any(k not in {'jfif', 'jfif_version',
                    'jfif_unit', 'jfif_density', 'dpi', 'aspect',
                    'progressive', 'progression'} for k in image.info)
        return dict(kind='image', format=SIGNATURES[suffix][0], width=width, height=height,
                    duration_seconds=None, fps=None, decoded_frames=1, metadata_present=metadata)
    common = ['-v', 'error', '-protocol_whitelist', 'file,pipe', '-f', SIGNATURES[suffix][1]]
    if suffix == '.webm':
        _webm_doctype(path)
    probe = json.loads(_run('ffprobe', [*common, '-show_entries',
        'stream=codec_type,codec_name,width,height,r_frame_rate:format=duration:format_tags', '-of', 'json', str(path)]))
    streams = probe.get('streams', [])
    if len(streams) != 1 or streams[0].get('codec_type') != 'video':
        raise ValueError('only_one_video_stream_without_audio_or_attachments_allowed')
    stream = streams[0]
    if suffix == '.webm' and stream.get('codec_name') not in {'vp8', 'vp9', 'av1'}:
        raise ValueError('webm_compatible_video_codec_required')
    width, height = int(stream['width']), int(stream['height'])
    duration = float(probe['format']['duration'])
    num, den = map(int, stream['r_frame_rate'].split('/'))
    fps = num / den
    if not 0 < width * height <= max_pixels:
        raise ValueError('pixel_limit_exceeded')
    if not math.isfinite(duration) or not 0 < duration <= max_duration:
        raise ValueError('duration_limit_exceeded')
    if not math.isfinite(fps) or not 0 < fps <= 120 or duration * fps > MAX_FRAMES:
        raise ValueError('frame_limit_exceeded')
    _run('ffmpeg', [*common[:2], '-nostdin', '-xerror', '-err_detect', 'explode',
        *common[2:], '-i', str(path), '-map', '0:v:0', '-an', '-sn', '-dn', '-threads', '1', '-f', 'null', '-'])
    counted = json.loads(_run('ffprobe', [*common, '-count_frames', '-select_streams', 'v:0',
        '-show_entries', 'stream=nb_read_frames', '-of', 'json', str(path)]))
    frames = int(counted['streams'][0]['nb_read_frames'])
    if not 0 < frames <= MAX_FRAMES:
        raise ValueError('decoded_frame_limit_exceeded')
    return dict(kind='video', format=SIGNATURES[suffix][0], width=width, height=height,
                duration_seconds=duration, fps=fps, decoded_frames=frames,
                metadata_present=bool(probe['format'].get('tags')))


def inspect_media(root, asset, *, max_bytes=MAX_BYTES, max_pixels=MAX_PIXELS,
                  max_duration=MAX_DURATION):
    result = dict(errors=[], temporal_interpretation_validated=False,
                  diagnostic_validation=False, deidentification_certified=False)
    try:
        with tempfile.TemporaryDirectory(prefix='emergency-media-') as directory:
            snapshot = _snapshot(root, asset, directory, max_bytes)
            result.update(_inspect_snapshot(snapshot, max_pixels, max_duration))
            result.update(sha256=asset['sha256'], asset_id=asset['id'], size_bytes=asset['size_bytes'])
    except Exception as exc:
        # Fixed codes only: parser exceptions can contain embedded identifiers.
        code = str(exc) if type(exc) is ValueError and re.fullmatch('[a-z0-9_]+', str(exc)) else 'invalid_media'
        result['errors'].append(code)
    return result


def extract_navigation_frames(root, asset, output_dir, *, count=4):
    if type(count) is not int or not 2 <= count <= 16:
        raise ValueError('frame_sample_count_out_of_range')
    output = Path(output_dir)
    # A fresh destination avoids overwriting files or following planted links.
    if output.exists():
        raise ValueError('frame_destination_must_be_new')
    with tempfile.TemporaryDirectory(prefix='emergency-video-') as directory:
        snapshot = _snapshot(root, asset, directory, MAX_BYTES)
        report = _inspect_snapshot(snapshot, MAX_PIXELS, MAX_DURATION)
        if report['kind'] != 'video' or report['decoded_frames'] < count:
            raise ValueError('insufficient_video_frames')
        total = report['decoded_frames']
        indices = [round(i * (total - 1) / (count - 1)) for i in range(count)]
        frames = []
        # Probe actual presentation timestamps once, not once per sampled frame.
        pts = json.loads(_run('ffprobe', ['-v', 'error', '-protocol_whitelist', 'file,pipe',
            '-f', SIGNATURES[snapshot.suffix][1], '-select_streams', 'v:0', '-show_frames',
            '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(snapshot)]))
        try:
            stamps = [float(frame['best_effort_timestamp_time']) for frame in pts['frames']]
            if len(stamps) != total or any(not math.isfinite(stamp) for stamp in stamps):
                raise ValueError('invalid_frame_timestamp')
        except (KeyError, TypeError, ValueError):
            raise ValueError('invalid_frame_timestamp') from None
        staging = Path(directory) / 'frames'
        staging.mkdir()
        for seq, index in enumerate(indices):
            file = staging / f'frame-{seq:03d}.png'
            _run('ffmpeg', ['-v', 'error', '-nostdin', '-xerror', '-protocol_whitelist', 'file,pipe',
                '-f', SIGNATURES[snapshot.suffix][1], '-i', str(snapshot), '-vf',
                f'select=eq(n\\,{index})', '-frames:v', '1', '-threads', '1', str(file)])
            stamp = stamps[index]
            frames.append(dict(sequence_index=seq, source_frame_index=index,
                presentation_time_seconds=stamp, file=file.name,
                sha256=hashlib.sha256(file.read_bytes()).hexdigest(), parent_sha256=asset['sha256']))
        manifest = dict(frames=frames, source_sha256=asset['sha256'],
            sampling='uniform_decoded_frame_index_navigation_only',
            temporal_interpretation_validated=False, diagnostic_validation=False,
            split_inheritance_required=True)
        (staging / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        shutil.copytree(staging, output)
        return manifest
