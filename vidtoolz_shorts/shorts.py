import moviepy as mpy
import os
import textwrap
import numpy as np
import subprocess
import argparse
from moviepy import vfx
from itertools import cycle
from moviepy.tools import convert_to_seconds

_HERE = os.path.dirname(os.path.abspath(__file__))
_ASSETS = os.path.join(_HERE, "assets")


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


def mainrun(args):

    fname = args.filename.strip()

    TEXTLIST = []
    if args.text_file is not None:
        with open(args.text_file, "r") as fin:
            TEXTLIST = fin.readlines()
    else:
        TEXTLIST = [" ".join(inp) for inp in args.input]

    print(TEXTLIST)

    start_time = convert_to_seconds(args.startat)

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

    dirname = os.path.dirname(fname)
    basename = os.path.basename(fname)
    outpath = os.path.join(dirname, "Shorts_{}".format(basename))
    outpath_tx = os.path.join(dirname, "Shorts.txt")

    if args.text_file is None:
        with open(outpath_tx, "w") as fout:
            fout.write("\n".join(TEXTLIST[:-1]))

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
