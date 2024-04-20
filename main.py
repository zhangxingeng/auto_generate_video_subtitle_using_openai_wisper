'''
Given a video, generate transcript using wisper model
'''

from pathlib import Path
import argparse
import json
import whisper
from whisper.tokenizer import LANGUAGES

import torch
from utils import segment_to_vtt, write_vtt, _msg, extract_audio, check_audio_integrity


def _parse_args():
    parser = argparse.ArgumentParser(description="Process some languages.")
    parser.add_argument('--lang', type=str, help="Language code (e.g., 'en', 'zh', 'ja')")
    parser.add_argument('--data_dir', type=str, default="./data/", help="file Dir, no need to change")
    parser.add_argument('--model_dir', type=str, default="./model/", help="model Dir, no need to change")
    parser.add_argument('--list_lang', action='store_true', help="List all supported languages")
    return parser.parse_args()


def try_get_lang(data_dir: Path, arg_lang):
    ''' try to get language from args or data directory '''
    if not arg_lang:
        subdirs = [x for x in data_dir.iterdir() if x.is_dir()]
        first_dir_name = str(subdirs[0].name) if len(subdirs) > 0 else None
        if first_dir_name and first_dir_name in LANGUAGES:
            return first_dir_name
    elif arg_lang in LANGUAGES:
        return arg_lang
    return None


if __name__ == "__main__":
    args = _parse_args()
    # --- list all supported languages ---
    if args.list_lang:
        print(json.dumps(LANGUAGES, indent=4))
        exit()
    # --- parse args, create directory ---
    DATA_DIR = Path(args.data_dir)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR = Path(args.model_dir)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    LANGUAGE = try_get_lang(DATA_DIR, args.lang)
    if not LANGUAGE:
        print("Please use supported Languages, run \
            `python main.py --list_lang` to list all supported languages")
        exit()
    VIDEO_DIR = DATA_DIR / LANGUAGE
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    # --- start getting videos ---
    # RGLOB_VIDEO = "**/*.{mp4,ts,avi,mkv,flv,mov,wmv,webm}"
    _extensions = ["mp4", "ts", "avi", "mkv", "flv", "mov", "wmv", "webm"]
    video_list = [f for ext in _extensions for f in VIDEO_DIR.rglob(f"**/*.{ext}")]
    if len(video_list) == 0:
        print(f"no video directory found, please put video files in {VIDEO_DIR}")
        exit()

    use_cuda = torch.cuda.is_available()
    DEVICE = "cuda" if use_cuda else "cpu"
    MODEL = whisper.load_model("large", device=DEVICE, download_root=MODEL_DIR)
    AUDIO_TYPE = ".wav"

    for vid_path in video_list:
        # if srt file already exists, skip
        _msg(f"------ Starting: {vid_path.name} ------")
        vtt_path = vid_path.with_suffix(f".{LANGUAGE}.vtt")
        audio_path = vid_path.with_suffix(AUDIO_TYPE)
        if vtt_path.exists():
            if audio_path.exists():
                audio_path.unlink()  # remove temp files
            _msg("vtt already exists, skip to next video.")
            continue

        if check_audio_integrity(audio_path) is False:
            audio_path = extract_audio(Path(vid_path), use_cuda, suffix=AUDIO_TYPE)
        pass_cond = audio_path.exists() and check_audio_integrity(audio_path)
        RES = _msg("audio extraction", yes=pass_cond)
        if not RES:
            continue

        result = MODEL.transcribe(str(audio_path), language=LANGUAGE)
        res_segment = result["segments"]
        RES = _msg("transcription", yes=len(res_segment) > 0)
        if not RES:
            continue

        vtt_str_list = segment_to_vtt(res_segment)
        write_vtt(vtt_str_list, vtt_path)
        # remove audio file
        if audio_path.exists():
            audio_path.unlink()
        RES = _msg("generate vtt file", yes=vtt_path.exists())

    _msg("------ All Task Finished: Exiting ------")
