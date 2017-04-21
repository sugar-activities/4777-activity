#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2015, Cristian García <cristian99garcia@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

from gi.repository import Gtk
from gi.repository import Vte
from gi.repository import GLib
from gi.repository import Pango


class Terminal(Vte.Terminal):

    def __init__(self):

        Vte.Terminal.__init__(self)

        # It depends on the version
        if hasattr(self, 'fork_command_full'):
            self.fork_command_full(
                Vte.PtyFlags.DEFAULT,
                os.environ['HOME'],
                ["/bin/sh"], [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                self.start_cb, self.end_cb)
        else:
            self.spawn_sync(
                Vte.PtyFlags.DEFAULT,
                os.environ['HOME'],
                ["/bin/sh"], [],
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                self.start_cb, self.end_cb)

    def start_cb(self, data):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "welcome.txt")

        if os.path.isfile(path):
            f = open(path, "r")
            print(f.read())
            f.close()

    def end_cb(self, data):
        print("\n")

    def set_font_size(self, size):
        font = self.get_font()
        font.set_size(Pango.SCALE * size)
        self.set_font(font)
