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
