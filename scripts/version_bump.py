#!/usr/bin/env python
import argparse
import sys

import semver

VERSION_FILE = 'server/__init__.py'
__version__ = "0.0.0"

release_types = ['major', 'minor', 'patch']

parser = argparse.ArgumentParser(description='Prepare for publishing.')
parser.add_argument("--release-type", choices=release_types, help='Type of release', default='patch')
args = parser.parse_args()

exec(open(VERSION_FILE).read())
version = semver.VersionInfo.parse(__version__)

if args.release_type == 'major':
    version = version.bump_major()
if args.release_type == 'minor':
    version = version.bump_minor()
if args.release_type == 'patch':
    version = version.bump_patch()

with open(VERSION_FILE, "w") as f:
    f.write(f"__version__ = '{version}'\n")
    f.close()

exec(open(VERSION_FILE).read())

sys.stdout.write(__version__)
sys.stdout.flush()
sys.exit(0)
