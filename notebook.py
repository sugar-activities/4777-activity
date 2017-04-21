#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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

from terminal import Terminal

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject

from sugar3.graphics.icon import Icon


class NotebookTab(Gtk.HBox):

    __gsignals__ = {
        "remove-tab": (GObject.SignalFlags.RUN_FIRST, None, []),
    }

    def __init__(self):

        Gtk.HBox.__init__(self)

        self.label = Gtk.Label("")
        self.pack_start(self.label, False, False, 0)

        self.button = Gtk.Button()
        self.button.add(Icon(icon_name="remove"))
        self.button.set_relief(Gtk.ReliefStyle.NONE)
        self.button.connect("clicked", lambda button: self.emit("remove-tab"))
        self.pack_end(self.button, False, False, 0)

        self.show_all()

    def set_label(self, label):
        self.label.set_label(label)

    def get_label(self, label):
        return self.label.get_label()


class Notebook(Gtk.Notebook):

    __gsignals__ = {
        "can-copy-changed": (GObject.SignalFlags.RUN_FIRST, None, [bool]),
        "exit": (GObject.SignalFlags.RUN_FIRST, None, []),
    }

    def __init__(self):

        Gtk.Notebook.__init__(self)

        self.button_position = None
        self.background_color = None
        self.text_color = None
        self.font_size = None
        self.button_add = None

        self.set_show_tabs(True)

        self.connect("switch-page", self.check_can_copy)
        self.connect("page-removed", self.page_removed)

    def check_can_copy(self, notebook, box, *args):
        terminal = box.get_children()[0]
        self.emit("can-copy-changed", terminal.get_has_selection())

    def page_removed(self, notebook, *args):
        if self.get_n_pages() == 0:
            self.emit("exit")

    def new_terminal(self, button=None):
        tab = NotebookTab()
        tab.set_label("Terminal " + str(self.get_n_pages() + 1))

        terminal = Terminal()
        terminal.connect("selection-changed", self.selection_changed)
        terminal.connect("window-title-changed", self.tab_title_changed, tab)

        scrollbar = Gtk.VScrollbar.new(terminal.get_vadjustment())

        box = Gtk.HBox()
        box.pack_start(terminal, True, True, 0)
        box.pack_start(scrollbar, False, True, 0)

        index = self.append_page(box, tab)

        tab.connect("remove-tab", self.remove_tab_from_box, box)
        terminal.connect("realize", self.terminal_realize_cb, tab, index)
        terminal.connect("child-exited", self.remove_tab_from_box, box)

        self.set_tab_reorderable(box, True)
        self.child_set_property(box, 'tab-expand', True)
        box.show_all()
        self.show_all()

        self.set_current_page(self.get_n_pages() - 1)

    def terminal_realize_cb(self, terminal, tab, index):
        terminal.set_font_size(self.font_size)
        terminal.grab_focus()

        terminal.set_color_background(self.background_color)
        terminal.set_color_foreground(self.text_color)
        terminal.set_font_size(self.font_size)

    def selection_changed(self, terminal):
        self.emit("can-copy-changed", terminal.get_has_selection())

    def tab_title_changed(self, terminal, tab):
        tab.set_label(terminal.get_window_title())

    def remove_tab_from_box(self, widget, box):
        self.remove_page(self.get_children().index(box))

    def set_button_position(self, position):
        self.button_position = position

        self.button_add = Gtk.Button()
        self.button_add.set_relief(Gtk.ReliefStyle.NONE)
        self.button_add.props.focus_on_click = False
        self.button_add.add(Icon(icon_name='add'))
        self.button_add.connect('clicked', self.new_terminal)
        self.set_action_widget(self.button_add, self.button_position)
        self.button_add.show_all()

        self.button_add.set_tooltip_text("New terminal\nMayus+Ctrl+T")

        if self.button_position == Gtk.PackType.START:
            self.set_action_widget(Gtk.Box(), Gtk.PackType.END)
        elif self.button_position == Gtk.PackType.END:
            self.set_action_widget(Gtk.Box(), Gtk.PackType.START)

