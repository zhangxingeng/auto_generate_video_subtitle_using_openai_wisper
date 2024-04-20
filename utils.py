'''
Helper functions for main.py
'''
import subprocess
import os
from pathlib import Path


def extract_audio(video_path: Path, use_gpu=False, suffix=".mp3") -> Path:
    ''' extract audio from video using ffmpeg '''
    audio_path = video_path.with_suffix(suffix)
    ffmpeg_opts = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error", "-y", "-i", str(video_path),
        "-vn", "-ar", "44100", "-b:a", "192K",
        "-c:a", "libmp3lame", "-af", "aformat=sample_fmts=fltp:channel_layouts=stereo"
    ]
    if use_gpu:
        ffmpeg_opts.extend(["-c:v", "h264_nvenc", "-gpu", "0"])
    ffmpeg_opts.append(str(audio_path))
    subprocess.check_call(ffmpeg_opts)
    return audio_path


def check_audio_integrity(audio_path: Path):
    """ Checks the integrity of an audio file using FFmpeg. """
    if not audio_path.exists():
        return False
    temp_file = Path("/dev/null") if audio_path.suffix != '.mp3' else Path("./null.mp3")
    ffmpeg_opts = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error", "-i", str(audio_path),
        "-f", "null",  # Directs FFmpeg to not produce any output files
        str(temp_file)
    ]
    try:
        subprocess.check_call(ffmpeg_opts, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        os.remove(audio_path)
        return False


def _msg(text, yes=None):
    ''' print a message '''
    if yes is None:
        print(f"{text}")
    else:
        pre = "✅" if yes else "❌"
        print(f"{pre} {text}")
    return yes


def _to_time_str(seconds: float) -> str:
    ''' Given a float timestamp in seconds, return a formatted timestamp in HH:MM:SS.mmm'''
    assert seconds >= 0, "Non-negative timestamp expected"
    total_milliseconds = round(seconds * 1000)
    hours, remainder = divmod(total_milliseconds, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def segment_cleanup(curr_seg, next_seg, max_text_len=50):
    """Clean up and prepare a single VTT segment."""
    start, end, text = curr_seg["start"], curr_seg["end"], curr_seg["text"].strip()

    if len(text.split()) > max_text_len:  # shorten if too long
        text = ' '.join(text.split()[:max_text_len]) + '...'
    if next_seg and text == next_seg["text"].strip():  # merge identical
        next_seg["start"] = start
        return None
    start_str, end_str = _to_time_str(start), _to_time_str(end)
    return f"\n{start_str} --> {end_str}\n{text}\n"


def segment_to_vtt(seg_list):
    """Convert a list of segments into formatted VTT entries."""
    res = []
    for i, seg in enumerate(seg_list):
        next_seg = seg_list[i + 1] if i + 1 < len(seg_list) else None
        vtt_entry = segment_cleanup(seg, next_seg)
        if vtt_entry:
            res.append(vtt_entry)
    return res


def write_vtt(str_list, vtt_path):
    """Write strings to a VTT file."""
    with open(vtt_path, "w", encoding='utf-8') as f:
        f.write("WEBVTT\n")
        f.writelines(str_list)
