#Symlink - EOG Plugin
Plugin for the Eye of Gnome image viewer to create a symlink for the current image in a subfolder


##Installation
Place the two files symlink.py & symlink.plugin in the EOG plugin directory.

Check [the EOG documentation](https://wiki.gnome.org/Apps/EyeOfGnome/Plugins) for the location on your machine.

Note: On Ubuntu 18.04: `/usr/lib/x86_64-linux-gnu/eog/plugins/`

##Configuration
Enable the plugin by going in the application menu -> Preferences -> Plugins tab -> Symlink in folder

Edit the `_FOLDER_NAME` in `symlink.py:28` to the name of your choosing

##Usage
Press the S key to create the symlink. Alternatively, you can click on the Application menu -> Create Symlink
