import json
import os
import re
import sys
from datetime import date
from subprocess import Popen, PIPE

# inspired byhttps://github.com/input-output-hk/jormungandr/blob/master/ci/release-info.py

def read_version(release_file, ref=None):
    """
    Reads the version from the release file,
    and optionally validates it against the given tag reference.
    """
    # p = Popen(
    #     ['cargo', 'read-manifest', '--manifest-path', release_file],
    #     stdout=PIPE
    # )
    # d = json.load(p.stdout)
    # version = d['version']

    # for now, set it to 1.0
    version = '1.0'
    if ref is not None and ref != 'refs/tags/v' + version:
        print(
            '::error file={path}::version {0} does not match release tag {1}'
            .format(version, ref, path=release_file)
        )
        sys.exit(1)
    return version


event_name = sys.argv[1]

date = date.today().strftime('%Y%m%d')

ref = None
if event_name == 'push':
    ref = os.getenv('GITHUB_REF')
    if ref.startswith('refs/tags/'):
        release_type = 'tagged'
    elif ref == 'refs/heads/ci/test/nightly':
        # emulate the nightly workflow
        release_type = 'nightly'
        ref = None
    else:
        raise ValueError('unexpected ref ' + ref)
elif event_name == 'schedule':
    release_type = 'nightly'
else:
    raise ValueError('unexpected event name ' + event_name)

version = read_version('release.ini', ref)
release_flags = ''
if release_type == 'tagged':
    tag = 'v' + version
elif release_type == 'nightly':
    version = re.sub(
        r'^(\d+\.\d+\.\d+)(-.*)?$',
        r'\1-nightly.' + date,
        version,
    )
    tag = 'nightly.' + date
    release_flags = '--prerelease'

for name in 'version', 'date', 'tag', 'release_type', 'release_flags':
    print('::set-output name={0}::{1}'.format(name, globals()[name]))
