#!/usr/bin/env python

"""
This module uses the sample.py script to load all test models it finds.

Note: this is not an exhaustive test suite, it does not check the
data structures in detail. It just verifies whether basic
loading and querying of 3d models using impasse works.
"""

import os
import os.path
import sys

import sample
from impasse import errors

# Paths to model files.
BASE_PATHS = [os.path.join('test', 'models'),
              os.path.join('test', 'models-nonbsd')]

# Valid extensions for 3D model files.
extensions = ['.3ds', '.x', '.lwo', '.obj', '.md5mesh', '.dxf', '.ply', '.stl',
              '.dae', '.md5anim', '.lws', '.irrmesh', '.nff', '.off', '.blend']


def run_tests(assimp_repo_path: str):
    ok, err = 0, 0
    paths = [os.path.join(assimp_repo_path, b) for b in BASE_PATHS]
    for path in paths:
        print("Looking for models in %s..." % path)
        for root, dirs, files in os.walk(path):
            for afile in files:
                base, ext = os.path.splitext(afile)
                # Don't want to trigger an OOM!
                if "/invalid" in root:
                    continue
                if ext in extensions:
                    full_path = os.path.join(root, afile)
                    try:
                        sample.main(full_path)
                        ok += 1
                    except errors.AssimpError as error:
                        # Assimp error is fine; this is a controlled case.
                        print(error)
                        err += 1
                    except Exception:
                        print("Error encountered while loading <%s>"
                              % os.path.join(root, afile))
    print('** Loaded %s models, got controlled errors for %s files'
          % (ok, err))


if __name__ == '__main__':
    run_tests(sys.argv[1])
