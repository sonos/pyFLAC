# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#
#  pyFLAC builder
#
#  Copyright (c) 2011-2021, Sonos, Inc.
#  All rights reserved.
#
# ------------------------------------------------------------------------------

import os
import platform
import subprocess


def get_build_kwargs():
    system = platform.system()
    builder_path = os.path.dirname(os.path.realpath(__file__))
    package_path = os.path.abspath(os.path.join(builder_path, os.pardir))

    build_kwargs = {
        'include_dirs': ['./pyflac/include'],
    }

    if system == 'Darwin':
        architecture = 'darwin-x86_64'
        build_kwargs['libraries'] = ['FLAC.8']
        build_kwargs['library_dirs'] = [os.path.join(package_path, 'libraries', architecture)]
        build_kwargs['extra_link_args'] = ['-Wl,-rpath,@loader_path/libraries/' + architecture]

    elif system == 'Linux':
        if os.uname()[4][:3] == 'arm':
            cpuinfo = subprocess.check_output(['cat', '/proc/cpuinfo']).decode()
            if 'neon' in cpuinfo:
                architecture = 'raspbian-armv7a'
            else:
                architecture = 'raspbian-armv6z'
        else:
            architecture = 'linux-x86_64'

        build_kwargs['libraries'] = ['FLAC-8.3.0']
        build_kwargs['library_dirs'] = [os.path.join(package_path, 'libraries', architecture)]
        build_kwargs['extra_link_args'] = ['-Wl,-rpath,$ORIGIN/libraries/' + architecture]

    elif system == 'Windows':
        if platform.architecture()[0] == '32bit':
            architecture = 'windows-i686'
        else:
            architecture = 'windows-x86_64'

        build_kwargs['libraries'] = ['FLAC-8']
        build_kwargs['library_dirs'] = [os.path.join(package_path, 'libraries', architecture)]
    else:
        raise RuntimeError('%s platform is not supported' % system)

    return build_kwargs
