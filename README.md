# vidtoolz-shorts

[![PyPI](https://img.shields.io/pypi/v/vidtoolz-shorts.svg)](https://pypi.org/project/vidtoolz-shorts/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/vidtoolz-shorts?include_prereleases&label=changelog)](https://github.com/sukhbinder/vidtoolz-shorts/releases)
[![Tests](https://github.com/sukhbinder/vidtoolz-shorts/workflows/Test/badge.svg)](https://github.com/sukhbinder/vidtoolz-shorts/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/vidtoolz-shorts/blob/main/LICENSE)

Create shorts from long form videos

## Installation

First install [vidtoolz](https://github.com/sukhbinder/vidtoolz).

```bash
pip install vidtoolz
```

Then install this plugin in the same environment as your vidtoolz application.

```bash
vidtoolz install vidtoolz-shorts
```
## Usage

type ``vidtoolz-shorts --help`` to get help



## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd vidtoolz-shorts
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
