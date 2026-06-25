import pytest
from vidtoolz_shorts import shorts
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, mock_open


def test_construct_prefix_empty():
    assert shorts.construct_prefix([]) == "shorts"


def test_construct_prefix_single():
    assert shorts.construct_prefix([["hello"]]) == "hello_#shorts"


def test_construct_prefix_multiple():
    assert (
        shorts.construct_prefix([["hello", "world"], ["foo"]])
        == "hello_world_foo_#shorts"
    )


def test_determine_output_path_no_output():
    assert (
        shorts.determine_output_path("/a/b/c.mp4", None, "prefix")
        == "/a/b/c_prefix.mp4"
    )


def test_determine_output_path_with_output_file():
    assert shorts.determine_output_path("/a/b/c.mp4", "d.mp4", "prefix") == "/a/b/d.mp4"


def test_determine_output_path_with_output_path():
    assert (
        shorts.determine_output_path("/a/b/c.mp4", "/x/y/d.mp4", "prefix")
        == "/x/y/d.mp4"
    )


def test_addcomment():
    comment, nline = shorts.addcomment("this is a test comment", size=10)
    assert comment == "this is a\ntest\ncomment"
    assert nline == 3


@patch("vidtoolz_shorts.shorts.mpy.VideoFileClip")
def test_create_shorts_from_vid(mock_videofileclip):
    mock_subclip = MagicMock()
    mock_subclip.size = (1920, 1080)

    mock_clip = MagicMock()
    mock_clip.subclipped.return_value = mock_subclip

    mock_videofileclip.return_value = mock_clip

    cclip = shorts.create_shorts_from_vid("dummy.mp4", startat=10.0, crop_ratio=0.5)

    mock_videofileclip.assert_called_with("dummy.mp4")
    mock_clip.subclipped.assert_called_with(start_time=10.0)

    mock_subclip.cropped.assert_called_with(x1=690, y1=0, x2=1230, y2=1080)


@patch("vidtoolz_shorts.shorts.mpy.TextClip")
@patch("vidtoolz_shorts.shorts.mpy.AudioFileClip")
def test_get_text_clips_n_notification(mock_audiofileclip, mock_textclip):
    textlist = ["Hello", "World"]
    clip_time = 10

    text_clips, notification_sounds = shorts.get_text_clips_n_notification(
        textlist, clip_time=clip_time
    )

    assert len(text_clips) == 3
    assert len(notification_sounds) == 4
    assert mock_textclip.call_count == 3
    assert mock_audiofileclip.call_count == 4


def test_build_ffmpeg_command_with_text_and_subscribe():
    command = shorts._build_ffmpeg_command(
        "input.mp4",
        "output.mp4",
        ["Entering God's own country, Kerala"],
        10,
        2.5,
        0.5625,
        False,
        True,
        ["/tmp/caption-0.txt", "/tmp/caption-1.txt"],
    )

    assert command[:4] == ["ffmpeg", "-y", "-i", "input.mp4"]
    assert command[-2:] == ["-shortest", "output.mp4"]
    assert command.count(os.path.join(shorts._ASSETS, "notification.mp3")) == 2
    assert command.count(os.path.join(shorts._ASSETS, "subscribe.mp3")) == 1

    filter_complex = command[command.index("-filter_complex") + 1]
    assert "trim=start=2.5:duration=10" in filter_complex
    assert "crop=w='trunc(min(iw\\,ih*0.5625)/2)*2'" in filter_complex
    assert "textfile='/tmp/caption-0.txt'" in filter_complex
    assert "textfile='/tmp/caption-1.txt'" in filter_complex
    assert "font='Helvetica-Bold'" in filter_complex
    assert "fontsize=54" in filter_complex
    assert "borderw=4" in filter_complex
    assert "shadowcolor=black@0.7" in filter_complex
    assert "boxborderw=24" in filter_complex
    assert "x=(w-text_w)/2" in filter_complex
    assert "y=h*0.12" in filter_complex
    assert "fps=30,format=yuv420p,split=2[vloopmain][vloophead]" in filter_complex
    assert (
        "[vloophead]trim=duration=1,setpts=PTS-STARTPTS,fps=30[vloopheadtrim]"
        in filter_complex
    )
    assert (
        "[vloopmain][vloopheadtrim]xfade=transition=fade:duration=1:offset=9[v]"
        in filter_complex
    )
    assert "amix=inputs=4" in filter_complex


def test_build_ffmpeg_filter_complex_without_audio_or_clipping():
    filter_complex = shorts._build_ffmpeg_filter_complex(
        [],
        5,
        0,
        1,
        True,
        False,
        [],
    )

    assert "crop=" not in filter_complex
    assert "drawtext=" not in filter_complex
    assert "xfade=transition=fade:duration=1:offset=4[v]" in filter_complex
    assert "anullsrc=channel_layout=stereo:sample_rate=44100:d=5[a0]" in filter_complex
    assert "[a0]amix=inputs=1" in filter_complex


@patch("vidtoolz_shorts.shorts._run_command")
@patch("vidtoolz_shorts.shorts._ffprobe_has_audio", return_value=True)
@patch("vidtoolz_shorts.shorts._ffprobe_video_size", return_value=(1920, 1080))
@patch("vidtoolz_shorts.shorts._ffprobe_duration", return_value=12.0)
@patch("builtins.open", new_callable=mock_open)
def test_mainrun_ffmpeg(
    mock_file,
    mock_duration,
    mock_video_size,
    mock_has_audio,
    mock_run_command,
):
    args = SimpleNamespace(
        filename="/tmp/input.mp4",
        input=[["Hello"]],
        text_file=None,
        output="/tmp/output.mp4",
        startat="2",
        time=5,
        ratio=1,
        no_clipping=True,
    )

    shorts.mainrun_ffmpeg(args)

    mock_duration.assert_called_once_with("/tmp/input.mp4")
    mock_video_size.assert_called_once_with("/tmp/input.mp4")
    mock_has_audio.assert_called_once_with("/tmp/input.mp4")
    mock_file.assert_called_once_with("/tmp/Shorts.txt", "w")
    command = mock_run_command.call_args.args[0]
    assert command[0] == "ffmpeg"
    assert command[-1] == "/tmp/output.mp4"
    assert "-filter_complex" in command
