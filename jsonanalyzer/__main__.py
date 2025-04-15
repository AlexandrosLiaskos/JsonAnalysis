# -*- coding: utf-8 -*-
"""
__main__.py: Makes the jsonanalyzer package executable.

Allows running the analyzer directly using `python -m jsonanalyzer <args>`.
"""

import sys
from .cli import main

if __name__ == "__main__":
    main()