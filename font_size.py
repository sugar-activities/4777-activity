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

from gi.repository import Gtk
from gi.repository import GObject

from sugar3.graphics import style
from sugar3.graphics.icon import Icon


class FontSize(Gtk.ToolItem):

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, [int]),
        }

    def __init__(self):

        Gtk.ToolItem.__init__(self)

        self._font_sizes = [4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 28, 30, 35, 42, 50, 60, 72]

        if style.zoom(100) == 100:
            subcell_size = 15
            default_padding = 6

        else:
            subcell_size = 11
            default_padding = 4

        vbox = Gtk.VBox()
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, True, True, default_padding)

        self._size_down = Gtk.Button()
        self._size_down.set_can_focus(False)
        icon = Icon(icon_name='resize-')
        self._size_down.set_image(icon)
        self._size_down.connect('clicked', self.__font_sizes_cb, False)
        hbox.pack_start(self._size_down, False, False, 5)

        self._default_size = 12
        self._font_size = self._default_size

        self._size_label = Gtk.Label(str(self._font_size))
        hbox.pack_start(self._size_label, False, False, 10)

        self._size_up = Gtk.Button()
        self._size_up.set_can_focus(False)
        icon = Icon(icon_name='resize+')
        self._size_up.set_image(icon)
        self._size_up.connect('clicked', self.__font_sizes_cb, True)
        hbox.pack_start(self._size_up, False, False, 5)

        radius = 2 * subcell_size
        theme_up = "GtkButton {border-radius:0px %dpx %dpx 0px;}" % (
            radius, radius)
        css_provider_up = Gtk.CssProvider()
        css_provider_up.load_from_data(theme_up)

        style_context = self._size_up.get_style_context()
        style_context.add_provider(css_provider_up,
                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

        theme_down = "GtkButton {border-radius: %dpx 0px 0px %dpx;}" % (
            radius, radius)
        css_provider_down = Gtk.CssProvider()
        css_provider_down.load_from_data(theme_down)
        style_context = self._size_down.get_style_context()
        style_context.add_provider(css_provider_down,
                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.add(vbox)
        self.show_all()

    def __font_sizes_cb(self, button, increase):
        if self._font_size in self._font_sizes:
            i = self._font_sizes.index(self._font_size)
            if increase:
                if i < len(self._font_sizes) - 1:
                    i += 1
            else:
                if i > 0:
                    i -= 1
        else:
            i = self._font_sizes.index(self._default_size)

        self._font_size = self._font_sizes[i]
        self._size_label.set_text(str(self._font_size))
        self._size_down.set_sensitive(i != 0)
        self._size_up.set_sensitive(i < len(self._font_sizes) - 1)
        self.emit('changed', self._font_size)

    def set_font_size(self, size, emit=True):
        if size not in self._font_sizes:
            for font_size in self._font_sizes:
                if font_size > size:
                    size = font_size
                    break
            if size > self._font_sizes[-1]:
                size = self._font_sizes[-1]

        self._font_size = size
        self._size_label.set_text(str(self._font_size))

        i = self._font_sizes.index(self._font_size)
        self._size_down.set_sensitive(i != 0)
        self._size_up.set_sensitive(i < len(self._font_sizes) - 1)

        if emit:
            self.emit('changed', self._font_size)

    def get_font_size(self):
        return self._font_size

