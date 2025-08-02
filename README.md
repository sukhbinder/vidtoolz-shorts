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

```bash
usage: vid shorts [-h] [-t TEXT_FILE] [-i [INPUT ...]] [-d TIME] [-st STARTAT]
                  [-r RATIO] [-o OUTPUT]
                  filename

Create shorts from long form videos

positional arguments:
  filename              File containing the list of files or .mp4 file which
                        is used for shorts

optional arguments:
  -h, --help            show this help message and exit
  -t TEXT_FILE, --text-file TEXT_FILE
                        Text file containing comments (default: None)
  -i [INPUT ...], --input [INPUT ...]
                        Text inputs (default: [])
  -d TIME, --time TIME  Duration of shorts in secs (default: 60)
  -st STARTAT, --startat STARTAT
                        Audio startat ex 30s or 1:15 or 1:24:30 (default: 0.0)
  -r RATIO, --ratio RATIO
                        Size Ratio: ex 9/16 (0.5625), 4/5 (0.8) or (default:
                        1.0)
  -o OUTPUT, --output OUTPUT
                        Path to save the trimmed video.
```


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
