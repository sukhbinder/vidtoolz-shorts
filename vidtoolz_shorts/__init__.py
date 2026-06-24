import vidtoolz
from vidtoolz_shorts.shorts import mainrun, mainrun_ffmpeg


def create_parser(subparser):

    MAX_CLIP_TIME = 60
    parser = subparser.add_parser(
        "shorts", description="Create shorts from long form videos"
    )

    parser.add_argument(
        "filename",
        type=str,
        help="File containing the list of files or .mp4 file  which is used for shorts",
    )
    parser.add_argument(
        "-t",
        "--text-file",
        type=str,
        help="Text file containing comments (default: %(default)s)",
        default=None,
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        nargs="*",
        action="append",
        help="Text inputs (default: %(default)s)",
        default=[],
    )
    parser.add_argument(
        "-d",
        "--time",
        type=int,
        help="Duration of shorts in secs (default: %(default)s)",
        default=MAX_CLIP_TIME,
    )
    parser.add_argument(
        "-st",
        "--startat",
        type=str,
        help="Audio startat ex 30s or 1:15 or 1:24:30 (default: %(default)s)",
        default=0.0,
    )
    parser.add_argument(
        "-r",
        "--ratio",
        type=float,
        help="Size Ratio: ex 9/16 (0.5625), 4/5 (0.8)  or (default: %(default)s)",
        default=1.0,
    )

    parser.add_argument(
        "-o", "--output", type=str, default=None, help="Path to save the trimmed video."
    )

    parser.add_argument(
        "--no-clipping", action="store_true", help="If provided, clip is kept as the input size. Used for video already in 16x9 size"
    )
    parser.add_argument(
        "--ffmpeg",
        action="store_true",
        help="Use ffmpeg instead of MoviePy for rendering.",
    )
    return parser


class ViztoolzPlugin:
    """Create shorts from long form videos"""

    __name__ = "shorts"

    @vidtoolz.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        if args.ffmpeg:
            mainrun_ffmpeg(args)
        else:
            mainrun(args)

    def hello(self, args):
        # this routine will be called when "vidtoolz "shorts is called."
        print("Hello! This is an example ``vidtoolz`` plugin.")


shorts_plugin = ViztoolzPlugin()
