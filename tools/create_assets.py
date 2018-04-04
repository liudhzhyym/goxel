#!/usr/bin/python

# Goxel 3D voxels editor
#
# copyright (c) 2016 Guillaume Chereau <guillaume@noctua-software.com>
#
# Goxel is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Goxel is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# goxel.  If not, see <http://www.gnu.org/licenses/>.

# Read all the files in 'data', and create assets.inl with all the data.  For
# text file, we try to keep the data as a string, for binary files we store it
# into a uint8_t array.

from collections import namedtuple
import os

if os.path.dirname(__file__) != "./tools":
    print "Should be run from goxel root directory"
    sys.exit(-1)

TYPES = {
    "png":   { "text": False, },
    "goxcf": { "text": True, },
    "gpl":   { "text": True, },
    "pov":   { "text": True, },
    "ttf":   { "text": False },
    "wav":   { "text": False },
    "ini":   { "text": True },
}
GROUPS = ['fonts', 'icons', 'images', 'other', 'palettes', 'progs',
          'sounds', 'themes']
TEMPLATE = '{{.path = "{path}", .size = {size}, .data =\n{data}\n}},'
File = namedtuple('File', 'path name data size')

HEADER = """/* Goxel 3D voxels editor
 *
 * copyright (c) 2018 Guillaume Chereau <guillaume@noctua-software.com>
 *
 * Goxel is free software: you can redistribute it and/or modify it under the
 * terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later
 * version.

 * Goxel is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 * FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 * details.

 * You should have received a copy of the GNU General Public License along with
 * goxel.  If not, see <http://www.gnu.org/licenses/>.
 */

/* This file is autogenerated by tools/create_assets.py */
"""

def list_files(group):
    ret = []
    for root, dirs, files in os.walk("data/%s" % group):
        for f in files:
            if any(f.endswith('.' + x) for x in TYPES):
                ret.append(os.path.join(root, f))
    return sorted(ret, key=lambda x: x.upper())

def encode_str(data):
    ret = '    "'
    for c in data:
        if c == '\n':
            ret += '\\n"\n    "'
            continue
        if c == '"': c = '\\"'
        if c == '\\': c = '\\\\'
        ret += c
    ret += '"'
    return ret

def encode_bin(data):
    ret = "(const uint8_t[]){\n"
    line = ""
    for i, c in enumerate(data):
        line += "{},".format(ord(c))
        if len(line) >= 70 or i == len(data) - 1:
            ret += "    " + line + "\n"
            line = ""
    ret += "}"
    return ret;

def create_file(f):
    data = open(f).read()
    size = len(data)
    name = f.replace('/', '_').replace('.', '_').replace('-', '_')
    ext = f.split(".")[-1]
    if TYPES[ext]['text']:
        size += 1 # So that we NULL terminate the string.
        data = encode_str(data)
    else:
        data = encode_bin(data)
    return File(f, name, data, size)


for group in GROUPS:
    out = open("src/assets/%s.inl" % group, "w")
    print >>out, HEADER
    files = []
    for f in list_files(group):
        files.append(create_file(f))
    for f in files:
        print >>out, TEMPLATE.format(**f._asdict())
    print >>out, "\n\n"
