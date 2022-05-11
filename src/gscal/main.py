#!/usr/bin/env python
import gi, re, sys, toml, getopt
from importlib import metadata
from os import path

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gscal.gscal import MainWindow

def run():
    # Default configuration
    default_config = {
        "window_resizable": False,
        "sunday_first": False,
        "sunday_color": "#CC0000",
    }

    # Default config file path
    config_path = "~/.config/gscal/gscal.toml"

    try:
        # Parsing options and arguments
        opts, args = getopt.getopt(sys.argv[1:], "hvc:", ["help", "version", "config="])
    except getopt.GetoptError as e:
        print("[ERRROR]", e)
        sys.exit(2)

    # Handling options
    for o, a in opts:
        if o in ["-h", "--help"]:
            f = open(path.dirname(__file__) + "/data/help.txt", "r")
            print(f.read())
            f.close()
            sys.exit()
        elif o in ["-v", "--version"]:
            print("gscal", metadata.version("gscal"))
            sys.exit()
        elif o in ["-c", "--config"]:
            if path.isfile(path.expanduser(a)):
                config_path = a
            else:
                print(f"[WARNING] File {a} not found: reading from default config path.")

    # Handling arguments (not supported)
    for a in args:
        print("[WARNING] Unknown argument:", a)

    try:
        # Importing settings from config file
        config = toml.load(path.expanduser(config_path))

        # For each key of the default config dict
        for i in default_config:
            # If the value type does not match the default type or if sunday_color does not match a hex color pattern it falls back to the default
            if i not in config or type(config[i]) != type(default_config[i]) or (i == "sunday_color" and re.match("^#[0-9a-fA-F]{6}$", config[i]) is None):
                config[i] = default_config[i]
    except FileNotFoundError:
        print("[WARNING] Config file not found: default configuration loaded.")
        config = default_config
    except ValueError as e:
        print(f"[WARNING] Error in the config file: {e}. Default configuration loaded.")
        config = default_config

    # Initializing main window
    win = MainWindow(config)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()

    try:
        # Launching the GTK loop
        Gtk.main()
    except KeyboardInterrupt:
        print("\n[WARNING] Interrupted by user.")

# Run the app when launched as script
if __name__ == "__main__":
    run()
