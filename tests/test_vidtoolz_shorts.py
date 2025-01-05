import pytest
import vidtoolz_shorts as w

from argparse import Namespace, ArgumentParser


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
