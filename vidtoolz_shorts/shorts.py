import moviepy as mpy
import os
import subprocess
import tempfile
import textwrap
import numpy as np
from itertools import cycle

try:
    from moviepy.tools import convert_to_seconds
except ImportError:
    def convert_to_seconds(time_value):
        if isinstance(time_value, (int, float)):
            return time_value

        time_value = str(time_value).strip()
        if time_value.endswith("s"):
            return float(time_value[:-1])

        parts = [float(part) for part in time_value.split(":")]
        total = 0.0
        for part in parts:
            total = total * 60 + part
        return total

try:
    from moviepy import vfx
except ImportError:
    class _VfxCompat:
        def __getattr__(self, name):
            def effect(*args, **kwargs):
                return (name, args, kwargs)

            return effect

    vfx = _VfxCompat()

if not hasattr(mpy, "VideoFileClip"):
    from moviepy.video.io.VideoFileClip import VideoFileClip

    mpy.VideoFileClip = VideoFileClip
if not hasattr(mpy, "TextClip"):
    from moviepy.video.VideoClip import TextClip

    mpy.TextClip = TextClip
if not hasattr(mpy, "AudioFileClip"):
    from moviepy.audio.io.AudioFileClip import AudioFileClip

    mpy.AudioFileClip = AudioFileClip
if not hasattr(mpy, "CompositeAudioClip"):
    from moviepy.audio.AudioClip import CompositeAudioClip

    mpy.CompositeAudioClip = CompositeAudioClip
if not hasattr(mpy, "CompositeVideoClip"):
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

    mpy.CompositeVideoClip = CompositeVideoClip

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_HERE, "assets")

_FFMPEG_TEXT_COLORS = [
    "plum",
    "0xB0C4DE",
    "0x87CEFA",
    "turquoise",
    "0x00FF7F",
    "0xFF8C00",
    "0x6B8E23",
    "yellow",
]


def construct_prefix(input_args):
    """
    Flattens the nested list from --input and joins all elements with underscores.

    Args:
        input_args (list): A nested list of inputs passed to --input.
                           Example: [['hello', 'world'], ['foo']] -> "hello_world_foo"

    Returns:
        str: A single string with all inputs joined by underscores.
    """
    if not input_args:
        return "shorts"

    # Flatten the nested list structure (because action="append", nargs="*")
    flat_inputs = [item for sublist in input_args for item in sublist] + ["#shorts"]

    # Join with underscores
    return "_".join(flat_inputs)


def determine_output_path(input_file, output_file, prefix):
    input_dir, input_filename = os.path.split(input_file)
    name, _ = os.path.splitext(input_filename)

    if output_file:
        output_dir, output_filename = os.path.split(output_file)
        if not output_dir:  # If no directory is specified, use input file's directory
            return os.path.join(input_dir, output_filename)
        return output_file
    else:
        return os.path.join(input_dir, f"{name}_{prefix}.mp4")


def create_shorts_from_vid(fname, startat=0.0, crop_ratio=1):
    clip = mpy.VideoFileClip(fname)
    clip = clip.subclipped(start_time=startat)
    w, h = clip.size

    # crop_ratio = 1 #  4/5 # 9/16
    crop_width = h * crop_ratio
    x1, x2 = (w - crop_width) // 2, (w + crop_width) // 2
    cclip = clip.cropped(x1=x1, y1=0, x2=x2, y2=h)

    return cclip


def addcomment(comment, size=20):
    lines = textwrap.wrap(comment, width=size)
    nline = len(lines)
    new_comment = "\n".join(lines)
    return new_comment, nline


def zoom_in_out(t):
    """Defines a zoom in and out function based on a sin wave"""
    return 0.9 + 0.3 * np.sin(t / 3)


def get_text_clips_n_notification(textlist, clip_time=60, height=800, wid=688, size=20):
    # colors from https://imagemagick.org/script/color.php
    colors = [
        "plum",
        "LightSteelBlue",
        "LightSkyBlue",
        "turquoise",
        "SpringGreen",
        # "LightGoldenrod",
        # "DarkGoldenrod",
        "DarkOrange",
        "OliveDrab",
        "yellow",
    ]

    notification_fname = os.path.join(_ASSETS, "notification.mp3")
    subcribe_fname = os.path.join(_ASSETS, "subscribe.mp3")

    cols = cycle(colors)
    if clip_time > 6:
        textlist.append("Visit the channel for full Videos!")

    text_clips = []
    notification_sounds = []
    ntext = len(textlist)
    try:
        interval = int(clip_time / ntext)
    except ZeroDivisionError:
        interval = 1
        pass
    for i, post in enumerate(textlist):
        return_comment, nline = addcomment(post, size=60)
        color = next(cols)
        fontsize = 30
        # color="white"
        text_hight = 60  # max(200, nline*fontsize)
        txt = mpy.TextClip(
            font="Courier",
            text=return_comment,
            font_size=fontsize,
            bg_color=color,
            size=(wid + 5, text_hight + 10),
            method="caption",
            stroke_width=2,
            stroke_color="black",
            color="white",
        )

        # txt = txt.on_color(size=(txt.w+10,txt.h-10),
        #          color=(0,0,0), pos=(6,'center'), col_opacity=0.6)
        # txt = txt.with_background_color(col_opacity=0.4)
        txt = txt.with_position((0, 100))
        txt = txt.with_start((0, 0 + (i * interval)))
        txt = txt.with_duration(interval + 1)
        # txt = txt.crossfadein(0.5)
        txt = txt.with_effects([vfx.CrossFadeIn(0.5)])
        txt = txt.with_effects([vfx.CrossFadeOut(0.5)])
        # txt = txt.crossfadeout(0.5)
        # animation
        txt = txt.resized(zoom_in_out)
        text_clips.append(txt)
        print(color, i, 0 + (i * interval))

        notification = mpy.AudioFileClip(notification_fname)
        notification = notification.with_start((0, 0 + (i * interval)))
        notification_sounds.append(notification)

    if clip_time > 6:
        subscribe = mpy.AudioFileClip(subcribe_fname)
        subscribe = subscribe.with_start((0, clip_time - 6))
        notification_sounds.append(subscribe)
    return text_clips, notification_sounds


def _read_text_inputs(args):
    if args.text_file is not None:
        with open(args.text_file, "r") as fin:
            return fin.readlines()
    return [" ".join(inp) for inp in args.input]


def _write_shorts_text_file(fname, textlist, has_text_file):
    if has_text_file:
        return

    outpath_tx = os.path.join(os.path.dirname(fname), "Shorts.txt")
    with open(outpath_tx, "w") as fout:
        fout.write("\n".join(textlist[:-1]))


def _run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr)
        result.check_returncode()
    return result


def _ffprobe_value(args):
    result = _run_command(["ffprobe", "-v", "error"] + args)
    return result.stdout.strip()


def _ffprobe_video_size(fname):
    output = _ffprobe_value(
        [
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=p=0:s=x",
            fname,
        ]
    )
    width, height = output.split("x", 1)
    return int(width), int(height)


def _ffprobe_duration(fname):
    output = _ffprobe_value(
        [
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            fname,
        ]
    )
    return float(output)


def _ffprobe_has_audio(fname):
    output = _ffprobe_value(
        [
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            fname,
        ]
    )
    return bool(output)


def _escape_drawtext_text(text):
    return (
        text.rstrip("\n")
        .replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace(",", "\\,")
        .replace(";", "\\;")
        .replace("\n", "\\n")
    )


def _escape_filter_value(value):
    return str(value).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _write_ffmpeg_text_files(textlist):
    paths = []
    for text in textlist:
        text_file = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False, suffix=".txt"
        )
        with text_file:
            text_file.write(text.rstrip("\n"))
        paths.append(text_file.name)
    return paths


def _delete_files(paths):
    for path in paths:
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass


def _make_ffmpeg_textlist(textlist, clip_time):
    textlist = list(textlist)
    if clip_time > 6:
        textlist.append("Visit the channel for full Videos!")
    return textlist


def _build_ffmpeg_filter_complex(
    textlist,
    clip_time,
    start_time,
    crop_ratio,
    no_clipping,
    has_audio,
    text_files=None,
):
    video_filters = [f"[0:v]trim=start={start_time}:duration={clip_time}", "setpts=PTS-STARTPTS"]

    if not no_clipping:
        crop_width = f"trunc(min(iw\\,ih*{crop_ratio})/2)*2"
        video_filters.append(f"crop=w='{crop_width}':h=ih:x='(iw-{crop_width})/2':y=0")

    textlist = _make_ffmpeg_textlist(textlist, clip_time)
    notification_starts = []
    interval = int(clip_time / len(textlist)) if textlist else 1
    colors = cycle(_FFMPEG_TEXT_COLORS)

    if text_files is not None and len(text_files) != len(textlist):
        raise ValueError("text_files must match textlist length")

    for i, post in enumerate(textlist):
        return_comment, _ = addcomment(post, size=60)
        start = i * interval
        end = start + interval + 1
        color = next(colors)
        if text_files is None:
            text_source = f"text='{_escape_drawtext_text(return_comment)}'"
        else:
            text_source = f"textfile='{_escape_filter_value(text_files[i])}'"
        video_filters.append(
            "drawtext="
            f"{text_source}:"
            "font='Helvetica-Bold':"
            "fontcolor=white:"
            "fontsize=54:"
            "borderw=4:"
            "bordercolor=black@0.85:"
            "shadowcolor=black@0.7:"
            "shadowx=3:"
            "shadowy=3:"
            "box=1:"
            f"boxcolor={color}@0.88:"
            "boxborderw=24:"
            "x=(w-text_w)/2:"
            "y=h*0.12:"
            f"enable='between(t,{start},{end})'"
        )
        notification_starts.append(start)

    fade_duration = min(1, clip_time)
    fade_start = max(clip_time - fade_duration, 0)
    video_filters.append(f"fade=t=out:st={fade_start}:d={fade_duration}")

    if clip_time > 1:
        loop_duration = 1
        loop_offset = clip_time - loop_duration
        video_filters.append("fps=30,format=yuv420p,split=2[vloopmain][vloophead]")
        filter_parts = [
            ",".join(video_filters),
            (
                f"[vloophead]trim=duration={loop_duration},"
                "setpts=PTS-STARTPTS,fps=30[vloopheadtrim]"
            ),
            (
                "[vloopmain][vloopheadtrim]"
                f"xfade=transition=fade:duration={loop_duration}:offset={loop_offset}[v]"
            ),
        ]
    else:
        video_filters.append("format=yuv420p[v]")
        filter_parts = [",".join(video_filters)]

    audio_labels = []
    if has_audio:
        filter_parts.append(
            f"[0:a]atrim=start={start_time}:duration={clip_time},asetpts=PTS-STARTPTS[a0]"
        )
    else:
        filter_parts.append(f"anullsrc=channel_layout=stereo:sample_rate=44100:d={clip_time}[a0]")
    audio_labels.append("[a0]")

    for input_number, start in enumerate(notification_starts, start=1):
        label = f"[a{input_number}]"
        delay_ms = int(start * 1000)
        filter_parts.append(
            f"[{input_number}:a]adelay={delay_ms}:all=1,atrim=duration={clip_time}{label}"
        )
        audio_labels.append(label)

    if clip_time > 6:
        subscribe_input = len(notification_starts) + 1
        subscribe_label = f"[a{subscribe_input}]"
        delay_ms = int((clip_time - 6) * 1000)
        filter_parts.append(
            f"[{subscribe_input}:a]adelay={delay_ms}:all=1,atrim=duration={clip_time}{subscribe_label}"
        )
        audio_labels.append(subscribe_label)

    filter_parts.append(
        "".join(audio_labels)
        + f"amix=inputs={len(audio_labels)}:duration=first:dropout_transition=0[a]"
    )
    return ";".join(filter_parts)


def _build_ffmpeg_command(
    fname,
    output,
    textlist,
    clip_time,
    start_time,
    crop_ratio,
    no_clipping,
    has_audio,
    text_files=None,
):
    notification_fname = os.path.join(_ASSETS, "notification.mp3")
    subscribe_fname = os.path.join(_ASSETS, "subscribe.mp3")
    ffmpeg_textlist = _make_ffmpeg_textlist(textlist, clip_time)

    command = ["ffmpeg", "-y", "-i", fname]
    for _ in ffmpeg_textlist:
        command.extend(["-i", notification_fname])
    if clip_time > 6:
        command.extend(["-i", subscribe_fname])

    command.extend(
        [
            "-filter_complex",
            _build_ffmpeg_filter_complex(
                textlist,
                clip_time,
                start_time,
                crop_ratio,
                no_clipping,
                has_audio,
                text_files,
            ),
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-t",
            str(clip_time),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-shortest",
            output,
        ]
    )
    return command


def mainrun_ffmpeg(args):
    fname = args.filename.strip()

    prefix = construct_prefix(args.input)
    output = determine_output_path(fname, args.output, prefix)
    textlist = _read_text_inputs(args)
    print(textlist)

    start_time = convert_to_seconds(args.startat)
    duration = max(_ffprobe_duration(fname) - start_time, 0)
    clip_time = duration if args.time < 0 else min(duration, args.time)
    _ffprobe_video_size(fname)
    has_audio = _ffprobe_has_audio(fname)

    _write_shorts_text_file(fname, textlist, args.text_file is not None)
    ffmpeg_textlist = _make_ffmpeg_textlist(textlist, clip_time)
    text_files = _write_ffmpeg_text_files(
        [addcomment(text, size=60)[0] for text in ffmpeg_textlist]
    )
    try:
        command = _build_ffmpeg_command(
            fname,
            output,
            textlist,
            clip_time,
            start_time,
            args.ratio,
            args.no_clipping,
            has_audio,
            text_files,
        )
        _run_command(command)
    finally:
        _delete_files(text_files)


def mainrun(args):

    fname = args.filename.strip()

    prefix = construct_prefix(args.input)
    output = determine_output_path(fname, args.output, prefix)

    TEXTLIST = _read_text_inputs(args)

    print(TEXTLIST)

    start_time = convert_to_seconds(args.startat)

    if args.no_clipping:
        cclip = mpy.VideoFileClip(fname)
        cclip = cclip.subclipped(start_time=start_time)
    else:
        cclip = create_shorts_from_vid(fname, startat=start_time, crop_ratio=args.ratio)
    # if Duration is given as negative use the entire Duration of the clip
    if args.time < 0:
        clip_time = cclip.duration
    else:
        clip_time = min(cclip.duration, args.time)
    cclip = cclip.subclipped(0, clip_time)
    audio = cclip.audio

    w, h = cclip.size
    texclips, notisounds = get_text_clips_n_notification(
        TEXTLIST, clip_time=clip_time, wid=w
    )
    new_audioclip = mpy.CompositeAudioClip([audio] + notisounds)

    clip = mpy.CompositeVideoClip([cclip] + texclips)
    clip.audio = new_audioclip
    # clip.fadeout(1)
    clip = clip.with_effects([vfx.FadeOut(1)])

    # basename = os.path.basename(fname)
    # outpath = os.path.join(dirname, "Shorts_{}".format(basename))
    outpath = output
    _write_shorts_text_file(fname, TEXTLIST, args.text_file is not None)

    # make loopable
    # clip = vfx.make_loopable(clip, 1)
    clip = clip.with_effects([vfx.MakeLoopable(1)])

    clip.write_videofile(
        outpath,
        temp_audiofile="out.m4a",
        audio=True,
        audio_codec="aac",
        codec="libx264",
    )
