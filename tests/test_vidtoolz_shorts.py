import os
from argparse import ArgumentParser
from pathlib import Path

import pytest

import vidtoolz_shorts as w


def test_create_parser():
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    assert parser is not None

    result = parser.parse_args(["hello"])
    assert result.filename == "hello"
    assert result.text_file is None
    assert len(result.input) == 0
    assert result.time == 60
    assert result.startat == 0.0
    assert result.ratio == 1.0


def test_plugin(capsys):
    w.shorts_plugin.hello(None)
    captured = capsys.readouterr()
    assert "Hello! This is an example ``vidtoolz`` plugin." in captured.out


IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_realcase_shorts(tmpdir):
    outfile = tmpdir / "test_intro.mp4"
    testdata = Path(__file__).parent / "test_data"
    introfile = testdata / "test.mp4"
    subparser = ArgumentParser().add_subparsers()
    parser = w.create_parser(subparser)

    argv = [str(introfile), "-o", str(outfile), "-i", "Hello", "-i", "World"]
    args = parser.parse_args(argv)
    args.func = None
    w.shorts_plugin.run(args)
    assert outfile.exists()
