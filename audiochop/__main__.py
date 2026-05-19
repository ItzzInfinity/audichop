"""Run the AudioChop splitter CLI with ``python -m audiochop``."""

import sys

from audiochop.cli import main


if __name__ == "__main__":
    sys.argv[0] = "python3 -m audiochop"
    main()
