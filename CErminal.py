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
import sys
import time
import json
import datetime
import globals as G

import utils

from notebook import Notebook
from font_size import FontSize

from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.activity import activity
from sugar3.graphics.alert import Alert
from sugar3.graphics.iconentry import IconEntry
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.colorbutton import ColorToolButton
from sugar3.activity.widgets import EditToolbar
from sugar3.activity.widgets import _create_activity_icon as ActivityIcon


class CErminal(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.background_color = None
        self.text_color = None
        self.font_size = None
        self.button_position = None

        self.load_data()

        self.vbox = Gtk.VBox()

        self.make_toolbar()

        self.notebook = Notebook()
        self.notebook.background_color = self.background_color
        self.notebook.text_color = self.text_color
        self.notebook.font_size = self.font_size
        self.notebook.set_button_position(self.button_position)
        self.notebook.new_terminal()
        self.notebook.connect("page-added", self.set_color)
        self.notebook.connect("can-copy-changed", self.can_copy_changed)
        self.notebook.connect("exit", self._close)

        self.vbox.pack_start(self.notebook, True, True, 0)

        self.set_canvas(self.vbox)
        self.show_all()

        self.button_new.hide()

    def load_data(self):
        if "saved-data" in self.metadata:
            self.background_color = Gdk.Color(*tuple(eval(self.metadata["background-color"])))
            self.text_color = Gdk.Color(*tuple(eval(self.metadata["text-color"])))
            self.font_size = int(self.metadata["font-size"])
            self.button_position = Gtk.PackType.START if self.metadata["button-position"] == "Left" else Gtk.PackType.END
        else:
            self.background_color = Gdk.Color(0, 0, 0)
            self.text_color = Gdk.Color(65535, 65535, 65535)
            self.font_size = 12
            self.button_position = Gtk.PackType.END

    def write_file(self, path):
        background = (self.background_color.red, self.background_color.green, self.background_color.blue)
        text = (self.text_color.red, self.text_color.green, self.text_color.blue)

        self.metadata["saved-data"] = "True"
        self.metadata["background-color"] = json.dumps(list(background))
        self.metadata["text-color"] = json.dumps(list(text))
        self.metadata["font-size"] = str(self.font_size)
        self.metadata["button-position"] = "Left" if self.notebook.button_position == Gtk.PackType.START else "Right"

    def make_toolbar(self):
        toolbar_box = ToolbarBox()
        toolbar = toolbar_box.toolbar

        activity_button = ToolButton()
        activity_button.set_icon_widget(ActivityIcon(None))
        toolbar.insert(activity_button, -1)

        utils.make_separator(toolbar, False)

        edit_toolbar = EditToolbar()
        edit_toolbar.undo.props.visible = False
        edit_toolbar.redo.props.visible = False
        edit_toolbar.separator.props.visible = False
        edit_toolbar.copy.connect("clicked", self.copy_cb)
        edit_toolbar.copy.props.accelerator = "<Ctrl><Shift>C"
        edit_toolbar.paste.connect("clicked", self.paste_cb)
        edit_toolbar.paste.props.accelerator = "<Ctrl><Shift>V"

        self.copy_button = edit_toolbar.copy
        self.copy_button.set_sensitive(False)

        edit_toolbar_button = ToolbarButton(page=edit_toolbar, icon_name="toolbar-edit")
        toolbar_box.toolbar.insert(edit_toolbar_button, -1)

        view_toolbar = Gtk.Toolbar()

        boton_toolbar_view = ToolbarButton(page=view_toolbar, icon_name="toolbar-view")
        toolbar.insert(boton_toolbar_view, -1)

        background_color_button = ColorToolButton()
        background_color_button.set_color(self.background_color)
        background_color_button.set_title("Background color")
        background_color_button.connect("color-set", self.background_color_changed)
        view_toolbar.insert(background_color_button, -1)

        text_color_button = ColorToolButton()
        text_color_button.set_color(self.text_color)
        text_color_button.set_title("Text color")
        text_color_button.connect("color-set", self.text_color_changed)
        view_toolbar.insert(text_color_button, -1)

        item_font_size = FontSize()
        item_font_size.set_font_size(self.font_size, False)
        item_font_size.connect("changed", self.font_size_changed)
        view_toolbar.insert(item_font_size, -1)

        utils.make_separator(view_toolbar, False)

        button_left = Gtk.RadioToolButton()
        button_left.set_icon_name('go-left')
        button_left.set_tooltip_text("Move 'add' button to the left")
        view_toolbar.insert(button_left, -1)

        button_right = Gtk.RadioToolButton.new_from_widget(button_left)
        button_right.set_icon_name('go-right')
        button_right.set_tooltip_text("Move 'add' button to the right")
        view_toolbar.insert(button_right, -1)

        if self.button_position == Gtk.PackType.START:
            button_left.set_active(True)
        elif self.button_position == Gtk.PackType.END:
            button_right.set_active(True)

        button_left.connect("toggled", self.move_button, Gtk.PackType.START)
        button_right.connect("toggled", self.move_button, Gtk.PackType.END)

        view_toolbar.show_all()

        self.button_new = ToolButton("add")
        self.button_new.props.accelerator = "<Ctrl><Shift>T"
        self.button_new.connect("clicked", lambda button: self.notebook.new_terminal())
        toolbar.insert(self.button_new, -1)

        utils.make_separator(toolbar, True)

        button_stop = ToolButton("activity-stop")
        button_stop.props.accelerator = "<Ctrl><Shift>C"
        button_stop.connect("clicked", self._close)
        toolbar.insert(button_stop, -1)

        toolbar.show_all()

        self.set_toolbar_box(toolbar_box)

    def set_color(self, notebook, box, page):
        terminal = box.get_children()[0]
        terminal.set_color_background(self.background_color)
        terminal.set_color_foreground(self.text_color)

    def can_copy_changed(self, notebook, can):
        self.copy_button.set_sensitive(can)

    def get_all_terminals(self):
        terminals = []
        for box in self.notebook.get_children():
            terminals.append(box.get_children()[0])

        return terminals

    def get_current_terminal(self):
        box = self.notebook.get_children()[self.notebook.get_current_page()]
        terminal = box.get_children()[0]

        return terminal

    def copy_cb(self, button):
        terminal = self.get_current_terminal()

        if terminal.get_has_selection():
            terminal.copy_clipboard()

    def paste_cb(self, button):
        terminal = self.get_current_terminal()
        terminal.paste_clipboard()

    def background_color_changed(self, button):
        self.background_color = button.get_color()
        self.notebook.background_color = self.background_color
        for terminal in self.get_all_terminals():
            terminal.set_color_background(self.background_color)

    def text_color_changed(self, button):
        self.text_color = button.get_color()
        self.notebook.text_color = self.text_color
        for terminal in self.get_all_terminals():
            terminal.set_color_foreground(self.text_color)

    def font_size_changed(self, item, size):
        self.font_size = size
        self.notebook.font_size = self.font_size
        for terminal in self.get_all_terminals():
            terminal.set_font_size(self.font_size)

    def move_button(self, button, position):
        self.button_position = position
        self.notebook.set_button_position(self.button_position)

    def _close(self, *args):
        self.close()

