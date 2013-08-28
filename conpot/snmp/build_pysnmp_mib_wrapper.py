# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import subprocess
import logging
import os
import sys
import re


logger = logging.getLogger(__name__)

BUILD_SCRIPT = 'build-pysnmp-mib'


def mib2pysnmp(mib_file):
    logger.debug('Compiling mib file: {0}'.format(mib_file))
    #force subprocess to use select
    subprocess._has_poll = False
    proc = subprocess.Popen([BUILD_SCRIPT, mib_file], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return_code = proc.returncode

    #if smidump is missing the build script will return 0 instead of failing hence the second check.
    if return_code != 0 or 'Autogenerated from smidump' not in stdout:
        logger.critical('Error while parsing processing MIB file using {0}. STDERR: {1}, STDOUT: {2}'
                        .format(BUILD_SCRIPT, stderr, stdout))
        raise Exception(stderr)
    else:
        logger.debug('Successfully compiled MIB file: {0}'.format(mib_file))
        return stdout


def _get_files(dir, recursive):
    for dir_path, dirs, files in os.walk(dir, followlinks=True):
        for file in files:
            yield os.path.join(dir_path, file)
        if not recursive:
            break


def find_mibs(raw_mibs_dirs, recursive=True):
    file_map = {}
    for raw_mibs_dir in raw_mibs_dirs:
        for file in _get_files(raw_mibs_dir, recursive):
            #check if the file contains MIB definitions
            mib_search = re.search(r'([\w-]+) DEFINITIONS ::= BEGIN', open(file).read(), re.IGNORECASE)
            if mib_search:
                file_map[mib_search.group(1)] = file
    return file_map


def compile_mib(mib_file, output_dir):
    pysnmp_str_obj = mib2pysnmp(mib_file)
    output_filename = os.path.basename(os.path.splitext(mib_file)[0]) + '.py'
    with open(os.path.join(output_dir, output_filename), 'w') as output:
        output.write(pysnmp_str_obj)


if __name__ == '__main__':
    print mib2pysnmp(sys.argv[1])