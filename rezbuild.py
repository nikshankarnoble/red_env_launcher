#!/usr/bin/env python
import os
import sys

from red_build_tools.builders.generic import GenericBuilder


def build(source_path, build_path, install_path, targets):
    """
    """
    builder = GenericBuilder(source_path, build_path, install_path, targets)
    if "install" in targets:
        builder.install()



if __name__ == "__main__":
    build(
        source_path=os.environ["REZ_BUILD_SOURCE_PATH"],
        build_path=os.environ["REZ_BUILD_PATH"],
        install_path=os.environ["REZ_BUILD_INSTALL_PATH"],
        targets=sys.argv[1:],
    )
