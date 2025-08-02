import pytest
from vidtoolz_shorts import shorts
import os
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


@patch("vidtoolz_shorts.shorts.construct_prefix")
@patch("vidtoolz_shorts.shorts.determine_output_path")
@patch("vidtoolz_shorts.shorts.create_shorts_from_vid")
@patch("vidtoolz_shorts.shorts.get_text_clips_n_notification")
@patch("vidtoolz_shorts.shorts.mpy.CompositeVideoClip")
@patch("vidtoolz_shorts.shorts.mpy.CompositeAudioClip")
@patch("builtins.open", new_callable=mock_open)
@pytest.mark.parametrize(
    "text_file, time, expected_textlist, expected_clip_time, expected_write_file",
    [
        ("text.txt", 10, ["line1", "line2"], 10, "text.txt"),
        (None, -1, ["hello world"], 20, "/tmp/Shorts.txt"),
    ],
)
def test_mainrun(
    mock_file,
    mock_compositeaudioclip,
    mock_compositevideoclip,
    mock_get_text_clips,
    mock_create_shorts,
    mock_determine_output,
    mock_construct_prefix,
    text_file,
    time,
    expected_textlist,
    expected_clip_time,
    expected_write_file,
):
    args = MagicMock()
    args.filename = "/tmp/test.mp4"
    args.input = [["hello", "world"]]
    args.output = "output.mp4"
    args.text_file = text_file
    args.startat = "0"
    args.time = time
    args.ratio = 1.0

    mock_construct_prefix.return_value = "prefix"
    mock_determine_output.return_value = "output.mp4"

    mock_sub_clip = MagicMock(size=(688, 800), audio="audio")
    mock_initial_clip = MagicMock(duration=20)
    mock_initial_clip.subclipped.return_value = mock_sub_clip
    mock_create_shorts.return_value = mock_initial_clip

    mock_get_text_clips.return_value = (["text_clip"], ["noti_sound"])

    mock_final_clip = MagicMock()
    mock_composite_clip = mock_compositevideoclip.return_value
    mock_composite_clip.with_effects.return_value = mock_final_clip
    mock_final_clip.with_effects.return_value = mock_final_clip

    if text_file:
        mock_file.return_value.readlines.return_value = expected_textlist

    shorts.mainrun(args)

    mock_create_shorts.assert_called_with("/tmp/test.mp4", startat=0.0, crop_ratio=1.0)
    mock_initial_clip.subclipped.assert_called_with(0, expected_clip_time)
    mock_get_text_clips.assert_called_with(
        expected_textlist, clip_time=expected_clip_time, wid=688
    )
    mock_compositeaudioclip.assert_called_with(["audio", "noti_sound"])
    mock_compositevideoclip.assert_called_with([mock_sub_clip, "text_clip"])

    mock_final_clip.write_videofile.assert_called_with(
        "output.mp4",
        temp_audiofile="out.m4a",
        audio=True,
        audio_codec="aac",
        codec="libx264",
    )

    if text_file:
        mock_file.assert_called_with(expected_write_file, "r")
    else:
        mock_file.assert_called_with(expected_write_file, "w")
