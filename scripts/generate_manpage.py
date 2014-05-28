# Copyright 2014 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Generate asciidoc source for qutebrowser based on docstrings."""

import os
import sys
import inspect

sys.path.insert(0, os.getcwd())

import qutebrowser.app
import qutebrowser.commands.utils as cmdutils
from qutebrowser.utils.usertypes import enum


def get_command_doc(name, func):
    """Generates documentation based on a docstring of a command handler.

    The docstring needs to follow the format described in HACKING.
    """
    State = enum('short', 'desc', 'arg_start', 'arg_inside')

    doc = inspect.getdoc(func)
    lines = doc.splitlines()

    cur_state = State.short

    short_desc = []
    long_desc = []
    arg_descs = {}
    cur_arg_name = None

    for line in lines:
        if cur_state == State.short:
            if not line:
                cur_state = State.desc
            else:
                short_desc.append(line.strip())
        elif cur_state == State.desc:
            if line.startswith('Args:'):
                cur_state = State.arg_start
            elif line.strip():
                long_desc.append(line.strip())
        elif cur_state == State.arg_start:
            cur_arg_name, argdesc = line.split(':', maxsplit=1)
            cur_arg_name = cur_arg_name.strip()
            arg_descs[cur_arg_name] = [argdesc.strip()]
            cur_state = State.arg_inside
        elif cur_state == State.arg_inside:
            if not line:
                break
            elif line[4:].startswith(' '):
                arg_descs[cur_arg_name].append(line.strip())
            else:
                cur_arg_name, argdesc = line.split(':', maxsplit=1)
                cur_arg_name = cur_arg_name.strip()
                arg_descs[cur_arg_name] = [argdesc.strip()]

    output = ['=== {}'.format(name)]
    output.append(' '.join(short_desc))
    output.append("")
    output.append(' '.join(long_desc))
    if arg_descs:
        output.append('==== Arguments')
        output.append("")
        for arg, desc in arg_descs.items():
            output.append("* {}: {}".format(arg, ' '.join(desc)))

        output.append("")
    output.append("")
    return '\n'.join(output)


def generate_commands():
    print("== Commands")
    for name, cmd in cmdutils.cmd_dict.items():
        print(get_command_doc(name, cmd.handler))


generate_commands()