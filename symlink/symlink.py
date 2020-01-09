# -*- coding: utf-8 -*-
#
# symlink.py -- Symlink plugin for eog
# Based on the Export to folder plugin by Jendrik Seipp (jendrikseipp@web.de)
#
# Copyright (c) 2019  Pierre Lebedel (p.lebedel@infoject.fr)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import os

from gi.repository import GObject, GLib, Eog, Gio, Gtk

_MENU_ID = 'Symlink'
_ACTION_NAME = 'symlink-in-folder'
_ACTION_NAME_PARENT = 'symlink-for-parent'
_ACTION_NAME_DELETE = 'delete-parent'
_FOLDER_NAME = 'Best'

class SymlinkPlugin(GObject.Object, Eog.WindowActivatable):
    window = GObject.property(type=Eog.Window)

    def __init__(self):
        GObject.Object.__init__(self)
        self.selection_changed_handler_id = None

    @property
    def symlink_dir(self):
        target_dir = os.path.join(os.path.dirname(self.window.get_image().get_file().get_path()), _FOLDER_NAME)

        return target_dir

    def do_activate(self):
        model = self.window.get_gear_menu_section('plugins-section')
        action = Gio.SimpleAction.new(_ACTION_NAME)
        action.connect('activate', self.symlink_cb, self.window)
        self.window.add_action(action)

        parentAction = Gio.SimpleAction.new(_ACTION_NAME_PARENT)
        parentAction.connect('activate', self.symlink_reduced_cb, self.window)
        self.window.add_action(parentAction)

        deleteAction = Gio.SimpleAction.new(_ACTION_NAME_DELETE)
        deleteAction.connect('activate', self.delete_parent_cb, self.window)
        self.window.add_action(deleteAction)

        # Add the menu entry
        menu = Gio.Menu()
        menu.append(_('_Create Symlink'), 'win.' + _ACTION_NAME)
        item = Gio.MenuItem.new_section(None, menu)
        item.set_attribute([('id', 's', _MENU_ID)])
        model.append_item(item)

        # Add accelerator key
        app = Eog.Application.get_instance()
        app.set_accels_for_action('win.' + _ACTION_NAME, ['S', None])
        app.set_accels_for_action('win.' + _ACTION_NAME_PARENT, ['D', None])
        app.set_accels_for_action('win.' + _ACTION_NAME_DELETE, ['<Control>X', None])

    def do_deactivate(self):
        menu = self.window.get_gear_menu_section('plugins-section')
        for i in range(0, menu.get_n_items()):
            value = menu.get_item_attribute_value(i, 'id', GLib.VariantType.new('s'))

            if value and value.get_string() == _MENU_ID:
                menu.remove(i)
                break

        # Disable accelerator key
        app = Eog.Application.get_instance()
        app.set_accels_for_action('win.' + _ACTION_NAME, ['S', None])
        app.set_accels_for_action('win.' + _ACTION_NAME_PARENT, ['D', None])
        app.set_accels_for_action('win.' + _ACTION_NAME_DELETE, ['<Control>X', None])

        self.window.remove_action(_ACTION_NAME)

    def symlink_cb(self, action, parameter, window):
        # Get path to current image.
        image = window.get_image()
        if not image:
            self.error_dialog('Did you forget to open an image ?')
            return
        src = image.get_file().get_path()
        name = os.path.basename(src)
        dest = os.path.join(self.symlink_dir, name)
        # Create directory if it doesn't exist.
        try:
            os.makedirs(self.symlink_dir)
        except OSError:
            pass

        os.symlink(src, dest)
        print('Symlink created for %s into %s' % (name, self.symlink_dir))

    def symlink_reduced_cb(self, action, parameter, window):
        # Get path to current image.
        reducedImage = window.get_image().get_file().get_path()
        if not reducedImage:
            self.error_dialog('Did you forget to open an image ?')
            return

        # Get path to the original image in the parent folder (not the reduced one)
        reducedDir = os.path.dirname(reducedImage)
        fileName = os.path.basename(reducedImage)
        fileShortName = os.path.splitext(fileName)[0]
        fileExtension = os.path.splitext(fileName)[1]
        parentDir = os.path.normpath(os.path.join(reducedDir, os.pardir))
        symlinkDir = os.path.join(parentDir, _FOLDER_NAME)
        symlinkFilename = fileShortName + fileExtension.upper()

        source = self.get_parent_file(reducedImage)
        dest = os.path.join(symlinkDir, symlinkFilename)

        isFile = os.path.isfile(source)
        if not isFile:
            self.error_dialog('Source image does not exists')
            return

        # Create directory if it doesn't exist.
        try:
            os.makedirs(symlinkDir)
        except OSError:
            pass

        os.symlink(source, dest)
        print('Symlink %s created for %s into %s' % (symlinkFilename, fileName, symlinkDir))

    def delete_parent_cb(self, action, parameter, window):
        # Get path to current image.
        reducedImage = window.get_image().get_file().get_path()

        source = self.get_parent_file(reducedImage)
        if not source:
            return

        os.remove(source)
        print('File %s deleted successfuly' % (source))

    def get_parent_file(self, reducedImage):
        if not reducedImage:
            self.error_dialog('Did you forget to open an image ?')
            return

        # Get path to the original image in the parent folder (not the reduced one)
        reducedDir = os.path.dirname(reducedImage)
        fileName = os.path.basename(reducedImage)
        fileShortName = os.path.splitext(fileName)[0]
        fileExtension = os.path.splitext(fileName)[1]
        parentDir = os.path.normpath(os.path.join(reducedDir, os.pardir))
        symlinkFilename = fileShortName + fileExtension.upper()

        source = os.path.join(parentDir, symlinkFilename)

        isFile = os.path.isfile(source)
        if not isFile:
            self.error_dialog('Source image does not exists')
            return

        return source

    def error_dialog(self, message):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "EOG Symlink plugin")
        dialog.format_secondary_text(message)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            dialog.destroy()


